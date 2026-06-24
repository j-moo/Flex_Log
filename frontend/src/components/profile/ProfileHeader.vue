<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  profile: {
    type: Object,
    required: true,
  },
  postCount: {
    type: Number,
    default: 0,
  },
  productCount: {
    type: Number,
    default: 0,
  },
  isOwn: Boolean,
  friendActionLabel: {
    type: String,
    default: '',
  },
  friendActionTone: {
    type: String,
    default: 'primary',
  },
  friendActionDisabled: Boolean,
})

defineEmits(['friends', 'edit', 'friend-action'])

const imageLoadFailed = ref(false)
const hasProfileImage = computed(() => Boolean(props.profile.image) && !imageLoadFailed.value)

watch(
  () => props.profile.image,
  () => {
    imageLoadFailed.value = false
  },
)
</script>

<template>
  <section class="profile-header-card vintage-card">
    <div class="profile-actions">
      <button v-if="isOwn" type="button" class="profile-action-button" @click="$emit('edit')">
        프로필 편집
      </button>
      <button
        v-else-if="friendActionLabel"
        type="button"
        class="profile-action-button"
        :class="friendActionTone"
        :disabled="friendActionDisabled"
        @click="$emit('friend-action')"
      >
        {{ friendActionLabel }}
      </button>
    </div>

    <div class="profile-main">
      <img v-if="hasProfileImage" :src="profile.image" alt="프로필 이미지" @error="imageLoadFailed = true">
      <span v-else class="profile-avatar" aria-hidden="true"></span>

      <div class="profile-copy">
        <div class="name-row">
          <h1 class="display-title">{{ profile.nickname || profile.username }}</h1>
        </div>
        <p class="username">@{{ profile.username }}</p>
        <p class="bio">{{ profile.bio || '아직 소개가 없습니다.' }}</p>
        <p v-if="profile.email" class="email">{{ profile.email }}</p>
      </div>
    </div>

    <div class="profile-stats">
      <div>
        <strong>{{ postCount }}</strong>
        <span>게시글</span>
      </div>
      <button type="button" @click="$emit('friends')">
        <strong>{{ profile.friend_count }}</strong>
        <span>친구</span>
      </button>
      <div>
        <strong>{{ productCount }}</strong>
        <span>가입상품</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.profile-header-card {
  position: relative;
  display: grid;
  gap: 22px;
  padding: 22px;
}

.profile-actions {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 2;
}

.profile-action-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-gold);
  color: var(--color-ink);
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 900;
  box-shadow: 3px 3px 0 var(--color-ink);
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.profile-action-button:hover {
  background: #e5b842;
  box-shadow: 1px 1px 0 var(--color-ink);
  transform: translate(2px, 2px);
}

.profile-action-button:active {
  box-shadow: 0 0 0 var(--color-ink);
  transform: translate(3px, 3px);
}

.profile-action-button.danger {
  background: rgba(182, 74, 53, 0.14);
  color: var(--color-red);
}

.profile-action-button:disabled {
  opacity: 0.65;
  cursor: wait;
}

.profile-main {
  display: grid;
  grid-template-columns: 112px 1fr;
  align-items: center;
  gap: 22px;
  padding-right: 112px;
}

.profile-main > img,
.profile-avatar {
  width: 108px;
  height: 108px;
  border: 3px solid var(--color-ink);
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 4px 4px 0 var(--color-ink);
}

.profile-avatar {
  display: grid;
  place-items: center;
  background: var(--color-money);
  color: var(--color-paper);
  font-size: 38px;
  font-weight: 900;
}

.profile-copy {
  min-width: 0;
}

.name-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.name-row h1 {
  margin: 0;
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1;
}

.username,
.email {
  margin: 4px 0;
  color: var(--color-muted);
  font-weight: 900;
}

.bio {
  margin: 10px 0 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  overflow: hidden;
  border: 2px solid var(--color-ink);
  border-radius: 18px;
  background: rgba(255, 248, 231, 0.66);
}

.profile-stats > div,
.profile-stats > button {
  display: grid;
  justify-items: center;
  gap: 3px;
  border: 0;
  border-right: 2px solid var(--color-ink);
  background: transparent;
  color: var(--color-ink);
  padding: 13px;
}

.profile-stats > *:last-child {
  border-right: 0;
}

.profile-stats strong {
  font-size: 22px;
}

.profile-stats span {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
}

@media (max-width: 560px) {
  .profile-actions {
    position: static;
    justify-self: end;
  }

  .profile-main {
    grid-template-columns: 1fr;
    justify-items: center;
    padding-right: 0;
    text-align: center;
  }

  .name-row {
    justify-content: center;
  }
}
</style>
