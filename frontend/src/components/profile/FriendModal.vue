<script setup>
import { computed, onMounted, ref } from 'vue'

import { deleteFriend, getFriends, searchUsers, sendFriendRequest, updateFriendStatus } from '../../api/friends'
import { useAccountStore } from '../../stores/account'

defineEmits(['close', 'changed'])

const account = useAccountStore()
const friends = ref([])
const tab = ref('friends')
const isLoading = ref(true)
const errorMessage = ref('')
const query = ref('')
const friendQuery = ref('')
const users = ref([])
const searchMessage = ref('')

const pending = computed(() => friends.value.filter((item) => item.status === 'pending'))
const accepted = computed(() => friends.value.filter((item) => item.status === 'accepted'))
const person = (item) => item.counterpart || (item.user.id === account.user?.id ? item.friend : item.user)
const isReceived = (item) => item.friend.id === account.user?.id
const filteredAccepted = computed(() => {
  const keyword = friendQuery.value.trim().toLowerCase()
  if (!keyword) return accepted.value
  return accepted.value.filter((item) => {
    const target = person(item)
    return [target.display_name, target.username, target.name].some((value) =>
      String(value || '').toLowerCase().includes(keyword),
    )
  })
})
const visible = computed(() => (tab.value === 'requests' ? pending.value : filteredAccepted.value))

const findRelation = (userId) =>
  friends.value.find((item) => {
    const target = person(item)
    return target?.id === userId
  })

const load = async () => {
  try {
    friends.value = (await getFriends()).data
  } catch {
    errorMessage.value = '친구 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const change = async (item, status) => {
  const updated = (await updateFriendStatus(item.id, status)).data
  friends.value = friends.value.map((value) => (value.id === item.id ? updated : value))
}

const remove = async (item) => {
  if (!window.confirm(item.status === 'accepted' ? '친구를 삭제할까요?' : '친구 요청을 취소할까요?')) return
  await deleteFriend(item.id)
  friends.value = friends.value.filter((value) => value.id !== item.id)
}

const findUsers = async () => {
  if (!query.value.trim()) return
  searchMessage.value = ''
  try {
    users.value = (await searchUsers(query.value.trim())).data
    if (!users.value.length) searchMessage.value = '검색 결과가 없습니다.'
  } catch {
    searchMessage.value = '사용자 검색에 실패했습니다.'
  }
}

const request = async (user) => {
  try {
    friends.value.unshift((await sendFriendRequest(user.id)).data)
    searchMessage.value = '친구 요청을 보냈습니다.'
  } catch (error) {
    searchMessage.value = Object.values(error.response?.data || {}).flat().join(' ') || '친구 요청에 실패했습니다.'
  }
}

onMounted(load)
</script>

<template>
  <Teleport to="body">
    <div class="sheet-backdrop" @click.self="$emit('close')">
      <section class="friend-sheet">
        <header>
          <span></span>
          <h2>친구 관리</h2>
          <button type="button" @click="$emit('close')">×</button>
        </header>

        <div class="sheet-tabs">
          <button :class="{ active: tab === 'friends' }" type="button" @click="tab = 'friends'">친구 {{ accepted.length }}</button>
          <button :class="{ active: tab === 'requests' }" type="button" @click="tab = 'requests'">요청 {{ pending.length }}</button>
          <button :class="{ active: tab === 'find' }" type="button" @click="tab = 'find'">친구 찾기</button>
        </div>

        <template v-if="tab === 'find'">
          <form class="friend-search" @submit.prevent="findUsers">
            <input v-model="query" placeholder="아이디, 이름, 닉네임">
            <button type="submit">검색</button>
          </form>
          <p v-if="searchMessage" class="search-message">{{ searchMessage }}</p>
          <div class="friend-list">
            <article v-for="user in users" :key="user.id">
              <RouterLink class="person-link" :to="{ name: 'user-profile', params: { userId: user.id } }" @click="$emit('close')">
                <span class="friend-avatar">{{ user.display_name.slice(0, 1) }}</span>
                <div>
                  <strong>{{ user.display_name }}</strong>
                  <small>@{{ user.username }}</small>
                </div>
              </RouterLink>

              <button
                v-if="findRelation(user.id)"
                class="remove"
                type="button"
                @click="remove(findRelation(user.id))"
              >
                삭제
              </button>
              <button v-else class="request-button" type="button" @click="request(user)">요청</button>
            </article>
          </div>
        </template>

        <template v-else>
          <form v-if="tab === 'friends'" class="friend-search compact" @submit.prevent>
            <input v-model="friendQuery" placeholder="친구 이름 또는 닉네임 검색">
          </form>
          <p v-if="isLoading" class="sheet-state">불러오는 중...</p>
          <p v-else-if="errorMessage" class="sheet-state error">{{ errorMessage }}</p>
          <p v-else-if="!visible.length" class="sheet-state">표시할 사용자가 없습니다.</p>
          <div v-else class="friend-list">
            <article v-for="item in visible" :key="item.id">
              <RouterLink
                class="person-link"
                :to="{ name: 'user-profile', params: { userId: person(item).id } }"
                @click="$emit('close')"
              >
                <span class="friend-avatar">{{ person(item).display_name.slice(0, 1) }}</span>
                <div>
                  <strong>{{ person(item).display_name }}</strong>
                  <small>
                    @{{ person(item).username }}
                    <em v-if="tab === 'requests'">{{ isReceived(item) ? '받은 요청' : '보낸 요청' }}</em>
                  </small>
                </div>
              </RouterLink>

              <div v-if="tab === 'requests' && isReceived(item)" class="request-actions">
                <button type="button" @click="change(item, 'accepted')">수락</button>
                <button type="button" @click="change(item, 'rejected')">거절</button>
              </div>
              <button v-else class="remove" type="button" @click="remove(item)">
                {{ tab === 'requests' ? '취소' : '삭제' }}
              </button>
            </article>
          </div>
        </template>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.sheet-backdrop {
  position: fixed;
  inset: 0;
  z-index: 130;
  display: grid;
  place-items: center;
  background: rgba(23, 19, 13, 0.32);
  padding: 18px;
  backdrop-filter: blur(8px);
}

.friend-sheet {
  display: grid;
  width: min(100%, 540px);
  max-height: min(84vh, 680px);
  overflow: hidden;
  border: 3px solid var(--color-ink);
  border-radius: 26px;
  background: rgba(255, 248, 231, 0.94);
  box-shadow: 7px 7px 0 var(--color-ink);
}

.friend-sheet header {
  display: grid;
  grid-template-columns: 34px 1fr 34px;
  align-items: center;
  border-bottom: 2px solid var(--color-ink);
  padding: 14px 16px;
}

.friend-sheet h2 {
  margin: 0;
  text-align: center;
}

.friend-sheet header button {
  border: 0;
  background: transparent;
  color: var(--color-ink);
  font-size: 28px;
}

.sheet-tabs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}

.sheet-tabs button {
  border: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--color-muted);
  padding: 13px 6px;
  font-weight: 900;
}

.sheet-tabs button.active {
  border-color: var(--color-ink);
  background: rgba(216, 165, 38, 0.16);
  color: var(--color-ink);
}

.sheet-state {
  min-height: 180px;
  margin: 0;
  padding: 50px 20px;
  color: var(--color-muted);
  text-align: center;
}

.sheet-state.error,
.search-message {
  color: var(--color-red);
}

.friend-list {
  overflow: auto;
}

.friend-list article {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(23, 19, 13, 0.14);
  padding: 12px 16px;
}

.person-link {
  display: grid;
  grid-template-columns: 42px 1fr;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.friend-avatar {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-money);
  color: var(--color-paper);
  font-weight: 900;
}

.person-link div {
  display: grid;
  min-width: 0;
}

.person-link strong,
.person-link small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.person-link small {
  color: var(--color-muted);
}

.person-link em {
  margin-left: 4px;
  color: var(--color-dark-gold);
  font-style: normal;
  font-weight: 900;
}

.request-actions {
  display: flex;
  gap: 5px;
}

.request-actions button,
.remove,
.request-button,
.friend-search button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-gold);
  color: var(--color-ink);
  padding: 7px 11px;
  font-size: 12px;
  font-weight: 900;
}

.request-actions button:last-child,
.remove {
  background: var(--color-paper);
}

.friend-search {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  padding: 14px;
}

.friend-search.compact {
  grid-template-columns: 1fr;
  padding-bottom: 8px;
}

.friend-search input {
  border: 2px solid rgba(23, 19, 13, 0.22);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.78);
  padding: 11px 14px;
}

.search-message {
  margin: 0;
  padding: 0 14px 10px;
  font-size: 13px;
}
</style>
