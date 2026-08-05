<script setup lang="ts">
import { SpendingPage } from '@/pages/spending'

definePageMeta({ middleware: ['auth', 'accountant'] })
</script>

<template>
  <SpendingPage manage-price />
</template>
