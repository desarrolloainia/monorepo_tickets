<script setup lang="ts">
import { SpendingPage } from '@/pages/spending'

definePageMeta({ middleware: ['auth', 'rrhh'] })
</script>

<template>
  <SpendingPage />
</template>
