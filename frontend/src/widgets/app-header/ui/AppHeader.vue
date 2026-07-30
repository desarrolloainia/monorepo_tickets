<script setup lang="ts">
import { useAuth } from '~/src/shared/auth'

const { logout, user } = useAuth()
</script>

<template>
  <header class="border-b border-default">
    <UContainer class="flex h-16 items-center justify-between">
      <NuxtLink to="/" class="font-semibold text-highlighted">Tickets</NuxtLink>
      <div v-if="user" class="flex items-center gap-3">
        <div class="hidden text-right sm:block">
          <p class="text-sm font-medium text-highlighted">{{ user.name }}</p>
          <p class="text-xs text-muted">{{ user.role }}</p>
        </div>
        <UButton color="neutral" variant="ghost" icon="i-lucide-log-out" aria-label="Cerrar sesión" @click="logout" />
      </div>
    </UContainer>
  </header>
</template>
