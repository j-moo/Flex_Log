<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import { getFriendFeed } from '../api/expenses'
import { getFriends, searchUsers, sendFriendRequest } from '../api/friends'
import FeedCard from '../components/feed/FeedCard.vue'
import { useAccountStore } from '../stores/account'

const account = useAccountStore()

const logs = ref([])
const suggestions = ref([])
const friendships = ref([])
const isLoading = ref(true)
const isLoadingMore = ref(false)
const errorMessage = ref('')
const actionMessage = ref('')
const requestingUserId = ref(null)
const feedOffset = ref(0)
const hasMoreFeed = ref(true)

const FEED_PAGE_SIZE = 8
const FEED_REFRESH_EVENT = 'flexlog:feed-saved'

const suggestedFriends = computed(() =>
  suggestions.value
    .filter((user) => user.id !== account.user?.id && !relationForUser(user.id))
    .sort((a, b) => {
      const countDiff = Number(b.mutual_friend_count || 0) - Number(a.mutual_friend_count || 0)
      return countDiff || String(a.username).localeCompare(String(b.username))
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

const normalizeFeedResponse = (data) => {
  if (Array.isArray(data)) {
    return {
      results: data,
      nextOffset: null,
    }
  }
  return {
    results: data.results || [],
    nextOffset: data.next_offset ?? null,
  }
}

const mergeLogs = (current, incoming) => {
  const byId = new Map(current.map((item) => [item.id, item]))
  incoming.forEach((item) => byId.set(item.id, item))
  return Array.from(byId.values())
}

const loadFeed = async ({ reset = false } = {}) => {
  if (!reset && (isLoading.value || isLoadingMore.value || !hasMoreFeed.value)) return
  if (reset) {
    isLoading.value = true
    feedOffset.value = 0
    hasMoreFeed.value = true
  } else {
    isLoadingMore.value = true
  }
  errorMessage.value = ''
  try {
    const response = await getFriendFeed({
      limit: FEED_PAGE_SIZE,
      offset: reset ? 0 : feedOffset.value,
    })
    const { results, nextOffset } = normalizeFeedResponse(response.data)
    logs.value = reset ? results : mergeLogs(logs.value, results)
    feedOffset.value = nextOffset ?? logs.value.length
    hasMoreFeed.value = nextOffset !== null
  } catch {
    errorMessage.value = '친구 피드를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
    await nextTick()
    handleWindowScroll()
  }
}

const handleWindowScroll = () => {
  if (!hasMoreFeed.value || isLoading.value || isLoadingMore.value) return
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  const viewportBottom = scrollTop + window.innerHeight
  const pageBottom = document.documentElement.scrollHeight
  if (viewportBottom >= pageBottom - 520) {
    loadFeed()
  }
}

const refreshFeedAfterSave = () => {
  loadFeed({ reset: true })
}

const loadSuggestions = async () => {
  try {
    const [usersResponse, friendsResponse] = await Promise.all([
      searchUsers('', { recommend: 1 }),
      getFriends(),
    ])
    suggestions.value = usersResponse.data
    friendships.value = friendsResponse.data
  } catch {
    suggestions.value = []
  }
}

onMounted(() => {
  loadFeed({ reset: true })
  loadSuggestions()
  window.addEventListener('scroll', handleWindowScroll, { passive: true })
  window.addEventListener(FEED_REFRESH_EVENT, refreshFeedAfterSave)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleWindowScroll)
  window.removeEventListener(FEED_REFRESH_EVENT, refreshFeedAfterSave)
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
              <span v-else class="suggest-avatar" aria-hidden="true"></span>
              <div>
                <strong>{{ friend.display_name || friend.username }}</strong>
                <small>@{{ friend.username }}</small>
                <small class="mutual-count">함께 아는 친구 {{ friend.mutual_friend_count || 0 }}명</small>
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

    <p v-if="isLoadingMore" class="feed-more">다음 피드를 불러오는 중입니다.</p>
    <p v-else-if="logs.length && !hasMoreFeed" class="feed-more">마지막 피드입니다.</p>
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
  width: min(100%, 350px);
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
  grid-template-columns: minmax(0, 1fr);
  align-items: start;
  gap: 10px;
  border: 2px solid rgba(23, 19, 13, 0.12);
  border-radius: 18px;
  background: rgba(255, 248, 231, 0.66);
  padding: 10px;
}

.suggest-profile {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr);
  align-items: start;
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
  overflow-wrap: anywhere;
  white-space: normal;
}

.suggest-profile small,
.suggest-empty {
  color: var(--color-muted);
  font-size: 12px;
}

.suggest-profile .mutual-count {
  color: var(--color-dark-gold);
  font-weight: 900;
}

.suggest-item button {
  justify-self: start;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-gold);
  color: var(--color-ink);
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 900;
  box-shadow: 3px 3px 0 var(--color-ink);
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
  white-space: nowrap;
}

.suggest-item button:hover:not(:disabled) {
  box-shadow: 1px 1px 0 var(--color-ink);
  transform: translate(2px, 2px);
}

.suggest-item button:active:not(:disabled) {
  box-shadow: 0 0 0 var(--color-ink);
  transform: translate(3px, 3px);
}

.suggest-item button:disabled {
  border-color: rgba(23, 19, 13, 0.22);
  background: rgba(200, 210, 170, 0.52);
  color: var(--color-muted);
  box-shadow: none;
  cursor: default;
}

.suggest-empty p {
  margin: 0;
}

.feed-more {
  grid-column: 2;
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
  font-weight: 900;
  text-align: center;
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
  .feed-sidebar,
  .feed-more {
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
