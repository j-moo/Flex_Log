import { createRouter, createWebHistory } from 'vue-router'

import { useAccountStore } from '../stores/account'

const AnalysisView = () => import('../views/AnalysisView.vue')
const EasterEggView = () => import('../views/EasterEggView.vue')
const ExpenseFeedView = () => import('../views/ExpenseFeedView.vue')
const ExpenseDetailView = () => import('../views/ExpenseDetailView.vue')
const ExpenseFormView = () => import('../views/ExpenseFormView.vue')
const ExpenseListView = () => import('../views/ExpenseListView.vue')
const FinancialRecommendationView = () => import('../views/FinancialRecommendationView.vue')
const FinanceDayView = () => import('../views/FinanceDayView.vue')
const FinanceHubView = () => import('../views/FinanceHubView.vue')
const FinanceProductsView = () => import('../views/FinanceProductsView.vue')
const FriendsView = () => import('../views/FriendsView.vue')
const HomeView = () => import('../views/HomeView.vue')
const LoginView = () => import('../views/LogInView.vue')
const MyPageView = () => import('../views/MyPageView.vue')
const NotificationView = () => import('../views/NotificationView.vue')
const ProfileView = () => import('../views/ProfileView.vue')
const SignUpView = () => import('../views/SignUpView.vue')
const StockHoldingView = () => import('../views/StockHoldingView.vue')
const CommodityPricesView = () => import('../views/CommodityPricesView.vue')
const NearbyBanksView = () => import('../views/NearbyBanksView.vue')
const YoutubeDetailView = () => import('../views/YoutubeDetailView.vue')
const YoutubeSearchView = () => import('../views/YoutubeSearchView.vue')


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView, meta: { guestOnly: true } },
    { path: '/signup', name: 'signup', component: SignUpView, meta: { guestOnly: true } },
    { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
    { path: '/feed', name: 'feed', component: ExpenseFeedView, meta: { requiresAuth: true } },
    { path: '/kerocya', name: 'easter-egg', component: EasterEggView, meta: { requiresAuth: true } },
    { path: '/mypage', name: 'mypage', component: MyPageView, meta: { requiresAuth: true } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/profile/:userId', name: 'user-profile', component: ProfileView, meta: { requiresAuth: true } },
    { path: '/logs', name: 'logs', component: ExpenseListView, meta: { requiresAuth: true } },
    { path: '/logs/new', name: 'log-create', component: ExpenseFormView, meta: { requiresAuth: true } },
    { path: '/logs/:id/edit', name: 'log-edit', component: ExpenseFormView, meta: { requiresAuth: true } },
    { path: '/logs/:id', name: 'log-detail', component: ExpenseDetailView, meta: { requiresAuth: true } },
    { path: '/friends', name: 'friends', component: FriendsView, meta: { requiresAuth: true } },
    { path: '/notifications', name: 'notifications', component: NotificationView, meta: { requiresAuth: true } },
    { path: '/analysis', name: 'analysis', component: AnalysisView, meta: { requiresAuth: true } },
    { path: '/finance', name: 'finance-hub', component: FinanceHubView, meta: { requiresAuth: true } },
    { path: '/finance/day/:date', name: 'finance-day', component: FinanceDayView, meta: { requiresAuth: true } },
    { path: '/finance/products', name: 'finance-products', component: FinanceProductsView, meta: { requiresAuth: true } },
    { path: '/finance/recommend', name: 'finance-recommend', component: FinancialRecommendationView, meta: { requiresAuth: true } },
    { path: '/finance/commodities', name: 'commodities', component: CommodityPricesView, meta: { requiresAuth: true } },
    { path: '/finance/youtube', name: 'youtube-search', component: YoutubeSearchView, meta: { requiresAuth: true } },
    { path: '/finance/youtube/:videoId', name: 'youtube-detail', component: YoutubeDetailView, meta: { requiresAuth: true } },
    { path: '/finance/banks', name: 'nearby-banks', component: NearbyBanksView, meta: { requiresAuth: true } },
    { path: '/stocks', name: 'stocks', component: StockHoldingView, meta: { requiresAuth: true } },
    { path: '/stocks/search', name: 'stock-search', component: YoutubeSearchView, meta: { requiresAuth: true } },
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
