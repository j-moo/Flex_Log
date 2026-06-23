<script setup>
import { computed, onMounted, ref } from 'vue'

import {
  deleteFriend,
  getFriends,
  searchUsers as searchUsersApi,
  sendFriendRequest,
  updateFriendStatus,
} from '../api/friends'
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
const acceptedFriends = computed(() => friends.value.filter((item) => item.status === 'accepted'))

const loadFriends = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    friends.value = (await getFriends()).data
  } catch {
    errorMessage.value = '친구 목록을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const searchUsers = async () => {
  message.value = ''
  errorMessage.value = ''
  try {
    users.value = (await searchUsersApi(search.value)).data
  } catch {
    errorMessage.value = '사용자 검색에 실패했습니다.'
  }
}

const requestFriend = async (user) => {
  try {
    const response = await sendFriendRequest(user.id)
    friends.value.unshift(response.data)
    users.value = users.value.filter((item) => item.id !== user.id)
    message.value = '친구 요청을 보냈습니다.'
  } catch (error) {
    errorMessage.value = Object.values(error.response?.data || {}).flat().join(' ') || '친구 요청에 실패했습니다.'
  }
}

const updateStatus = async (friend, status) => {
  const response = await updateFriendStatus(friend.id, status)
  friends.value = friends.value.map((item) => (item.id === friend.id ? response.data : item))
}

const removeFriend = async (friend) => {
  await deleteFriend(friend.id)
  friends.value = friends.value.filter((item) => item.id !== friend.id)
}

onMounted(loadFriends)
</script>

<template>
  <section class="friends-page page-shell">
    <div class="section-head">
      <div>
        <h1>친구</h1>
        <p>친구를 찾고 요청 상태를 관리합니다.</p>
      </div>
    </div>

    <p v-if="message" class="notice-card">{{ message }}</p>
    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>

    <section class="search-card glass-panel">
      <h2>사용자 찾기</h2>
      <form @submit.prevent="searchUsers">
        <input v-model.trim="search" class="form-control" placeholder="아이디, 이름, 이메일, 닉네임">
        <button class="vintage-button">검색</button>
      </form>
      <div v-if="users.length" class="user-results">
        <article v-for="user in users" :key="user.id">
          <RouterLink :to="{ name: 'user-profile', params: { userId: user.id } }">
            <strong>{{ user.display_name }}</strong>
            <small>@{{ user.username }}</small>
          </RouterLink>
          <button type="button" @click="requestFriend(user)">요청</button>
        </article>
      </div>
    </section>

    <div v-if="isLoading" class="state-card">불러오는 중입니다.</div>

    <div class="friend-columns">
      <section class="friend-panel vintage-card">
        <h2>받은 요청</h2>
        <div v-if="!receivedPending.length" class="mini-empty">받은 요청이 없습니다.</div>
        <article v-for="friend in receivedPending" :key="friend.id">
          <strong>{{ friend.user.display_name }}</strong>
          <small>{{ formatDate(friend.created_at) }}</small>
          <div>
            <button type="button" @click="updateStatus(friend, 'accepted')">수락</button>
            <button type="button" @click="updateStatus(friend, 'rejected')">거절</button>
          </div>
        </article>
      </section>

      <section class="friend-panel vintage-card">
        <h2>보낸 요청</h2>
        <div v-if="!sentPending.length" class="mini-empty">보낸 요청이 없습니다.</div>
        <article v-for="friend in sentPending" :key="friend.id">
          <RouterLink :to="{ name: 'user-profile', params: { userId: friend.friend.id } }">
            <strong>{{ friend.friend.display_name }}</strong>
            <small>{{ formatDate(friend.created_at) }}</small>
          </RouterLink>
          <button type="button" @click="removeFriend(friend)">취소</button>
        </article>
      </section>

      <section class="friend-panel vintage-card">
        <h2>친구 목록</h2>
        <div v-if="!acceptedFriends.length" class="mini-empty">친구가 없습니다.</div>
        <article v-for="friend in acceptedFriends" :key="friend.id">
          <RouterLink :to="{ name: 'user-profile', params: { userId: friend.counterpart.id } }">
            <strong>{{ friend.counterpart.display_name }}</strong>
            <small>@{{ friend.counterpart.username }}</small>
          </RouterLink>
          <button type="button" @click="removeFriend(friend)">삭제</button>
        </article>
      </section>
    </div>
  </section>
</template>

<style scoped>
.friends-page {
  display: grid;
  gap: 18px;
}

.notice-card {
  border: 2px solid var(--color-ink);
  border-radius: 16px;
  background: var(--color-money-light);
  margin: 0;
  padding: 12px;
  font-weight: 900;
}

.search-card {
  display: grid;
  gap: 14px;
  padding: 18px;
}

.search-card h2,
.friend-panel h2 {
  margin: 0;
  font-size: 22px;
}

.search-card form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.user-results,
.friend-panel {
  display: grid;
  gap: 10px;
}

.user-results article,
.friend-panel article {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-radius: 16px;
  background: rgba(255, 248, 231, 0.7);
  padding: 11px;
}

.user-results a,
.friend-panel a,
.friend-panel article > strong {
  display: grid;
}

small,
.mini-empty {
  color: var(--color-muted);
}

.user-results button,
.friend-panel button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-gold);
  color: var(--color-ink);
  padding: 7px 11px;
  font-size: 12px;
  font-weight: 900;
}

.friend-columns {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.friend-panel {
  align-content: start;
  padding: 16px;
}

@media (max-width: 900px) {
  .friend-columns,
  .search-card form {
    grid-template-columns: 1fr;
  }
}
</style>
