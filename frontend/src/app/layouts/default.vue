<script setup lang="ts">
import { useAuth } from '@/shared/auth'

const { logout, user } = useAuth()
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <UContainer class="header-inner">
        <NuxtLink to="/" class="brand-link" aria-label="Tickets, inicio">
          <span class="brand-mark" aria-hidden="true">T</span>
          <span>Tickets</span>
        </NuxtLink>

        <div class="header-actions">
          <nav v-if="user?.role === 'approver'" aria-label="Navegación principal">
            <NuxtLink to="/recepcion" class="reception-link">
              <UIcon name="i-lucide-clipboard-check" aria-hidden="true" />
              <span>Recepción</span>
            </NuxtLink>
          </nav>

          <div v-if="user" class="account">
            <span class="account-name">{{ user.name }}</span>
            <UButton
              color="neutral"
              variant="ghost"
              icon="i-lucide-log-out"
              aria-label="Cerrar sesión"
              @click="logout"
            />
          </div>
        </div>
      </UContainer>
    </header>

    <main>
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 8% 0%, rgb(255 255 255 / 72%), transparent 30rem),
    var(--tickets-canvas);
}

.app-header {
  border-bottom: 1px solid rgb(20 33 61 / 10%);
  background: rgb(251 250 247 / 88%);
  backdrop-filter: blur(14px);
}

.header-inner {
  display: flex;
  min-height: 4.5rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand-link,
.account,
.header-actions,
.reception-link {
  display: flex;
  align-items: center;
}

.brand-link {
  gap: 0.7rem;
  color: var(--tickets-ink);
  font-size: 0.95rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 2rem;
  height: 2rem;
  place-items: center;
  border-radius: 0.5rem;
  background: var(--tickets-ink);
  color: #fff;
  font-size: 0.8rem;
}

.account {
  gap: 0.5rem;
}

.header-actions {
  gap: clamp(0.4rem, 2vw, 1.25rem);
}

.reception-link {
  gap: 0.45rem;
  padding: 0.55rem 0.75rem;
  border-radius: 0.65rem;
  color: var(--tickets-muted);
  font-size: 0.82rem;
  font-weight: 700;
  text-decoration: none;
  transition: background-color 160ms ease, color 160ms ease;
}

.reception-link:hover,
.reception-link.router-link-active {
  background: #e7ece7;
  color: #2d6654;
}

.reception-link:focus-visible {
  outline: 3px solid rgb(45 102 84 / 28%);
  outline-offset: 2px;
}

.reception-link svg {
  width: 1rem;
  height: 1rem;
}

.account-name {
  max-width: 14rem;
  overflow: hidden;
  color: var(--tickets-muted);
  font-size: 0.875rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 520px) {
  .account-name {
    display: none;
  }

  .reception-link {
    padding-inline: 0.6rem;
  }

  .reception-link span {
    display: none;
  }
}
</style>
