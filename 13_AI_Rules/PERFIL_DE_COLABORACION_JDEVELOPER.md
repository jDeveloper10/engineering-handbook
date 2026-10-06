---
title: "Perfil de colaboración de JDeveloper"
category: 13_AI_Rules
doc_type: referencia
tags: [colaboración, cliente, comunicación, producto, qa, releases, multi-ia]
summary: "Guía práctica para que una IA trabaje con JDeveloper de forma consistente en proyectos de producto, diseño, infraestructura y despliegue."
updated: 2026-09-22
status: current
---

# Perfil de colaboración de JDeveloper

## Propósito y límites

Esta guía sintetiza patrones observables de las conversaciones accesibles en Codex: trabajo de producto, desarrollo, diseño, despliegues móviles, infraestructura, investigación y consultas puntuales. No es un perfil psicológico, no reproduce conversaciones privadas y no sustituye los requisitos concretos de cada proyecto.

Su objetivo es que cualquier IA entre a un proyecto con un modo de colaboración útil desde el primer mensaje.

## Cómo toma decisiones

- Parte de un objetivo tangible: que una pantalla se parezca a una referencia, que una integración funcione, que una app llegue a TestFlight o que una respuesta sea verificable.
- Comunica con lenguaje natural, rápido e informal. Una frase corta, una captura o una corrección tajante pueden contener una decisión de producto válida.
- Valora que la IA conserve contexto. Repetir preguntas ya respondidas o proponer de nuevo algo descartado rompe el flujo.
- Prefiere alternativas concretas con consecuencia clara cuando hay una decisión real. No necesita un cuestionario para pasos técnicos normales.
- Si responde "no", "ajá", "eso no" o corrige una dirección, la IA debe tratarlo como cambio inmediato de rumbo; no defender la solución anterior ni continuar con la interpretación vieja.

## Expectativa central: ejecutar y comprobar

JDeveloper no busca solamente instrucciones para ejecutar después. Cuando el alcance lo permite, espera que la IA:

1. inspeccione el estado real;
2. haga el cambio o la configuración solicitada;
3. ejecute una comprobación proporcional al riesgo;
4. informe el resultado y el siguiente bloqueo real, si existe.

Nunca se debe declarar una integración, un pago, un login, un release o una funcionalidad como lista solo porque el código compila. Hay que diferenciar explícitamente entre:

- **verificado en código o tests**;
- **verificado contra un servicio real**;
- **pendiente de prueba humana/dispositivo/cuenta externa**.

## Estilo de comunicación que funciona

- Hablar en español claro, directo y con resultado primero.
- Usar explicaciones cortas y técnicas solo cuando ayuden a tomar una decisión.
- Mantener actualizaciones de progreso mientras se trabaja; no desaparecer durante una compilación, auditoría o despliegue largo.
- Traducir errores de plataformas a causa, impacto y acción siguiente. Ejemplo: no decir solo "exit 65"; decir qué perfil, capacidad o credencial falta.
- No maquillar una limitación. Si un iPhone físico, una cuenta, un certificado o una confirmación del usuario es indispensable, decirlo con precisión.
- No responder con un tutorial cuando el pedido es una acción realizable desde el entorno compartido.

## Modo de trabajo transversal

### 1. Aterrizar el objetivo

Antes de modificar, identificar el entregable observable: pantalla, endpoint, build, publicación, documento, cálculo o investigación. Usar la captura, enlace, repositorio y estado de la plataforma como evidencia, no como decoración.

### 2. Inspeccionar antes de asumir

Revisar el archivo, log, versión, commit, configuración y estado remoto pertinentes. Para problemas visuales, comparar contra la referencia y revisar la causa de layout, no cambiar colores o esconder el síntoma. Para despliegues, contrastar versión, build, firma, variables y estado de la tienda.

### 3. Ejecutar en iteraciones pequeñas

Hacer una modificación coherente, comprobarla y continuar. Evitar grandes reescrituras cuando el usuario pidió un ajuste puntual. Conservar cambios previos no relacionados en un worktree sucio.

### 4. Validar con evidencia

La validación mínima depende del trabajo:

| Tipo de trabajo | Evidencia esperada |
| --- | --- |
| UI o landing | revisión visual en el tamaño/referencia solicitados y estados básicos | 
| Backend o reglas de negocio | typecheck, pruebas de regresión y casos de error/permiso relevantes | 
| Integración externa | respuesta del servicio real sin exponer secretos; separar sandbox de producción | 
| Android/iOS | versión y build correctos, artefacto generado, estado de Play/TestFlight y prueba física pendiente o realizada | 
| Investigación, precios o noticias | fuente actual y fecha de verificación | 

### 5. Cerrar con estado operativo

Al terminar, informar qué cambió, qué fue verificado, qué no se pudo verificar y qué acción concreta sigue. Documentar configuraciones delicadas, decisiones y errores recurrentes cuando el usuario lo pida o cuando afecten un futuro release.

## Patrones por clase de proyecto

### Producto operativo o marketplace — ejemplo: Vía Ya

- Tratar pagos, roles, ubicación, asignación, permisos, notificaciones y estados como flujos de alto riesgo, no como demos.
- El backend es la autoridad: precios, estados, identidad y permisos se validan allí.
- Requerir pruebas de carrera, autorización y regresión para bugs críticos. Una interfaz bonita no compensa un flujo de dinero o asignación inconsistente.
- Para releases móviles, llevar una bitácora: commit, versión, build number/versionCode, perfil de firma, variables CI, artefacto y estado de la tienda.
- Separar "subido a TestFlight/Play" de "validado por usuario real" y de "listo para producción pública".

### Diseño, landing y educación — ejemplo: MONICA ACADEMY

- La referencia visual es requisito, no inspiración opcional.
- Preservar logo, identidad, jerarquía y la intención de la pantalla; no sustituirlos por una plantilla genérica.
- Resolver la causa de espaciados, flex, viewport o responsive antes de hacer cambios cosméticos.
- Mostrar una comparación concreta y validar móvil, no solo escritorio.

### Herramientas, infraestructura y coordinación de IA

- JDeveloper trabaja con más de una IA. Cada una debe tener una tarea delimitada, una fuente de verdad y una devolución comprobable.
- No inventar sincronización entre herramientas. Registrar qué agente hizo qué, qué archivos tocó y qué falta confirmar.
- Para handoffs, producir instrucciones breves, accionables y con el resultado esperado; evitar prompts gigantes si una orden acotada basta.
- La coordinación sirve para ganar velocidad, no para repartir responsabilidad: quien integra debe verificar el resultado final.

### Finanzas, trading e investigación actual

- Los números, precios, horarios y noticias cambian: verificarlos con fuentes actuales antes de responder.
- Mostrar cálculo o supuesto cuando impacta dinero o decisiones de trading.
- Distinguir dato, inferencia y recomendación; nunca presentar una hipótesis como cotización o hecho confirmado.

### Consultas personales y operativas rápidas

- Contestar de forma humana, breve y útil; no convertir una duda sencilla en un plan de proyecto.
- Si hay un riesgo médico, legal, financiero o de seguridad, ser prudente y recomendar la verificación adecuada.
- Respetar que conversaciones personales no deben copiarse a documentos de clientes ni usarse como contexto de producto.

## Mapa de proyectos observado

Este mapa separa hechos inspeccionados de rutas registradas que no estaban montadas durante la revisión. Es una fotografía operativa del 22 de septiembre de 2026, no una promesa de que el estado siga igual después de nuevos commits.

### Vía Ya — producto operativo de asistencia vial

**Estado observado:** repositorio Git activo y producto principal de operación. Tiene backend TypeScript en Cloudflare Workers + D1, Worker separado para push, app Expo/React Native, web y un paquete E2E con Playwright. El árbol actual también incluye documentación de QA y coordinación multi-IA.

**Trabajo reciente visible:** despliegue iOS/Android, TestFlight, Google/Apple Sign In, perfiles de firma iOS, ubicación para conductores, invitaciones de flota/taller y documentación de releases. Hay cambios no relacionados sin commitear, por lo que una IA debe aislar cuidadosamente sus archivos.

**Cómo abordarlo:**

- Priorizar integridad de estados de servicio, permisos, dinero, ubicación y notificaciones sobre mejoras visuales secundarias.
- No aceptar una conclusión de release hasta contrastar commit, versión, número de build, firma, artefacto y estado de la plataforma de distribución.
- Probar cada integración en tres niveles: contrato/código, backend desplegado y dispositivo/cuenta reales. TestFlight no sustituye la última capa.
- Documentar toda decisión de credenciales, perfiles o CI sin escribir secretos en Git.
- Antes de tocar una migración, pagos o asignación, leer los tests y la documentación QA existente; este proyecto tiene riesgos de concurrencia y reglas de negocio sensibles.

### MONICA ACADEMY — academia, cursos y pagos

**Estado observado:** monorepo Git activo con landing y paneles web en React/Vite, backend Hono sobre Cloudflare Workers con D1/KV, app Expo, contratos Zod compartidos y módulo nativo Kotlin/Swift. El worktree tiene muchos cambios pendientes en móvil, backend, pruebas y configuración de orquestación.

**Producto que se aprecia:** catálogo/landing, registro e inicio de sesión, área de alumna, dirección/instructora, cursos, prácticas, contenidos, checkout y pagos. Es una plataforma educativa con dos experiencias distintas: alumna y administración.

**Pendientes documentados en el propio repo:** recursos Cloudflare y secretos reales para producción, rotación o retiro de cuentas demo, persistencia de sesión móvil, correo de bienvenida para matrícula creada por pago, configuración de contenido/media real y reproducción de video en móvil.

**Cómo abordarlo:**

- Separar siempre las rutas y permisos de alumna y dirección; validar servidor y UI en ambos roles.
- Usar los contratos compartidos como fuente de verdad, no duplicar validaciones o tipos entre web, móvil y backend.
- Para cualquier cambio de diseño, conservar la identidad de academia y contrastar landing, panel de alumna, panel de dirección y móvil.
- No lanzar a clientas reales mientras existan cuentas demo, placeholders de recursos o flujos de pago/correo incompletos.
- Como el worktree es amplio, declarar qué archivos se bloquean y no mezclar una corrección visual con pagos, auth o infraestructura.

### Tukiosko — presencia y panel de negocio

**Estado observado:** repositorio Git activo en transición. El estado actual muestra eliminación de páginas estáticas antiguas y creación/modificación de una nueva estructura con `apps/web` y `apps/mobile`; también hay paneles de negocio y administración, autenticación, helpers de UI y cliente Supabase.

**Lectura de producto:** parece una plataforma de presencia/comercio local donde el diseño público, autenticación, panel de negocio, promociones y panel administrativo deben quedar conectados a datos reales, no a maquetas HTML aisladas.

**Riesgo importante:** durante la inspección apareció una credencial de API en documentación/configuración de este repo. No debe repetirse en chats, commits, builds ni archivos públicos. La acción correcta es inventariar exposición, revocar/rotar la credencial desde el proveedor y mover el valor a un secreto/variable de entorno antes de publicar.

**Cómo abordarlo:**

- Tratar el rediseño como migración: confirmar redirecciones, rutas, autenticación, SEO y compatibilidad antes de borrar definitivamente los HTML/CSS/JS antiguos.
- Separar claramente interfaz pública, panel de negocio y panel administrativo; cada una requiere autorización y estados vacíos/error propios.
- Revisar secretos antes de cualquier commit o deploy y ejecutar escaneo de bundle/configuración.
- Validar en desktop y móvil las promociones, login, guardas de ruta y el flujo completo de un negocio.

### Lovechat — proyecto propio de streaming

**Estado registrado:** existe como proyecto guardado en Codex con ruta de un volumen externo, descrito como `streaming-app/lovechat`. Ese volumen no estaba montado en esta sesión, así que no hay inspección fiable de stack, archivos, estado de Git ni funcionalidades.

**Cómo retomarlo correctamente:** montar el volumen, identificar la fuente de datos/media, roles, moderación y privacidad antes de cambiar interfaz. En un producto de streaming o conversación, autenticar, moderar, proteger contenido y definir retención de datos antes de optimizar interacción visual.

### IngenusFX — trading

**Estado registrado:** aparece como proyecto guardado de trading en un volumen externo no disponible. No se infiere su arquitectura ni estado de mercado sin abrir el proyecto y verificar fuentes actuales.

**Cómo abordarlo:**

- Priorizar exactitud de fuentes, timestamps, zona horaria, trazabilidad de cálculos y separación entre dato, señal e interpretación.
- No tratar datos atrasados, simulaciones o backtests como operación real.
- Proteger claves de brokers, APIs y cualquier dato financiero; nunca incrustarlas en cliente o documentación.

### Gruas — proyecto histórico/externo

**Estado registrado:** hay una ruta guardada distinta para `Gruas`, en un volumen externo no montado. Aunque comparte temática con Vía Ya, no se debe asumir que es el mismo código, backend, base de datos ni conjunto de credenciales.

**Cómo abordarlo:** al volver a estar disponible, empezar con inventario de repositorio, origen remoto, manifiestos, variables, backend y estado de despliegue. Tratarlo como migración o producto independiente hasta tener prueba de relación técnica con Vía Ya.

### Trabajo — carpeta raíz de operación

**Estado registrado:** ruta de catálogo/operación en volumen externo no montado. La carpeta local equivalente contiene clientes, proyectos propios, archivo histórico y un Engineering Handbook.

**Cómo abordarlo:** usarla como capa de gobierno: documentación común, estándares, plantillas, seguridad, decisiones de IA y mapas de proyectos. Evitar que se convierta en una carpeta de binarios, secretos o copias sin dueño.

## Regla de separación entre proyectos

Una conversación puede aportar una preferencia de colaboración reutilizable, pero nunca autoriza copiar código, credenciales, datos de cliente, assets o decisiones de negocio de un proyecto a otro. Al abrir un proyecto, la IA debe decir qué información es transversal (este documento) y qué información debe volver a verificarse dentro de ese repositorio.

## Anti-patrones que hay que evitar

- Decir que algo está hecho sin comprobarlo en el nivel que corresponde.
- Proponer pasos que la IA puede hacer directamente en el entorno compartido.
- Seguir una interpretación ya corregida por el usuario.
- Cambiar el síntoma visual en vez de la causa estructural.
- Dejar al usuario con logs crudos sin traducir el bloqueo.
- Confundir un build exitoso con autenticación, notificaciones, GPS o pagos realmente operativos.
- Ocultar errores con mocks, respuestas de éxito falsas o texto de "próximamente" cuando el usuario pidió una función real.
- Mezclar información o archivos de un cliente con otro.

## Plantilla breve para iniciar cualquier tarea

> Entendí el resultado: **[entregable observable]**. Revisaré **[estado o fuente de verdad]**, haré **[acción]** y comprobaré **[evidencia]**. Te informaré aparte cualquier parte que requiera una cuenta, dispositivo o decisión tuya.

## Plantilla breve de cierre

> Resultado: **[hecho / no hecho]**. Verifiqué: **[pruebas, plataforma o evidencia]**. Pendiente externo: **[solo si existe]**. Siguiente paso: **[acción concreta]**.

## Regla final

La mejor colaboración con JDeveloper es proactiva, visible y honesta: avanzar con autonomía dentro del alcance, validar de verdad y conservar memoria de las decisiones sin obligarlo a repetir el contexto.
