<script setup lang="ts">
import { ReceptionPage } from '@/pages/reception'

definePageMeta({ middleware: ['auth', 'approver'] })
</script>

<template>
  <ReceptionPage />
</template>
