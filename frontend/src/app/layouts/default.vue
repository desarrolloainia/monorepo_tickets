<script setup lang="ts">
import { computed, shallowRef } from 'vue'

import { useAuth } from '@/shared/auth'

const { logout, user } = useAuth()
const mobileOpen = shallowRef(false)

const navigation = computed(() => {
  if (user.value?.role === 'accountant') {
    return [
      { label: 'Contabilidad', icon: 'i-lucide-calculator', to: '/contabilidad' },
      { label: 'Mis tickets', icon: 'i-lucide-ticket', to: '/user' }
    ]
  }
  if (user.value?.role === 'approver') {
    return [{ label: 'Recepción', icon: 'i-lucide-clipboard-check', to: '/recepcion' }]
  }

  const links = [{ label: 'Mis tickets', icon: 'i-lucide-ticket', to: '/user' }]
  if (user.value?.role === 'rrhh') {
    links.push(
      { label: 'Gasto', icon: 'i-lucide-wallet-cards', to: '/gasto' },
      { label: 'Control de acceso', icon: 'i-lucide-user-lock', to: '/bloqueos' }
    )
  }
  return links
})
</script>

<template>
  <div class="app-shell">
    <aside class="desktop-sidebar" aria-label="Barra lateral">
      <NuxtLink to="/" class="brand-link" aria-label="Tickets, inicio">
        <span class="brand-mark" aria-hidden="true">T</span>
        <span>Tickets</span>
      </NuxtLink>

      <nav class="sidebar-nav" aria-label="Navegación principal">
        <NuxtLink v-for="item in navigation" :key="item.to" :to="item.to" class="nav-link">
          <UIcon :name="item.icon" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <div v-if="user" class="sidebar-account">
        <span class="account-avatar" aria-hidden="true">{{ user.name.charAt(0).toUpperCase() }}</span>
        <span class="account-details">
          <strong>{{ user.name }}</strong>
          <span>{{ user.email }}</span>
        </span>
        <UButton
          color="neutral"
          variant="ghost"
          icon="i-lucide-log-out"
          aria-label="Cerrar sesión"
          @click="logout"
        />
      </div>
    </aside>

    <div class="content-shell">
      <header class="mobile-header">
        <NuxtLink to="/" class="brand-link" aria-label="Tickets, inicio">
          <span class="brand-mark" aria-hidden="true">T</span>
          <span>Tickets</span>
        </NuxtLink>

        <USlideover v-model:open="mobileOpen" side="left" title="Navegación">
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-lucide-menu"
            aria-label="Abrir navegación"
          />

          <template #body>
            <nav class="sidebar-nav mobile-nav" aria-label="Navegación principal">
              <NuxtLink
                v-for="item in navigation"
                :key="item.to"
                :to="item.to"
                class="nav-link"
                @click="mobileOpen = false"
              >
                <UIcon :name="item.icon" aria-hidden="true" />
                <span>{{ item.label }}</span>
              </NuxtLink>
            </nav>
          </template>

          <template v-if="user" #footer>
            <div class="mobile-account">
              <span class="account-details">
                <strong>{{ user.name }}</strong>
                <span>{{ user.email }}</span>
              </span>
              <UButton color="neutral" variant="outline" icon="i-lucide-log-out" label="Salir" @click="logout" />
            </div>
          </template>
        </USlideover>
      </header>

      <main>
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  min-height: 100vh;
  grid-template-columns: 17rem minmax(0, 1fr);
  background:
    radial-gradient(circle at 8% 0%, rgb(255 255 255 / 72%), transparent 30rem),
    var(--tickets-canvas);
}

.desktop-sidebar {
  position: sticky;
  top: 0;
  display: flex;
  height: 100vh;
  height: 100dvh;
  flex-direction: column;
  padding: 1.5rem 1rem;
  border-right: 1px solid rgb(20 33 61 / 10%);
  background: rgb(251 250 247 / 92%);
  backdrop-filter: blur(14px);
}

.brand-link,
.nav-link,
.sidebar-account,
.mobile-account {
  display: flex;
  align-items: center;
}

.brand-link {
  gap: 0.7rem;
  padding-inline: 0.45rem;
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

.sidebar-nav {
  display: grid;
  gap: 0.3rem;
  margin-top: 2.5rem;
}

.nav-link {
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.7rem;
  color: var(--tickets-muted);
  font-size: 0.84rem;
  font-weight: 700;
  text-decoration: none;
  transition: background-color 160ms ease, color 160ms ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: #e7ece7;
  color: #2d6654;
}

.nav-link:focus-visible,
.brand-link:focus-visible {
  outline: 3px solid rgb(45 102 84 / 28%);
  outline-offset: 2px;
}

.nav-link svg {
  width: 1.1rem;
  height: 1.1rem;
  flex: 0 0 auto;
}

.sidebar-account {
  gap: 0.65rem;
  margin-top: auto;
  padding: 0.85rem 0.45rem 0;
  border-top: 1px solid var(--tickets-line);
}

.account-avatar {
  display: grid;
  width: 2rem;
  height: 2rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 50%;
  background: #e7ece7;
  color: #2d6654;
  font-size: 0.75rem;
  font-weight: 800;
}

.account-details {
  display: grid;
  min-width: 0;
  flex: 1;
  gap: 0.1rem;
}

.account-details strong,
.account-details span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.account-details strong {
  font-size: 0.78rem;
}

.account-details span {
  color: var(--tickets-muted);
  font-size: 0.68rem;
}

.content-shell,
main {
  min-width: 0;
}

.mobile-header {
  display: none;
}

.mobile-nav {
  margin-top: 0;
}

.mobile-account {
  width: 100%;
  gap: 1rem;
}

@media (max-width: 800px) {
  .app-shell {
    display: block;
  }

  .desktop-sidebar {
    display: none;
  }

  .mobile-header {
    position: sticky;
    z-index: 20;
    top: 0;
    display: flex;
    min-height: 4rem;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgb(20 33 61 / 10%);
    background: rgb(251 250 247 / 92%);
    backdrop-filter: blur(14px);
  }
}
</style>
