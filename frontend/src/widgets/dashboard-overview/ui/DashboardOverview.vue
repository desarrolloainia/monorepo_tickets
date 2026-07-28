<script setup lang="ts">
import type { Ticket } from '~/src/entities/ticket/model/ticket'
import TicketStatus from '~/src/entities/ticket/ui/TicketStatus.vue'

defineProps<{ tickets: Ticket[] }>()
</script>

<template>
  <UCard>
    <template #header>
      <div class="flex items-center justify-between">
        <h2 class="font-semibold text-highlighted">Actividad reciente</h2>
        <UButton to="/tickets" color="neutral" variant="ghost" size="sm">Ver todos</UButton>
      </div>
    </template>

    <ul class="divide-y divide-default">
      <li v-for="ticket in tickets" :key="ticket.id" class="flex items-center justify-between gap-4 py-4 first:pt-0 last:pb-0">
        <div>
          <p class="font-medium text-highlighted">{{ ticket.title }}</p>
          <p class="text-sm text-muted">Actualizado {{ ticket.updatedAt }}</p>
        </div>
        <TicketStatus :status="ticket.status" />
      </li>
    </ul>
  </UCard>
</template>