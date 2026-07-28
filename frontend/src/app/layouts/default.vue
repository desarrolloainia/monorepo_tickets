<script setup lang="ts">
import AppHeader from '~/src/widgets/app-header/ui/AppHeader.vue'
</script>

<template>
  <div class="min-h-screen bg-default">
    <AppHeader />
    <main>
      <slot />
    </main>
  </div>
</template>