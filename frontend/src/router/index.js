import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import TeamView from '@/views/TeamView.vue'

const routes = [
  { path: '/',            component: HomeView },
  { path: '/team/:code',  component: TeamView },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
