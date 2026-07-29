---
title: "Catálogo de Estilos Visuales"
category: 01_Frontend
tags: [frontend, estilos, design-tokens, tailwind]
summary: "Catálogo de 30 estilos visuales con criterio de elección y el procedimiento para convertir un estilo del catálogo en tokens semánticos de Tailwind."
keywords: [estilos, catalogo, paleta, tokens, tailwind, design-system]
updated: 2026-07-27
status: current
---

# FRONTEND UI STYLE CATALOG

> Nivel 2 del handbook, depende de [FRONTEND_ENGINEERING_STANDARD.md](../Core/FRONTEND_ENGINEERING_STANDARD.md) sección 01 (Design System). Este documento **no define reglas de estructura** (eso lo hace el estándar de Nivel 1) — es un catálogo de datos de referencia (identidades visuales), no un conjunto de reglas REQUIRED/RECOMMENDED como el resto del handbook. La única regla dura del documento está marcada explícitamente en la sección "Cómo elegir un estilo".
>
> Uso: al arrancar un proyecto nuevo, elegir un estilo de aquí (o combinar dos con criterio), extraer sus tokens (colores, radios, tipografía, efectos) y cargarlos siguiendo las reglas de escala/semántica de la sección 01 del estándar de Nivel 1. Nunca copiar el HTML del prototipo tal cual a producción — son referencias de tokens, no componentes productivos.
>
> Fuente de cada demo: `E:\Pruebas\<Nombre>\index.html`.

---

## Cómo elegir un estilo

**[RECOMMENDED]** El estilo lo decide el tipo de producto y el usuario final, no el gusto del momento — tabla de referencia:

| Tipo de proyecto | Estilos recomendados | Por qué |
|---|---|---|
| Apps de trading / finanzas (jonnyTrader, señales) | **Fintech**, Pro_Dark_Mode, SaaS_Modern | Confianza, legibilidad de números, dark mode serio — nada que compita visualmente con los datos |
| Academias / cursos online | **SaaS_Modern**, Bento_UI, Minimalism | Claridad de navegación, foco en contenido, no fatiga visual en sesiones largas |
| E-commerce / tiendas (Gaby and Beauty, delivery) | **E_commerce**, Flat_Design, SaaS_Modern | Patrones ya validados por conducta de compra (Amazon-like), reduce fricción |
| Landing/marketing de producto nuevo | **Glassmorphism**, Aurora_UI, Web3, Liquid_Glass | Impacto visual inmediato, diferenciación de marca |
| Dashboards internos / admin / bots WA | **Dashboard**, Enterprise, Pro_Dark_Mode | Densidad de información, cero decoración que distraiga |
| Salud / bienestar / bienestar financiero suave | **Healthcare**, Claymorphism, Neumorphism | Calma, confianza, bajo estrés visual |
| Gaming / comunidad / torneos (torneos-gaming) | **Cyberpunk**, 8_bit, Retro_Y2K, Memphis_Design | Identidad lúdica, energía, target joven |
| Branding personal / portfolio | **Swiss_Design**, Minimalism, Bauhaus | El contenido/trabajo es el protagonista, no el chrome de la UI |

**[REQUIRED]** Un estilo decorativo (Grunge, Vaporwave, Pop_Art, Steampunk, Skeuomorphism, Frutiger_Aero) nunca se usa en pantallas transaccionales (checkout, formularios de pago, dashboards financieros).

**Por qué:** estos estilos priorizan personalidad visual sobre legibilidad/eficiencia — correcto en una landing o un sitio de evento, pero un riesgo real de conversión y confianza en una pantalla donde el usuario está a punto de pagar o tomar una decisión financiera. Sirven para landings, campañas puntuales o proyectos donde la personalidad visual es el producto.

---

## Catálogo completo (30 estilos)

### 8_bit
- Colores: bg `#000000`, acento `#0000aa` (tarjeta) / `#aa0000` (botón), texto `#ffffff` con highlight `#ffff55`
- Tipografía: 'Press Start 2P' (pixel font monoespaciada), tamaños pequeños 12-20px
- Forma: 0px border-radius, bordes gruesos 4px sólidos blancos
- Efectos: box-shadow duro sin blur (8px 8px 0px), inset invertido en `:active` (botón presionado)
- Vibe: retro consola de 8 bits, arcade de los 80s
- Úsalo en: eventos gaming, easter eggs, landing de producto retro. No en producto serio.

### Aurora_UI
- Colores: bg `#121212`, gradiente `#14ffcc` / `#ff3399`, violeta `rgba(153,51,255,*)`
- Tipografía: 'Inter'; título con gradiente de texto vía `background-clip`
- Forma: border-radius 24px, borde fino 1px semitransparente
- Efectos: fondo radial-gradient animado + `blur(60px)`, card con `backdrop-filter blur(20px)`
- Vibe: etéreo, luminoso, auroras boreales tras vidrio
- Úsalo en: landing de producto premium, apps creativas/IA.

### Bauhaus
- Colores: bg `#f4f4f4`, rojo `#e32636`, azul `#0033a0`, amarillo `#ffd700`, texto `#1a1a1a`
- Tipografía: Futura/Helvetica Neue; 40px bold, letter-spacing 5px, uppercase
- Forma: geometría pura (cuadrado, círculo, triángulo), sin bordes gruesos
- Efectos: sombra suave, `mix-blend-mode: difference`, sin gradientes
- Vibe: modernismo de escuela de arte, colores primarios puros
- Úsalo en: branding editorial/cultural, portfolio de diseño.

### Bento_UI
- Colores: bg `#f7f7f8`, tarjetas blancas con acentos pastel, bloque oscuro `#000`/`#fff`
- Tipografía: system font stack; h3 1.2rem
- Forma: border-radius 20px, grid tipo "bento box" con spans variables
- Efectos: sombra ligera, sin gradientes, look plano
- Vibe: modular, ordenado, minimalista
- Úsalo en: dashboards de producto, landing de features, academias.

### Brutalism
- Colores: bg `#0000ff`, acento `#ff0000`, botón `#00ff00`, texto `#ffff00`/`#fff`
- Tipografía: Courier New monospace; uppercase, bold
- Forma: 0 border-radius, bordes gruesos 3-5px negros
- Efectos: box-shadow duro sin blur, colapsa en hover
- Vibe: crudo, chocante, RGB puro
- Úsalo en: portfolio creativo con actitud, campañas de impacto. Nunca en fintech/salud.

### Claymorphism
- Colores: bg `#f1f3f6`, rosa pastel `#ffb6b9`, durazno `#fae3d9`
- Tipografía: Poppins
- Forma: border-radius 40px card / 20px botón, muy redondeado ("inflado")
- Efectos: triple box-shadow (arcilla 3D), scale en hover
- Vibe: suave, esponjoso, táctil
- Úsalo en: apps de bienestar, salud mental, productos infantiles/lifestyle.

### Cyberpunk
- Colores: bg `#0a0a0a`, cian `#0ff`, magenta `#f0f`, verde `#0f0`
- Tipografía: Courier New monospace, uppercase, letter-spacing 5px
- Forma: bordes finos 2px, 0 border-radius
- Efectos: grid de fondo, glow (`box-shadow 0 0 15px`), texto duplicado con shadow
- Vibe: neón futurista, hacker
- Úsalo en: gaming, comunidad tech/cripto, eventos.

### Dashboard
- Colores: bg `#f3f4f6`, sidebar `#1f2937`, texto `#111827`, acento verde `#10b981`
- Tipografía: system stack; stat-value 32px bold
- Forma: border-radius 6-8px, sin bordes gruesos
- Efectos: sombra muy sutil, sin gradientes/blur
- Vibe: funcional, corporativo, panel de admin
- Úsalo en: paneles internos, bots de WhatsApp, herramientas de operación.

### E_commerce
- Colores: bg `#f5f5f5`, precio `#b12704`, CTA `#ffd814`
- Tipografía: Arial/Helvetica; precio 22px bold
- Forma: border-radius 4px card, pill en "Add to Cart"
- Efectos: sombra que se intensifica en hover
- Vibe: comercial, confiable, estética Amazon
- Úsalo en: tiendas (Gaby and Beauty, delivery), catálogos de producto.

### Enterprise
- Colores: bg `#ffffff`, acento `#1890ff`, bordes `#d9d9d9`
- Tipografía: Arial; base 13px (alta densidad de datos)
- Forma: border-radius 2px, bordes finos 1px
- Efectos: sin sombras, hover en filas de tabla
- Vibe: sobrio, back-office empresarial (Ant Design)
- Úsalo en: paneles de gestión con muchas tablas/datos.

### Fintech
- Colores: bg `#0f172a` navy oscuro, acento `#10b981` esmeralda, superficie `#1e293b`
- Tipografía: system stack; balance-amount 42px/700
- Forma: border-radius 20px card / 12px botones
- Efectos: elevación pronunciada `0 20px 25px -5px rgba(0,0,0,0.5)`
- Vibe: confianza corporativa nocturna, banca premium
- Úsalo en: **jonnyTrader, apps de trading, señales, cualquier producto financiero.** Candidato fuerte por defecto.

### Flat_Design
- Colores: bg `#34495e`, tarjeta `#ecf0f1`, acento `#3498db`
- Tipografía: Segoe UI/Tahoma
- Forma: border-radius bajo (3-5px)
- Efectos: sin sombras ni 3D
- Vibe: minimalismo sólido, flat clásico
- Úsalo en: MVPs rápidos, herramientas internas sin necesidad de personalidad fuerte.

### Fluent_Design
- Colores: acento `#0078D4`, superficie `rgba(243,243,243,0.7)`
- Tipografía: Segoe UI Variable
- Forma: border-radius 8px card / 4px botón
- Efectos: `backdrop-filter blur(30px)` ("acrylic"), efecto reveal que sigue el mouse
- Vibe: material acrílico translúcido, Windows 11
- Úsalo en: herramientas de productividad, apps tipo dashboard con look Microsoft.

### Frutiger_Aero
- Colores: bg gradiente `#87CEEB`→`#E0F7FA`, botón `#4da6ff`→`#0059b3`
- Tipografía: Segoe UI/Tahoma
- Forma: border-radius 15-20px, burbuja 50%
- Efectos: gradientes glossy, reflejo de luz, blur sutil
- Vibe: skeuomorfismo acuoso, nostalgia Vista/XP
- Úsalo en: proyectos nostálgicos/nicho. No para producto serio actual.

### Glassmorphism
- Colores: bg gradiente `#fc466b`→`#3f5efb`, card `rgba(255,255,255,0.1)`
- Tipografía: Segoe UI; h2 600 letter-spacing 1px
- Forma: border-radius 20px card / 50px botón
- Efectos: `backdrop-filter blur(10px)`, sombra pronunciada, fondo diagonal vibrante
- Vibe: vidrio esmerilado sobre fondo vibrante, look iOS
- Úsalo en: landings de producto, apps creativas, IA. Evitar en dashboards densos (el blur cansa con mucho contenido).

### Grunge
- Colores: bg `#2b2b2b` textura concreto, acento `#9a0000`
- Tipografía: 'Special Elite' (máquina de escribir)
- Forma: 0 border-radius, bordes gruesos + dashed decorativo, rotación leve
- Efectos: textura, viñeta inset, "cinta adhesiva" simulada
- Vibe: crudo, underground, punk/90s
- Úsalo en: proyectos de música/arte/eventos con identidad alternativa. No en producto B2B.

### Healthcare
- Colores: bg `#f0f7f9`, acento `#00a896` verde menta
- Tipografía: Segoe UI; doctor-name 18px/600
- Forma: border-radius 16px card, border-top grueso de acento
- Efectos: sombra suave con tinte de color
- Vibe: limpio, calmado, clínico friendly
- Úsalo en: apps de salud, bienestar, wellness financiero (tono calmado para trading emocional).

### Liquid_Glass
- Colores: bg gradiente `#00c6ff`→`#0072ff`
- Tipografía: sans-serif genérico
- Forma: border-radius orgánico mutante (blob animado)
- Efectos: `backdrop-filter blur(15px)`, `@keyframes morph` 8s
- Vibe: gota de vidrio viva, futurista orgánico
- Úsalo en: landing experimental, showcase de producto IA/creativo.

### Material_Design
- Colores: bg `#fafafa`, acento `#6200ea` púrpura
- Tipografía: Roboto (400/500/700)
- Forma: border-radius uniforme 4px
- Efectos: elevación por capas (sombra triple clásica Material)
- Vibe: ordenado, Material Design clásico (Google)
- Úsalo en: apps Android-first, productos que priorizan familiaridad sobre diferenciación.

### Material_You
- Colores: superficie `#FFFBFE`, primario `#6750A4`, container `#EADDFF` (vía CSS custom properties)
- Tipografía: Roboto/system-ui
- Forma: border-radius muy alto (28px card, 100px pill)
- Efectos: sin sombras, capas tonales planas
- Vibe: personalizado, suave, Material Design 3
- Úsalo en: apps modernas Android-first con paleta dinámica por usuario.

### Memphis_Design
- Colores: bg `#ffd6e8`, acentos `#00e5ff`/`#ffef00`/`#ff0055`
- Tipografía: Arial Black uppercase
- Forma: bordes muy gruesos, mayormente anguloso con círculo decorativo
- Efectos: sombra sólida, `clip-path` triángulo, rayas diagonales
- Vibe: caos geométrico ochentero, pastel + flúor
- Úsalo en: campañas creativas, target Gen-Z/joven. No producto serio.

### Minimalism
- Colores: bg `#ffffff`, acento `#1a1a1a`
- Tipografía: Helvetica Neue; h1 weight 300, letter-spacing -1px
- Forma: sin border-radius, borde delgado 1px
- Efectos: ninguno
- Vibe: limpieza extrema, tipografía como protagonista
- Úsalo en: portfolio personal, branding, cualquier producto donde el contenido debe dominar.

### Neumorphism
- Colores: bg `#e0e5ec`, monocromático tono sobre tono
- Tipografía: Arial
- Forma: border-radius grande (20px card)
- Efectos: doble sombra claro/oscuro simulando relieve extruido
- Vibe: superficie suave "extruida", táctil
- Úsalo en: apps de configuración/ajustes, controles físicos simulados (poco uso en producto data-heavy — baja legibilidad de contraste).

### Pop_Art
- Colores: bg `#ffff00`, acento `#ff0000`/`#0000ff`
- Tipografía: Comic Sans MS uppercase
- Forma: bordes gruesos, sin border-radius, rotación leve
- Efectos: patrón halftone, sombra sólida 12px, globo de cómic
- Vibe: cómic explosivo, colores primarios saturados
- Úsalo en: campañas puntuales, contenido divertido/viral. Nunca en UI transaccional.

### Pro_Dark_Mode
- Colores: bg `#1e1e1e`, acento `#007acc` (azul VS Code), sintaxis coloreada
- Tipografía: Consolas/Courier New monospace, 12-14px
- Forma: border-radius pequeño (4px)
- Efectos: sombra sutil de profundidad
- Vibe: herramienta developer estilo VS Code, sobria
- Úsalo en: dashboards internos, herramientas técnicas, admin de bots/n8n.

### Retro_Y2K
- Colores: bg `#000080`, acentos `#ff00ff`/`#00ffff`/`#ff9900`
- Tipografía: Comic Sans MS; header 4rem
- Forma: bordes 3D outset/inset estilo Windows 9x
- Efectos: textura stardust, marquee animado, gradientes metálicos
- Vibe: nostalgia web Y2K, caótica
- Úsalo en: proyectos nicho nostálgicos, eventos temáticos.

### SaaS_Modern
- Colores: bg `#f9fafb`, acento `#6366f1` índigo
- Tipografía: Inter (400/500/600)
- Forma: border-radius moderado (12px card, 6px inputs)
- Efectos: sombra suave multicapa, focus ring en input
- Vibe: producto SaaS pulido tipo Stripe/Linear
- Úsalo en: **candidato por defecto para academias, herramientas B2B, cualquier proyecto sin identidad visual fuerte ya definida.**

### Skeuomorphism
- Colores: bg `#8b5a2b` madera, botón gradiente gris metálico
- Tipografía: Times New Roman serif
- Forma: botón circular 50%
- Efectos: textura madera, gradiente metálico, volumen físico simulado
- Vibe: imitación foto-realista, táctil old-school
- Úsalo en: casi nunca en web moderna — solo referencias/nostalgia.

### Steampunk
- Colores: bg `#2c1a10`, acento dorado `#d4af37`
- Tipografía: Palatino serif (cuerpo), Courier New uppercase (headers)
- Forma: bordes muy gruesos, texturas de madera/latón
- Efectos: gradientes bronce, remaches simulados
- Vibe: victoriano industrial, mecánico ornamentado
- Úsalo en: proyectos temáticos/eventos, nunca producto genérico.

### Swiss_Design
- Colores: bg `#efefef`, acento rojo `#d11`
- Tipografía: Helvetica Neue; header 5vw bold, letter-spacing -2px
- Forma: sin border-radius, grid estricto, sin bordes
- Efectos: overlay de líneas de grid, sin sombras decorativas
- Vibe: tipografía editorial internacional, claridad extrema
- Úsalo en: portfolio, branding personal, contenido editorial.

### Vaporwave
- Colores: bg gradiente `#ff00ff`→`#00ffff`, ventana `#c0c0c0`
- Tipografía: Times New Roman/Arial; letter-spacing 5px
- Forma: bordes Windows 95 outset/inset
- Efectos: grid de perspectiva animado, sombra de ventana retro
- Vibe: synth retro-futuro, grid neón sobre ventana Win95
- Úsalo en: proyectos musicales/creativos nicho.

### Web3
- Colores: bg `#050510`, acento `#bb86fc`/`#03dac6`
- Tipografía: Inter; h2 con gradiente de texto
- Forma: border-radius grande (20px card, 30px pill)
- Efectos: mesh gradient animado, `backdrop-filter blur(20px)`, glow
- Vibe: dark mode cripto/futurista
- Úsalo en: proyectos cripto/Web3, landing de producto IA con identidad futurista.

---

## Cómo pasar un estilo del catálogo a tokens de Tailwind

1. Copiar los 3-4 hex codes de "Colores" a `tailwind.config.ts` → `theme.extend.colors` como tokens semánticos (no como `custom1`, `custom2`).
2. Mapear "Forma" (border-radius) a `theme.extend.borderRadius` si se desvía de la escala default de Tailwind.
3. "Efectos" (blur, glow, sombras) van a `theme.extend.boxShadow`/`backdropBlur` como utilidades nombradas (`shadow-glow`, no un valor arbitrario repetido en cada componente).
4. Validar contraste AA antes de fijar la paleta final (ver sección 13 de accesibilidad del estándar principal) — varios estilos de este catálogo (Cyberpunk, Vaporwave, Web3) tienen combinaciones vibrantes que pueden fallar contraste en texto pequeño.
