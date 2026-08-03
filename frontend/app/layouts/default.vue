<script setup lang="ts">
import { AppHeader } from '@/widgets/app-header'
</script>

<template>
  <div class="min-h-screen bg-default">
    <AppHeader />
    <main>
      <slot />
    </main>
  </div>
</template>
