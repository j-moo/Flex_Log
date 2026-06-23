<script setup>
import { computed, onMounted, ref } from 'vue'

import { getFriendFeed } from '../api/expenses'
import { getFriends, searchUsers, sendFriendRequest } from '../api/friends'
import FeedCard from '../components/feed/FeedCard.vue'
import { useAccountStore } from '../stores/account'

const account = useAccountStore()

const logs = ref([])
const suggestions = ref([])
const friendships = ref([])
const isLoading = ref(true)
const errorMessage = ref('')
const actionMessage = ref('')
const requestingUserId = ref(null)

const suggestedFriends = computed(() =>
  suggestions.value
    .filter((user) => user.id !== account.user?.id)
    .sort((a, b) => {
      const aRelation = relationForUser(a.id)
      const bRelation = relationForUser(b.id)
      return Number(Boolean(aRelation)) - Number(Boolean(bRelation))
    })
    .slice(0, 6),
)

const relationForUser = (userId) =>
  friendships.value.find((item) =>
    item.counterpart?.id === userId || item.user?.id === userId || item.friend?.id === userId,
  )

const relationLabel = (userId) => {
  const relation = relationForUser(userId)
  if (!relation) return '친구 요청'
  if (relation.status === 'accepted') return '친구'
  return relation.user?.id === account.user?.id ? '요청중' : '요청 받음'
}

const canRequest = (userId) => !relationForUser(userId)

const requestFriend = async (user) => {
  if (!canRequest(user.id)) return
  requestingUserId.value = user.id
  actionMessage.value = ''
  errorMessage.value = ''
  try {
    friendships.value.unshift((await sendFriendRequest(user.id)).data)
    actionMessage.value = `${user.display_name || user.username}님에게 친구 요청을 보냈습니다.`
  } catch (error) {
    errorMessage.value = error.response?.data?.friend?.[0] || '친구 요청을 보내지 못했습니다.'
  } finally {
    requestingUserId.value = null
  }
}

const loadFeed = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    logs.value = (await getFriendFeed()).data
  } catch {
    errorMessage.value = '친구 피드를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const loadSuggestions = async () => {
  try {
    const [usersResponse, friendsResponse] = await Promise.all([
      searchUsers(''),
      getFriends(),
    ])
    suggestions.value = usersResponse.data
    friendships.value = friendsResponse.data
  } catch {
    suggestions.value = []
  }
}

onMounted(() => {
  loadFeed()
  loadSuggestions()
})
</script>

<template>
  <section class="feed-page">
    <main class="feed-stream" aria-label="피드 목록">
      <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
      <p v-if="actionMessage" class="notice-card">{{ actionMessage }}</p>
      <p v-if="isLoading" class="state-card">피드를 불러오는 중입니다.</p>
      <TransitionGroup v-else-if="logs.length" name="feed-list" tag="div" class="feed-list">
        <FeedCard
          v-for="(log, index) in logs"
          :key="log.id"
          class="stagger-item"
          :style="{ '--delay': `${index * 70}ms` }"
          :log="log"
        />
      </TransitionGroup>
      <div v-else class="state-card empty">
        <strong>아직 친구 피드가 비어 있어요.</strong>
        <p>프로필에서 친구를 관리하거나 첫 소비 기록을 공유해보세요.</p>
        <RouterLink class="vintage-button" :to="{ name: 'profile' }">프로필로 이동</RouterLink>
      </div>
    </main>

    <aside class="feed-sidebar">
      <section class="suggest-panel vintage-card">
        <div class="suggest-head">
          <span>추천 친구</span>
          <RouterLink :to="{ name: 'friends' }">관리</RouterLink>
        </div>

        <div v-if="suggestedFriends.length" class="suggest-list">
          <article v-for="friend in suggestedFriends" :key="friend.id" class="suggest-item">
            <RouterLink class="suggest-profile" :to="{ name: 'user-profile', params: { userId: friend.id } }">
              <img
                v-if="friend.profile_image && !friend.imageLoadFailed"
                class="suggest-avatar"
                :src="friend.profile_image"
                alt="profile image"
                @error="friend.imageLoadFailed = true"
              >
              <span v-else class="suggest-avatar">{{ (friend.display_name || friend.username).slice(0, 1).toUpperCase() }}</span>
              <div>
                <strong>{{ friend.display_name || friend.username }}</strong>
                <small>@{{ friend.username }}</small>
              </div>
            </RouterLink>
            <button
              type="button"
              :disabled="!canRequest(friend.id) || requestingUserId === friend.id"
              @click="requestFriend(friend)"
            >
              {{ requestingUserId === friend.id ? '요청중' : relationLabel(friend.id) }}
            </button>
          </article>
        </div>

        <div v-else class="suggest-empty">
          <p>추천할 사용자를 찾지 못했습니다.</p>
        </div>
      </section>
    </aside>
  </section>
</template>

<style scoped>
.feed-page {
  position: relative;
  display: grid;
  grid-template-columns: 1fr minmax(0, 650px) 1fr;
  gap: 28px;
  width: min(100%, 1240px);
  margin: 0 auto;
}

.feed-stream {
  grid-column: 2;
}

.feed-stream,
.feed-list {
  display: grid;
  gap: 22px;
}

.notice-card {
  border: 2px solid var(--color-ink);
  border-radius: 16px;
  background: var(--color-money-light);
  margin: 0;
  padding: 12px 14px;
  font-weight: 900;
}

.feed-sidebar {
  grid-column: 3;
  position: sticky;
  top: 112px;
  align-self: start;
  width: min(100%, 310px);
  margin-left: 18px;
}

.suggest-panel {
  display: grid;
  gap: 12px;
  padding: 18px;
}

.suggest-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.suggest-head span {
  color: var(--color-dark-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.suggest-head a {
  color: var(--color-dark-gold);
  font-size: 12px;
  font-weight: 900;
}

.suggest-list {
  display: grid;
  gap: 10px;
}

.suggest-item {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 10px;
  border: 2px solid rgba(23, 19, 13, 0.12);
  border-radius: 18px;
  background: rgba(255, 248, 231, 0.66);
  padding: 10px;
}

.suggest-profile {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.suggest-avatar {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-money);
  color: var(--color-paper);
  font-weight: 900;
}

img.suggest-avatar {
  object-fit: cover;
}

.suggest-profile div {
  display: grid;
  min-width: 0;
}

.suggest-profile strong,
.suggest-profile small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggest-profile small,
.suggest-empty {
  color: var(--color-muted);
  font-size: 12px;
}

.suggest-item button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-gold);
  color: var(--color-ink);
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 900;
  white-space: nowrap;
}

.suggest-item button:disabled {
  border-color: rgba(23, 19, 13, 0.22);
  background: rgba(200, 210, 170, 0.52);
  color: var(--color-muted);
  cursor: default;
}

.suggest-empty p {
  margin: 0;
}

.feed-list-enter-active,
.feed-list-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.feed-list-enter-from,
.feed-list-leave-to {
  opacity: 0;
  transform: translateY(18px);
}

@media (max-width: 1080px) {
  .feed-page {
    grid-template-columns: 1fr;
  }

  .feed-stream,
  .feed-sidebar {
    grid-column: 1;
  }

  .feed-sidebar {
    position: static;
    width: min(100%, 650px);
    margin: 0 auto;
    order: 2;
  }
}
</style>
