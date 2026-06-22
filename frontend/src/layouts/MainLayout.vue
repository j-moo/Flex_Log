<script setup>
import HeaderBar from '../components/common/HeaderBar.vue'
defineEmits(['logout'])
</script>

<template>
  <div class="main-layout">
    <HeaderBar @logout="$emit('logout')" />
    <main class="layout-content"><slot /></main>
  </div>
</template>

<style scoped>
.main-layout{min-height:100vh}.layout-content{width:min(100% - 24px,1020px);margin:0 auto;padding:22px 0 54px}@media(min-width:760px){.layout-content{padding-top:30px;padding-bottom:70px}}
</style>
