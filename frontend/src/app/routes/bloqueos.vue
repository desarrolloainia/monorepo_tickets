<script setup lang="ts">
import { BlockedUsersPage } from '@/pages/blocked-users'

definePageMeta({ middleware: ['auth', 'rrhh'] })
</script>

<template>
  <BlockedUsersPage />
</template>
