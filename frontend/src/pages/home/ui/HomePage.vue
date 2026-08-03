<script setup lang="ts">
import { useAuth } from '@/shared/auth'

import { useTicketRequests } from '../model/use-ticket-requests'
import TicketRequestForm from './TicketRequestForm.vue'
import TicketRequestHistory from './TicketRequestHistory.vue'

const { user } = useAuth()
const {
  isLoading,
  isSubmitting,
  loadError,
  printBaseUrl,
  refresh,
  selectedAmount,
  sortedRequests,
  submit,
  submitError,
  submitSuccess
} = await useTicketRequests()
</script>

<template>
  <UContainer class="user-page">
    <header class="page-intro">
      <p class="page-eyebrow">Portal personal</p>
      <h1 class="page-title">Hola, {{ user?.name }}</h1>
      <p class="page-description">
        Solicita tus tickets de comida y consulta su estado desde un único lugar.
      </p>
    </header>

    <div class="page-grid">
      <TicketRequestForm v-model="selectedAmount" :error="submitError" :submitting="isSubmitting"
        :success="submitSuccess" @submit="submit" />

      <TicketRequestHistory :failed="Boolean(loadError)" :loading="isLoading" :print-base-url="printBaseUrl"
        :requests="sortedRequests" @retry="refresh" />
    </div>
  </UContainer>
</template>

<style scoped>
.user-page {
  padding-block: clamp(2.5rem, 6vw, 5rem);
}

.page-intro {
  max-width: 42rem;
  margin-bottom: clamp(2rem, 5vw, 3.5rem);
}

.page-eyebrow {
  margin: 0 0 0.85rem;
  color: #2d6654;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.page-title {
  margin: 0;
  color: var(--tickets-ink);
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: clamp(2.4rem, 6vw, 4.25rem);
  font-weight: 500;
  letter-spacing: -0.055em;
  line-height: 0.98;
  text-wrap: balance;
}

.page-description {
  max-width: 34rem;
  margin: 1.25rem 0 0;
  color: var(--tickets-muted);
  font-size: clamp(0.95rem, 2vw, 1.05rem);
  line-height: 1.65;
}

.page-grid {
  display: grid;
  align-items: start;
  grid-template-columns: minmax(17rem, 0.78fr) minmax(0, 1.55fr);
  gap: clamp(1rem, 2.5vw, 1.75rem);
}

@media (max-width: 860px) {
  .page-grid {
    grid-template-columns: 1fr;
  }
}
</style>
