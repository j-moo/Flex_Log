import { createRouter, createWebHistory } from 'vue-router'

import AnalysisView from '../views/AnalysisView.vue'
import ExpenseFeedView from '../views/ExpenseFeedView.vue'
import ExpenseFormView from '../views/ExpenseFormView.vue'
import ExpenseListView from '../views/ExpenseListView.vue'
import FinancialRecommendationView from '../views/FinancialRecommendationView.vue'
import FinanceProductsView from '../views/FinanceProductsView.vue'
import FriendsView from '../views/FriendsView.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LogInView.vue'
import ProfileView from '../views/ProfileView.vue'
import SignUpView from '../views/SignUpView.vue'
import { useAccountStore } from '../stores/account'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/signup', name: 'signup', component: SignUpView, meta: { guestOnly: true } },
    { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/logs', name: 'logs', component: ExpenseListView, meta: { requiresAuth: true } },
    { path: '/logs/new', name: 'log-create', component: ExpenseFormView, meta: { requiresAuth: true } },
    { path: '/logs/:id/edit', name: 'log-edit', component: ExpenseFormView, meta: { requiresAuth: true } },
    { path: '/feed', name: 'feed', component: ExpenseFeedView, meta: { requiresAuth: true } },
    { path: '/friends', name: 'friends', component: FriendsView, meta: { requiresAuth: true } },
    { path: '/analysis', name: 'analysis', component: AnalysisView, meta: { requiresAuth: true } },
    { path: '/finance/products', name: 'finance-products', component: FinanceProductsView, meta: { requiresAuth: true } },
    { path: '/finance/recommend', name: 'finance-recommend', component: FinancialRecommendationView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach((to) => {
  const account = useAccountStore()
  if (to.meta.requiresAuth && !account.isAuthenticated) return { name: 'login' }
  if (to.meta.guestOnly && account.isAuthenticated) return { name: 'home' }
})

export default router
