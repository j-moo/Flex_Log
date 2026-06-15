<script setup>
import { onMounted, ref } from 'vue'

import {
  searchUsers,
  getFriends,
  sendFriendRequest,
  updateFriendStatus,
} from '@/api/friends'

const keyword = ref('')

const searchResults = ref([])
const friends = ref([])

const loadFriends = async () => {
  const response = await getFriends()
  friends.value = response.data
}

const search = async () => {
  if (!keyword.value.trim()) {
    searchResults.value = []
    return
  }

  const response =
    await searchUsers(keyword.value)

  searchResults.value = response.data
}

const requestFriend = async (id) => {
  try {
    await sendFriendRequest(id)

    alert('친구 요청을 보냈습니다.')

    await loadFriends()
  } catch (error) {
    console.error(error)
    alert('친구 요청 실패')
  }
}

const accept = async (id) => {
  await updateFriendStatus(
    id,
    'accepted',
  )

  await loadFriends()
}

const reject = async (id) => {
  await updateFriendStatus(
    id,
    'rejected',
  )

  await loadFriends()
}

onMounted(loadFriends)
</script>

<template>
  <section>
    <h1>친구</h1>

    <h2>유저 검색</h2>

    <input
      v-model="keyword"
      placeholder="아이디 검색"
    >

    <button @click="search">
      검색
    </button>

    <div
      v-for="user in searchResults"
      :key="user.id"
    >
      {{ user.username }}

      <button
        @click="requestFriend(user.id)"
      >
        친구 요청
      </button>
    </div>

    <hr>

    <h2>친구 요청</h2>

    <div
      v-for="friend in friends"
      :key="friend.id"
    >
      <div
        v-if="
          friend.status === 'pending'
        "
      >
        {{ friend.user_username }}
        →
        {{ friend.friend_username }}

        <button
          @click="accept(friend.id)"
        >
          수락
        </button>

        <button
          @click="reject(friend.id)"
        >
          거절
        </button>
      </div>
    </div>

    <hr>

    <h2>친구 목록</h2>

    <div
      v-for="friend in friends"
      :key="friend.id"
    >
      <div
        v-if="
          friend.status === 'accepted'
        "
      >
        {{ friend.user_username }}
        ↔
        {{ friend.friend_username }}
      </div>
    </div>
  </section>
</template>