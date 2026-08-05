<script setup lang="ts">
import { shallowRef } from 'vue'

import { useBlockedUsers } from '../model/use-blocked-users'

const {
  block,
  blockedUsers,
  error,
  hasSearched,
  isLoading,
  mutationError,
  notice,
  pendingIds,
  query,
  refresh,
  results,
  search,
  searchError,
  searchedQuery,
  searching,
  unblock
} = useBlockedUsers()

const confirmingId = shallowRef<string | null>(null)

async function confirmBlock(user: Parameters<typeof block>[0]) {
  await block(user)
  confirmingId.value = null
}
</script>

<template>
  <UContainer class="blocked-page">
    <header class="page-header">
      <p class="eyebrow">Recursos Humanos</p>
      <h1>Control de acceso</h1>
      <p>Busca una persona en Microsoft 365 y gestiona su acceso al portal.</p>
    </header>

    <form class="search-card" role="search" @submit.prevent="search">
      <label for="directory-search">Nombre o correo corporativo</label>
      <div class="search-row">
        <input
          id="directory-search"
          v-model="query"
          type="search"
          autocomplete="off"
          placeholder="Ej. Ana García o ana@empresa.es"
          aria-describedby="search-hint"
        >
        <UButton type="submit" icon="i-lucide-search" label="Buscar" :loading="searching" />
      </div>
      <p id="search-hint" class="search-hint">Los resultados se actualizan mientras escribes.</p>
      <p v-if="searchError" class="error-text" role="alert">{{ searchError }}</p>
    </form>

    <p v-if="mutationError" class="notice notice-error" role="alert">{{ mutationError }}</p>
    <p v-else-if="notice" class="notice notice-success" role="status">{{ notice }}</p>

    <section
      v-if="hasSearched && !searchError"
      class="panel"
      aria-labelledby="results-title"
      :aria-busy="searching"
    >
      <header class="panel-header">
        <div>
          <h2 id="results-title">Resultados</h2>
          <p v-if="searchedQuery">Coincidencias para “{{ searchedQuery }}”</p>
        </div>
        <span>{{ searching ? '…' : results.length }}</span>
      </header>
      <div v-if="searching && results.length === 0" class="loading-list" aria-label="Buscando usuarios">
        <USkeleton v-for="index in 3" :key="index" class="h-16 w-full" />
      </div>
      <div v-else-if="results.length === 0" class="empty-state">
        <UIcon name="i-lucide-search-x" aria-hidden="true" />
        <p>No hay coincidencias en Microsoft 365.</p>
      </div>
      <ul v-else class="user-list">
        <li
          v-for="user in results"
          :key="user.microsoft_oid"
          :class="{ 'is-confirming': confirmingId === user.microsoft_oid }"
        >
          <div class="user-summary">
            <span class="user-avatar" aria-hidden="true">{{ user.name.charAt(0).toUpperCase() }}</span>
            <span class="user-identity">
              <strong>{{ user.name }}</strong>
              <span>{{ user.email ?? 'Sin correo disponible' }}</span>
            </span>
          </div>
          <div v-if="confirmingId === user.microsoft_oid" class="confirm-actions" role="group" :aria-label="`Confirmar bloqueo de ${user.name}`">
            <span>¿Bloquear su acceso?</span>
            <UButton
              color="error"
              label="Confirmar"
              :loading="pendingIds.has(user.microsoft_oid)"
              @click="confirmBlock(user)"
            />
            <UButton color="neutral" variant="ghost" label="Cancelar" @click="confirmingId = null" />
          </div>
          <template v-else>
            <UButton
              v-if="!user.blocked"
              color="error"
              variant="soft"
              label="Bloquear"
              :aria-label="`Bloquear a ${user.name}`"
              @click="confirmingId = user.microsoft_oid"
            />
            <span v-else class="blocked-label">Bloqueado</span>
          </template>
        </li>
      </ul>
    </section>

    <section class="panel" aria-labelledby="blocked-title">
      <header class="panel-header">
        <div>
          <p class="eyebrow">Acceso denegado</p>
          <h2 id="blocked-title">Usuarios bloqueados</h2>
        </div>
        <span>{{ blockedUsers.length }}</span>
      </header>

      <div v-if="isLoading" class="loading-list" aria-label="Cargando usuarios bloqueados">
        <USkeleton v-for="index in 3" :key="index" class="h-16 w-full" />
      </div>
      <div v-else-if="error" class="empty-state" role="alert">
        <p>No se pudo cargar la lista.</p>
        <UButton color="neutral" variant="outline" label="Reintentar" @click="() => refresh()" />
      </div>
      <div v-else-if="blockedUsers.length === 0" class="empty-state">
        <UIcon name="i-lucide-shield-check" aria-hidden="true" />
        <p>No hay usuarios bloqueados.</p>
      </div>
      <ul v-else class="user-list">
        <li v-for="user in blockedUsers" :key="user.microsoft_oid">
          <div class="user-summary">
            <span class="user-avatar" aria-hidden="true">{{ user.name.charAt(0).toUpperCase() }}</span>
            <span class="user-identity">
              <strong>{{ user.name }}</strong>
              <span>{{ user.email ?? 'Sin correo disponible' }}</span>
            </span>
          </div>
          <UButton
            color="neutral"
            variant="outline"
            label="Desbloquear"
            :aria-label="`Desbloquear a ${user.name}`"
            :loading="pendingIds.has(user.microsoft_oid)"
            @click="unblock(user)"
          />
        </li>
      </ul>
    </section>
  </UContainer>
</template>

<style scoped>
.blocked-page {
  max-width: 64rem;
  padding-block: clamp(2.5rem, 6vw, 5rem);
}

.page-header {
  max-width: 44rem;
  margin-bottom: 2rem;
}

.eyebrow {
  margin: 0 0 0.55rem;
  color: #2d6654;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
  font-size: clamp(2.6rem, 6vw, 4.6rem);
  font-weight: 500;
  letter-spacing: -0.06em;
  line-height: 0.95;
}

.page-header > p:last-child {
  margin: 1rem 0 0;
  color: var(--tickets-muted);
  line-height: 1.6;
}

.search-card,
.panel {
  border: 1px solid var(--tickets-line);
  border-radius: 1rem;
  background: var(--tickets-paper);
}

.search-card {
  display: grid;
  gap: 0.55rem;
  padding: clamp(1.25rem, 3vw, 1.75rem);
}

.search-card label {
  font-size: 0.76rem;
  font-weight: 750;
}

.search-hint,
.panel-header p {
  margin: 0;
  color: var(--tickets-muted);
  font-size: 0.76rem;
}

.search-row {
  display: flex;
  gap: 0.75rem;
}

.search-row input {
  min-width: 0;
  height: 2.75rem;
  flex: 1;
  padding-inline: 0.9rem;
  border: 1px solid #cfd5d1;
  border-radius: 0.7rem;
  background: #fff;
  color: var(--tickets-ink);
  font: inherit;
}

.search-row input:focus-visible {
  outline: 3px solid rgb(45 102 84 / 28%);
  outline-offset: 2px;
}

.error-text,
.notice {
  margin: 0;
  font-size: 0.8rem;
}

.error-text {
  color: #a13333;
}

.notice {
  margin-top: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 0.7rem;
}

.notice-success {
  background: #e7efe9;
  color: #285b4b;
}

.notice-error {
  border: 1px solid #efcaca;
  background: #fff1f1;
  color: #8d2929;
}

.panel {
  overflow: hidden;
  margin-top: 1.25rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--tickets-line);
}

.panel-header h2 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
}

.panel-header > span,
.blocked-label {
  border-radius: 999px;
  background: #e7ece7;
  color: #2d6654;
  font-size: 0.72rem;
  font-weight: 750;
}

.panel-header > span {
  min-width: 1.75rem;
  padding: 0.25rem 0.5rem;
  text-align: center;
}

.user-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.user-list li {
  display: flex;
  min-height: 4.75rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1.5rem;
  border-bottom: 1px solid var(--tickets-line);
}

.user-list li:last-child {
  border-bottom: 0;
}

.user-summary,
.user-identity {
  display: flex;
  min-width: 0;
}

.user-summary {
  align-items: center;
  gap: 0.75rem;
}

.user-identity {
  flex-direction: column;
  gap: 0.2rem;
}

.user-avatar {
  display: grid;
  width: 2.25rem;
  height: 2.25rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: #e7ece7;
  color: #2d6654;
  font-size: 0.78rem;
  font-weight: 800;
}

.user-list strong,
.user-list span {
  overflow-wrap: anywhere;
}

.user-list strong {
  font-size: 0.88rem;
}

.user-identity > span {
  color: var(--tickets-muted);
  font-size: 0.78rem;
}

.is-confirming {
  background: #fff8f1;
}

.confirm-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confirm-actions > span {
  color: #8d2929;
  font-size: 0.78rem;
  font-weight: 700;
}

.blocked-label {
  padding: 0.45rem 0.7rem;
}

.loading-list {
  display: grid;
  gap: 0.75rem;
  padding: 1.25rem;
}

.empty-state {
  display: grid;
  min-height: 10rem;
  place-items: center;
  align-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--tickets-muted);
  text-align: center;
}

.empty-state p {
  margin: 0;
}

.empty-state svg {
  width: 1.75rem;
  height: 1.75rem;
}

@media (max-width: 560px) {
  .search-row,
  .user-list li {
    align-items: stretch;
    flex-direction: column;
  }

  .confirm-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .confirm-actions > span {
    grid-column: 1 / -1;
  }

  .search-row button,
  .user-list button {
    width: 100%;
    justify-content: center;
  }
}
</style>
