import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/auth/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/auth/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard.vue'),
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/pages/projects/ProjectList.vue'),
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/pages/projects/ProjectDetail.vue'),
      },
      {
        path: 'ingestion/wizard',
        name: 'IngestionWizard',
        component: () => import('@/pages/ingestion/IngestionWizard.vue'),
      },
      {
        path: 'ingestion/jobs',
        name: 'IngestionJobs',
        component: () => import('@/pages/ingestion/JobList.vue'),
      },
      {
        path: 'graph/builder',
        name: 'GraphBuilder',
        component: () => import('@/pages/graph/GraphBuilder.vue'),
      },
      {
        path: 'graph/jobs',
        name: 'GraphJobs',
        component: () => import('@/pages/graph/GraphJobs.vue'),
      },
      {
        path: 'graph/visualization',
        name: 'GraphVisualization',
        component: () => import('@/pages/graph/GraphVisualization.vue'),
      },
      {
        path: 'graph/visualization/:projectId',
        name: 'ProjectVisualization',
        component: () => import('@/pages/graph/GraphVisualization.vue'),
      },
      {
        path: 'query',
        name: 'QueryBuilder',
        component: () => import('@/pages/query/QueryBuilder.vue'),
      },
      {
        path: 'reasoning',
        name: 'ReasoningManager',
        component: () => import('@/pages/reasoning/ReasoningManager.vue'),
        meta: { title: '规则管理', requiresAuth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // 如果有 token 但没有用户信息，尝试获取用户
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }

  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (!requiresAuth && authStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
