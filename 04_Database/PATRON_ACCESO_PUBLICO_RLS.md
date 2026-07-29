---
title: "Patrón: Acceso Público con RLS (Token Anónimo)"
category: 04_Database
tags: [rls, seguridad, public-access, supabase]
status: current
---

# Patrón: Acceso Público con RLS (Token Anónimo)

## El Problema
Existen escenarios donde un usuario externo (sin cuenta ni sesión en el sistema) necesita ver o interactuar con un recurso específico. Ejemplos clásicos:
- Un cliente que recibe un link para ver y aceptar una propuesta.
- Un usuario invitado viendo un tablero compartido.

El problema radica en que si la tabla tiene RLS activado (Obligatorio por regla DB-007), un usuario anónimo (Rol `anon`) por defecto no tiene acceso a nada porque no hay un `auth.uid()`.

## La Solución: Token RLS Inyectado

El patrón consiste en generar un UUID único e incognoscible por cada registro compartido y usar ese UUID como "llave" temporal. El cliente frontend envía ese token en los headers de la petición al Worker, y el Worker inyecta este token en la sesión de base de datos antes de hacer la query, permitiendo que las políticas RLS lo lean.

### 1. Esquema SQL (La Llave)

Se añade una columna de token público a la tabla.

```sql
ALTER TABLE proposals ADD COLUMN public_token UUID UNIQUE DEFAULT gen_random_uuid();
CREATE INDEX idx_proposals_public_token ON proposals(public_token);
```

### 2. Política RLS (La Cerradura)

La política concede acceso al rol `anon` **solo si** el token que el Worker inyectó en el contexto de la base de datos coincide con el `public_token` de la fila.

```sql
-- Permitir lectura si el token coincide
CREATE POLICY "Cliente público lee propuesta por token" ON proposals 
FOR SELECT TO anon
USING (
    public_token::text = current_setting('request.jwt.claims', true)::json->>'public_token'
); 

-- Permitir actualización (ej. cambiar estado a aceptado) con el mismo token
CREATE POLICY "Cliente público actualiza estado" ON proposals 
FOR UPDATE TO anon
USING (
    public_token::text = current_setting('request.jwt.claims', true)::json->>'public_token'
)
WITH CHECK (
    status IN ('accepted', 'rejected') -- Evitar que editen otros campos
);
```

### 3. Código del Worker (El Llavero)

El backend extrae el token de la petición (puede venir en la URL `/api/public/proposals/:token` o en un header) y crea un cliente de Supabase asumiendo el rol anónimo, pero **firmando un JWT custom** o usando la API para setear el contexto. 

*Nota en Supabase*: Como Cloudflare Workers no puede usar `set_config` directamente en una pool HTTP sin riesgo de ensuciar la conexión para otros requests, la forma segura es inyectar el token en los JWT claims firmando un token temporal o pasándolo en los headers que Supabase lee nativamente.

```javascript
// src/services/publicProposalService.js
import jwt from '@tsndr/cloudflare-worker-jwt'; // O librería compatible en Edge

export async function getPublicProposal(env, publicToken) {
  // 1. Firmamos un token JWT anónimo que inyecta nuestro claim 'public_token'
  // Esto requiere tener el SUPABASE_JWT_SECRET en el worker
  const token = await jwt.sign({
    role: 'anon',
    public_token: publicToken,
    exp: Math.floor(Date.now() / 1000) + (60 * 5) // Expiración corta (5 min)
  }, env.SUPABASE_JWT_SECRET);

  // 2. Creamos el cliente Supabase pasándole este token JWT
  const supabase = createClient(env.SUPABASE_URL, env.SUPABASE_ANON_KEY, {
    global: {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  });

  // 3. La query pasa transparente; RLS hará el bloqueo si el token es incorrecto
  const { data, error } = await supabase
    .from('proposals')
    .select('id, status, items(...)')
    .single();

  if (error || !data) throw new Error("Propuesta no encontrada o token inválido");
  return data;
}
```

## Reglas de Seguridad Asociadas

1. **[REQUIRED] Rate Limiting Obligatorio:** Todo endpoint que acepte un token público DEBE estar protegido por Rate Limiting estricto (ej. 10 req/min) para evitar ataques de fuerza bruta adivinando UUIDs (ver `05_Security/ESTANDAR_RATE_LIMITING.md`).
2. **[RECOMMENDED] Expiración Lógica:** Si el recurso tiene vida útil corta, añadir una columna `expires_at` y chequearla tanto en la RLS como en el Worker.
3. **[REQUIRED] Un Solo Uso (Si Aplica):** Si el link es para una acción de un solo uso (ej. aceptar propuesta), tras completarse la acción el token público puede regenerarse (`public_token = gen_random_uuid()`) o anularse para invalidar el link original.
