<script setup lang="ts">
import type { TicketAmount } from '../api/tickets'

const amount = defineModel<TicketAmount>({ required: true })

defineProps<{
  error: string | null
  submitting: boolean
  success: string | null
}>()

defineEmits<{
  submit: []
}>()

const quantities = [11, 22] as const
</script>

<template>
  <form class="request-form" @submit.prevent="$emit('submit')">
    <fieldset class="request-fieldset" :disabled="submitting">
      <legend class="request-title">Nueva solicitud</legend>
      <p class="request-copy">Selecciona el número de tickets que necesitas.</p>

      <div class="quantity-grid">
        <label
          v-for="quantity in quantities"
          :key="quantity"
          class="quantity-option"
          :class="{ 'quantity-option--selected': amount === quantity }"
        >
          <input v-model="amount" class="sr-only" type="radio" name="cantidad" :value="quantity">
          <span class="quantity-number">{{ quantity }}</span>
          <span class="quantity-label">tickets</span>
          <UIcon
            v-if="amount === quantity"
            name="i-lucide-check"
            class="quantity-check"
            aria-hidden="true"
          />
        </label>
      </div>

      <button class="submit-button" type="submit" :disabled="submitting">
        <UIcon
          :name="submitting ? 'i-lucide-loader-circle' : 'i-lucide-arrow-right'"
          class="submit-icon"
          :class="{ 'submit-icon--spinning': submitting }"
          aria-hidden="true"
        />
        {{ submitting ? 'Enviando solicitud…' : 'Enviar solicitud' }}
      </button>

      <p v-if="error" class="form-message form-message--error" role="alert">{{ error }}</p>
      <p v-else-if="success" class="form-message form-message--success" role="status">{{ success }}</p>
    </fieldset>
  </form>
</template>

<style scoped>
.request-form {
  padding: clamp(1.4rem, 3vw, 2rem);
  border: 1px solid var(--tickets-line);
  border-radius: 1.1rem;
  background: var(--tickets-paper);
  box-shadow: 0 1rem 3rem rgb(20 33 61 / 5%);
}

.request-fieldset {
  min-width: 0;
  margin: 0;
  padding: 0;
  border: 0;
}

.request-title {
  padding: 0;
  color: var(--tickets-ink);
  font-size: 1.05rem;
  font-weight: 750;
  letter-spacing: -0.025em;
}

.request-copy {
  margin: 0.5rem 0 1.5rem;
  color: var(--tickets-muted);
  font-size: 0.875rem;
  line-height: 1.55;
}

.quantity-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.quantity-option {
  position: relative;
  display: flex;
  min-height: 7.5rem;
  cursor: pointer;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1rem;
  border: 1px solid var(--tickets-line);
  border-radius: 0.8rem;
  background: #fff;
  transition: border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;
}

.quantity-option:hover {
  border-color: rgb(20 33 61 / 38%);
  transform: translateY(-1px);
}

.quantity-option:has(input:focus-visible) {
  outline: 3px solid rgb(45 102 84 / 26%);
  outline-offset: 2px;
}

.quantity-option--selected {
  border-color: #2d6654;
  box-shadow: inset 0 0 0 1px #2d6654;
}

.quantity-number {
  color: var(--tickets-ink);
  font-size: 2.25rem;
  font-variant-numeric: tabular-nums;
  font-weight: 720;
  letter-spacing: -0.06em;
  line-height: 1;
}

.quantity-label {
  margin-top: 0.35rem;
  color: var(--tickets-muted);
  font-size: 0.8rem;
}

.quantity-check {
  position: absolute;
  top: 0.8rem;
  right: 0.8rem;
  width: 1rem;
  height: 1rem;
  color: #2d6654;
}

.submit-button {
  display: flex;
  width: 100%;
  min-height: 3rem;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  margin-top: 1rem;
  border: 0;
  border-radius: 0.7rem;
  background: var(--tickets-ink);
  color: #fff;
  cursor: pointer;
  font: inherit;
  font-size: 0.875rem;
  font-weight: 700;
  transition: background-color 150ms ease, transform 150ms ease;
}

.submit-button:hover:not(:disabled) {
  background: #223354;
  transform: translateY(-1px);
}

.submit-button:focus-visible {
  outline: 3px solid rgb(45 102 84 / 30%);
  outline-offset: 3px;
}

.submit-button:disabled {
  cursor: wait;
  opacity: 0.7;
}

.submit-icon {
  width: 1rem;
  height: 1rem;
}

.submit-icon--spinning {
  animation: spin 800ms linear infinite;
}

.form-message {
  margin: 0.9rem 0 0;
  font-size: 0.8rem;
  line-height: 1.45;
}

.form-message--error {
  color: #a43c32;
}

.form-message--success {
  color: #2d6654;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .quantity-option,
  .submit-button {
    transition: none;
  }
}
</style>
