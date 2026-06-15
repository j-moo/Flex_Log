<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAccountStore } from '@/stores/account'

const router = useRouter()
const accountStore = useAccountStore()

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')


const signup = async () => {
  try {
    await accountStore.signupUser({
      username: username.value,
      email: email.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    })

    alert('회원가입 성공!')
    router.push('/login')

  } catch (error) {
    console.error('회원가입 실패')

    if (error.response) {
      console.log('status:', error.response.status)
      console.log('data:', error.response.data)
    } else {
      console.log(error)
    }

    alert('회원가입 실패')
  }
}
</script>


<template>
  <div>
    <h2>회원가입</h2>

    <input
      v-model="username"
      placeholder="아이디"
    />
    <br>

    <input
      v-model="email"
      type="email"
      placeholder="이메일"
    />
    <br>

    <input
      v-model="password"
      type="password"
      placeholder="비밀번호"
    />
    <br>

    <input
      v-model="passwordConfirm"
      type="password"
      placeholder="비밀번호 확인"
    />
    <br>

    <button @click="signup">
      가입하기
    </button>
  </div>
</template>