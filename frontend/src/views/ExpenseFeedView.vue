<script setup>
import { reactive, onMounted, ref } from 'vue'

import {
  createComment,
  getComments,
  getFriendFeed,
  toggleExpenseLike,
} from '../api/expenses'
import { formatAmount, formatDate, isVideo } from '../utils/format'


const logs = ref([])
const commentsByLog = reactive({})
const commentForms = reactive({})
const isLoading = ref(true)
const errorMessage = ref('')

const loadFeed = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await getFriendFeed()
    logs.value = response.data
  } catch {
    errorMessage.value = '친구 피드를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const toggleLike = async (log) => {
  const response = await toggleExpenseLike(log.id)
  log.is_liked = response.data.liked
  log.like_count = response.data.like_count
}

const loadComments = async (log) => {
  if (commentsByLog[log.id]) {
    delete commentsByLog[log.id]
    return
  }
  const response = await getComments(log.id)
  commentsByLog[log.id] = response.data
  commentForms[log.id] = ''
}

const addComment = async (log) => {
  const content = (commentForms[log.id] || '').trim()
  if (!content) return
  const response = await createComment(log.id, content)
  commentsByLog[log.id].push(response.data)
  commentForms[log.id] = ''
  log.comment_count += 1
}

onMounted(loadFeed)
</script>

<template>
  <section>
    <div class="section-head">
      <div>
        <h1>메인 피드</h1>
        <p>친구들이 공유한 소비 기록을 최신순으로 확인합니다.</p>
      </div>
      <RouterLink class="btn btn-primary" :to="{ name: 'log-create' }">소비 기록 작성</RouterLink>
    </div>

    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
    <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-else-if="logs.length" class="row g-3">
      <div v-for="log in logs" :key="log.id" class="col-12 col-lg-6">
        <article class="surface overflow-hidden h-100">
          <div v-if="log.media" class="media-frame">
            <video v-if="isVideo(log.media)" class="log-media" :src="log.media" controls></video>
            <img v-else class="log-media" :src="log.media" alt="소비 기록 이미지">
            <div v-if="log.overlay_text" class="overlay-text">
              {{ log.overlay_text }}
            </div>
          </div>
          <div class="p-3 d-grid gap-3">
            <div class="d-flex justify-content-between gap-2">
              <div>
                <RouterLink class="fw-bold" :to="{ name: 'user-profile', params: { userId: log.user_id } }">
                  {{ log.display_name }}
                </RouterLink>
                <div class="small text-secondary">{{ formatDate(log.created_at) }}</div>
              </div>
              <div class="text-end">
                <span class="badge text-bg-light border">{{ log.category_name }}</span>
                <div class="fw-bold mt-1">{{ formatAmount(log.amount) }}</div>
              </div>
            </div>

            <div class="d-grid gap-1">
              <strong v-if="log.product_name">{{ log.product_name }}</strong>
              <span v-if="log.merchant" class="text-secondary small">{{ log.merchant }}</span>
              <p v-if="log.content" class="content-preline mb-0">{{ log.content }}</p>
            </div>

            <div class="d-flex gap-2 flex-wrap">
              <button
                class="btn btn-sm"
                :class="log.is_liked ? 'btn-primary' : 'btn-outline-primary'"
                type="button"
                @click="toggleLike(log)"
              >
                좋아요 {{ log.like_count }}
              </button>
              <button class="btn btn-outline-secondary btn-sm" type="button" @click="loadComments(log)">
                댓글 {{ log.comment_count }}
              </button>
            </div>

            <div v-if="commentsByLog[log.id]" class="border-top pt-3 d-grid gap-2">
              <div v-if="!commentsByLog[log.id].length" class="small text-secondary">댓글이 없습니다.</div>
              <div v-for="comment in commentsByLog[log.id]" :key="comment.id" class="small">
                <strong>{{ comment.display_name }}</strong>
                <span class="ms-2">{{ comment.content }}</span>
              </div>
              <form class="input-group input-group-sm" @submit.prevent="addComment(log)">
                <input v-model="commentForms[log.id]" class="form-control" placeholder="댓글">
                <button class="btn btn-outline-secondary">등록</button>
              </form>
            </div>
          </div>
        </article>
      </div>
    </div>
    <div v-else class="surface grid-empty">
      <div>
        <p class="mb-2">아직 표시할 친구 피드가 없습니다.</p>
        <RouterLink class="btn btn-outline-primary btn-sm" :to="{ name: 'friends' }">친구 찾기</RouterLink>
      </div>
    </div>
  </section>
</template>
