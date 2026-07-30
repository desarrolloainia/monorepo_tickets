<script setup lang="ts">
import { useAuth } from '~/src/shared/auth'

const { user } = useAuth()
</script>

<template>
  <UContainer class="py-12 sm:py-20">
    <div class="max-w-2xl space-y-4">
      <p class="text-sm font-medium uppercase tracking-[0.18em] text-primary">Sesión activa</p>
      <h1 class="text-3xl font-semibold tracking-tight text-highlighted sm:text-4xl">
        Hola, {{ user?.name }}
      </h1>
      <p class="text-lg text-muted">Tu acceso está listo. La gestión de tickets se conectará a continuación.</p>
    </div>
  </UContainer>
</template>
