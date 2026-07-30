<script setup lang="ts">
import { HomePage } from '~/src/pages/home'

definePageMeta({ middleware: 'auth' })
</script>

<template>
  <HomePage />
</template>
