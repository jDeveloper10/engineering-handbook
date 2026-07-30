// Capa de tema del Engineering Handbook.
//
// Extiende el tema por defecto de VitePress sin reemplazar ningún componente:
// solo aporta una hoja de estilos que sobrescribe las variables CSS del tema
// (`--vp-*`) para portar el lenguaje visual de jcdigital.online.
//
// Por qué `extends` y no `...DefaultTheme`: `extends` conserva el Layout, el
// enhanceApp y los slots del tema por defecto aunque cambien entre versiones
// menores de VitePress, así que la personalización se limita a CSS y no queda
// atada a la estructura interna del tema.
import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default {
  extends: DefaultTheme,
}
