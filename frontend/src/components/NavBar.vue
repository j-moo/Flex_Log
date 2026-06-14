<template><nav class="nav"><div class="nav-inner"><RouterLink class="brand" :to="{name:'HomeView'}">Flex-log</RouterLink><div class="nav-links"><template v-if="store.isLogin"><RouterLink :to="{name:'ExpenseCreateView'}">기록</RouterLink><RouterLink :to="{name:'MyLogsView'}">내 로그</RouterLink><RouterLink :to="{name:'FeedView'}">피드</RouterLink><RouterLink :to="{name:'FriendsView'}">친구</RouterLink><RouterLink :to="{name:'AnalysisView'}">AI 분석</RouterLink><RouterLink :to="{name:'FinanceView'}">추천</RouterLink><RouterLink :to="{name:'ProfileView'}">프로필</RouterLink><button class="secondary" @click="logout">로그아웃</button></template><template v-else><RouterLink :to="{name:'SignUpView'}">회원가입</RouterLink><RouterLink :to="{name:'LogInView'}">로그인</RouterLink></template></div></div></nav></template>
<script setup>
import { useRouter } from 'vue-router'
import { useAccountStore } from '@/stores/account'
const router=useRouter(); const store=useAccountStore(); const logout=()=>{store.logOut(); router.push({name:'LogInView'})}
</script>
