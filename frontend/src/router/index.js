import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import SignupView from '@/views/SignupView.vue'
import LoginView from '@/views/LoginView.vue'
import ProfileView from '@/views/ProfileView.vue'
import ExpenseListView from '@/views/ExpenseListView.vue'
import ExpenseCreateView from '@/views/ExpenseCreateView.vue'
import ExpenseEditView from '@/views/ExpenseEditView.vue'
import FriendView from '@/views/FriendView.vue'
import FriendFeedView from '@/views/FriendFeedView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
    {
      path: '/expenses',
      name: 'expenses',
      component: ExpenseListView,
    },
    {
      path: '/expenses/create',
      name: 'expense-create',
      component: ExpenseCreateView,
    },
    {
      path: '/expenses/:id/edit',
      name: 'expense-edit',
      component: ExpenseEditView,
    },
    {
  path: '/friends',
  name: 'friends',
  component: FriendView,
  },
  {
  path: '/feed',
  name: 'friend-feed',
  component: FriendFeedView,
  },
  ],
})

export default router