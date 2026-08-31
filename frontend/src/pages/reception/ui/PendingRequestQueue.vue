<script setup lang="ts">
import { computed, shallowRef, watch } from 'vue'

import type { PendingTicketRequestDTO } from '@/shared/api'

const props = defineProps<{
  approvingIds: Set<string>
  failed: boolean
  loading: boolean
  requests: PendingTicketRequestDTO[]
}>()

const emit = defineEmits<{
  approve: [id: string]
  retry: []
}>()

const itemsPerPage = 8
const page = shallowRef(1)
const printModalOpen = shallowRef(false)
const selectedRequest = shallowRef<PendingTicketRequestDTO>()

const dateFormatter = new Intl.DateTimeFormat('es-ES', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit'
})

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

function formatDate(value: string) {
  return dateFormatter.format(new Date(value))
}

function openPrintModal(request: PendingTicketRequestDTO) {
  selectedRequest.value = request
  printModalOpen.value = true
}

function confirmApproval() {
  if (!selectedRequest.value) return
  emit('approve', selectedRequest.value.id)
  printModalOpen.value = false
}
</script>

<template>
  <section class="queue" aria-labelledby="queue-title">
    <header class="queue-header">
      <div>
        <p class="queue-eyebrow">Cola de trabajo</p>
        <h2 id="queue-title" class="queue-title">Pendientes de aprobación</h2>
      </div>
      <span v-if="!loading && !failed" class="queue-count">{{ requests.length }}</span>
    </header>

    <div v-if="loading" class="queue-loading" aria-label="Cargando solicitudes">
      <div v-for="index in 5" :key="index" class="loading-row">
        <USkeleton class="h-4 w-32" />
        <USkeleton class="h-4 w-24" />
        <USkeleton class="h-4 w-14" />
        <USkeleton class="h-8 w-24 rounded-lg" />
      </div>
    </div>

    <div v-else-if="failed" class="queue-state" role="alert">
      <UIcon name="i-lucide-wifi-off" class="state-icon" aria-hidden="true" />
      <h3 class="state-title">No pudimos cargar la cola</h3>
      <p class="state-copy">Comprueba la conexión con el servidor y vuelve a intentarlo.</p>
      <UButton color="neutral" variant="outline" label="Reintentar" @click="$emit('retry')" />
    </div>

    <div v-else-if="requests.length === 0" class="queue-state">
      <span class="empty-check" aria-hidden="true">
        <UIcon name="i-lucide-check" />
      </span>
      <h3 class="state-title">Todo está al día</h3>
      <p class="state-copy">No quedan solicitudes pendientes de aprobación.</p>
    </div>

    <template v-else>
      <div class="desktop-table">
        <table>
          <caption class="sr-only">Solicitudes de tickets pendientes de aprobación</caption>
          <thead>
            <tr>
              <th scope="col">Solicitante</th>
              <th scope="col">Fecha</th>
              <th scope="col">Cantidad</th>
              <th scope="col"><span class="sr-only">Acción</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in paginatedRequests" :key="request.id">
              <td>
                <span class="requester-avatar" aria-hidden="true">{{ request.requester_name.charAt(0) }}</span>
                <strong class="requester-name">{{ request.requester_name }}</strong>
              </td>
              <td><time :datetime="request.fecha_creacion">{{ formatDate(request.fecha_creacion) }}</time></td>
              <td><strong class="ticket-amount">{{ request.cantidad }}</strong> tickets</td>
              <td class="action-cell">
                <UButton color="success" variant="soft" icon="i-lucide-printer" :loading="approvingIds.has(request.id)"
                  :aria-label="`Aprobar e imprimir solicitud de ${request.requester_name}`"
                  @click="openPrintModal(request)">
                  Aprobar e imprimir
                </UButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <ul class="mobile-list">
        <li v-for="request in paginatedRequests" :key="request.id" class="mobile-request">
          <div class="mobile-requester">
            <span class="requester-avatar" aria-hidden="true">{{ request.requester_name.charAt(0) }}</span>
            <div>
              <span class="mobile-label">Solicitante</span>
              <strong class="requester-name">{{ request.requester_name }}</strong>
            </div>
          </div>
          <dl class="mobile-details">
            <div>
              <dt>Fecha</dt>
              <dd><time :datetime="request.fecha_creacion">{{ formatDate(request.fecha_creacion) }}</time></dd>
            </div>
            <div>
              <dt>Cantidad</dt>
              <dd><strong class="ticket-amount">{{ request.cantidad }}</strong> tickets</dd>
            </div>
          </dl>
          <UButton block color="success" variant="soft" icon="i-lucide-printer" :loading="approvingIds.has(request.id)"
            @click="openPrintModal(request)">
            Aprobar e imprimir
          </UButton>
        </li>
      </ul>

      <footer class="queue-footer">
        <p>{{ rangeStart }}–{{ rangeEnd }} de {{ requests.length }} solicitudes</p>
        <UPagination v-model:page="page" :items-per-page="itemsPerPage" :total="requests.length" :sibling-count="1"
          color="primary" active-color="primary" variant="ghost" size="sm" />
      </footer>
    </template>
  </section>

  <UModal v-model:open="printModalOpen" title="Aprobar e imprimir"
    description="Chrome te pedirá que elijas una impresora antes de imprimir." :ui="{ content: 'sm:max-w-lg' }">
    <template #body>
      <div v-if="selectedRequest" class="grid gap-4">
        <div class="rounded-xl border border-default bg-elevated p-4">
          <p class="m-0 text-xs font-bold uppercase tracking-widest text-primary">Solicitud</p>
          <strong class="mt-2 block text-lg text-highlighted">{{ selectedRequest.requester_name }}</strong>
          <p class="mt-1 mb-0 text-sm text-muted">
            {{ selectedRequest.cantidad }} tickets · {{ formatDate(selectedRequest.fecha_creacion) }}
          </p>
        </div>

        <div class="flex gap-3 rounded-xl bg-success/10 p-4 text-sm leading-6 text-success">
          <UIcon name="i-lucide-printer-check" class="mt-1 size-4 shrink-0" aria-hidden="true" />
          <p class="m-0">
            Después de aprobar se abrirá una pestaña con la vista A4 y el diálogo de impresión de Chrome.
          </p>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton color="neutral" variant="ghost" label="Cancelar" @click="printModalOpen = false" />
        <UButton color="success" icon="i-lucide-printer" label="Aprobar y elegir impresora" @click="confirmApproval" />
      </div>
    </template>
  </UModal>
</template>

<style scoped>
.queue {
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--ui-border);
  border-radius: 1.1rem;
  background: var(--ui-bg-elevated);
  box-shadow: 0 18px 50px color-mix(in srgb, black 5%, transparent);
}

.queue-header {
  display: flex;
  min-height: 5.75rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem clamp(1.25rem, 3vw, 1.75rem);
  border-bottom: 1px solid var(--ui-border);
}

.queue-eyebrow {
  margin: 0 0 0.25rem;
  color: var(--ui-primary);
  font-size: 0.68rem;
  font-weight: 750;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.queue-title {
  margin: 0;
  color: var(--ui-text-highlighted);
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.025em;
}

.queue-count {
  display: grid;
  min-width: 1.8rem;
  height: 1.8rem;
  place-items: center;
  border-radius: 999px;
  background: color-mix(in srgb, var(--ui-warning) 14%, transparent);
  color: var(--ui-warning);
  font-size: 0.75rem;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
}

.queue-loading {
  padding-inline: 1.5rem;
}

.loading-row {
  display: grid;
  min-height: 4.8rem;
  align-items: center;
  grid-template-columns: 1.35fr 1fr 0.7fr auto;
  gap: 1rem;
  border-bottom: 1px solid var(--ui-border);
}

.loading-row:last-child {
  border-bottom: 0;
}

.queue-state {
  display: flex;
  min-height: 24rem;
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
  color: var(--ui-error);
}

.empty-check {
  display: grid;
  width: 3.2rem;
  height: 3.2rem;
  place-items: center;
  margin-bottom: 1.1rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--ui-success) 14%, transparent);
  color: var(--ui-success);
}

.empty-check svg {
  width: 1.35rem;
  height: 1.35rem;
}

.state-title {
  margin: 0;
  color: var(--ui-text-highlighted);
  font-size: 1rem;
  font-weight: 750;
}

.state-copy {
  max-width: 22rem;
  margin: 0.5rem 0 1.25rem;
  color: var(--ui-text-muted);
  font-size: 0.82rem;
  line-height: 1.55;
}

.desktop-table {
  overflow-x: auto;
}

.desktop-table table {
  width: 100%;
  border-collapse: collapse;
}

.desktop-table th {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--ui-border);
  background: var(--ui-bg);
  color: var(--ui-text-muted);
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-align: left;
  text-transform: uppercase;
}

.desktop-table th:first-child,
.desktop-table td:first-child {
  padding-left: 1.5rem;
}

.desktop-table th:last-child,
.desktop-table td:last-child {
  padding-right: 1.5rem;
}

.desktop-table td {
  height: 4.8rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--ui-border);
  color: var(--ui-text-muted);
  font-size: 0.78rem;
  white-space: nowrap;
}

.desktop-table tbody tr:last-child td {
  border-bottom: 0;
}

.desktop-table tbody tr {
  transition: background-color 140ms ease;
}

.desktop-table tbody tr:hover {
  background: color-mix(in srgb, var(--ui-primary) 12%, transparent);
}

.desktop-table td:first-child {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.requester-avatar {
  display: grid;
  width: 2rem;
  height: 2rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: color-mix(in srgb, var(--ui-primary) 14%, transparent);
  color: var(--ui-primary);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}

.requester-name {
  color: var(--ui-text-highlighted);
  font-size: 0.82rem;
}

.ticket-amount {
  color: var(--ui-text-highlighted);
  font-size: 0.95rem;
  font-variant-numeric: tabular-nums;
}

.action-cell {
  text-align: right;
}

.mobile-list {
  display: none;
  margin: 0;
  padding: 1rem;
  list-style: none;
}

.queue-footer {
  display: flex;
  min-height: 4.4rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 1.5rem;
  border-top: 1px solid var(--ui-border);
  background: var(--ui-bg);
}

.queue-footer p {
  margin: 0;
  color: var(--ui-text-muted);
  font-size: 0.72rem;
  font-variant-numeric: tabular-nums;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  padding: 0;
  margin: -1px;
  border: 0;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

@media (max-width: 700px) {
  .desktop-table {
    display: none;
  }

  .mobile-list {
    display: grid;
    gap: 0.8rem;
  }

  .mobile-request {
    padding: 1rem;
    border: 1px solid var(--ui-border);
    border-radius: 0.9rem;
    background: var(--ui-bg);
  }

  .mobile-requester {
    display: flex;
    align-items: center;
    gap: 0.7rem;
  }

  .mobile-label,
  .mobile-details dt {
    display: block;
    margin-bottom: 0.18rem;
    color: var(--ui-text-muted);
    font-size: 0.61rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .mobile-details {
    display: grid;
    grid-template-columns: 1.4fr 0.8fr;
    gap: 1rem;
    margin: 1rem 0;
    padding-block: 0.85rem;
    border-block: 1px solid var(--ui-border);
  }

  .mobile-details dd {
    margin: 0;
    color: var(--ui-text-muted);
    font-size: 0.75rem;
    line-height: 1.4;
  }

  .queue-footer {
    align-items: flex-start;
    flex-direction: column;
    padding: 1rem;
  }

  .queue-footer> :last-child {
    align-self: center;
  }
}
</style>
