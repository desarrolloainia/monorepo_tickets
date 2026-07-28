<script setup lang="ts">
import type { Ticket } from '~/src/entities/ticket/model/ticket'
import TicketStatus from '~/src/entities/ticket/ui/TicketStatus.vue'

defineProps<{ tickets: Ticket[] }>()
</script>

<template>
  <UCard>
    <template #header>
      <h1 class="text-xl font-semibold text-highlighted">Tickets</h1>
    </template>

    <ul class="divide-y divide-default">
      <li v-for="ticket in tickets" :key="ticket.id" class="flex items-center justify-between gap-4 py-4 first:pt-0 last:pb-0">
        <div>
          <p class="font-medium text-highlighted">{{ ticket.title }}</p>
          <p class="text-sm text-muted">{{ ticket.id }} · Actualizado {{ ticket.updatedAt }}</p>
        </div>
        <TicketStatus :status="ticket.status" />
      </li>
    </ul>
  </UCard>
</template>