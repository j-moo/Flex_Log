<script setup>
import { computed, onMounted, ref } from 'vue'
import { deleteFriend, getFriends, searchUsers, sendFriendRequest, updateFriendStatus } from '../../api/friends'
import { useAccountStore } from '../../stores/account'

defineEmits(['close','changed'])
const account=useAccountStore(), friends=ref([]), tab=ref('friends'), isLoading=ref(true), errorMessage=ref('')
const query=ref(''), users=ref([]), searchMessage=ref('')
const pending=computed(()=>friends.value.filter(item=>item.status==='pending'))
const accepted=computed(()=>friends.value.filter(item=>item.status==='accepted'))
const visible=computed(()=>tab.value==='requests'?pending.value:accepted.value)
const isReceived=(item)=>item.friend.id===account.user?.id
const person=(item)=>item.counterpart || (item.user.id===account.user?.id?item.friend:item.user)
const load=async()=>{try{friends.value=(await getFriends()).data}catch{errorMessage.value='친구 정보를 불러오지 못했습니다.'}finally{isLoading.value=false}}
const change=async(item,status)=>{const updated=(await updateFriendStatus(item.id,status)).data;friends.value=friends.value.map(value=>value.id===item.id?updated:value)}
const remove=async(item)=>{if(!window.confirm(item.status==='accepted'?'친구를 삭제할까요?':'친구 요청을 취소할까요?'))return;await deleteFriend(item.id);friends.value=friends.value.filter(value=>value.id!==item.id)}
const findUsers=async()=>{if(!query.value.trim())return;searchMessage.value='';try{users.value=(await searchUsers(query.value.trim())).data;if(!users.value.length)searchMessage.value='검색 결과가 없습니다.'}catch{searchMessage.value='사용자 검색에 실패했습니다.'}}
const request=async(user)=>{try{friends.value.unshift((await sendFriendRequest(user.id)).data);users.value=users.value.filter(item=>item.id!==user.id);searchMessage.value='친구 요청을 보냈습니다.'}catch(error){searchMessage.value=Object.values(error.response?.data||{}).flat().join(' ')||'친구 요청에 실패했습니다.'}}
onMounted(load)
</script>

<template>
  <Teleport to="body">
    <div class="sheet-backdrop" @click.self="$emit('close')">
      <section class="friend-sheet">
        <header><span></span><h2>친구 관리</h2><button type="button" @click="$emit('close')">×</button></header>
        <div class="sheet-tabs"><button :class="{active:tab==='friends'}" type="button" @click="tab='friends'">친구 {{ accepted.length }}</button><button :class="{active:tab==='requests'}" type="button" @click="tab='requests'">요청 {{ pending.length }}</button><button :class="{active:tab==='find'}" type="button" @click="tab='find'">친구 찾기</button></div>
        <template v-if="tab==='find'">
          <form class="friend-search" @submit.prevent="findUsers"><input v-model="query" placeholder="아이디, 이름, 닉네임"><button type="submit">검색</button></form>
          <p v-if="searchMessage" class="search-message">{{ searchMessage }}</p>
          <div class="friend-list"><article v-for="user in users" :key="user.id"><span class="friend-avatar">{{ user.display_name.slice(0,1) }}</span><div><strong>{{ user.display_name }}</strong><small>@{{ user.username }}</small></div><button class="request-button" type="button" @click="request(user)">요청</button></article></div>
        </template>
        <template v-else>
          <p v-if="isLoading" class="sheet-state">불러오는 중...</p><p v-else-if="errorMessage" class="sheet-state error">{{ errorMessage }}</p><p v-else-if="!visible.length" class="sheet-state">표시할 사용자가 없습니다.</p>
          <div v-else class="friend-list"><article v-for="item in visible" :key="item.id"><span class="friend-avatar">{{ person(item).display_name.slice(0,1) }}</span><div><strong>{{ person(item).display_name }}</strong><small>@{{ person(item).username }} <em v-if="tab==='requests'">{{ isReceived(item)?'받은 요청':'보낸 요청' }}</em></small></div><div v-if="tab==='requests'&&isReceived(item)" class="request-actions"><button type="button" @click="change(item,'accepted')">수락</button><button type="button" @click="change(item,'rejected')">거절</button></div><button v-else class="remove" type="button" @click="remove(item)">{{ tab==='requests'?'취소':'삭제' }}</button></article></div>
        </template>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.sheet-backdrop{position:fixed;inset:0;z-index:100;display:flex;align-items:flex-end;justify-content:center;background:rgba(36,79,112,.28);backdrop-filter:blur(6px)}.friend-sheet{display:grid;width:min(100%,540px);max-height:min(82vh,680px);overflow:hidden;border:1px solid rgba(255,255,255,.9);border-radius:24px 24px 0 0;background:rgba(247,252,255,.94);box-shadow:0 -20px 60px rgba(57,115,160,.2);backdrop-filter:blur(24px)}.friend-sheet header{display:grid;grid-template-columns:30px 1fr 30px;align-items:center;padding:13px 16px;border-bottom:1px solid var(--border)}.friend-sheet h2{margin:0;font-size:16px;text-align:center}.friend-sheet header button{margin:0;border:0;background:none;color:var(--ink);font-size:25px}.sheet-tabs{display:grid;grid-template-columns:repeat(3,1fr)}.sheet-tabs button{margin:0;border:0;border-bottom:2px solid transparent;background:transparent;color:var(--muted);padding:12px 6px;font-size:11px}.sheet-tabs button.active{border-color:var(--accent);color:var(--accent);font-weight:800}.sheet-state{min-height:180px;margin:0;padding:50px 20px;color:var(--muted);text-align:center}.sheet-state.error{color:#d93025}.friend-list{overflow:auto}.friend-list article{display:grid;grid-template-columns:40px 1fr auto;align-items:center;gap:10px;padding:11px 15px;border-bottom:1px solid var(--border)}.friend-avatar{display:grid;width:40px;height:40px;place-items:center;border-radius:50%;background:#e5f4ff;color:#438bd5;font-weight:900}.friend-list article>div:nth-child(2){display:grid}.friend-list small{color:var(--muted);font-size:10px}.friend-list em{margin-left:4px;color:var(--accent);font-style:normal}.request-actions{display:flex;gap:5px}.request-actions button,.remove,.request-button{margin:0;border:0;border-radius:8px;padding:7px 10px;font-size:10px}.request-actions button:first-child,.request-button{background:var(--accent);color:white}.request-actions button:last-child,.remove{background:rgba(226,237,246,.8);color:var(--ink)}.friend-search{display:grid;grid-template-columns:1fr auto;gap:8px;padding:14px}.friend-search input{width:100%;max-width:none;margin:0;border:1px solid var(--border);border-radius:10px;background:rgba(255,255,255,.74);padding:10px}.friend-search button{margin:0;border:0;border-radius:9px;background:var(--accent);color:white;padding:0 15px;font-size:11px;font-weight:800}.search-message{margin:0;padding:0 14px 10px;color:var(--muted);font-size:11px}@media(min-width:600px){.sheet-backdrop{align-items:center}.friend-sheet{border-radius:24px}}
</style>
