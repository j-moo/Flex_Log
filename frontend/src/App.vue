<script setup>
</script>

<template>
  <h1>Flex-Log</h1>

  <nav>
    <RouterLink to="/">
      Home
    </RouterLink>
    |
    <RouterLink to="/signup">
      회원가입
    </RouterLink>
    |
    <RouterLink to="/login">
      로그인
    </RouterLink>
    |
    <RouterLink to="/profile">
      내 프로필
    </RouterLink>
    |
    <RouterLink to="/expenses">
    소비 기록
    </RouterLink>
    |
    <RouterLink to="/expenses/create">
    소비 등록
    </RouterLink>
    |
    <RouterLink to="/friends">
    친구
    </RouterLink>
    |
    <RouterLink to="/feed">
    친구 피드
    </RouterLink>
    
  </nav>

  <hr>

  <RouterView />
</template>