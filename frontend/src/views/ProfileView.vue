<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getUserExpenses } from '../api/expenses'
import { cancelProduct } from '../api/financial'
import { deleteFriend, getFriends, sendFriendRequest } from '../api/friends'
import { getMyProfile, getProfile, updateMyProfile } from '../api/profile'
import FriendModal from '../components/profile/FriendModal.vue'
import ProfileGrid from '../components/profile/ProfileGrid.vue'
import ProfileHeader from '../components/profile/ProfileHeader.vue'
import { useAccountStore } from '../stores/account'

const route = useRoute()
const account = useAccountStore()

const profile = ref(null)
const logs = ref([])
const friendships = ref([])
const isLoading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')
const isEditing = ref(false)
const isSubmitting = ref(false)
const imageFile = ref(null)
const imagePreview = ref('')
const showFriends = ref(false)
const activeTab = ref('posts')
const cancellingId = ref(null)
const friendActionPending = ref(false)
const form = reactive({ name: '', nickname: '', bio: '' })

const MOCK_PRODUCTS = [
  {
    id: 'mock-1',
    isMock: true,
    joined_at: '2026-03-12',
    product: { product_type: 'deposit', kor_co_nm: '카카오뱅크', fin_prdt_nm: '카카오뱅크 정기예금' },
    option: { save_trm: 12, intr_rate2: 3.4 },
  },
  {
    id: 'mock-2',
    isMock: true,
    joined_at: '2026-04-03',
    product: { product_type: 'saving', kor_co_nm: '신한은행', fin_prdt_nm: '신한 청년적금' },
    option: { save_trm: 24, intr_rate2: 4.2 },
  },
  {
    id: 'mock-3',
    isMock: true,
    joined_at: '2026-05-21',
    product: { product_type: 'saving', kor_co_nm: 'KB국민은행', fin_prdt_nm: '국민 자유적금' },
    option: { save_trm: 12, intr_rate2: 3.8 },
  },
]

const requestedUserId = computed(() => (route.params.userId ? Number(route.params.userId) : account.user?.id))
const isOwnProfile = computed(() => requestedUserId.value === account.user?.id)
const displayedProducts = computed(() =>
  profile.value?.joined_products?.length ? profile.value.joined_products : MOCK_PRODUCTS,
)
const productCount = computed(() => displayedProducts.value.length)
const maxRate = computed(() =>
  Math.max(1, ...displayedProducts.value.map((item) => Number(item.option.intr_rate2 || item.option.intr_rate || 0))),
)
const targetRelation = computed(() =>
  friendships.value.find((item) =>
    item.counterpart?.id === requestedUserId.value
    || item.user?.id === requestedUserId.value
    || item.friend?.id === requestedUserId.value,
  ),
)
const friendActionLabel = computed(() => {
  if (isOwnProfile.value) return ''
  if (!targetRelation.value) return '친구 요청'
  if (targetRelation.value.status === 'accepted') return '친구 삭제'
  return '요청 삭제'
})
const friendActionTone = computed(() => (targetRelation.value ? 'danger' : 'primary'))

const applyProfile = (data) => {
  profile.value = data
  form.name = data.name || ''
  form.nickname = data.nickname || ''
  form.bio = data.bio || ''
  imagePreview.value = data.image || ''
  if (isOwnProfile.value) {
    account.user = {
      ...account.user,
      name: data.name || '',
      username: data.username,
      email: data.email,
    }
  }
}

const loadFriendships = async () => {
  friendships.value = (await getFriends()).data
}

const loadProfileData = async () => {
  const response = isOwnProfile.value ? await getMyProfile() : await getProfile(requestedUserId.value)
  applyProfile(response.data)
  logs.value = (await getUserExpenses(response.data.user_id)).data
}

const loadProfile = async () => {
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  isEditing.value = false
  try {
    await Promise.all([loadProfileData(), loadFriendships()])
  } catch {
    errorMessage.value = '프로필을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const selectImage = (event) => {
  imageFile.value = event.target.files?.[0] || null
  if (imageFile.value) imagePreview.value = URL.createObjectURL(imageFile.value)
}

const submit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const payload = new FormData()
  payload.append('name', form.name)
  payload.append('nickname', form.nickname)
  payload.append('bio', form.bio)
  if (imageFile.value) payload.append('image', imageFile.value)

  try {
    applyProfile((await updateMyProfile(payload)).data)
    isEditing.value = false
    successMessage.value = '프로필을 저장했습니다.'
  } catch (error) {
    errorMessage.value = Object.values(error.response?.data || {}).flat().join(' ') || '프로필 저장에 실패했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

const handleFriendAction = async () => {
  if (isOwnProfile.value || !requestedUserId.value) return
  friendActionPending.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    if (targetRelation.value) {
      await deleteFriend(targetRelation.value.id)
      successMessage.value = '친구 관계를 삭제했습니다.'
    } else {
      await sendFriendRequest(requestedUserId.value)
      successMessage.value = '친구 요청을 보냈습니다.'
    }
    await Promise.all([loadFriendships(), loadProfileData()])
  } catch (error) {
    errorMessage.value = error.response?.data?.friend?.[0] || error.response?.data?.detail || '친구 관계 처리에 실패했습니다.'
  } finally {
    friendActionPending.value = false
  }
}

const cancelSubscription = async (item) => {
  if (!window.confirm(`${item.product.fin_prdt_nm} 가입을 해지할까요?`)) return
  cancellingId.value = item.id
  try {
    await cancelProduct(item.id)
    await loadProfileData()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '가입상품 해지에 실패했습니다.'
  } finally {
    cancellingId.value = null
  }
}

watch(() => route.params.userId, loadProfile)
onMounted(loadProfile)
</script>

<template>
  <section class="profile-page page-shell">
    <div v-if="isLoading" class="state-card">프로필을 불러오는 중입니다.</div>
    <div v-else-if="errorMessage && !profile" class="state-card error">{{ errorMessage }}</div>

    <template v-else-if="profile">
      <ProfileHeader
        :profile="profile"
        :post-count="logs.length"
        :product-count="productCount"
        :is-own="isOwnProfile"
        :friend-action-label="friendActionLabel"
        :friend-action-tone="friendActionTone"
        :friend-action-disabled="friendActionPending"
        @friends="isOwnProfile ? (showFriends = true) : null"
        @edit="isEditing = !isEditing"
        @friend-action="handleFriendAction"
      />

      <p v-if="successMessage" class="profile-message">{{ successMessage }}</p>
      <p v-if="errorMessage" class="profile-message error">{{ errorMessage }}</p>

      <form v-if="isOwnProfile && isEditing" class="edit-card glass-panel" @submit.prevent="submit">
        <div class="edit-photo">
          <img v-if="imagePreview" :src="imagePreview" alt="프로필 이미지">
          <span v-else>{{ (profile.nickname || profile.username || 'F').slice(0, 1) }}</span>
          <label>
            사진 변경
            <input type="file" accept="image/*" @change="selectImage">
          </label>
        </div>

        <div class="edit-fields">
          <label>
            이름
            <input v-model.trim="form.name" maxlength="50">
          </label>
          <label>
            닉네임
            <input v-model.trim="form.nickname" maxlength="30" required>
          </label>
          <label>
            소개
            <textarea v-model="form.bio" rows="3"></textarea>
          </label>
          <div>
            <button class="vintage-button" type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? '저장 중...' : '저장' }}
            </button>
            <button class="ghost-button" type="button" @click="isEditing = false">취소</button>
          </div>
        </div>
      </form>

      <nav class="profile-tabs">
        <button :class="{ active: activeTab === 'posts' }" type="button" @click="activeTab = 'posts'">게시글</button>
        <button :class="{ active: activeTab === 'products' }" type="button" @click="activeTab = 'products'">가입상품</button>
      </nav>

      <Transition name="fade-slide" mode="out-in">
        <ProfileGrid v-if="activeTab === 'posts'" key="posts" :logs="logs" />

        <section v-else key="products" class="joined-products">
          <div class="product-section-head">
            <div>
              <h2>가입 금융상품</h2>
              <p>
                선택한 상품의 최고 금리를 비교합니다.
                <span v-if="!profile.joined_products?.length">현재 예시 데이터가 표시됩니다.</span>
              </p>
            </div>
            <RouterLink v-if="isOwnProfile" :to="{ name: 'finance-hub', query: { tab: 'products' } }">상품 찾기</RouterLink>
          </div>

          <article v-for="item in displayedProducts" :key="item.id" class="product-card glass-panel">
            <span class="product-avatar">{{ item.product.product_type === 'deposit' ? '예' : '적' }}</span>
            <div class="product-copy">
              <strong>{{ item.product.fin_prdt_nm }}</strong>
              <small>
                {{ item.product.kor_co_nm }} · {{ item.option.save_trm }}개월 ·
                {{ new Date(item.joined_at).toLocaleDateString('ko-KR') }}
              </small>
              <div class="rate-track">
                <i :style="{ width: `${Number(item.option.intr_rate2 || item.option.intr_rate || 0) / maxRate * 100}%` }"></i>
              </div>
            </div>
            <div class="product-rate">
              <strong>{{ Number(item.option.intr_rate2 || item.option.intr_rate || 0).toFixed(2) }}%</strong>
              <button
                v-if="isOwnProfile && !item.isMock"
                type="button"
                :disabled="cancellingId === item.id"
                @click="cancelSubscription(item)"
              >
                해지
              </button>
            </div>
          </article>
        </section>
      </Transition>

      <FriendModal v-if="showFriends" @close="showFriends = false" />
    </template>
  </section>
</template>

<style scoped>
.profile-page {
  width: min(100%, 840px);
  margin: 0 auto;
}

.profile-message {
  border: 2px solid var(--color-ink);
  border-radius: 16px;
  background: var(--color-money-light);
  color: var(--color-ink);
  margin: 0;
  padding: 10px 13px;
  font-weight: 900;
}

.profile-message.error {
  background: rgba(182, 74, 53, 0.12);
  color: var(--color-red);
}

.edit-card {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 20px;
  padding: 18px;
}

.edit-photo {
  display: grid;
  align-content: start;
  justify-items: center;
  gap: 9px;
}

.edit-photo img,
.edit-photo > span {
  display: grid;
  width: 82px;
  height: 82px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  object-fit: cover;
  background: var(--color-money);
  color: var(--color-paper);
  font-size: 26px;
  font-weight: 900;
}

.edit-photo label {
  color: var(--color-dark-gold);
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}

.edit-photo input {
  display: none;
}

.edit-fields {
  display: grid;
  gap: 10px;
}

.edit-fields label {
  display: grid;
  gap: 5px;
  color: var(--color-muted);
  font-weight: 900;
}

.edit-fields input,
.edit-fields textarea {
  width: 100%;
  border: 2px solid rgba(23, 19, 13, 0.22);
  border-radius: 14px;
  background: rgba(255, 248, 231, 0.8);
  padding: 10px;
}

.edit-fields > div {
  display: flex;
  gap: 8px;
}

.ghost-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 9px 14px;
  font-weight: 900;
}

.profile-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  overflow: hidden;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.68);
  padding: 5px;
}

.profile-tabs button {
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--color-muted);
  padding: 11px;
  font-weight: 900;
}

.profile-tabs button.active {
  background: var(--color-gold);
  color: var(--color-ink);
}

.joined-products {
  display: grid;
  gap: 12px;
}

.product-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.product-section-head h2 {
  margin: 0;
  font-size: 23px;
}

.product-section-head p {
  margin: 4px 0 0;
  color: var(--color-muted);
}

.product-section-head a {
  color: var(--color-dark-gold);
  font-weight: 900;
}

.product-card {
  display: grid;
  grid-template-columns: 50px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 13px;
}

.product-avatar {
  display: grid;
  width: 50px;
  height: 50px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-gold);
  color: var(--color-ink);
  font-weight: 900;
}

.product-copy {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.product-copy strong,
.product-copy small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-copy small {
  color: var(--color-muted);
}

.rate-track {
  height: 7px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(23, 19, 13, 0.12);
}

.rate-track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--color-money);
}

.product-rate {
  display: grid;
  justify-items: end;
}

.product-rate strong {
  color: var(--color-dark-gold);
  font-size: 20px;
}

.product-rate button {
  border: 0;
  background: transparent;
  color: var(--color-red);
  padding: 0;
  font-size: 12px;
  font-weight: 900;
}

@media (max-width: 600px) {
  .edit-card {
    grid-template-columns: 1fr;
  }

  .product-card {
    grid-template-columns: 46px 1fr;
  }

  .product-rate {
    grid-column: 2;
    display: flex;
    justify-content: space-between;
    width: 100%;
  }
}
</style>
