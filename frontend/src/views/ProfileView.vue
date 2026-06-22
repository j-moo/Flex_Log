<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { cancelProduct } from '../api/financial'
import { getUserExpenses } from '../api/expenses'
import { getMyProfile, getProfile, updateMyProfile } from '../api/profile'
import FriendModal from '../components/profile/FriendModal.vue'
import ProfileGrid from '../components/profile/ProfileGrid.vue'
import ProfileHeader from '../components/profile/ProfileHeader.vue'
import { useAccountStore } from '../stores/account'

const route=useRoute(), account=useAccountStore()
const profile=ref(null), logs=ref([]), isLoading=ref(true), errorMessage=ref(''), successMessage=ref('')
const isEditing=ref(false), isSubmitting=ref(false), imageFile=ref(null), imagePreview=ref(''), showFriends=ref(false), activeTab=ref('posts'), cancellingId=ref(null)
const form=reactive({name:'',nickname:'',bio:''})
const MOCK_PRODUCTS=[
  {id:'mock-1',isMock:true,joined_at:'2026-03-12',product:{product_type:'deposit',kor_co_nm:'카카오뱅크',fin_prdt_nm:'카카오뱅크 정기예금'},option:{save_trm:12,intr_rate2:3.4}},
  {id:'mock-2',isMock:true,joined_at:'2026-04-03',product:{product_type:'saving',kor_co_nm:'신한은행',fin_prdt_nm:'신한은행 청년적금'},option:{save_trm:24,intr_rate2:4.2}},
  {id:'mock-3',isMock:true,joined_at:'2026-05-21',product:{product_type:'saving',kor_co_nm:'KB국민은행',fin_prdt_nm:'국민은행 자유적금'},option:{save_trm:12,intr_rate2:3.8}},
]
const requestedUserId=computed(()=>route.params.userId?Number(route.params.userId):account.user?.id)
const isOwnProfile=computed(()=>requestedUserId.value===account.user?.id)
const displayedProducts=computed(()=>profile.value?.joined_products?.length?profile.value.joined_products:MOCK_PRODUCTS)
const productCount=computed(()=>displayedProducts.value.length)
const maxRate=computed(()=>Math.max(1,...displayedProducts.value.map(item=>Number(item.option.intr_rate2||item.option.intr_rate||0))))

const applyProfile=(data)=>{profile.value=data;form.name=data.name||'';form.nickname=data.nickname||'';form.bio=data.bio||'';imagePreview.value=data.image||'';if(isOwnProfile.value)account.user={...account.user,name:data.name||'',username:data.username,email:data.email}}
const loadProfile=async()=>{isLoading.value=true;errorMessage.value='';try{const response=isOwnProfile.value?await getMyProfile():await getProfile(requestedUserId.value);applyProfile(response.data);logs.value=(await getUserExpenses(response.data.user_id)).data}catch{errorMessage.value='프로필을 불러오지 못했습니다.'}finally{isLoading.value=false}}
const selectImage=(event)=>{imageFile.value=event.target.files?.[0]||null;if(imageFile.value)imagePreview.value=URL.createObjectURL(imageFile.value)}
const submit=async()=>{isSubmitting.value=true;errorMessage.value='';successMessage.value='';const payload=new FormData();payload.append('name',form.name);payload.append('nickname',form.nickname);payload.append('bio',form.bio);if(imageFile.value)payload.append('image',imageFile.value);try{applyProfile((await updateMyProfile(payload)).data);isEditing.value=false;successMessage.value='프로필을 저장했습니다.'}catch(error){errorMessage.value=Object.values(error.response?.data||{}).flat().join(' ')||'프로필 저장에 실패했습니다.'}finally{isSubmitting.value=false}}
const cancelSubscription=async(item)=>{if(!window.confirm(`${item.product.fin_prdt_nm} 가입을 해지할까요?`))return;cancellingId.value=item.id;try{await cancelProduct(item.id);await loadProfile()}catch(error){errorMessage.value=error.response?.data?.detail||'가입상품 해지에 실패했습니다.'}finally{cancellingId.value=null}}
watch(()=>route.params.userId,loadProfile)
onMounted(loadProfile)
</script>

<template>
  <section class="profile-page">
    <div v-if="isLoading" class="profile-state">프로필을 불러오는 중입니다.</div><div v-else-if="errorMessage&&!profile" class="profile-state error">{{ errorMessage }}</div>
    <template v-else-if="profile">
      <ProfileHeader :profile="profile" :post-count="logs.length" :product-count="productCount" :is-own="isOwnProfile" @friends="isOwnProfile ? showFriends=true : null" @edit="isEditing=!isEditing" />
      <p v-if="successMessage" class="profile-message">{{ successMessage }}</p><p v-if="errorMessage" class="profile-message error">{{ errorMessage }}</p>
      <form v-if="isOwnProfile&&isEditing" class="edit-card" @submit.prevent="submit">
        <div class="edit-photo"><img v-if="imagePreview" :src="imagePreview" alt="프로필 이미지"><span v-else>{{ profile.nickname.slice(0,1) }}</span><label>사진 변경<input type="file" accept="image/*" @change="selectImage"></label></div>
        <div class="edit-fields"><label>이름<input v-model.trim="form.name" maxlength="50"></label><label>닉네임<input v-model.trim="form.nickname" maxlength="30" required></label><label>소개<textarea v-model="form.bio" rows="3"></textarea></label><div><button type="submit" :disabled="isSubmitting">{{ isSubmitting?'저장 중...':'저장' }}</button><button type="button" @click="isEditing=false">취소</button></div></div>
      </form>

      <nav class="profile-tabs"><button :class="{active:activeTab==='posts'}" type="button" @click="activeTab='posts'"><span>▦</span> 게시물</button><button :class="{active:activeTab==='products'}" type="button" @click="activeTab='products'"><span>◇</span> 가입상품</button></nav>
      <ProfileGrid v-if="activeTab==='posts'" :logs="logs" />
      <section v-else class="joined-products">
        <div class="product-section-head"><div><h2>가입 금융상품</h2><p>선택한 상품의 최고 금리를 비교합니다. <span v-if="!profile.joined_products.length">현재 예시 데이터가 표시됩니다.</span></p></div><RouterLink v-if="isOwnProfile" :to="{name:'finance-hub',query:{tab:'products'}}">상품 찾기</RouterLink></div>
        <article v-for="item in displayedProducts" :key="item.id"><span class="product-avatar">{{ item.product.product_type==='deposit'?'예':'적' }}</span><div class="product-copy"><strong>{{ item.product.fin_prdt_nm }}</strong><small>{{ item.product.kor_co_nm }} · {{ item.option.save_trm }}개월 · {{ new Date(item.joined_at).toLocaleDateString('ko-KR') }}</small><div class="rate-track"><i :style="{width:`${Number(item.option.intr_rate2||item.option.intr_rate||0)/maxRate*100}%`}"></i></div></div><div class="product-rate"><strong>{{ Number(item.option.intr_rate2||item.option.intr_rate||0).toFixed(2) }}%</strong><button v-if="isOwnProfile&&!item.isMock" type="button" :disabled="cancellingId===item.id" @click="cancelSubscription(item)">해지</button></div></article>
      </section>
      <FriendModal v-if="showFriends" @close="showFriends=false" />
    </template>
  </section>
</template>

<style scoped>
.profile-page{width:min(100%,780px);margin:auto}.profile-state{display:grid;min-height:260px;place-content:center;color:var(--muted);text-align:center}.profile-state.error{color:#d93025}.profile-message{border-radius:9px;background:#edf8f1;color:#247a4a;padding:9px 12px;font-size:12px}.profile-message.error{background:#fff0f0;color:#d93025}.edit-card{display:grid;grid-template-columns:100px 1fr;gap:20px;border:1px solid var(--border);border-radius:14px;background:white;margin-top:18px;padding:18px}.edit-photo{display:grid;align-content:start;justify-items:center;gap:8px}.edit-photo img,.edit-photo>span{display:grid;width:76px;height:76px;place-items:center;border-radius:50%;object-fit:cover;background:var(--accent-soft);color:var(--accent);font-size:24px;font-weight:900}.edit-photo label{color:var(--accent);font-size:11px;font-weight:800;cursor:pointer}.edit-photo input{display:none}.edit-fields{display:grid;gap:10px}.edit-fields label{display:grid;gap:4px;color:var(--muted);font-size:11px}.edit-fields input,.edit-fields textarea{width:100%;max-width:none;margin:0;border:1px solid var(--border);border-radius:8px;padding:9px;background:#fafafa}.edit-fields>div{display:flex;gap:7px}.edit-fields button{margin:0;border:0;border-radius:8px;background:var(--accent);color:white;padding:8px 14px;font-size:11px;font-weight:800}.edit-fields button+button{background:#eee;color:var(--ink)}.profile-tabs{display:grid;grid-template-columns:1fr 1fr;margin-top:12px;border-bottom:1px solid var(--border);background:transparent;padding:0}.profile-tabs button{display:flex;align-items:center;justify-content:center;gap:5px;margin:0;border:0;border-bottom:2px solid transparent;background:transparent;color:var(--muted);padding:13px;font-size:11px}.profile-tabs button.active{border-color:var(--ink);color:var(--ink);font-weight:800}.joined-products{display:grid}.product-section-head{display:flex;align-items:center;justify-content:space-between;padding:18px 4px}.product-section-head h2{margin:0;font-size:17px}.product-section-head p{margin:4px 0 0;color:var(--muted);font-size:11px}.product-section-head a{color:var(--accent);font-size:11px;font-weight:800}.joined-products>article{display:grid;grid-template-columns:44px 1fr auto;align-items:center;gap:11px;border-bottom:1px solid var(--border);padding:13px 4px}.product-avatar{display:grid;width:44px;height:44px;place-items:center;border-radius:12px;background:var(--accent-soft);color:var(--accent);font-weight:900}.product-copy{display:grid;gap:3px;min-width:0}.product-copy strong,.product-copy small{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.product-copy small{color:var(--muted);font-size:10px}.rate-track{height:5px;overflow:hidden;border-radius:9px;background:#eef0f3}.rate-track i{display:block;height:100%;border-radius:9px;background:var(--accent)}.product-rate{display:grid;justify-items:end}.product-rate strong{color:var(--accent)}.product-rate button{margin:2px 0 0;border:0;background:none;color:#ed4956;padding:0;font-size:10px}@media(max-width:520px){.edit-card{grid-template-columns:1fr}.edit-photo{grid-template-columns:76px auto;align-items:center;justify-content:start}.joined-products>article{grid-template-columns:40px 1fr}.product-rate{grid-column:2;display:flex;justify-content:space-between;width:100%}}
</style>
