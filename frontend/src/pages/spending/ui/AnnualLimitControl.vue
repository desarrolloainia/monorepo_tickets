<script setup lang="ts">
import type { components } from '@/shared/api'

type AnnualLimit = components['schemas']['AnnualLimitDTO']
const config = useRuntimeConfig()
const headers = useRequestHeaders(['cookie'])
const options = { baseURL: config.public.apiBase, headers, credentials: 'include' as const }
const { data, error, refresh, status } = useAsyncData('annual-limit',
  () => $fetch<AnnualLimit>('/tickets/annual-limit', options))
const unlimited = ref(true)
const maximum = ref<number | string>(22)
const saving = ref(false)
const message = ref('')
watch(data, value => {
  if (value) {
    unlimited.value = value.cantidad_maxima === null
    maximum.value = value.cantidad_maxima ?? 22
  }
}, { immediate: true })
async function save() {
  message.value = ''
  const value = unlimited.value ? null : Number(maximum.value)
  if (value !== null && (!Number.isInteger(value) || value <= 0 || value > 2147483647)) {
    message.value = 'Introduce un entero positivo.'
    return
  }
  saving.value = true
  try {
    data.value = await $fetch<AnnualLimit>('/tickets/annual-limit', {
      ...options, method: 'PUT', body: { cantidad_maxima: value }
    })
    message.value = 'Máximo anual guardado.'
  } catch {
    message.value = 'No se pudo guardar el máximo anual.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="limit-card" aria-labelledby="annual-limit-title">
    <h2 id="annual-limit-title">Máximo anual por empleado</h2>
    <p>Cuenta las cantidades pendientes y aprobadas del año natural. Se mantiene en años posteriores hasta cambiarlo.</p>
    <p v-if="error" role="alert">No se pudo cargar el máximo. <button @click="() => refresh()">Reintentar</button></p>
    <form v-else-if="data" @submit.prevent="save">
      <fieldset :disabled="saving || status === 'pending'">
        <legend>Configuración vigente: {{ data.cantidad_maxima ?? 'Sin límite' }}</legend>
        <label><input v-model="unlimited" type="checkbox"> Sin límite</label>
        <label v-if="!unlimited">Cantidad máxima <input v-model="maximum" type="number" min="1" max="2147483647" step="1" required></label>
        <UButton type="submit" label="Guardar máximo" :loading="saving" />
      </fieldset>
      <small v-if="data.updated_at">Última modificación: {{ new Date(data.updated_at).toLocaleString('es-ES', { timeZone: 'Europe/Madrid' }) }}</small>
    </form>
    <p v-if="message" role="status">{{ message }}</p>
  </section>
</template>

<style scoped>
.limit-card { padding: 1.25rem; border: 1px solid var(--ui-border); border-radius: 1rem; margin-bottom: 1rem; }
fieldset { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem; border: 0; padding-block: 0.75rem; }
input[type="number"] { border: 1px solid var(--ui-border); padding: 0.5rem; border-radius: 0.5rem; max-width: 10rem; }
p, small { color: var(--ui-text-muted); }
</style>
