// Capa de tema del Engineering Handbook.
//
// Extiende el tema por defecto de VitePress sin reemplazar ningún componente:
// solo aporta una hoja de estilos que sobrescribe las variables CSS del tema
// ('--vp-*') para portar el lenguaje visual de jcdigital.online.
import DefaultTheme from 'vitepress/theme'
import './custom.css'
import RecipeRouter from './RecipeRouter.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('RecipeRouter', RecipeRouter)
  }
}
