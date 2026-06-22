<script setup>
import { isVideo } from '../../utils/format'
defineProps({ logs:{type:Array,default:()=>[]} })
const icons={식비:'🍽',카페:'☕',교통:'🚇',쇼핑:'🛍',문화:'🎬',주거:'🏠'}
</script>
<template>
  <div v-if="logs.length" class="profile-post-grid">
    <RouterLink v-for="log in logs" :key="log.id" :to="{ name:'log-detail',params:{id:log.id} }">
      <video v-if="log.media && isVideo(log.media)" :src="log.media" muted></video><img v-else-if="log.media" :src="log.media" :alt="log.title"><div v-else class="grid-fallback"><span>{{ icons[log.category_name] || '₩' }}</span><strong>{{ log.category_name }}</strong></div>
      <div class="grid-overlay"><span>♥ {{ log.like_count }}</span><span>● {{ log.comment_count }}</span></div>
    </RouterLink>
  </div>
  <div v-else class="empty-grid"><span>▦</span><strong>게시물 없음</strong><p>소비 순간을 첫 게시물로 남겨보세요.</p></div>
</template>
<style scoped>
.profile-post-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px}.profile-post-grid>a{position:relative;display:grid;aspect-ratio:1;place-items:center;overflow:hidden;background:#f1f3f6}.profile-post-grid img,.profile-post-grid video{width:100%;height:100%;object-fit:cover}.grid-fallback{display:grid;justify-items:center;gap:5px;color:var(--muted)}.grid-fallback span{font-size:27px}.grid-fallback strong{font-size:10px}.grid-overlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:12px;background:rgba(0,0,0,.44);color:white;opacity:0;font-size:12px;font-weight:800;transition:opacity .16s}.profile-post-grid>a:hover .grid-overlay{opacity:1}.empty-grid{display:grid;min-height:240px;place-content:center;justify-items:center;text-align:center}.empty-grid>span{display:grid;width:55px;height:55px;place-items:center;border:1px solid var(--ink);border-radius:50%;font-size:26px}.empty-grid strong{margin-top:12px}.empty-grid p{margin:4px 0;color:var(--muted);font-size:12px}@media(min-width:700px){.profile-post-grid{gap:4px}}
</style>
