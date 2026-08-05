<script setup lang="ts">
import { shallowRef } from 'vue'

import { useSpending } from '../model/use-spending'

const props = withDefaults(defineProps<{ managePrice?: boolean }>(), { managePrice: false })

const months = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]
const currentYear = new Date().getFullYear()
const years = Array.from({ length: currentYear - 2019 }, (_, index) => currentYear - index)
const moneyFormatter = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' })
const dateFormatter = new Intl.DateTimeFormat('es-ES', { dateStyle: 'medium' })
const dateTimeFormatter = new Intl.DateTimeFormat('es-ES', {
  dateStyle: 'medium',
  timeStyle: 'short'
})

const {
  detail,
  detailError,
  detailLoading,
  error,
  isLoading,
  modalOpen,
  month,
  openDetail,
  period,
  priceLoadError,
  priceLoading,
  priceMessage,
  priceMutationError,
  priceOverview,
  priceSaving,
  refresh,
  report,
  scope,
  search,
  savePrice,
  selectedUser,
  users,
  year
} = useSpending(props.managePrice)

const editingPrice = shallowRef(false)
const priceInput = shallowRef('')

const periodLabel = computed(() => scope.value === 'year'
  ? String(year.value)
  : `${months[month.value - 1]} ${year.value}`)

function formatMoney(value: number | string | undefined) {
  const amount = Number(value ?? 0)
  return moneyFormatter.format(Number.isFinite(amount) ? amount : 0)
}

function formatDate(value: string) {
  return dateFormatter.format(new Date(value))
}

function startPriceEdit() {
  priceInput.value = String(priceOverview.value?.precio_unitario ?? '5.50').replace('.', ',')
  editingPrice.value = true
}

async function submitPrice() {
  if (await savePrice(priceInput.value)) editingPrice.value = false
}
</script>

<template>
  <UContainer class="spending-page">
    <header class="page-header">
      <div class="page-heading">
        <p class="eyebrow">{{ managePrice ? 'Contabilidad' : 'Recursos Humanos' }}</p>
        <h1>Panel financiero</h1>
        <p>Gasto, actividad y empleados en una sola vista.</p>
      </div>

      <div class="period-controls">
        <fieldset class="scope-filter">
          <legend>Alcance del informe</legend>
          <button type="button" :aria-pressed="scope === 'month'" @click="scope = 'month'">Mes</button>
          <button type="button" :aria-pressed="scope === 'year'" @click="scope = 'year'">Año</button>
        </fieldset>

        <fieldset class="period-filter">
          <legend>Periodo del informe</legend>
          <label v-if="scope === 'month'">
            <span>Mes</span>
            <select v-model="month">
              <option v-for="(label, index) in months" :key="label" :value="index + 1">{{ label }}</option>
            </select>
          </label>
          <label>
            <span>Año</span>
            <select v-model="year">
              <option v-for="option in years" :key="option" :value="option">{{ option }}</option>
            </select>
          </label>
        </fieldset>
      </div>
    </header>

    <div v-if="isLoading && !report" class="metrics" aria-label="Cargando resumen">
      <USkeleton v-for="index in 3" :key="index" class="metric-skeleton" />
    </div>

    <section v-else-if="error && !report" class="page-state" role="alert">
      <UIcon name="i-lucide-wifi-off" aria-hidden="true" />
      <h2>No pudimos cargar el gasto</h2>
      <p>Comprueba tu conexión y vuelve a intentarlo.</p>
      <UButton color="neutral" variant="outline" label="Reintentar" @click="() => refresh()" />
    </section>

    <template v-else>
      <section class="metrics" aria-label="Resumen del periodo" aria-live="polite">
        <article class="metric metric--primary">
          <span>Gasto aprobado</span>
          <strong>{{ formatMoney(report?.total_gastado) }}</strong>
          <small>{{ periodLabel }}</small>
        </article>
        <article class="metric">
          <span>Tickets emitidos</span>
          <strong>{{ report?.tickets_emitidos ?? 0 }}</strong>
          <small>Aprobados en el periodo</small>
        </article>
        <article class="metric">
          <span>Gasto medio</span>
          <strong>{{ formatMoney(report?.gasto_medio_por_usuario) }}</strong>
          <small>Por empleado</small>
        </article>
      </section>

      <section v-if="managePrice" class="price-card" aria-labelledby="price-title">
        <div class="price-summary">
          <span>Tarifa vigente</span>
          <strong id="price-title">{{ formatMoney(priceOverview?.precio_unitario) }}</strong>
          <small>Por ticket aprobado</small>
        </div>

        <USkeleton v-if="priceLoading && !priceOverview" class="h-20 w-full" />
        <div v-else-if="priceLoadError && !priceOverview" class="price-state" role="alert">
          <span>No se pudo cargar la tarifa.</span>
        </div>
        <form v-else-if="editingPrice" class="price-form" @submit.prevent="submitPrice">
          <label for="ticket-price">Nueva tarifa</label>
          <div class="price-input">
            <input
              id="ticket-price"
              v-model="priceInput"
              type="text"
              inputmode="decimal"
              autocomplete="off"
              placeholder="5,50"
              aria-describedby="price-help"
            >
            <span>€</span>
          </div>
          <small id="price-help">Se aplicará solo a futuras aprobaciones.</small>
          <div class="price-actions">
            <UButton type="submit" label="Guardar tarifa" :loading="priceSaving" />
            <UButton color="neutral" variant="ghost" label="Cancelar" @click="editingPrice = false" />
          </div>
        </form>
        <div v-else class="price-controls">
          <p>Los tickets ya emitidos conservan su importe original.</p>
          <UButton icon="i-lucide-pencil" label="Ajustar tarifa" @click="startPriceEdit" />
        </div>

        <p v-if="priceMutationError" class="price-notice price-notice--error" role="alert">
          {{ priceMutationError }}
        </p>
        <p v-else-if="priceMessage" class="price-notice price-notice--success" role="status">
          {{ priceMessage }}
        </p>

        <details v-if="priceOverview?.historial.length" class="price-history">
          <summary>Historial de tarifas</summary>
          <ul>
            <li v-for="change in priceOverview.historial" :key="change.id">
              <strong>{{ formatMoney(change.precio_unitario) }}</strong>
              <span>{{ change.updated_by_name }}</span>
              <time :datetime="change.updated_at">{{ dateTimeFormatter.format(new Date(change.updated_at)) }}</time>
            </li>
          </ul>
        </details>
      </section>

      <section class="directory" aria-labelledby="directory-title">
        <header class="directory-header">
          <div>
            <p class="eyebrow">Desglose</p>
            <div class="directory-title">
              <h2 id="directory-title">Gasto por empleado</h2>
              <span>{{ users.length }}</span>
            </div>
          </div>
          <label class="search-field">
            <span class="sr-only">Buscar por nombre o email</span>
            <UIcon name="i-lucide-search" aria-hidden="true" />
            <input v-model="search" type="search" placeholder="Buscar nombre o email" autocomplete="off">
          </label>
        </header>

        <div v-if="isLoading" class="table-loading" aria-label="Actualizando informe">
          <USkeleton v-for="index in 4" :key="index" class="h-14 w-full" />
        </div>

        <div v-else-if="error" class="table-state" role="alert">
          <p>No se pudo actualizar el periodo.</p>
          <UButton color="neutral" variant="outline" size="sm" label="Reintentar" @click="() => refresh()" />
        </div>

        <div v-else-if="report?.usuarios.length === 0" class="table-state">
          <UIcon name="i-lucide-users" aria-hidden="true" />
          <h3>No hay empleados para mostrar</h3>
          <p>El directorio aparecerá aquí cuando haya usuarios.</p>
        </div>

        <div v-else-if="users.length === 0" class="table-state" aria-live="polite">
          <UIcon name="i-lucide-search-x" aria-hidden="true" />
          <h3>Sin resultados</h3>
          <p>No hay coincidencias para “{{ search }}”.</p>
        </div>

        <template v-else>
          <div class="desktop-table">
            <table>
            <caption class="sr-only">Gasto aprobado de todos los empleados durante {{ period }}</caption>
            <thead>
              <tr>
                <th scope="col">Empleado</th>
                <th scope="col" class="number-cell">Aprobadas</th>
                <th scope="col" class="number-cell">Gasto</th>
                <th scope="col"><span class="sr-only">Ver detalle</span></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="user in users"
                :key="user.user_id"
                tabindex="0"
                :aria-label="`Ver detalle de ${user.nombre}`"
                @click="openDetail(user)"
                @keydown.enter="openDetail(user)"
                @keydown.space.prevent="openDetail(user)"
              >
                <td>
                  <div class="employee-cell">
                    <span class="employee-avatar" aria-hidden="true">{{ user.nombre.charAt(0) }}</span>
                    <span>
                      <strong>{{ user.nombre }}</strong>
                      <small>{{ user.email }}</small>
                    </span>
                  </div>
                </td>
                <td class="number-cell">{{ user.tickets_emitidos }}</td>
                <td class="number-cell amount">{{ formatMoney(user.total_gastado) }}</td>
                <td class="arrow-cell"><UIcon name="i-lucide-chevron-right" aria-hidden="true" /></td>
              </tr>
            </tbody>
            </table>
          </div>

          <ul class="mobile-list">
            <li v-for="user in users" :key="user.user_id">
              <button type="button" :aria-label="`Ver detalle de ${user.nombre}`" @click="openDetail(user)">
                <span class="mobile-employee">
                  <span class="employee-avatar" aria-hidden="true">{{ user.nombre.charAt(0) }}</span>
                  <span>
                    <strong>{{ user.nombre }}</strong>
                    <small>{{ user.email }}</small>
                  </span>
                </span>
                <span class="mobile-amount">
                  <strong>{{ formatMoney(user.total_gastado) }}</strong>
                  <small>{{ user.tickets_emitidos }} tickets</small>
                </span>
                <UIcon name="i-lucide-chevron-right" aria-hidden="true" />
              </button>
            </li>
          </ul>
        </template>
      </section>
    </template>
  </UContainer>

  <UModal
    v-model:open="modalOpen"
    :title="selectedUser?.nombre ?? 'Detalle de gasto'"
    :description="selectedUser?.email"
    scrollable
    :ui="{ content: 'sm:max-w-2xl' }"
  >
    <template #body>
      <div v-if="detailLoading" class="detail-loading" aria-label="Cargando detalle">
        <USkeleton class="h-20 w-full" />
        <USkeleton v-for="index in 3" :key="index" class="h-12 w-full" />
      </div>

      <div v-else-if="detailError" class="detail-state" role="alert">
        <UIcon name="i-lucide-circle-alert" aria-hidden="true" />
        <p>No pudimos cargar el detalle aprobado.</p>
        <UButton v-if="selectedUser" color="neutral" variant="outline" size="sm" label="Reintentar"
          @click="openDetail(selectedUser)" />
      </div>

      <div v-else-if="detail">
        <div class="detail-summary">
          <span>Gasto aprobado en {{ periodLabel }}</span>
          <strong>{{ formatMoney(detail.total_gastado) }}</strong>
          <small>{{ detail.tickets_emitidos }} tickets emitidos</small>
        </div>

        <div v-if="detail.solicitudes.length === 0" class="detail-state">
          <UIcon name="i-lucide-receipt-text" aria-hidden="true" />
          <p>No hay solicitudes aprobadas en este periodo.</p>
        </div>

        <ul v-else class="detail-list" aria-label="Solicitudes aprobadas">
          <li v-for="request in detail.solicitudes" :key="request.id">
            <div>
              <strong>{{ request.tickets_emitidos }} tickets</strong>
              <time :datetime="request.fecha_emision">{{ formatDate(request.fecha_emision) }}</time>
            </div>
            <span>{{ formatMoney(request.total_gastado) }}</span>
          </li>
        </ul>
      </div>
    </template>
  </UModal>
</template>

<style scoped>
.spending-page {
  max-width: 92rem;
  padding-block: clamp(1.5rem, 4vw, 3rem);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  margin-bottom: clamp(1.5rem, 3vw, 2.25rem);
}

.page-heading {
  max-width: 44rem;
}

.eyebrow {
  margin: 0 0 0.65rem;
  color: #2d6654;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.page-heading h1 {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: clamp(2.3rem, 5vw, 3.8rem);
  font-weight: 500;
  letter-spacing: -0.06em;
  line-height: 0.95;
}

.page-heading > p:last-child {
  margin: 1.15rem 0 0;
  color: var(--tickets-muted);
  line-height: 1.6;
}

.period-controls,
.period-filter,
.scope-filter {
  display: flex;
}

.period-controls {
  align-items: end;
  gap: 0.9rem;
}

.period-filter {
  gap: 0.65rem;
  margin: 0;
  padding: 0;
  border: 0;
}

.period-filter legend,
.scope-filter legend {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.scope-filter {
  overflow: hidden;
  margin: 0;
  padding: 0.2rem;
  border: 1px solid #cfd5d1;
  border-radius: 0.7rem;
  background: #e8e9e5;
}

.scope-filter button {
  padding: 0.58rem 0.8rem;
  border: 0;
  border-radius: 0.5rem;
  background: transparent;
  color: var(--tickets-muted);
  font: inherit;
  font-size: 0.78rem;
  font-weight: 750;
  cursor: pointer;
}

.scope-filter button[aria-pressed="true"] {
  background: var(--tickets-paper);
  color: #285b4b;
  box-shadow: 0 1px 3px rgb(20 33 61 / 12%);
}

.period-filter label {
  display: grid;
  gap: 0.35rem;
  color: var(--tickets-muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.period-filter select {
  min-width: 8.5rem;
  height: 2.75rem;
  padding: 0 2.2rem 0 0.85rem;
  border: 1px solid #cfd5d1;
  border-radius: 0.7rem;
  background: var(--tickets-paper);
  color: var(--tickets-ink);
  font: inherit;
  font-size: 0.82rem;
  font-weight: 650;
  letter-spacing: 0;
  text-transform: none;
}

.period-filter label:last-child select {
  min-width: 6.5rem;
}

.period-filter select:focus-visible,
.scope-filter button:focus-visible,
.search-field:focus-within,
.price-input:focus-within,
tbody tr:focus-visible {
  outline: 3px solid rgb(45 102 84 / 28%);
  outline-offset: 2px;
}

.price-card {
  display: grid;
  grid-template-columns: minmax(11rem, 0.65fr) minmax(18rem, 1.35fr);
  gap: 1.5rem;
  margin-bottom: 1rem;
  padding: clamp(1.25rem, 3vw, 1.75rem);
  border: 1px solid #c8d8cf;
  border-radius: 1rem;
  background: #edf3ef;
}

.price-summary {
  display: grid;
  align-content: center;
}

.price-summary > span,
.price-summary small,
.price-form label,
.price-form small {
  color: var(--tickets-muted);
  font-size: 0.72rem;
}

.price-summary strong {
  margin-block: 0.25rem;
  color: #285b4b;
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: 2.5rem;
  font-weight: 500;
  line-height: 1;
}

.price-controls,
.price-form {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
}

.price-controls p {
  margin: 0;
  color: var(--tickets-muted);
  font-size: 0.8rem;
}

.price-form {
  display: grid;
  grid-template-columns: minmax(8rem, 12rem) auto;
}

.price-form label,
.price-form small {
  grid-column: 1;
}

.price-input {
  display: flex;
  height: 2.75rem;
  align-items: center;
  grid-column: 1;
  padding-inline: 0.85rem;
  border: 1px solid #bfcac4;
  border-radius: 0.7rem;
  background: #fff;
}

.price-input input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--tickets-ink);
  font: inherit;
}

.price-input span {
  color: var(--tickets-muted);
}

.price-actions {
  display: flex;
  align-items: center;
  grid-column: 2;
  grid-row: 1 / 4;
  gap: 0.4rem;
}

.price-state {
  display: flex;
  align-items: center;
  color: #8d2929;
  font-size: 0.8rem;
}

.price-notice,
.price-history {
  grid-column: 1 / -1;
}

.price-notice {
  margin: 0;
  padding: 0.75rem 0.9rem;
  border-radius: 0.65rem;
  font-size: 0.8rem;
}

.price-notice--success {
  background: #dceadf;
  color: #285b4b;
}

.price-notice--error {
  background: #fff1f1;
  color: #8d2929;
}

.price-history {
  padding-top: 1rem;
  border-top: 1px solid #c8d8cf;
}

.price-history summary {
  color: #285b4b;
  font-size: 0.8rem;
  font-weight: 750;
  cursor: pointer;
}

.price-history ul {
  margin: 0.75rem 0 0;
  padding: 0;
  list-style: none;
}

.price-history li {
  display: grid;
  grid-template-columns: 6rem minmax(8rem, 1fr) auto;
  gap: 1rem;
  padding-block: 0.65rem;
  border-bottom: 1px solid #d6e0da;
  font-size: 0.78rem;
}

.price-history li:last-child {
  border-bottom: 0;
}

.price-history li span,
.price-history time {
  color: var(--tickets-muted);
}

.metrics {
  display: grid;
  grid-template-columns: 1.35fr 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.metric,
.metric-skeleton {
  min-height: 9.5rem;
  border-radius: 1rem;
}

.metric {
  display: flex;
  justify-content: center;
  flex-direction: column;
  padding: clamp(1.25rem, 3vw, 1.75rem);
  border: 1px solid var(--tickets-line);
  background: var(--tickets-paper);
}

.metric--primary {
  border-color: #315f50;
  background: #315f50;
  color: #fff;
}

.metric > span {
  color: var(--tickets-muted);
  font-size: 0.73rem;
  font-weight: 700;
}

.metric--primary > span,
.metric--primary small {
  color: #d9e8e1;
}

.metric strong {
  margin-block: 0.35rem;
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: clamp(2rem, 4vw, 2.8rem);
  font-weight: 500;
  letter-spacing: -0.045em;
  line-height: 1;
}

.metric small {
  color: #8a929e;
  font-size: 0.7rem;
}

.directory {
  overflow: hidden;
  border: 1px solid var(--tickets-line);
  border-radius: 1rem;
  background: var(--tickets-paper);
}

.directory-header {
  display: flex;
  min-height: 6.5rem;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.25rem clamp(1.25rem, 3vw, 1.75rem);
  border-bottom: 1px solid var(--tickets-line);
}

.directory-header h2 {
  margin: 0;
  font-size: 1.1rem;
  letter-spacing: -0.025em;
}

.directory-title {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}

.directory-title > span {
  display: grid;
  min-width: 1.7rem;
  height: 1.7rem;
  place-items: center;
  padding-inline: 0.4rem;
  border-radius: 999px;
  background: #e7ece7;
  color: #2d6654;
  font-size: 0.7rem;
  font-variant-numeric: tabular-nums;
  font-weight: 800;
}

.search-field {
  display: flex;
  width: min(100%, 20rem);
  height: 2.65rem;
  align-items: center;
  gap: 0.6rem;
  padding-inline: 0.8rem;
  border: 1px solid #d5d9d6;
  border-radius: 0.7rem;
  background: #fff;
  color: #89919e;
}

.search-field input {
  min-width: 0;
  flex: 1;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--tickets-ink);
  font: inherit;
  font-size: 0.8rem;
}

.desktop-table {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 36rem;
  border-collapse: collapse;
}

th,
td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--tickets-line);
  text-align: left;
}

th {
  background: #f5f4f0;
  color: #7b8491;
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

td {
  color: var(--tickets-muted);
  font-size: 0.8rem;
}

td strong {
  color: var(--tickets-ink);
  font-size: 0.86rem;
}

.employee-cell,
.mobile-employee {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.75rem;
}

.employee-cell > span:last-child,
.mobile-employee > span:last-child {
  display: grid;
  min-width: 0;
  gap: 0.15rem;
}

.employee-cell small,
.mobile-employee small {
  overflow: hidden;
  color: var(--tickets-muted);
  font-size: 0.7rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.employee-avatar {
  display: grid;
  width: 2rem;
  height: 2rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: #e5e9e3;
  color: #315f50;
  font-size: 0.72rem;
  font-weight: 850;
  text-transform: uppercase;
}

tbody tr {
  cursor: pointer;
  transition: background-color 140ms ease;
}

tbody tr:hover,
tbody tr:focus-visible {
  background: #f0f4f0;
}

tbody tr:last-child td {
  border-bottom: 0;
}

.number-cell {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.amount {
  color: var(--tickets-ink);
  font-weight: 750;
}

.arrow-cell {
  width: 2rem;
  padding-left: 0;
  color: #8b948f;
}

.mobile-list {
  display: none;
  margin: 0;
  padding: 0.8rem;
  list-style: none;
}

.mobile-list li + li {
  margin-top: 0.65rem;
}

.mobile-list button {
  display: grid;
  width: 100%;
  align-items: center;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--tickets-line);
  border-radius: 0.85rem;
  background: #fffefa;
  color: var(--tickets-ink);
  font: inherit;
  text-align: left;
}

.mobile-list button:focus-visible {
  outline: 3px solid rgb(45 102 84 / 28%);
  outline-offset: 2px;
}

.mobile-amount {
  display: grid;
  justify-items: end;
  gap: 0.15rem;
}

.mobile-amount strong {
  font-size: 0.82rem;
  font-variant-numeric: tabular-nums;
}

.mobile-amount small {
  color: var(--tickets-muted);
  font-size: 0.66rem;
}

.mobile-list svg {
  color: #8b948f;
}

.table-loading,
.detail-loading {
  display: grid;
  gap: 0.75rem;
  padding: 1.5rem;
}

.page-state,
.table-state,
.detail-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  padding: 3.5rem 1.5rem;
  text-align: center;
}

.page-state {
  min-height: 20rem;
  border: 1px solid var(--tickets-line);
  border-radius: 1rem;
  background: var(--tickets-paper);
}

.page-state svg,
.table-state svg,
.detail-state svg {
  width: 1.5rem;
  height: 1.5rem;
  margin-bottom: 0.75rem;
  color: #87918b;
}

.page-state h2,
.table-state h3 {
  margin: 0;
  font-size: 1rem;
}

.page-state p,
.table-state p,
.detail-state p {
  margin: 0.45rem 0 1rem;
  color: var(--tickets-muted);
  font-size: 0.82rem;
}

.detail-summary {
  display: grid;
  padding: 1.4rem;
  border-radius: 0.8rem;
  background: #e9f0eb;
  color: #285b4b;
}

.detail-summary span,
.detail-summary small {
  font-size: 0.72rem;
}

.detail-summary strong {
  margin-block: 0.25rem;
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: 2.25rem;
  font-weight: 500;
}

.detail-list {
  margin: 1.25rem 0 0;
  padding: 0;
  list-style: none;
}

.detail-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0.25rem;
  border-bottom: 1px solid var(--tickets-line);
  font-size: 0.82rem;
}

.detail-list li > div {
  display: grid;
  gap: 0.2rem;
}

.detail-list time {
  color: var(--tickets-muted);
  font-size: 0.72rem;
}

.detail-list li > span {
  color: #fff;
  font-variant-numeric: tabular-nums;
  font-weight: 750;
}

.detail-list li strong {
  color: #fff;
}

@media (max-width: 760px) {
  .page-header,
  .directory-header {
    align-items: stretch;
    flex-direction: column;
  }

  .period-controls {
    align-items: stretch;
    flex-direction: column;
  }

  .scope-filter {
    align-self: start;
  }

  .metrics {
    grid-template-columns: 1fr 1fr;
  }

  .price-card {
    grid-template-columns: 1fr;
  }

  .price-controls {
    align-items: stretch;
    flex-direction: column;
  }

  .price-form {
    grid-template-columns: 1fr;
  }

  .price-actions {
    grid-column: 1;
    grid-row: auto;
  }

  .price-history li {
    grid-template-columns: 5rem 1fr;
  }

  .price-history time {
    grid-column: 1 / -1;
  }

  .metric--primary {
    grid-column: 1 / -1;
  }

  .search-field {
    width: 100%;
  }
}

@media (max-width: 700px) {
  .desktop-table {
    display: none;
  }

  .mobile-list {
    display: block;
  }
}

@media (max-width: 480px) {
  .period-filter label,
  .period-filter select {
    min-width: 0;
    width: 100%;
  }

  .period-filter label {
    flex: 1;
  }

  .metrics {
    grid-template-columns: 1fr;
  }

  .metric--primary {
    grid-column: auto;
  }

  .mobile-list button {
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .mobile-amount {
    grid-column: 1;
    grid-row: 2;
    justify-items: start;
    padding-left: 2.75rem;
  }

  .mobile-list svg {
    grid-column: 2;
    grid-row: 1 / 3;
  }
}
</style>
