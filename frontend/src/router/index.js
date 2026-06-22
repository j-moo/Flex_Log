import { createRouter, createWebHistory } from 'vue-router'

import AnalysisView from '../views/AnalysisView.vue'
import ExpenseFeedView from '../views/ExpenseFeedView.vue'
import ExpenseDetailView from '../views/ExpenseDetailView.vue'
import ExpenseFormView from '../views/ExpenseFormView.vue'
import ExpenseListView from '../views/ExpenseListView.vue'
import FinancialRecommendationView from '../views/FinancialRecommendationView.vue'
import FinanceHubView from '../views/FinanceHubView.vue'
import FinanceProductsView from '../views/FinanceProductsView.vue'
import FriendsView from '../views/FriendsView.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LogInView.vue'
import MyPageView from '../views/MyPageView.vue'
import ProfileView from '../views/ProfileView.vue'
import SignUpView from '../views/SignUpView.vue'
import StockHoldingView from '../views/StockHoldingView.vue'
import CommodityPricesView from '../views/CommodityPricesView.vue'
import NearbyBanksView from '../views/NearbyBanksView.vue'
import YoutubeDetailView from '../views/YoutubeDetailView.vue'
import YoutubeSearchView from '../views/YoutubeSearchView.vue'
import { useAccountStore } from '../stores/account'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { guestOnly: true } },
    { path: '/signup', name: 'signup', component: SignUpView, meta: { guestOnly: true } },
    { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
    { path: '/feed', name: 'feed', component: ExpenseFeedView, meta: { requiresAuth: true } },
    { path: '/mypage', name: 'mypage', component: MyPageView, meta: { requiresAuth: true } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/profile/:userId', name: 'user-profile', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/logs', name: 'logs', component: ExpenseListView, meta: { requiresAuth: true } },
    { path: '/logs/new', name: 'log-create', component: ExpenseFormView, meta: { requiresAuth: true } },
    { path: '/logs/:id/edit', name: 'log-edit', component: ExpenseFormView, meta: { requiresAuth: true } },
    { path: '/logs/:id', name: 'log-detail', component: ExpenseDetailView, meta: { requiresAuth: true } },
    { path: '/friends', name: 'friends', component: FriendsView, meta: { requiresAuth: true } },
    { path: '/analysis', name: 'analysis', component: AnalysisView, meta: { requiresAuth: true } },
    { path: '/finance', name: 'finance-hub', component: FinanceHubView, meta: { requiresAuth: true } },
    { path: '/finance/products', name: 'finance-products', component: FinanceProductsView, meta: { requiresAuth: true } },
    { path: '/finance/recommend', name: 'finance-recommend', component: FinancialRecommendationView, meta: { requiresAuth: true } },
    { path: '/finance/commodities', name: 'commodities', component: CommodityPricesView, meta: { requiresAuth: true } },
    { path: '/finance/youtube', name: 'youtube-search', component: YoutubeSearchView, meta: { requiresAuth: true } },
    { path: '/finance/youtube/:videoId', name: 'youtube-detail', component: YoutubeDetailView, meta: { requiresAuth: true } },
    { path: '/finance/banks', name: 'nearby-banks', component: NearbyBanksView, meta: { requiresAuth: true } },
    { path: '/stocks', name: 'stocks', component: StockHoldingView, meta: { requiresAuth: true } },
    { path: '/:pathMatch(.*)*', redirect: { name: 'home' } },
  ],
})

router.beforeEach((to) => {
  const account = useAccountStore()
  if (to.meta.requiresAuth && !account.isAuthenticated) return { name: 'login' }
  if (to.meta.guestOnly && account.isAuthenticated) return { name: 'feed' }
  return true
})

export default router
