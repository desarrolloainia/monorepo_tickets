<script setup lang="ts">
import { usePendingTicketRequests } from '../model/use-pending-ticket-requests'
import PendingRequestQueue from './PendingRequestQueue.vue'
import PrinterSetupCard from './PrinterSetupCard.vue'

const {
  approve,
  approvingIds,
  isLoading,
  loadError,
  refresh,
  sortedRequests
} = await usePendingTicketRequests()
</script>

<template>
  <UContainer class="reception-page">
    <header class="page-intro">
      <div>
        <p class="page-eyebrow">Mesa de recepción</p>
        <h1 class="page-title">Solicitudes por atender</h1>
        <p class="page-description">
          Revisa cada solicitud y apruébala con un solo clic. La impresión se inicia automáticamente.
        </p>
      </div>

      <div v-if="!isLoading && !loadError" class="pending-summary" aria-live="polite">
        <span class="summary-number">{{ sortedRequests.length }}</span>
        <span class="summary-label">pendientes</span>
      </div>
    </header>

    <div class="reception-grid">
      <PrinterSetupCard />
      <PendingRequestQueue
        :approving-ids="approvingIds"
        :failed="Boolean(loadError)"
        :loading="isLoading"
        :requests="sortedRequests"
        @approve="approve"
        @retry="refresh"
      />
    </div>
  </UContainer>
</template>

<style scoped>
.reception-page {
  padding-block: clamp(2.5rem, 6vw, 5rem);
}

.page-intro {
  display: flex;
  max-width: 68rem;
  align-items: end;
  justify-content: space-between;
  gap: 2rem;
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
  max-width: 48rem;
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
  max-width: 40rem;
  margin: 1.25rem 0 0;
  color: var(--tickets-muted);
  font-size: clamp(0.95rem, 2vw, 1.05rem);
  line-height: 1.65;
}

.pending-summary {
  display: flex;
  min-width: 7rem;
  align-items: center;
  flex-direction: column;
  padding: 1rem 1.25rem;
  border: 1px solid #cbd9d1;
  border-radius: 1rem;
  background: #e8f0eb;
  color: #285b4b;
}

.summary-number {
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: 2rem;
  line-height: 1;
}

.summary-label {
  margin-top: 0.25rem;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.reception-grid {
  display: grid;
  align-items: start;
  grid-template-columns: minmax(17rem, 0.72fr) minmax(0, 1.7fr);
  gap: clamp(1rem, 2.5vw, 1.75rem);
}

@media (max-width: 940px) {
  .reception-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .page-intro {
    align-items: start;
    flex-direction: column;
  }

  .pending-summary {
    align-items: baseline;
    flex-direction: row;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
  }

  .summary-number {
    font-size: 1.5rem;
  }
}
</style>
