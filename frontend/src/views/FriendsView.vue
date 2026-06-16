<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '../api/client'
import { useAccountStore } from '../stores/account'
import { formatDate } from '../utils/format'


const account = useAccountStore()
const friends = ref([])
const users = ref([])
const search = ref('')
const isLoading = ref(true)
const message = ref('')
const errorMessage = ref('')

const receivedPending = computed(() =>
  friends.value.filter((item) => item.status === 'pending' && item.friend.id === account.user?.id),
)
const sentPending = computed(() =>
  friends.value.filter((item) => item.status === 'pending' && item.user.id === account.user?.id),
)
const acceptedFriends = computed(() =>
  friends.value.filter((item) => item.status === 'accepted'),
)

const loadFriends = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/api/v1/friends/')
    friends.value = response.data
  } catch {
    errorMessage.value = '친구 목록을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const searchUsers = async () => {
  message.value = ''
  errorMessage.value = ''
  const response = await api.get('/api/v1/friends/users/', {
    params: { search: search.value },
  })
  users.value = response.data
}

const requestFriend = async (user) => {
  try {
    const response = await api.post('/api/v1/friends/', { friend: user.id })
    friends.value.unshift(response.data)
    users.value = users.value.filter((item) => item.id !== user.id)
    message.value = '친구 요청을 보냈습니다.'
  } catch (error) {
    errorMessage.value = Object.values(error.response?.data || {}).flat().join(' ') || '친구 요청에 실패했습니다.'
  }
}

const updateStatus = async (friend, status) => {
  const response = await api.patch(`/api/v1/friends/${friend.id}/`, { status })
  friends.value = friends.value.map((item) => (item.id === friend.id ? response.data : item))
}

const removeFriend = async (friend) => {
  await api.delete(`/api/v1/friends/${friend.id}/`)
  friends.value = friends.value.filter((item) => item.id !== friend.id)
}

onMounted(loadFriends)
</script>

<template>
  <section class="d-grid gap-4">
    <div>
      <h1 class="h3 mb-1">친구</h1>
      <p class="text-secondary mb-0">친구 요청과 친구 관계를 관리합니다.</p>
    </div>

    <div v-if="message" class="alert alert-success mb-0">{{ message }}</div>
    <div v-if="errorMessage" class="alert alert-danger mb-0">{{ errorMessage }}</div>

    <div class="card">
      <div class="card-header bg-white">
        <h2 class="h5 mb-0">사용자 찾기</h2>
      </div>
      <div class="card-body">
        <form class="row g-2" @submit.prevent="searchUsers">
          <div class="col-12 col-sm">
            <input v-model.trim="search" class="form-control" placeholder="아이디, 이름, 이메일">
          </div>
          <div class="col-12 col-sm-auto">
            <button class="btn btn-primary w-100">검색</button>
          </div>
        </form>
        <div v-if="users.length" class="list-group mt-3">
          <div v-for="user in users" :key="user.id" class="list-group-item d-flex justify-content-between align-items-center gap-2">
            <div>
              <strong>{{ user.display_name }}</strong>
              <div class="small text-secondary">@{{ user.username }}</div>
            </div>
            <button class="btn btn-outline-primary btn-sm" type="button" @click="requestFriend(user)">요청</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>

    <div class="row g-3">
      <div class="col-12 col-lg-4">
        <div class="card h-100">
          <div class="card-header bg-white"><h2 class="h5 mb-0">받은 요청</h2></div>
          <div class="list-group list-group-flush">
            <div v-if="!receivedPending.length" class="list-group-item text-secondary">받은 요청이 없습니다.</div>
            <div v-for="friend in receivedPending" :key="friend.id" class="list-group-item">
              <strong>{{ friend.user.display_name }}</strong>
              <div class="small text-secondary mb-2">{{ formatDate(friend.created_at) }}</div>
              <div class="d-flex gap-2">
                <button class="btn btn-primary btn-sm" type="button" @click="updateStatus(friend, 'accepted')">수락</button>
                <button class="btn btn-outline-secondary btn-sm" type="button" @click="updateStatus(friend, 'rejected')">거절</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-4">
        <div class="card h-100">
          <div class="card-header bg-white"><h2 class="h5 mb-0">보낸 요청</h2></div>
          <div class="list-group list-group-flush">
            <div v-if="!sentPending.length" class="list-group-item text-secondary">보낸 요청이 없습니다.</div>
            <div v-for="friend in sentPending" :key="friend.id" class="list-group-item d-flex justify-content-between align-items-center gap-2">
              <div>
                <strong>{{ friend.friend.display_name }}</strong>
                <div class="small text-secondary">{{ formatDate(friend.created_at) }}</div>
              </div>
              <button class="btn btn-outline-danger btn-sm" type="button" @click="removeFriend(friend)">취소</button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-4">
        <div class="card h-100">
          <div class="card-header bg-white"><h2 class="h5 mb-0">친구 목록</h2></div>
          <div class="list-group list-group-flush">
            <div v-if="!acceptedFriends.length" class="list-group-item text-secondary">친구가 없습니다.</div>
            <div v-for="friend in acceptedFriends" :key="friend.id" class="list-group-item d-flex justify-content-between align-items-center gap-2">
              <div>
                <strong>{{ friend.counterpart.display_name }}</strong>
                <div class="small text-secondary">@{{ friend.counterpart.username }}</div>
              </div>
              <button class="btn btn-outline-danger btn-sm" type="button" @click="removeFriend(friend)">삭제</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
