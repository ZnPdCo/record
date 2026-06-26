import { createRouter, createWebHashHistory } from 'vue-router'
import IndexView from './views/IndexView.vue'
import EditView from './views/EditView.vue'

const routes = [
  { path: '/', name: 'index', component: IndexView },
  { path: '/edit', name: 'edit', component: EditView },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
