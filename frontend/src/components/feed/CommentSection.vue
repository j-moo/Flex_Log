<script setup>
import { ref } from 'vue'

import { createComment, deleteComment, getComments, updateComment } from '../../api/expenses'

const props = defineProps({
  logId: {
    type: Number,
    required: true,
  },
  count: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['count-change'])

const isOpen = ref(false)
const isLoading = ref(false)
const comments = ref([])
const content = ref('')
const errorMessage = ref('')

const toggle = async () => {
  isOpen.value = !isOpen.value
  if (!isOpen.value || comments.value.length) return

  isLoading.value = true
  errorMessage.value = ''
  try {
    comments.value = (await getComments(props.logId)).data
  } catch {
    errorMessage.value = '댓글을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

defineExpose({ toggle })

const submit = async () => {
  const value = content.value.trim()
  if (!value) return

  try {
    comments.value.push((await createComment(props.logId, value)).data)
    content.value = ''
    emit('count-change', props.count + 1)
  } catch {
    errorMessage.value = '댓글을 등록하지 못했습니다.'
  }
}

const edit = async (comment) => {
  const value = window.prompt('댓글을 수정하세요.', comment.content)?.trim()
  if (!value || value === comment.content) return
  Object.assign(comment, (await updateComment(props.logId, comment.id, value)).data)
}

const remove = async (comment) => {
  if (!window.confirm('댓글을 삭제할까요?')) return
  await deleteComment(props.logId, comment.id)
  comments.value = comments.value.filter((item) => item.id !== comment.id)
  emit('count-change', Math.max(0, props.count - 1))
}
</script>

<template>
  <div class="comment-section">
    <button class="comment-toggle" type="button" @click="toggle">
      댓글 {{ count }}개 {{ isOpen ? '숨기기' : '모두 보기' }}
    </button>

    <Transition name="fade-slide">
      <div v-if="isOpen" class="comment-panel">
        <p v-if="isLoading" class="comment-status">댓글을 불러오는 중...</p>
        <p v-else-if="!comments.length" class="comment-status">첫 댓글을 남겨보세요.</p>

        <div v-for="comment in comments" :key="comment.id" class="comment-row">
          <p><strong>{{ comment.display_name }}</strong> {{ comment.content }}</p>
          <div v-if="comment.can_edit" class="comment-menu">
            <button type="button" @click="edit(comment)">수정</button>
            <button type="button" @click="remove(comment)">삭제</button>
          </div>
        </div>

        <p v-if="errorMessage" class="comment-error">{{ errorMessage }}</p>

        <form class="comment-form" @submit.prevent="submit">
          <input v-model="content" maxlength="500" placeholder="댓글 쓰기..." aria-label="댓글 내용">
          <button type="submit" :disabled="!content.trim()">게시</button>
        </form>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.comment-section {
  display: grid;
}

.comment-toggle {
  justify-self: start;
  border: 0;
  background: transparent;
  color: var(--color-muted);
  padding: 5px 0;
  font-size: 13px;
  font-weight: 900;
}

.comment-panel {
  display: grid;
  gap: 10px;
  margin-top: 8px;
}

.comment-status,
.comment-error {
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
}

.comment-error {
  color: var(--color-red);
}

.comment-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.comment-row p {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
}

.comment-row strong {
  margin-right: 5px;
}

.comment-menu {
  display: flex;
  gap: 6px;
}

.comment-menu button {
  border: 0;
  background: transparent;
  color: var(--color-muted);
  padding: 0;
  font-size: 11px;
  font-weight: 900;
}

.comment-menu button:last-child {
  color: var(--color-red);
}

.comment-form {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  border-top: 2px solid rgba(23, 19, 13, 0.12);
  margin-top: 4px;
}

.comment-form input {
  width: 100%;
  border: 0;
  background: transparent;
  padding: 12px 0;
  outline: none;
}

.comment-form button {
  border: 0;
  background: transparent;
  color: var(--color-dark-gold);
  padding: 8px;
  font-weight: 900;
}
</style>
