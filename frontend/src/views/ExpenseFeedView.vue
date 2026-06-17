<script setup>
import { reactive, onMounted, ref } from 'vue'

import api from '../api/client'
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
    const response = await api.get('/api/v1/expenses/feed/')
    logs.value = response.data
  } catch {
    errorMessage.value = '친구 피드를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const toggleLike = async (log) => {
  const response = await api.post(`/api/v1/expenses/${log.id}/like/`)
  log.is_liked = response.data.liked
  log.like_count = response.data.like_count
}

const loadComments = async (log) => {
  if (commentsByLog[log.id]) {
    delete commentsByLog[log.id]
    return
  }
  const response = await api.get(`/api/v1/expenses/${log.id}/comments/`)
  commentsByLog[log.id] = response.data
  commentForms[log.id] = ''
}

const addComment = async (log) => {
  const content = (commentForms[log.id] || '').trim()
  if (!content) return
  const response = await api.post(`/api/v1/expenses/${log.id}/comments/`, { content })
  commentsByLog[log.id].push(response.data)
  commentForms[log.id] = ''
  log.comment_count += 1
}

onMounted(loadFeed)
</script>

<template>
  <section class="d-grid gap-3">
    <div>
      <h1 class="h3 mb-1">친구 피드</h1>
      <p class="text-secondary mb-0">수락된 친구의 공개 로그만 표시됩니다.</p>
    </div>

    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
    <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-else-if="logs.length" class="row g-3">
      <div v-for="log in logs" :key="log.id" class="col-12 col-lg-6">
        <article class="card h-100">
          <video v-if="log.media && isVideo(log.media)" class="log-media card-img-top" :src="log.media" controls></video>
          <img v-else-if="log.media" class="log-media card-img-top" :src="log.media" alt="친구 소비 로그 미디어">
          <div class="card-body d-grid gap-3">
            <div class="d-flex justify-content-between gap-2">
              <div>
                <strong>{{ log.display_name }}</strong>
                <div class="small text-secondary">{{ formatDate(log.created_at) }}</div>
              </div>
              <div class="text-end">
                <span class="badge text-bg-light border">{{ log.category_name }}</span>
                <div class="fw-bold mt-1">{{ formatAmount(log.amount) }}</div>
              </div>
            </div>

            <p v-if="log.content" class="content-preline mb-0">{{ log.content }}</p>

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
    <div v-else class="card">
      <div class="card-body text-center py-5 text-secondary">표시할 친구 피드가 없습니다.</div>
    </div>
  </section>
</template>
