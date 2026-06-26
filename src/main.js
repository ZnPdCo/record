import { createApp } from 'vue'
import FomanticUI from 'vue-fomantic-ui'
import 'fomantic-ui-css/semantic.min.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(FomanticUI)
app.use(router)
app.mount('#app')
