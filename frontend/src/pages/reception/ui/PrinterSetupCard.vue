<script setup lang="ts">
import { computed, shallowRef } from 'vue'

const printers = [
  { id: 'reception-zebra', label: 'Zebra ZD421 · Recepción' },
  { id: 'kitchen-epson', label: 'Epson TM-T20III · Cocina' },
  { id: 'office-brother', label: 'Brother QL-820NWB · Oficina' }
]

const selectedPrinterId = shallowRef<string>()
const connectedPrinterId = shallowRef<string>()

const connectedPrinter = computed(() => printers.find(printer => printer.id === connectedPrinterId.value))

function addPrinter() {
  connectedPrinterId.value = selectedPrinterId.value
}
</script>

<template>
  <section class="printer-card" aria-labelledby="printer-title">
    <div class="printer-icon" aria-hidden="true">
      <UIcon name="i-lucide-printer" />
    </div>

    <p class="card-eyebrow">Dispositivo de salida</p>
    <h2 id="printer-title" class="card-title">Impresora</h2>
    <p class="card-description">
      Busca una impresora cercana y déjala preparada para las próximas aprobaciones.
    </p>

    <div v-if="connectedPrinter" class="connected-printer" aria-live="polite">
      <span class="connection-dot" aria-hidden="true" />
      <div>
        <span class="connection-label">Añadida</span>
        <strong>{{ connectedPrinter.label }}</strong>
      </div>
    </div>

    <form class="printer-form" @submit.prevent="addPrinter">
      <label for="printer-select" class="field-label">Buscar impresora</label>
      <USelectMenu
        id="printer-select"
        v-model="selectedPrinterId"
        :items="printers"
        value-key="id"
        label-key="label"
        icon="i-lucide-search"
        placeholder="Selecciona un dispositivo"
        :search-input="{ placeholder: 'Buscar por nombre…' }"
        class="printer-select"
      />
      <UButton
        type="submit"
        block
        color="neutral"
        icon="i-lucide-plus"
        :disabled="!selectedPrinterId || selectedPrinterId === connectedPrinterId"
      >
        {{ connectedPrinter ? 'Cambiar impresora' : 'Añadir impresora' }}
      </UButton>
    </form>

    <p class="demo-note">
      <UIcon name="i-lucide-info" aria-hidden="true" />
      Configuración de demostración guardada solo durante esta sesión.
    </p>
  </section>
</template>

<style scoped>
.printer-card {
  position: relative;
  overflow: hidden;
  padding: clamp(1.4rem, 3vw, 1.8rem);
  border: 1px solid var(--tickets-line);
  border-radius: 1.1rem;
  background: var(--tickets-paper);
  box-shadow: 0 18px 50px rgb(20 33 61 / 5%);
}

.printer-card::after {
  position: absolute;
  top: -4rem;
  right: -4rem;
  width: 10rem;
  height: 10rem;
  border: 1px solid rgb(45 102 84 / 12%);
  border-radius: 50%;
  content: "";
}

.printer-icon {
  display: grid;
  width: 2.8rem;
  height: 2.8rem;
  place-items: center;
  margin-bottom: 1.5rem;
  border-radius: 0.8rem;
  background: var(--tickets-ink);
  color: #fff;
}

.printer-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.card-eyebrow {
  margin: 0 0 0.35rem;
  color: #2d6654;
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.card-title {
  margin: 0;
  color: var(--tickets-ink);
  font-size: 1.3rem;
  font-weight: 750;
  letter-spacing: -0.035em;
}

.card-description {
  margin: 0.75rem 0 1.35rem;
  color: var(--tickets-muted);
  font-size: 0.82rem;
  line-height: 1.6;
}

.connected-printer {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  margin-bottom: 1.25rem;
  padding: 0.85rem;
  border: 1px solid #cbded4;
  border-radius: 0.75rem;
  background: #edf4ef;
}

.connection-dot {
  width: 0.5rem;
  height: 0.5rem;
  flex: 0 0 auto;
  margin-top: 0.3rem;
  border-radius: 50%;
  background: #2d8063;
  box-shadow: 0 0 0 4px rgb(45 128 99 / 12%);
}

.connection-label,
.connected-printer strong {
  display: block;
}

.connection-label {
  margin-bottom: 0.18rem;
  color: #35705c;
  font-size: 0.64rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.connected-printer strong {
  color: var(--tickets-ink);
  font-size: 0.76rem;
  line-height: 1.35;
}

.printer-form {
  display: grid;
  gap: 0.75rem;
}

.field-label {
  color: var(--tickets-ink);
  font-size: 0.75rem;
  font-weight: 700;
}

.printer-select {
  width: 100%;
}

.demo-note {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  margin: 1rem 0 0;
  color: #858d99;
  font-size: 0.68rem;
  line-height: 1.45;
}

.demo-note svg {
  width: 0.8rem;
  height: 0.8rem;
  flex: 0 0 auto;
  margin-top: 0.1rem;
}
</style>
