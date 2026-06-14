<template><article class="card"><img v-if="log.media" class="expense-image" :src="mediaUrl(log.media)" alt="소비 로그"><div class="row" style="margin-top:12px"><span class="badge">{{log.category_name}}</span><strong>{{Number(log.amount).toLocaleString()}}원</strong><span class="muted">@{{log.username}}</span></div><p>{{log.content || '내용 없음'}}</p><p class="muted">좋아요 {{log.like_count}} · 댓글 {{log.comment_count}}</p><div class="actions"><button class="secondary" @click="$emit('like', log)">{{log.is_liked?'좋아요 취소':'좋아요'}}</button><button v-if="canDelete" class="danger" @click="$emit('delete', log)">삭제</button></div></article></template>
<script setup>
import { computed } from 'vue'
import { useAccountStore } from '@/stores/account'
const props=defineProps({log:{type:Object,required:true}}); defineEmits(['like','delete']); const store=useAccountStore(); const canDelete=computed(()=>store.user?.id===props.log.user)
const mediaUrl=(path)=> path?.startsWith('http') ? path : `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}${path}`
</script>
