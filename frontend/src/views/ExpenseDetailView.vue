<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getExpense } from '../api/expenses'
import FeedCard from '../components/feed/FeedCard.vue'
const route=useRoute(), log=ref(null), errorMessage=ref('')
onMounted(async()=>{try{log.value=(await getExpense(route.params.id)).data}catch{errorMessage.value='게시물을 불러오지 못했습니다.'}})
</script>
<template><section class="detail-wrap"><p v-if="errorMessage" class="detail-state error">{{ errorMessage }}</p><p v-else-if="!log" class="detail-state">게시물을 불러오는 중입니다.</p><template v-else><FeedCard :log="log"/><div v-if="log.can_edit" class="owner-actions"><RouterLink :to="{name:'log-edit',params:{id:log.id}}">게시물 수정</RouterLink></div></template></section></template>
<style scoped>.detail-wrap{width:min(100%,620px);margin:auto}.detail-state{display:grid;min-height:250px;place-content:center;color:var(--muted)}.detail-state.error{color:#d93025}.owner-actions{display:flex;justify-content:center;padding:15px}.owner-actions a{color:var(--accent);font-size:12px;font-weight:800}</style>
