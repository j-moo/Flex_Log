<script setup>
import TopBar from './TopBar.vue'

defineEmits(['logout', 'compose'])
</script>

<template>
  <TopBar @logout="$emit('logout')" @compose="$emit('compose')" />
</template>
