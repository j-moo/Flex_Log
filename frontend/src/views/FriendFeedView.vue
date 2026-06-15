<script setup>
import { onMounted, reactive, ref } from 'vue'

import {
  getFriendFeed,
  toggleExpenseLike,
  createComment,
  deleteComment,
} from '@/api/expenses'

const feed = ref([])
const loading = ref(true)
const errorMessage = ref('')
const commentInputs = reactive({})

const loadFeed = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await getFriendFeed()
    feed.value = response.data
  } catch (error) {
    console.error(error)
    errorMessage.value = '피드를 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const toggleLike = async (expense) => {
  try {
    const response = await toggleExpenseLike(expense.id)

    expense.is_liked = response.data.liked
    expense.like_count += response.data.liked ? 1 : -1
  } catch (error) {
    console.error(error)
    alert('좋아요 처리에 실패했습니다.')
  }
}

const submitComment = async (expense) => {
  const content = commentInputs[expense.id]

  if (!content || !content.trim()) return

  try {
    const response = await createComment(expense.id, content)

    expense.comments.push(response.data)
    expense.comment_count += 1
    commentInputs[expense.id] = ''
  } catch (error) {
    console.error(error)
    alert('댓글 작성에 실패했습니다.')
  }
}

const removeComment = async (expense, commentId) => {
  if (!confirm('댓글을 삭제하시겠습니까?')) return

  try {
    await deleteComment(commentId)

    expense.comments = expense.comments.filter(
      comment => comment.id !== commentId
    )

    expense.comment_count -= 1
  } catch (error) {
    console.error(error)
    alert('댓글 삭제에 실패했습니다.')
  }
}

onMounted(loadFeed)
</script>

<template>
  <section>
    <h1>피드</h1>

    <p v-if="loading">불러오는 중...</p>

    <p v-else-if="errorMessage">
      {{ errorMessage }}
    </p>

    <div
      v-else-if="feed.length"
      v-for="expense in feed"
      :key="expense.id"
      class="feed-card"
    >
      <h3>{{ expense.username }}</h3>

      <p>카테고리: {{ expense.category_name }}</p>
      <p>금액: {{ Number(expense.amount).toLocaleString() }}원</p>
      <p>내용: {{ expense.content }}</p>
      <p>작성일: {{ expense.created_at.slice(0, 10) }}</p>

      <img
        v-if="expense.media"
        :src="expense.media"
        alt="소비 기록 미디어"
        class="feed-media"
      >

      <div class="actions">
        <button @click="toggleLike(expense)">
          {{ expense.is_liked ? '좋아요 취소' : '좋아요' }}
        </button>

        <span>
          좋아요 {{ expense.like_count }}
        </span>

        <span>
          댓글 {{ expense.comment_count }}
        </span>
      </div>

      <div class="comments">
        <h4>댓글</h4>

        <div
          v-for="comment in expense.comments"
          :key="comment.id"
          class="comment"
        >
          <strong>{{ comment.username }}</strong>
          :
          {{ comment.content }}

          <button
            class="comment-delete"
            @click="removeComment(expense, comment.id)"
          >
            삭제
          </button>
        </div>

        <form @submit.prevent="submitComment(expense)">
          <input
            v-model="commentInputs[expense.id]"
            placeholder="댓글 작성"
          >

          <button>
            등록
          </button>
        </form>
      </div>
    </div>

    <p v-else>
      친구의 공개 소비 기록이 없습니다.
    </p>
  </section>
</template>

<style scoped>
.feed-card {
  border: 1px solid #ddd;
  margin: 10px 0;
  padding: 15px;
  border-radius: 8px;
}

.feed-media {
  display: block;
  max-width: 240px;
  margin: 10px 0;
}

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin: 10px 0;
}

.comments {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.comment {
  margin: 5px 0;
}

.comment-delete {
  margin-left: 8px;
}
</style>