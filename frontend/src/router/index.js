import { createRouter, createWebHistory } from 'vue-router'
import { useAccountStore } from '@/stores/account'
import HomeView from '@/views/HomeView.vue'
import SignUpView from '@/views/SignUpView.vue'
import LogInView from '@/views/LogInView.vue'
import ProfileView from '@/views/ProfileView.vue'
import ExpenseCreateView from '@/views/ExpenseCreateView.vue'
import MyLogsView from '@/views/MyLogsView.vue'
import FeedView from '@/views/FeedView.vue'
import FriendsView from '@/views/FriendsView.vue'
import AnalysisView from '@/views/AnalysisView.vue'
import FinanceView from '@/views/FinanceView.vue'
const router=createRouter({history:createWebHistory(import.meta.env.BASE_URL),routes:[
{path:'/',name:'HomeView',component:HomeView}, {path:'/signup',name:'SignUpView',component:SignUpView,meta:{guestOnly:true}}, {path:'/login',name:'LogInView',component:LogInView,meta:{guestOnly:true}},
{path:'/profile',name:'ProfileView',component:ProfileView,meta:{requiresAuth:true}}, {path:'/expenses/new',name:'ExpenseCreateView',component:ExpenseCreateView,meta:{requiresAuth:true}}, {path:'/expenses',name:'MyLogsView',component:MyLogsView,meta:{requiresAuth:true}},
{path:'/feed',name:'FeedView',component:FeedView,meta:{requiresAuth:true}}, {path:'/friends',name:'FriendsView',component:FriendsView,meta:{requiresAuth:true}}, {path:'/analysis',name:'AnalysisView',component:AnalysisView,meta:{requiresAuth:true}}, {path:'/finance',name:'FinanceView',component:FinanceView,meta:{requiresAuth:true}},
]})
router.beforeEach((to)=>{ const store=useAccountStore(); if(to.meta.requiresAuth && !store.isLogin) return {name:'LogInView'}; if(to.meta.guestOnly && store.isLogin) return {name:'HomeView'} })
export default router
