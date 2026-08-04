<script setup lang="ts">
import { computed, shallowRef, watch } from 'vue'

import type { TicketRequestDTO, TicketRequestStatus } from '@/shared/api'

const props = defineProps<{
  failed: boolean
  loading: boolean
  printBaseUrl: string
  requests: TicketRequestDTO[]
}>()

defineEmits<{
  retry: []
}>()

const itemsPerPage = 8
const page = shallowRef(1)
const previewOpen = shallowRef(false)
const selectedPreviewUrl = shallowRef<string>()
const previewLoading = shallowRef(false)

const dateFormatter = new Intl.DateTimeFormat('es-ES', {
  day: '2-digit',
  month: 'short',
  year: 'numeric'
})

const statusLabels: Record<TicketRequestStatus, string> = {
  approved: 'Aprobada',
  pending: 'Pendiente',
  rejected: 'Rechazada'
}

const paginatedRequests = computed(() => {
  const start = (page.value - 1) * itemsPerPage
  return props.requests.slice(start, start + itemsPerPage)
})

const rangeStart = computed(() => props.requests.length === 0 ? 0 : (page.value - 1) * itemsPerPage + 1)
const rangeEnd = computed(() => Math.min(page.value * itemsPerPage, props.requests.length))

watch(() => props.requests.length, (length) => {
  const lastPage = Math.max(1, Math.ceil(length / itemsPerPage))
  if (page.value > lastPage) page.value = lastPage
})

watch(previewOpen, (open) => {
  if (open) return
  selectedPreviewUrl.value = undefined
  previewLoading.value = false
})

function formatDate(value: string) {
  return dateFormatter.format(new Date(value))
}

function previewUrl(id: string) {
  return new URL(`/tickets/${id}/print`, props.printBaseUrl).href
}

function openPreview(id: string) {
  previewLoading.value = true
  selectedPreviewUrl.value = previewUrl(id)
  previewOpen.value = true
}
</script>

<template>
  <section class="history" aria-labelledby="history-title">
    <header class="history-header">
      <div>
        <p class="history-eyebrow">Historial</p>
        <h2 id="history-title" class="history-title">Mis solicitudes</h2>
      </div>
      <span v-if="!loading && !failed" class="history-count">{{ requests.length }}</span>
    </header>

    <div v-if="loading" class="history-loading" aria-label="Cargando solicitudes">
      <div v-for="index in 3" :key="index" class="loading-row">
        <USkeleton class="h-4 w-28" />
        <USkeleton class="h-4 w-12" />
        <USkeleton class="h-6 w-20 rounded-full" />
      </div>
    </div>

    <div v-else-if="failed" class="history-state" role="alert">
      <UIcon name="i-lucide-wifi-off" class="state-icon" aria-hidden="true" />
      <h3 class="state-title">No pudimos cargar tus solicitudes</h3>
      <p class="state-copy">Comprueba tu conexión y vuelve a intentarlo.</p>
      <UButton color="neutral" variant="outline" label="Reintentar" @click="$emit('retry')" />
    </div>

    <div v-else-if="requests.length === 0" class="history-state">
      <UIcon name="i-lucide-ticket" class="state-icon" aria-hidden="true" />
      <h3 class="state-title">Todavía no tienes solicitudes</h3>
      <p class="state-copy">Cuando solicites tickets, podrás seguir su estado aquí.</p>
    </div>

    <ul v-else class="request-list">
      <li v-for="request in paginatedRequests" :key="request.id" class="request-row">
        <div class="request-date">
          <span class="mobile-label">Fecha</span>
          <time :datetime="request.fecha_creacion">{{ formatDate(request.fecha_creacion) }}</time>
        </div>

        <div class="request-quantity">
          <span class="mobile-label">Cantidad</span>
          <strong>{{ request.cantidad }}</strong>
          <span>tickets</span>
        </div>

        <div class="request-status">
          <span
            class="status-pill"
            :class="`status-pill--${request.status}`"
          >
            <span class="status-dot" aria-hidden="true" />
            {{ statusLabels[request.status] }}
          </span>
        </div>

        <div class="request-action">
          <button
            v-if="request.status === 'approved'"
            type="button"
            class="view-link"
            @click="openPreview(request.id)"
          >
            Previsualizar tickets
            <UIcon name="i-lucide-eye" class="view-icon" aria-hidden="true" />
          </button>
          <span v-else class="action-placeholder">—</span>
        </div>
      </li>
    </ul>

    <footer v-if="requests.length > 0" class="history-footer">
      <p>{{ rangeStart }}–{{ rangeEnd }} de {{ requests.length }} solicitudes</p>
      <UPagination
        v-model:page="page"
        :items-per-page="itemsPerPage"
        :total="requests.length"
        :sibling-count="1"
        color="neutral"
        active-color="success"
        variant="ghost"
        size="sm"
      />
    </footer>
  </section>

  <UModal
    v-model:open="previewOpen"
    fullscreen
    title="Previsualización de tickets"
    description="Documento A4 de solo lectura"
    :ui="{ body: 'p-0 sm:p-0 overflow-hidden' }"
  >
    <template #body>
      <div class="preview-viewer">
        <div v-if="previewLoading" class="preview-loading" aria-live="polite">
          <UIcon name="i-lucide-loader-circle" class="preview-spinner" aria-hidden="true" />
          <span>Preparando documento…</span>
        </div>
        <iframe
          v-if="selectedPreviewUrl"
          class="preview-frame"
          :class="{ 'preview-frame--loading': previewLoading }"
          :src="selectedPreviewUrl"
          title="Documento A4 con los tickets aprobados"
          @load="previewLoading = false"
        />
      </div>
    </template>
  </UModal>
</template>

<style scoped>
.history {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--tickets-line);
  border-radius: 1.1rem;
  background: var(--tickets-paper);
}

.history-header {
  display: flex;
  min-height: 5.75rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem clamp(1.25rem, 3vw, 1.75rem);
  border-bottom: 1px solid var(--tickets-line);
}

.history-eyebrow {
  margin: 0 0 0.25rem;
  color: #2d6654;
  font-size: 0.68rem;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.history-title {
  margin: 0;
  color: var(--tickets-ink);
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.025em;
}

.history-count {
  display: grid;
  min-width: 1.8rem;
  height: 1.8rem;
  place-items: center;
  border-radius: 999px;
  background: #ebece8;
  color: var(--tickets-muted);
  font-size: 0.75rem;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}

.history-loading {
  padding: 0 1.5rem;
}

.loading-row {
  display: grid;
  min-height: 4.7rem;
  align-items: center;
  grid-template-columns: 1.4fr 0.8fr 1fr;
  gap: 1rem;
  border-bottom: 1px solid var(--tickets-line);
}

.loading-row:last-child {
  border-bottom: 0;
}

.history-state {
  display: flex;
  min-height: 18rem;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 2rem;
  text-align: center;
}

.state-icon {
  width: 1.5rem;
  height: 1.5rem;
  margin-bottom: 1rem;
  color: #89919e;
}

.state-title {
  margin: 0;
  color: var(--tickets-ink);
  font-size: 0.95rem;
  font-weight: 700;
}

.state-copy {
  max-width: 20rem;
  margin: 0.5rem 0 1.25rem;
  color: var(--tickets-muted);
  font-size: 0.82rem;
  line-height: 1.55;
}

.request-list {
  margin: 0;
  padding: 0 1.5rem;
  list-style: none;
}

.history-footer {
  display: flex;
  min-height: 4.5rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1.5rem;
  border-top: 1px solid var(--tickets-line);
  color: var(--tickets-muted);
  font-size: 0.72rem;
}

.history-footer p {
  margin: 0;
  white-space: nowrap;
}

.request-row {
  display: grid;
  min-height: 4.8rem;
  align-items: center;
  grid-template-columns: 1.3fr 0.8fr 1fr auto;
  gap: 1rem;
  border-bottom: 1px solid var(--tickets-line);
  color: var(--tickets-muted);
  font-size: 0.82rem;
}

.request-row:last-child {
  border-bottom: 0;
}

.request-quantity {
  display: flex;
  align-items: baseline;
  gap: 0.3rem;
}

.request-quantity strong {
  color: var(--tickets-ink);
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.status-dot {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 999px;
  background: currentColor;
}

.status-pill--pending {
  background: #f7edcf;
  color: #8b6415;
}

.status-pill--approved {
  background: #dcece5;
  color: #28634f;
}

.status-pill--rejected {
  background: #f4dfdc;
  color: #9c4037;
}

.request-action {
  text-align: right;
}

.view-link {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0;
  border: 0;
  background: none;
  color: var(--tickets-ink);
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 700;
  text-decoration: none;
}

.preview-viewer {
  position: relative;
  height: calc(100dvh - 5.5rem);
  overflow: hidden;
  background: #343b48;
}

.preview-frame {
  width: 100%;
  height: 100%;
  border: 0;
  background: #f1f5f9;
  transition: opacity 160ms ease;
}

.preview-frame--loading {
  opacity: 0;
}

.preview-loading {
  position: absolute;
  z-index: 1;
  inset: 0;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 0.75rem;
  color: #fff;
  font-size: 0.82rem;
}

.preview-spinner {
  width: 1.5rem;
  height: 1.5rem;
  animation: spin 900ms linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.view-link:hover {
  text-decoration: underline;
  text-underline-offset: 0.2rem;
}

.view-link:focus-visible {
  border-radius: 0.2rem;
  outline: 3px solid rgb(45 102 84 / 28%);
  outline-offset: 3px;
}

.view-icon {
  width: 0.85rem;
  height: 0.85rem;
}

.action-placeholder,
.mobile-label {
  color: #a1a7b0;
}

.mobile-label {
  display: none;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

@media (max-width: 720px) {
  .request-list {
    padding: 0 1.25rem;
  }

  .request-row {
    min-height: auto;
    align-items: start;
    grid-template-columns: 1fr auto;
    gap: 1rem;
    padding: 1.15rem 0;
  }

  .request-date,
  .request-quantity {
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    gap: 0.25rem;
  }

  .request-status {
    grid-column: 1;
  }

  .request-action {
    align-self: center;
    grid-column: 2;
    grid-row: 2;
  }

  .mobile-label {
    display: block;
  }

  .history-footer {
    align-items: flex-start;
    flex-direction: column;
    padding-inline: 1.25rem;
  }
}
</style>
