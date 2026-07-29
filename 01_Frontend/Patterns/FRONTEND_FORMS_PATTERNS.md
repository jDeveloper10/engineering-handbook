---
title: "Patrones de Formularios"
category: 01_Frontend
tags: [frontend, formularios, validacion, ux]
summary: "Anatomía del campo, validación en tres momentos con una sola fuente de reglas, tratamiento de errores de servidor, submit, contraseñas y códigos OTP para MFA."
keywords: [formularios, validacion, zod, errores, submit, password, otp, mfa]
updated: 2026-07-27
status: current
---

# FRONTEND FORMS PATTERNS

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) (Nivel 1, especialmente secciones 09 Forms y 13 Accessibility). Sigue el formato de [00_HANDBOOK_FORMAT.md](../../00_HANDBOOK_FORMAT.md).
>
> **Herencia explícita — qué NO cubre este documento:**
> - Login, registro, recuperación de contraseña y layouts de auth → hereda de [FRONTEND_AUTH_PATTERNS.md](../Core/FRONTEND_AUTH_PATTERNS.md). Aquí solo se definen las piezas reutilizables (password toggle, OTP, anatomía de campo) que auth consume.
> - Diseño de estados loading/error/empty genéricos → hereda de [FRONTEND_STATES_PATTERNS.md](FRONTEND_STATES_PATTERNS.md). Aquí solo lo específico de forms (doble submit, foco al error).
> - Tono, glosario y redacción de los mensajes de error → hereda de [FRONTEND_MICROCOPY_STANDARD.md](../UI_Components/FRONTEND_MICROCOPY_STANDARD.md). Aquí se define *cuándo y dónde* aparece el mensaje, no *cómo* se redacta.
> - Contrato del envelope de error de la API y schemas compartidos → `03_API` §04 (envelope) y §08 (schemas zod en paquete compartido).
>
> Este documento define el comportamiento de cualquier formulario del producto: campos, validación, submit, errores de servidor, y los patrones especializados (OTP, wizard, autosave, upload, campos dinámicos).

---

## 1. Anatomía del campo

**[REQUIRED]** Todo campo de formulario tiene esta estructura, en este orden vertical:

```
Label (siempre visible)
[ Input ]                ← placeholder opcional, solo como ejemplo de formato
Texto de ayuda           ← opcional, visible antes de interactuar
Mensaje de error         ← reemplaza o acompaña a la ayuda, debajo del campo
```

Reglas agnósticas:

- El label es **siempre visible** — el placeholder no es un label. Un placeholder puede existir solo como ejemplo de formato (`ej. juan@correo.com`), nunca como única identificación del campo.
- Label e input están **asociados programáticamente** (en HTML: `htmlFor`/`id`), de modo que hacer clic en el label enfoca el input y un lector de pantalla anuncia el label al enfocar.
- El texto de ayuda (formato esperado, restricciones) se muestra **antes** de que el usuario falle, no como castigo después.
- El mensaje de error aparece **debajo del campo al que pertenece**, asociado por `aria-describedby`, y el input marca `aria-invalid="true"` mientras el error esté activo.

**Por qué:** el placeholder desaparece al escribir — el usuario pierde la referencia de qué iba en el campo justo cuando más la necesita (al revisar antes de enviar). La asociación programática no es cosmética: es lo que permite que un lector de pantalla anuncie label + error juntos, y que el error quede ligado a *su* campo y no flotando en la página.

**Implementación de referencia (React + TS):**

```tsx
type FieldProps = {
  id: string;
  label: string;
  help?: string;
  error?: string;
  children: (a11yProps: {
    id: string;
    "aria-invalid": boolean | undefined;
    "aria-describedby": string | undefined;
  }) => React.ReactNode;
};

export function Field({ id, label, help, error, children }: FieldProps) {
  const helpId = help ? `${id}-help` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [errorId, helpId].filter(Boolean).join(" ") || undefined;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      {children({
        id,
        "aria-invalid": error ? true : undefined,
        "aria-describedby": describedBy,
      })}
      {help && !error && (
        <p id={helpId} className="text-sm text-muted-foreground">{help}</p>
      )}
      {error && (
        <p id={errorId} className="text-sm text-destructive">{error}</p>
      )}
    </div>
  );
}

// Uso:
// <Field id="email" label="Correo" help="Lo usaremos para avisos" error={errors.email?.message}>
//   {(a11y) => <input type="email" {...a11y} {...register("email")} />}
// </Field>
```

---

## 2. Validación — 3 momentos, 1 fuente de reglas

### 2.1 Los 3 momentos

**[REQUIRED]** La validación de cada campo sigue esta secuencia, en cualquier formulario:

1. **On-blur la primera vez** — un campo no muestra error mientras el usuario lo escribe por primera vez. Se valida al salir del campo.
2. **On-change después del primer error** — una vez que el campo mostró un error, se revalida en cada tecla, para que el error desaparezca en el instante en que el usuario lo corrige.
3. **On-submit siempre** — el submit valida el formulario completo, independientemente de qué campos fueron tocados.

**Por qué:** validar on-change desde la primera tecla "grita" al usuario por un email incompleto que todavía está escribiendo — genera errores falsos y ansiedad. Validar solo on-submit hace que el usuario descubra todos sus errores de golpe al final. La secuencia blur → change combina lo mejor: silencio mientras escribe, feedback inmediato cuando corrige. (La excepción de feedback positivo en vivo — requisitos de password durante registro — está en `FRONTEND_AUTH_PATTERNS.md` §6 y en la sección 5 de este documento.)

```
❌ El usuario escribe "j" en el campo email y ya ve "Correo inválido" en rojo.
✅ Escribe "juan@gmail" completo, sale del campo → "Falta el dominio." →
   vuelve, escribe ".com" → el error desaparece en esa misma tecla.
```

**Implementación de referencia:** `react-hook-form` con `mode: "onBlur"` + `reValidateMode: "onChange"` implementa exactamente esta secuencia sin código manual.

### 2.2 Fuente de las reglas

**[REQUIRED]** Las reglas de validación viven en el **schema zod compartido con el backend** (`03_API` §08 — el paquete compartido). El formulario importa el schema; **nunca redeclara** reglas (longitudes, regex, campos obligatorios) en el componente.

**[REQUIRED]** El mensaje que ve el usuario para una regla dada es **el mismo** que devolvería el backend para esa regla — el mensaje se define una vez en el schema, no dos veces.

```
❌ El form valida "mínimo 8 caracteres" y el backend "mínimo 10" — el usuario pasa
   la validación local y falla en el servidor con otro mensaje distinto.
✅ zodResolver(sharedSchemas.createProject) — una sola definición, cliente y
   servidor no pueden divergir.
```

**Por qué:** dos declaraciones de la misma regla divergen con el tiempo, siempre. La validación de cliente es UX (feedback inmediato); la del servidor es la de verdad (`05_Security`) — compartir el schema hace que ambas cuenten la misma historia sin costo de sincronización.

**Implementación de referencia:** `useForm({ resolver: zodResolver(createProjectSchema), mode: "onBlur", reValidateMode: "onChange" })` donde `createProjectSchema` se importa del paquete compartido con los Workers.

### 2.3 Validación Asíncrona (Chequeos en vivo)

**[REQUIRED]** Cuando la validación requiere consultar a la API (ej: verificar si un email ya existe, si un slug está disponible), se usa **debounce** para no bombardear el servidor por cada tecla.

- Siempre debounce **> 300ms** (500ms recomendado).
- Abortar request anterior si el usuario sigue tecleando (`AbortController`).
- Mostrar indicador de carga (spinner) DENTRO del input durante la validación.

**Implementación de referencia:**
```tsx
const checkEmailUnique = useDebouncedCallback(async (value: string) => {
  const { exists } = await api.checkEmail(value);
  // Retorna string si hay error (lo agarra react-hook-form), true si pasa
  return exists ? 'El email ya está registrado' : true;
}, 500);
```

---

## 3. Errores de servidor

El cliente valida primero, pero el servidor siempre revalida y puede rechazar por razones que el cliente no puede conocer (unicidad, permisos, estado del recurso).

**[REQUIRED]** La respuesta de error de la API (envelope de `03_API` §04, con `error.code` y opcionalmente `error.details`) se mapea así:

- Si el error trae `details` con referencia a campos → el mensaje se muestra **en el campo concreto**, con la misma anatomía de la sección 1 (como si lo hubiera detectado la validación local).
- Si el error es global (sin campo identificable: conflicto, permiso, fallo de red) → se muestra **un solo error a nivel de formulario**, encima del botón de submit, anunciado por `aria-live` (sección 10).

**[REQUIRED]** Un error de servidor **nunca borra lo que el usuario tecleó**. El formulario conserva todos los valores; solo cambia el estado de error.

**[RECOMMENDED]** Mantener un mapa explícito `error.code → campo/mensaje` por formulario, con un caso default para códigos no mapeados (mensaje global accionable, sin código crudo — redacción según `FRONTEND_MICROCOPY_STANDARD.md`; diseño del estado de error según `FRONTEND_STATES_PATTERNS.md` §3).

```
❌ Submit falla por email duplicado → banner rojo genérico arriba y el form se resetea.
✅ Submit falla con code EMAIL_TAKEN → el error aparece bajo el campo email
   ("Ese correo ya está registrado."), el resto del form queda intacto.
```

**Por qué:** perder lo tecleado tras un error es la forma más rápida de perder el submit entero — el usuario que tiene que reescribir 10 campos abandona. Y un error global para un problema de un campo obliga al usuario a adivinar cuál corregir.

**Implementación de referencia:**

```tsx
import type { UseFormSetError, FieldValues, Path } from "react-hook-form";
import type { ApiError } from "@acme/shared"; // envelope tipado de 03_API §04

// Mapa por formulario: code → campo. Solo los códigos que este form puede recibir.
const FIELD_BY_CODE: Record<string, string> = {
  EMAIL_TAKEN: "email",
  SLUG_TAKEN: "slug",
};

export function applyServerErrors<T extends FieldValues>(
  error: ApiError,
  setError: UseFormSetError<T>,
) {
  // 1) details con campos → error en el campo concreto, mismo mensaje del schema
  // (contrato 03_API §04: `details` es un array de { field, message })
  if (error.details?.length) {
    for (const { field, message } of error.details) {
      setError(field as Path<T>, { type: "server", message });
    }
    return;
  }
  // 2) code conocido sin details → mapa explícito
  const field = FIELD_BY_CODE[error.code];
  if (field) {
    setError(field as Path<T>, { type: "server", message: error.message });
    return;
  }
  // 3) default → error global del form (root), nunca código crudo al usuario
  setError("root.server" as Path<T>, {
    type: "server",
    message: "No pudimos guardar los cambios. Inténtalo nuevamente.",
  });
}
```

El error `root.server` se renderiza encima del botón de submit, dentro de la región `aria-live` (sección 11).

---

## 4. Submit

### 4.1 Estado del botón y doble submit

**[REQUIRED]** Durante el request, el botón de submit muestra estado de loading y queda deshabilitado — mismo patrón `idle → submitting → success | error` de `FRONTEND_ENGINEERING_STANDARD.md` 9.3; el diseño visual del loading hereda de `FRONTEND_STATES_PATTERNS.md` §1 (spinner en botón = acción puntual corta).

**[REQUIRED]** Prevención de doble submit: mientras hay un request en vuelo, un segundo submit (clic repetido, Enter, doble clic) **no dispara un segundo request**. Deshabilitar el botón es la primera barrera; el handler además ignora submits si `isSubmitting`.

**Por qué:** el doble submit no es un problema cosmético — crea recursos duplicados, cobra dos veces, envía dos correos. La idempotencia real vive en el backend (`03_API`), pero el frontend no debe depender de ella para el caso común.

### 4.2 Foco al primer error tras submit fallido

**[REQUIRED]** Si el submit falla por validación (local o de servidor mapeada a campos), el foco se mueve **al primer campo con error**, en orden visual del formulario, con scroll para que el campo y su mensaje queden visibles.

**Por qué:** en un formulario largo, el error puede estar fuera del viewport — sin foco + scroll, el usuario ve que "no pasó nada" al hacer clic en enviar y no sabe por qué. Mover el foco resuelve al usuario vidente (scroll) y al usuario de lector de pantalla (anuncio del campo + error asociado) con el mismo gesto.

**Implementación de referencia:**

```tsx
// react-hook-form ya enfoca el primer error de validación local
// (shouldFocusError: true, default). Para errores de SERVIDOR mapeados
// a campos, replicamos ese comportamiento manualmente:

function focusFirstError(form: HTMLFormElement) {
  const firstInvalid = form.querySelector<HTMLElement>('[aria-invalid="true"]');
  if (firstInvalid) {
    firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
    firstInvalid.focus({ preventScroll: true });
  }
}

const onSubmit = handleSubmit(async (values) => {
  const res = await api.createProject(values);
  if (!res.ok) {
    applyServerErrors(res.error, setError); // mapa code → setError (sección 3)
    requestAnimationFrame(() => formRef.current && focusFirstError(formRef.current));
    return;
  }
  onSuccess(res.data);
});
```

### 4.3 Qué hacer con el éxito

**[RECOMMENDED]** Según contexto:

- **Redirect** cuando el submit crea/lleva a un recurso con pantalla propia (crear proyecto → detalle del proyecto). El destino confirma el éxito por sí mismo; opcionalmente un toast breve.
- **Confirmación inline** (mensaje de éxito + form reseteado o valores actualizados) cuando el usuario se queda en la misma pantalla (guardar ajustes, editar perfil).

**Por qué:** redirigir tras guardar ajustes desorienta ("¿guardó?"); quedarse en la pantalla tras crear un recurso obliga a navegar a mano hasta él. La regla es: el usuario debe *ver* la consecuencia de su acción sin adivinarla.

---

## 5. Password

Los flujos completos (login, registro, recuperación) heredan de `FRONTEND_AUTH_PATTERNS.md` §§3-7. Este documento define las piezas del campo password que esos flujos consumen:

- **[REQUIRED]** Toggle mostrar/ocultar: oculta por defecto, botón accesible por teclado dentro del campo, con label accesible ("Mostrar contraseña" / "Ocultar contraseña") que refleja la acción, no el estado.
- **[REQUIRED]** `autocomplete` correcto según contexto: `current-password` en login, `new-password` en registro y en cambio/reset de contraseña. `autocomplete="new-password"` en los **dos** campos (password y confirmación).
- **[REQUIRED]** Reglas de contraseña visibles **antes** de fallar, actualizándose mientras se escribe (hereda de `FRONTEND_AUTH_PATTERNS.md` §6 — es la excepción legítima al "no on-change agresivo": aquí el feedback en vivo es positivo/informativo, no un grito de error).
- **[RECOMMENDED]** Medidor de fortaleza **solo en registro/creación** de contraseña — nunca en login (la contraseña ya existe; medirla ahí es ruido y filtra información en pantalla).

**Por qué el autocomplete importa:** es lo que le dice al gestor de contraseñas del navegador si debe *rellenar* la existente o *proponer* una nueva. Con el valor equivocado, el gestor rellena la contraseña vieja en el campo de "nueva contraseña" — el usuario "cambia" su contraseña por la misma, o el gestor no guarda la nueva. Es un atributo, no una feature: su ausencia rompe silenciosamente a todos los usuarios de gestores.

**Implementación de referencia (toggle):**

```tsx
export function PasswordInput({
  autoComplete, // "current-password" en login, "new-password" en registro/reset
  ...a11y       // id, aria-invalid, aria-describedby — vienen de <Field> (sección 1)
}: { autoComplete: "current-password" | "new-password" } & React.ComponentProps<"input">) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="relative">
      <input
        {...a11y}
        type={visible ? "text" : "password"}
        autoComplete={autoComplete}
        className="w-full pr-10"
      />
      <button
        type="button" // nunca submit — el toggle no debe enviar el form
        onClick={() => setVisible((v) => !v)}
        aria-label={visible ? "Ocultar contraseña" : "Mostrar contraseña"}
        className="absolute inset-y-0 right-2 flex items-center"
      >
        {visible ? <EyeOffIcon aria-hidden /> : <EyeIcon aria-hidden />}
      </button>
    </div>
  );
}
```

Detalle no negociable del ejemplo: el toggle es `type="button"` — un botón sin tipo dentro de un `<form>` es `submit` por defecto y enviaría el formulario al querer ver la contraseña.

---

## 6. OTP / MFA

**[REQUIRED]** El campo de código de un solo uso cumple, sea input segmentado (una caja por dígito) o input único:

- `autocomplete="one-time-code"` e `inputmode="numeric"` — habilita el autollenado desde SMS/gestor en móvil.
- **Pegar el código completo funciona** — pegar "482913" en cualquier posición rellena todo el campo/las cajas. En el segmentado, escribir un dígito avanza al siguiente y Backspace retrocede.
- Un solo label para el grupo — las cajas individuales no son 6 campos independientes para un lector de pantalla.

**[REQUIRED]** El reenvío del código tiene **cooldown visible** ("Reenviar código (0:42)") — el botón deshabilitado muestra cuánto falta, no falla en silencio ni desaparece.

**[RECOMMENDED]** Input único (no segmentado) como default — el segmentado es estético pero es donde viven todos los bugs de foco/pegado; si se usa, debe pasar las reglas de arriba.

**Por qué:** el flujo real del usuario es *copiar el código del SMS/email y pegarlo* — un input segmentado que solo acepta tecleo dígito a dígito rompe el camino más común. Y el cooldown visible evita el spam de reenvíos y la duda de "¿me llegó? ¿lo reenvío?".

**Implementación de referencia (input único):**

```tsx
export function OtpInput({ length = 6, onComplete }: { length?: number; onComplete: (code: string) => void }) {
  const [code, setCode] = useState("");

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    // Acepta tecleo Y pegado: filtra a dígitos, recorta a la longitud
    const digits = e.target.value.replace(/\D/g, "").slice(0, length);
    setCode(digits);
    if (digits.length === length) onComplete(digits);
  }

  return (
    <Field id="otp" label="Código de verificación" help={`Te enviamos un código de ${length} dígitos`}>
      {(a11y) => (
        <input
          {...a11y}
          value={code}
          onChange={handleChange}
          autoComplete="one-time-code"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={length}
          className="tracking-[0.5em] text-center text-lg"
        />
      )}
    </Field>
  );
}
```

---

## 7. Wizard multi-paso

**[RECOMMENDED]** Un formulario se divide en wizard solo cuando supera ~7 campos **y** existe una agrupación natural en pasos con sentido propio (datos personales → datos de facturación → confirmación). Menos campos, o campos sin agrupación lógica, permanecen en un solo formulario — el wizard agrega clics y fricción; solo se justifica cuando reduce carga cognitiva real.

Cuando hay wizard:

- **[REQUIRED]** Indicador de progreso visible: en qué paso estoy, cuántos hay ("Paso 2 de 4 — Facturación"), con nombre de paso, no solo números.
- **[REQUIRED]** Validación **por paso**: "Siguiente" valida solo los campos del paso actual (sub-schema del schema zod compartido, p. ej. `.pick()`); no se puede avanzar con el paso actual inválido, y no se acusan errores de pasos aún no visitados.
- **[REQUIRED]** Estado persistente entre pasos: avanzar y **volver atrás nunca pierde datos** — todos los pasos escriben sobre el mismo estado del formulario; los pasos no visibles se ocultan, no se desmontan con pérdida de valores.
- **[REQUIRED]** El submit real (al backend) ocurre una sola vez al final, validando el schema completo — los pasos intermedios no crean recursos parciales salvo diseño explícito de borrador (ver autosave, sección 8).
- **[RECOMMENDED]** Al entrar a un paso, el foco se mueve al encabezado del paso (con `tabIndex={-1}`), para que teclado y lector de pantalla sepan que el contenido cambió.

**Por qué volver atrás sin perder datos es REQUIRED:** revisar un dato anterior es un movimiento normal, no una cancelación — un wizard que castiga el "atrás" con pérdida de datos enseña al usuario a no verificar, o a abandonar.

**Implementación de referencia:** un solo `useForm` con el schema completo compartido por todos los pasos; cada "Siguiente" llama `trigger(camposDelPaso)` y solo avanza si pasa; los pasos renderizan condicionalmente pero el estado vive en el form, no en cada paso.

---

## 8. Autosave

**[RECOMMENDED]** Autosave (guardado automático como borrador) en formularios **largos de contenido** — editores de texto, descripciones extensas, formularios que toman varios minutos y cuyo valor es el contenido en sí.

- Guardado con **debounce** (~1-2s tras dejar de escribir — suficiente para no guardar en cada tecla, corto para no perder casi nada ante un cierre) y con indicador de estado visible: "Guardando…" → "Guardado".
- El indicador nunca miente: "Guardado" solo cuando el servidor confirmó. Si el autosave falla, se comunica ("No se pudo guardar — reintentando") en vez de fingir éxito.

**[REQUIRED]** **Nunca** autosave en formularios con submit transaccional — pagos, órdenes, transferencias, cualquier form donde "enviar" ejecuta una acción con efectos. En esos, el único envío de datos es el submit explícito del usuario.

**Por qué:** en un form de contenido, perder 20 minutos de escritura por una pestaña cerrada es catastrófico y el guardado parcial es inocuo — autosave es puro beneficio. En un form transaccional es al revés: un "guardado" automático puede disparar o dejar a medias una acción con consecuencias reales, y el usuario pierde la certeza de que *nada pasa hasta que él confirma*. Esa certeza es la base de la confianza en un checkout.

**Implementación de referencia (esquema):**

```tsx
type SaveState = "idle" | "saving" | "saved" | "error";

// watch() de react-hook-form + debounce; el estado del indicador
// solo pasa a "saved" cuando el servidor confirmó (res.ok).
useEffect(() => {
  const sub = watch((values) => {
    setSaveState("saving");
    debouncedSave(values); // ~1-2s; internamente: api.saveDraft →
                           // ok ? setSaveState("saved") : setSaveState("error")
  });
  return () => sub.unsubscribe();
}, [watch]);

// Indicador junto al título del form, en región aria-live="polite":
// "Guardando…" | "Guardado" | "No se pudo guardar — reintentando"
```

### 8.1 Protección contra pérdida de datos (Dirty State)

**[REQUIRED]** En formularios sin Autosave, perder datos por cerrar la pestaña accidentalmente es catastrófico. Todo formulario largo de creación/edición debe implementar protección.

**Estrategia:**
1. Activar flag `isDirty` cuando los valores actuales difieren de `initialValues`.
2. Bloquear navegación nativa (cerrar pestaña) con `beforeunload`.
3. Bloquear navegación interna (cambio de ruta en el SPA) con un Router guard.
4. Mostrar modal de confirmación: *"Tienes cambios sin guardar. ¿Seguro que quieres salir y descartarlos?"*

**Edge cases (Casos límite):**
- Si el usuario hace logout con un form "sucio" → salvar a `localStorage` de emergencia.
- Si la API falla al guardar (500, timeout) → **nunca** descartar los datos. Mantener el form intacto y mostrar un toast de error.

---

## 9. File upload

**[REQUIRED]** El área de carga acepta **drag-and-drop y clic** (input file real, accesible por teclado) — nunca solo drag-and-drop, que es inoperable por teclado y en móvil.

**[REQUIRED]** Tipo y tamaño se validan **en el cliente, antes de subir**, contra los límites definidos en el contrato compartido con el backend. **Por qué antes de subir:** rechazar un archivo de 80MB *después* de subirlo desperdicia minutos del usuario y ancho de banda para un "no" que se conocía desde el byte cero. Y la validación de cliente es solo UX: **el servidor revalida siempre** (`05_Security`) — el límite del cliente puede saltarse con una request manual; el del servidor no.

**[REQUIRED]** Estados por archivo, no solo globales — en carga múltiple, cada archivo tiene su propio estado (en cola / subiendo con progreso / listo / error con motivo y reintento). Un archivo rechazado no bloquea ni descarta a los demás.

- **[RECOMMENDED]** Barra o porcentaje de progreso para archivos donde la subida es perceptible (regla práctica hoy: >1MB o >2s); un spinner indefinido no dice si avanza (`FRONTEND_STATES_PATTERNS.md` §1).
- **[RECOMMENDED]** Preview para imágenes (miniatura local vía object URL antes de que termine la subida) + nombre y peso para cualquier tipo de archivo, con acción de quitar antes del submit.

**Implementación de referencia (validación previa a la subida):**

```tsx
import { UPLOAD_LIMITS } from "@acme/shared"; // mismos límites que valida el Worker

type FileCheck = { ok: true } | { ok: false; reason: string };

function validateFile(file: File): FileCheck {
  if (!UPLOAD_LIMITS.acceptedTypes.includes(file.type)) {
    return { ok: false, reason: "Formato no admitido. Usa JPG, PNG o PDF." };
  }
  if (file.size > UPLOAD_LIMITS.maxBytes) {
    const maxMb = Math.round(UPLOAD_LIMITS.maxBytes / 1024 / 1024);
    return { ok: false, reason: `El archivo supera el límite de ${maxMb} MB.` };
  }
  return { ok: true };
}

// En el handler de drop/change: los archivos inválidos entran a la lista
// con estado "error" y su motivo; los válidos inician subida con progreso.
// El servidor revalida tipo real (magic bytes) y tamaño — 05_Security.
```

---

## 10. Dynamic forms (campos condicionales)

Campos que aparecen/desaparecen según respuestas previas ("¿Facturas como empresa?" → aparece RUC/razón social):

- **[REQUIRED]** El campo nuevo aparece **inmediatamente después** (en orden DOM y visual) del campo que lo disparó — nunca en otra parte de la página donde el usuario (y el orden de tabulación) no lo encuentre.
- **[REQUIRED]** Mostrar u ocultar campos **nunca roba el foco**: el foco permanece en el control que el usuario estaba operando. Un radio/checkbox que al marcarse teletransporta el foco rompe la navegación por teclado.
- **[REQUIRED]** Los campos ocultos **no validan ni bloquean el submit**: el schema refleja la condicionalidad (en zod: uniones discriminadas / `superRefine`), no se "esconde el error de un campo invisible".
- **[RECOMMENDED]** Al ocultarse, el valor del campo se conserva en el estado mientras dure la sesión del formulario (si el usuario alterna la opción, recupera lo que había escrito), pero **se excluye del payload** cuando la condición final lo deja fuera.

**Por qué:** el peor bug de un form dinámico es el submit bloqueado por un campo que el usuario no puede ver — no hay forma de corregir lo invisible. El segundo peor es el foco saltando solo: para un usuario de teclado o lector de pantalla equivale a que la página lo mueva de sitio sin avisar.

---

## 11. Accesibilidad transversal

Lo general (contraste, `focus-visible`, targets táctiles, semántica) hereda de `FRONTEND_ACCESSIBILITY_STANDARD.md` — no se repite aquí. Lo específico de formularios:

**[REQUIRED]**

- Todo el formulario es **operable 100% por teclado**: cada control (incluidos toggle de password, quitar archivo, pasos del wizard, dropzones) es alcanzable con Tab y accionable con Enter/Espacio, en orden visual.
- Grupos de radio buttons y checkboxes relacionados van dentro de `fieldset` con `legend` — el label del grupo ("Método de pago") es el legend, no un texto suelto que el lector de pantalla no asocia a las opciones.
- Errores **anunciados**, no solo pintados: el error global del formulario vive en una región `aria-live="polite"` (o `role="alert"` si es bloqueante); los errores por campo se anuncian vía `aria-describedby` + `aria-invalid` al enfocar el campo (sección 1) y vía el foco al primer error (sección 4.2).
- `Enter` envía el formulario desde cualquier input de texto (form semántico con botón `type="submit"` — no un `div` con `onClick`).

**Por qué `fieldset`/`legend`:** un usuario vidente asocia las opciones a su título por proximidad visual; un lector de pantalla solo lo hace si la asociación existe en el markup — sin legend, el usuario escucha "Tarjeta" sin saber "¿tarjeta de qué pregunta?".

---

## 12. Anti-patrones

- ❌ Placeholder como único label (desaparece al escribir).
- ❌ Validación on-change desde la primera tecla, gritando errores mientras el usuario aún escribe.
- ❌ Reglas de validación redeclaradas en el componente en vez de importar el schema compartido.
- ❌ Error de servidor que resetea el formulario o se muestra global cuando la API señaló el campo.
- ❌ Botón de submit que permite doble clic con request en vuelo.
- ❌ Submit fallido sin mover el foco ni el scroll al primer error.
- ❌ Input OTP segmentado donde pegar el código no funciona.
- ❌ Wizard que pierde datos al volver atrás.
- ❌ Autosave en un formulario de pago.
- ❌ Upload que valida tamaño/tipo después de subir, o solo-drag-and-drop sin input clicable.
- ❌ Campo condicional invisible que bloquea el submit con un error que no se puede ver.
- ❌ Grupo de radios sin `fieldset`/`legend`.

---

## Checklist rápido antes de dar por terminado un formulario

- [ ] ¿Todo campo tiene label visible asociado por `htmlFor`, ayuda antes del error, y error debajo con `aria-describedby` + `aria-invalid`?
- [ ] ¿Validación on-blur la primera vez, on-change tras el primer error, on-submit siempre?
- [ ] ¿Las reglas vienen del schema zod compartido con el backend — cero reglas redeclaradas, mismo mensaje?
- [ ] ¿Errores de servidor mapeados a campo cuando hay `details`, globales cuando no, sin perder jamás lo tecleado?
- [ ] ¿Botón con loading + disabled durante el request, sin posibilidad de doble submit?
- [ ] ¿Submit fallido mueve foco + scroll al primer campo con error?
- [ ] ¿Éxito con redirect o confirmación inline según contexto, nunca silencio?
- [ ] ¿Password con toggle, `autocomplete` correcto (`current-password`/`new-password`), reglas visibles antes de fallar, medidor solo en registro?
- [ ] ¿OTP con `autocomplete="one-time-code"`, pegado completo funcional, reenvío con cooldown visible?
- [ ] ¿Wizard solo si >7 campos con agrupación natural — progreso visible, validación por paso, atrás sin perder datos?
- [ ] ¿Autosave con debounce e indicador honesto solo en forms de contenido — nunca en forms transaccionales?
- [ ] ¿Upload con drag-and-drop + clic, validación de tipo/tamaño antes de subir, progreso y estados por archivo?
- [ ] ¿Campos dinámicos que aparecen junto a su disparador, sin robar foco, sin validar ocultos?
- [ ] ¿Operable 100% por teclado, `fieldset`/`legend` en grupos, errores anunciados por `aria-live`?
