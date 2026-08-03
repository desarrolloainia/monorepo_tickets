<script setup lang="ts">
import { HomePage } from '@/pages/home'

definePageMeta({ middleware: ['auth', 'user'] })
</script>

<template>
  <HomePage />
</template>
