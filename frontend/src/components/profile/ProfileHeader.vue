<script setup>
import { computed } from 'vue'
const props = defineProps({ profile: { type:Object, required:true }, postCount:{type:Number,default:0}, productCount:{type:Number,default:0}, isOwn:Boolean })
defineEmits(['friends','edit'])
const initial = computed(() => (props.profile.nickname || props.profile.username || '?').slice(0,1).toUpperCase())
</script>
<template>
  <section class="profile-header-card">
    <div class="profile-main">
      <img v-if="profile.image" :src="profile.image" alt="프로필 이미지"><span v-else class="profile-avatar">{{ initial }}</span>
      <div class="profile-copy"><div class="name-row"><h1>{{ profile.nickname }}</h1><button v-if="isOwn" type="button" @click="$emit('edit')">프로필 편집</button></div><p class="username">@{{ profile.username }}</p><p class="bio">{{ profile.bio || '아직 소개가 없습니다.' }}</p></div>
    </div>
    <div class="profile-stats"><div><strong>{{ postCount }}</strong><span>게시물</span></div><button type="button" @click="$emit('friends')"><strong>{{ profile.friend_count }}</strong><span>친구</span></button><div><strong>{{ productCount }}</strong><span>가입 상품</span></div></div>
  </section>
</template>
<style scoped>
.profile-header-card{display:grid;gap:20px;border:1px solid rgba(255,255,255,.86);border-radius:22px;background:rgba(255,255,255,.6);box-shadow:0 16px 45px rgba(76,145,201,.1);padding:20px;backdrop-filter:blur(18px)}.profile-main{display:grid;grid-template-columns:92px 1fr;align-items:center;gap:22px}.profile-main>img,.profile-avatar{width:88px;height:88px;border-radius:50%;object-fit:cover}.profile-avatar{display:grid;place-items:center;background:linear-gradient(135deg,#bce5ff,#4f8cff);color:white;font-size:30px;font-weight:900}.profile-copy{min-width:0}.name-row{display:flex;align-items:center;gap:12px}.name-row h1{overflow:hidden;margin:0;font-size:23px;text-overflow:ellipsis;white-space:nowrap}.name-row button{flex:0 0 auto;margin:0;border:1px solid rgba(255,255,255,.9);border-radius:10px;background:rgba(255,255,255,.7);color:var(--ink);padding:7px 11px;font-size:11px;font-weight:750}.username{margin:3px 0;color:var(--muted);font-size:12px}.bio{margin:8px 0 0;font-size:13px;line-height:1.55;white-space:pre-wrap}.profile-stats{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid rgba(255,255,255,.86);border-radius:15px;background:rgba(255,255,255,.58)}.profile-stats>div,.profile-stats>button{display:grid;justify-items:center;gap:2px;margin:0;border:0;border-right:1px solid var(--border);background:transparent;color:var(--ink);padding:10px}.profile-stats>*:last-child{border-right:0}.profile-stats strong{font-size:17px}.profile-stats span{color:var(--muted);font-size:10px}@media(min-width:700px){.profile-header-card{grid-template-columns:1fr 330px;align-items:center}.profile-main{grid-template-columns:112px 1fr}.profile-main>img,.profile-avatar{width:108px;height:108px}.profile-stats{align-self:center}}
</style>
