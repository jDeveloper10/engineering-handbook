---
title: "00_Fundamentos — Historia de Internet"
category: 00_Fundamentos
doc_type: referencia
tags:
  - history
  - internet
  - networking
  - web
  - technology
summary: "Recorrido cronológico y conceptual de Internet: desde ARPANET (1969) y la conmutación de paquetes hasta la web moderna, las redes sociales, la nube y el impacto de Internet en la ingeniería de software."
keywords:
  - arpanet
  - tcp-ip
  - tim-berners-lee
  - world-wide-web
  - html
  - http
  - dns
  - mosaic
  - netscape
  - burbuja-puntocom
  - web-2.0
  - cloud-computing
  - redes-sociales
updated: 2026-07-26
status: current
---

# Historia de Internet

> Este documento no contiene reglas `[REQUIRED]` ni `[RECOMMENDED]`. Es el **contexto histórico**
> de la red que hizo posible la ingeniería de software moderna: sin Internet, no existirían los
> estándares de APIs, cloud, despliegue continuo ni la colaboración global que este handbook
> presupone.

---

## 1. Los fundamentos teóricos (1960–1968)

### 1.1 J.C.R. Licklider y la "Red Galáctica" (1962)

J.C.R. Licklider, científico del MIT y primer director de la **IPTO** (Information Processing Techniques
Office) de ARPA, fue el primero en concebir una red global interconectada. En una serie de memorandos
(1962–1963) describió su visión de una **"Galactic Network"**: una red donde cualquier usuario pudiera
acceder a datos y programas desde cualquier lugar del mundo.

**Por qué importa:** Licklider no construyó nada, pero su visión fue el combustible intelectual que
guió las inversiones de ARPA en redes de computadoras durante la década siguiente.

### 1.2 Paul Baran y la conmutación de paquetes (1964)

Paul Baran, trabajando en la **RAND Corporation** (un think tank militar de EE.UU.), diseñó un sistema
de comunicación distribuido capaz de **sobrevivir a un ataque nuclear**.

Su innovación clave fue la **conmutación de paquetes**: dividir los mensajes en pequeños bloques
("paquetes"), enviarlos por rutas distintas a través de la red, y reensamblarlos en el destino.
A diferencia de la **conmutación de circuitos** (usada en telefonía, que requiere un circuito
dedicado continuo), la conmutación de paquetes usaba la red de forma más eficiente y resiliente.

Independientemente, **Donald Davies** en el Reino Unido desarrolló el mismo concepto y acuñó el
término **"paquete"** (packet).

### 1.3 El nacimiento de ARPANET (1969)

El Departamento de Defensa de EE.UU., a través de **ARPA** (Advanced Research Projects Agency),
financió un proyecto para conectar centros de investigación y permitir que compartieran recursos
de computadoras remotas. Nació **ARPANET**.

**Hitos fundacionales de ARPANET:**

| Fecha | Evento |
|-------|--------|
| 29 oct 1969 | Primer mensaje entre UCLA y Stanford: "LO" (se cayó antes de escribir "LOGIN") |
| 1969 | Se conectan 4 nodos: UCLA, Stanford, UCSB, Universidad de Utah |
| 1971 | 15 nodos conectados |
| 1973 | Primeras conexiones internacionales (Inglaterra y Noruega) |

### 1.4 El primer email (1971)

**Ray Tomlinson** envió el primer correo electrónico en 1971. Introdujo el uso del símbolo **@**
para separar el nombre del usuario del nombre del host—una convención que 50 años después sigue
siendo universal.

---

## 2. TCP/IP: el protocolo que unificó todo (1974–1983)

### 2.1 Cerf y Kahn (1974)

**Vint Cerf** y **Bob Kahn** publicaron en 1974 el paper *"A Protocol for Packet Network
Intercommunication"*, donde describían el **TCP** (Transmission Control Protocol). Este protocolo
permitía que **redes diferentes** (ARPANET, radio-paquetes, satélite) se interconectaran entre sí,
creando una "red de redes".

En 1978, el protocolo se dividió en dos:
- **TCP:** se encarga de la fiabilidad de la transmisión
- **IP:** se encarga del direccionamiento y encaminamiento de los paquetes

### 2.2 El Día que cambió todo: 1 de enero de 1983

ARPANET adoptó oficialmente **TCP/IP** como su protocolo estándar, abandonando el protocolo anterior
(NCP). Esta fecha se considera el **nacimiento técnico de Internet** como la conocemos: una red global
de redes heterogéneas que hablan el mismo idioma.

### 2.3 DNS (1984)

**Paul Mockapetris** inventó el **Domain Name System (DNS)** en 1984, reemplazando el archivo
`HOSTS.TXT` que se distribuía manualmente. DNS permite traducir nombres legibles por humanos
(`google.com`) a direcciones IP numéricas.

Los primeros dominios `.com`, `.org`, `.edu`, `.gov` y `.mil` se crearon en 1985. El primer
dominio `.com` registrado fue **symbolics.com** (15 de marzo de 1985).

---

## 3. La World Wide Web (1989–1993)

### 3.1 Tim Berners-Lee y el CERN (1989)

En marzo de 1989, **Tim Berners-Lee**, un científico del **CERN** (Organización Europea para la
Investigación Nuclear) en Ginebra, Suiza, propuso un sistema de gestión de información basado en
**hipertexto** para facilitar el intercambio de documentos entre los investigadores del CERN.

Para finales de 1990, Berners-Lee había creado los tres pilares de la Web:

| Componente | Descripción |
|------------|-------------|
| **HTML** (HyperText Markup Language) | Lenguaje de marcado para crear páginas web |
| **HTTP** (HyperText Transfer Protocol) | Protocolo para transferir documentos |
| **URL** (Uniform Resource Locator) | Sistema de direcciones únicas para cada recurso |

También escribió el **primer navegador web** (llamado *WorldWideWeb*) y el **primer servidor web**.

### 3.2 La Web se hace pública (1991)

El **6 de agosto de 1991**, Berners-Lee publicó un resumen del proyecto World Wide Web en el
newsgroup `alt.hypertext`, invitando a otros a participar. Esta es la fecha en que la Web se
hizo pública.

El **30 de abril de 1993**, el CERN liberó el código de la Web al dominio público—una decisión
que probablemente cambió el mundo más que cualquier descubrimiento hecho en el CERN.

### 3.3 Mosaic (1993)

**Marc Andreessen** y **Eric Bina** (NCSA, Universidad de Illinois) crearon **Mosaic**, el primer
navegador que integraba **imágenes con texto** en la misma página, con una interfaz gráfica intuitiva.
Mosaic fue el primer navegador en llegar al público masivo.

---

## 4. La explosión comercial (1994–2000)

### 4.1 Netscape y la guerra de navegadores

Andreessen cofundó **Netscape Communications** y lanzó **Netscape Navigator** en 1994. Fue el
navegador dominante con más del 80% del mercado.

Microsoft respondió con **Internet Explorer** en 1995, integrándolo con Windows 95. Comenzó la
**"guerra de navegadores"**, que Microsoft ganó en gran parte por su integración con el sistema
operativo (llevando luego al caso antimonopolio de EE.UU. contra Microsoft en 1998).

### 4.2 Nacen los gigantes

| Empresa | Fundación | Impacto |
|---------|-----------|---------|
| **Amazon** | 1994 (Jeff Bezos) | Comercio electrónico |
| **Yahoo!** | 1994 (Jerry Yang, David Filo) | Directorio web / portal |
| **eBay** | 1995 (Pierre Omidyar) | Subastas online |
| **Google** | 1998 (Larry Page, Sergey Brin) | Búsqueda web revolucionaria (PageRank) |
| **Wikipedia** | 2001 (Jimmy Wales, Larry Sanger) | Enciclopedia colaborativa |

### 4.3 La burbuja .com (1995–2001)

Un período de **especulación financiera masiva** en el que se invirtió capital excesivo en empresas
de Internet sin modelos de negocio sólidos. El índice NASDAQ pasó de ~1,000 puntos (1995) a ~5,000
puntos (marzo 2000), para luego desplomarse.

**Sobrevivieron:** Amazon, Google, eBay, Yahoo!
**Cayeron:** Pets.com, Webvan, Boo.com, cientos más.

La burbuja dejó una lección que este handbook hereda: **la tecnología sin un modelo de negocio
sostenible no es un negocio, es un experimento.**

---

## 5. Web 2.0 y la era social (2004–2015)

### 5.1 El término "Web 2.0" (2004)

**Tim O'Reilly** acuñó el término **Web 2.0** en 2004 para describir la transición de la web como
conjunto de sitios estáticos a una **plataforma interactiva** donde los usuarios crean contenido.

### 5.2 Las redes sociales

| Plataforma | Año | Fundador(es) | Innovación |
|------------|-----|-------------|------------|
| **Facebook** | 2004 | Mark Zuckerberg | Red social universal |
| **YouTube** | 2005 | Chad Hurley, Steve Chen, Jawed Karim | Video generado por usuarios |
| **Twitter** | 2006 | Jack Dorsey, Biz Stone, Evan Williams | Microblogging en tiempo real |
| **WhatsApp** | 2009 | Jan Koum, Brian Acton | Mensajería móvil |
| **Instagram** | 2010 | Kevin Systrom, Mike Krieger | Fotografía móvil |
| **Telegram** | 2013 | Pavel Durov | Mensajería cifrada |

### 5.3 Cloud Computing (2006–)

| Proveedor | Año | Servicio clave |
|-----------|-----|----------------|
| **Amazon AWS** | 2006 | EC2, S3 — infraestructura como servicio |
| **Google Cloud** | 2008 | App Engine |
| **Microsoft Azure** | 2010 | Plataforma cloud de Microsoft |
| **Cloudflare** | 2010 | CDN + seguridad + edge computing |

La nube transformó la ingeniería de software: ya no se necesitaban servidores físicos. Cualquier
desarrollador podía desplegar una aplicación global con una tarjeta de crédito. Este handbook
hereda esa filosofía en sus estándares de `07_DevOps/` y `08_Cloud/`.

### 5.4 El iPhone y la revolución móvil (2007)

El **iPhone** (2007) y el **Android** (2008) llevaron Internet al bolsillo de miles de millones
de personas. Las aplicaciones móviles redefinieron la experiencia de usuario y crearon un nuevo
paradigma de desarrollo:

- APIs REST/GraphQL como columna vertebral de las apps móviles
- Diseño responsive (que este handbook estandariza en `01_Frontend/`)
- Push notifications, geolocalización, cámara como APIs nativas

---

## 6. La web moderna (2015–2026)

### 6.1 HTTPS como estándar (2015–)

A partir de 2015 (impulsado por Google, Let's Encrypt y el movimiento HTTPS Everywhere), el
protocolo **HTTPS** pasó de ser opcional a ser el estándar. Hoy, más del 95% del tráfico web es
cifrado — un cambio radical desde los años 90 donde todo viajaba en texto plano.

### 6.2 HTTP/2 y HTTP/3

| Versión | Año | Mejora clave |
|---------|-----|-------------|
| HTTP/1.1 | 1997 | El estándar durante 20 años |
| HTTP/2 | 2015 | Multiplexing, compresión de headers, server push |
| HTTP/3 | 2022 | Basado en QUIC (UDP), menor latencia |

### 6.3 APIs y la economía de las APIs

REST (2000, Roy Fielding), GraphQL (2015, Facebook), y gRPC (2016, Google) transformaron Internet
de una red de **páginas** a una red de **servicios**. Hoy, el tráfico de APIs supera al tráfico
de páginas web.

### 6.4 Internet en la era de la IA (2022–2026)

La IA generativa (ChatGPT, Copilot) está transformando Internet nuevamente:
- **Búsqueda:** de enlaces a respuestas generadas (Google SGE, Bing Copilot)
- **Contenido:** generación automatizada de texto, imágenes, video
- **Desarrollo:** código generado por IA desplegado globalmente en segundos

---

## 7. Figuras clave de la historia de Internet

| Persona | Aporte | Frase/año |
|---------|--------|-----------|
| **J.C.R. Licklider** | Visión de la "Red Galáctica" | 1962 |
| **Paul Baran** | Conmutación de paquetes | 1964 |
| **Donald Davies** | Acuñó el término "paquete" | 1965 |
| **Ray Tomlinson** | Primer email, creó el @ | 1971 |
| **Vint Cerf & Bob Kahn** | Protocolo TCP/IP | 1974 |
| **Paul Mockapetris** | DNS (Domain Name System) | 1984 |
| **Tim Berners-Lee** | World Wide Web (HTML, HTTP, URL) | 1989 |
| **Marc Andreessen** | Navegador Mosaic, Netscape | 1993 |
| **Larry Page & Sergey Brin** | Google, PageRank | 1998 |
| **Tim O'Reilly** | Acuñó el término "Web 2.0" | 2004 |
| **Jeff Bezos** | AWS, comercio electrónico masivo | 2006 |

---

## 8. Cronología visual

```
1962 ─ Licklider: visión de la "Red Galáctica"
1964 ─ Baran: conmutación de paquetes (RAND)
1969 ─ ARPANET: primer nodo (UCLA) ─ primer mensaje "LO"
1971 ─ Primer email (Tomlinson) ─ nace el @
1974 ─ Cerf & Kahn: paper del TCP
1983 ─ 1 de enero: ARPANET adopta TCP/IP ─ NACIMIENTO DE INTERNET
1984 ─ DNS (Mockapetris) ─ primeros dominios .com, .org
1989 ─ Tim Berners-Lee propone la Web (CERN)
1991 ─ Web se hace pública ─ primer sitio web
1993 ─ Mosaic (Andreessen) ─ imágenes + texto
1994 ─ Netscape Navigator ─ Amazon ─ Yahoo!
1995 ─ Internet Explorer ─ Burbuja .com comienza
1998 ─ Google ─ Caso antimonopolio Microsoft
2000 ─ Estallido de la burbuja .com
2001 ─ Wikipedia
2004 ─ Facebook ─ Web 2.0 (O'Reilly)
2005 ─ YouTube ─ AJAX populariza apps web dinámicas
2006 ─ Twitter ─ AWS EC2/S3 (cloud computing)
2007 ─ iPhone ─ Internet en el bolsillo
2008 ─ Android ─ HTTP/1.1 sigue siendo rey
2010 ─ Instagram ─ Cloudflare CDN
2015 ─ HTTP/2 ─ HTTPS se vuelve estándar
2019 ─ COVID-19: Internet se vuelve indispensable
2022 ─ HTTP/3 (QUIC) ─ ChatGPT ─ IA generativa
2026 ─ Internet como infraestructura crítica global
```

---

## 9. Lecciones de Internet para el handbook

| Lección | Fundamento histórico | Documento del handbook |
|---------|---------------------|----------------------|
| Los protocolos abiertos ganan | TCP/IP vs protocolos propietarios | [`../03_API/`](../03_API/), [`../04_Database/`](../04_Database/) |
| La descentralización da resiliencia | Conmutación de paquetes, DNS distribuido | [`../08_Cloud/`](../08_Cloud/), [`../Engineering-OS/06-Architecture.md`](../Engineering-OS/06-Architecture.md) |
| Los estándares abiertos aceleran la innovación | HTTP/HTML públicos vs propietarios | [`../01_Frontend/`](../01_Frontend/), [`../13_AI_Rules/`](../13_AI_Rules/) |
| HTTPS no es opcional | Transición 2015+ de texto plano a cifrado | [`../05_Security/`](../05_Security/) |
| El cloud eliminó la fricción de escalar | AWS 2006 cambió la economía del software | [`../07_DevOps/`](../07_DevOps/), [`../08_Cloud/`](../08_Cloud/) |
| Las APIs son el nuevo HTML | REST → GraphQL → gRPC | [`../03_API/`](../03_API/) |
| La seguridad debe diseñarse desde el principio | Internet nació sin seguridad (TCP/IP años 70) | [`../05_Security/`](../05_Security/) |

---

## 10. Para seguir aprendiendo

| Recurso | Tipo | Por qué |
|---------|------|---------|
| *Where Wizards Stay Up Late* (Hafner & Lyon, 1996) | Libro | La historia definitiva de los orígenes de Internet |
| *The Innovators* (Walter Isaacson, 2014) | Libro | Contexto amplio de la revolución digital |
| *Weaving the Web* (Tim Berners-Lee, 1999) | Libro | La historia de la Web contada por su creador |
| *A Protocol for Packet Network Intercommunication* (Cerf & Kahn, 1974) | Paper | El paper fundacional de TCP/IP |
| [Internet Society: History](https://www.internetsociety.org/internet/history/) | Web | Cronología oficial por la organización que preserva Internet |
| [Wikipedia: History of the Internet](https://en.wikipedia.org/wiki/History_of_the_Internet) | Web | Referencia abierta y actualizada |
| [RFC 1 (Host Software, 1969)](https://tools.ietf.org/html/rfc1) | RFC | El primer RFC de ARPANET — el comienzo de todo |

---

## Checklist de verificación

- [ ] ¿El documento cubre desde 1962 hasta el presente (2026)?
- [ ] ¿Cada hito importante tiene su año y contexto?
- [ ] ¿Las figuras clave están nombradas con su aporte específico?
- [ ] ¿La cronología es coherente y completa?
- [ ] ¿El documento explica *por qué* Internet importa para el resto del handbook?
- [ ] ¿Las lecciones históricas se mapean contra documentos reales del handbook?
- [ ] ¿El frontmatter YAML tiene title, category, tags, summary, keywords, updated y status?
