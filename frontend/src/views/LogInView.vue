<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAccountStore } from '@/stores/account'

const router = useRouter()
const accountStore = useAccountStore()


const username = ref('')
const password = ref('')


const login = async () => {
  try {
    await accountStore.loginUser({
      username: username.value,
      password: password.value,
    })

    alert('로그인 성공!')

    router.push('/')

  } catch (error) {
    console.error(error)
    alert('로그인 실패')
  }
}
</script>


<template>
  <div>
    <h2>로그인</h2>

    <input
      v-model="username"
      placeholder="username"
    >
    <br>

    <input
      v-model="password"
      type="password"
      placeholder="password"
    >
    <br>

    <button @click="login">
      로그인
    </button>
  </div>
</template>