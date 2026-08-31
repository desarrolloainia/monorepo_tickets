<script setup lang="ts">
import { useAuth } from '@/shared/auth'

const { loaded, login, refresh, user } = useAuth()
const blocked = useRoute().query.error === 'blocked'

onMounted(async () => {
  await refresh()
  if (user.value) await navigateTo('/')
})
</script>

<template>
  <main class="login-page">
    <section class="brand-panel" aria-label="Portal de tickets de comida">
      <div class="brand-content">
        <div class="brand-lockup">
          <div class="brand-mark" aria-hidden="true">T</div>

          <div>
            <p class="brand-name">Tickets</p>
            <p class="brand-type">Portal interno</p>
          </div>
        </div>

        <div class="brand-copy">
          <p class="eyebrow">Gestión de tickets de comida</p>

          <h1 class="brand-title">
            Gestiona tus tickets de comida fácilmente.
          </h1>

          <p class="brand-description">
            Solicita, consulta y realiza el seguimiento de tus tickets de comida
            desde un único portal.
          </p>
        </div>
      </div>

      <p class="brand-footer">
        Acceso exclusivo para personal autorizado
      </p>
    </section>

    <section class="access-panel" aria-labelledby="login-title">
      <UColorModeButton
        class="color-mode-button"
        color="primary"
        variant="soft"
        aria-label="Cambiar tema de color"
      />

      <div class="access-card">
        <div class="mobile-lockup">
          <div class="mobile-mark" aria-hidden="true">T</div>
          <span>Tickets</span>
        </div>

        <div class="access-copy">
          <p class="eyebrow">Acceso seguro</p>

          <h2 id="login-title" class="access-title">
            Inicia sesión
          </h2>

          <p class="access-description">
            Accede al portal utilizando tu cuenta corporativa.
          </p>
        </div>

        <button
          class="microsoft-button"
          type="button"
          :disabled="!loaded"
          :aria-busy="!loaded"
          @click="login"
        >
          <span class="microsoft-logo" aria-hidden="true">
            <i class="microsoft-tile tile-red" />
            <i class="microsoft-tile tile-green" />
            <i class="microsoft-tile tile-blue" />
            <i class="microsoft-tile tile-yellow" />
          </span>

          <span>
            {{ loaded ? 'Continuar con Microsoft' : 'Comprobando acceso…' }}
          </span>
        </button>

        <p v-if="blocked" class="access-error" role="alert">
          Tu acceso al portal está bloqueado. Contacta con Recursos Humanos.
        </p>

        <p class="access-note">
          Utiliza tu cuenta corporativa de Microsoft.
        </p>
      </div>

      <p class="support-copy">
        ¿Necesitas acceso? Contacta con el equipo responsable.
      </p>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  grid-template-columns: minmax(0, 52fr) minmax(28rem, 48fr);
  background: var(--ui-bg);
  color: var(--ui-text-highlighted);
}

.brand-panel {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  justify-content: space-between;
  padding: 3rem clamp(2.5rem, 6vw, 7rem);
  background: var(--ui-bg-accented);
  color: var(--ui-text-highlighted);
}

.brand-content {
  display: grid;
  gap: clamp(5rem, 15vh, 10rem);
}

.brand-lockup,
.mobile-lockup {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-mark,
.mobile-mark {
  display: grid;
  width: 2.75rem;
  height: 2.75rem;
  place-items: center;
  border-radius: 0.625rem;
  background: color-mix(in srgb, var(--ui-primary) 12%, transparent);
  color: var(--ui-primary);
  font-size: 1.125rem;
  font-weight: 750;
  box-shadow: 0 4px 12px rgb(0 0 0 / 12%);
}

.brand-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.brand-type,
.brand-footer {
  margin: 0.125rem 0 0;
  color: var(--ui-text-muted);
  font-size: 0.8125rem;
}

.brand-copy {
  max-width: 36rem;
}

.eyebrow {
  margin: 0;
  color: var(--ui-text-muted);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.brand-copy .eyebrow {
  color: var(--ui-primary);
}

.brand-title,
.access-title {
  margin: 0.875rem 0 0;
  letter-spacing: -0.045em;
}

.brand-title {
  max-width: 35rem;
  font-size: clamp(2.75rem, 4.2vw, 4.5rem);
  font-weight: 650;
  line-height: 1.03;
  text-wrap: balance;
}

.brand-description {
  max-width: 30rem;
  margin: 1.5rem 0 0;
  color: var(--ui-text-toned);
  font-size: 1rem;
  line-height: 1.65;
}

.access-panel {
  position: relative;
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  justify-content: center;
  padding: 3rem clamp(2rem, 5vw, 6rem);
  background:
    radial-gradient(
      circle at top right,
      color-mix(in srgb, var(--ui-primary) 12%, transparent),
      transparent 32rem
    ),
    var(--ui-bg);
}

.color-mode-button {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
}

.access-card {
  width: 100%;
  max-width: 27rem;
  margin: auto;
  padding: clamp(2rem, 4vw, 2.75rem);
  border: 1px solid var(--ui-border);
  border-radius: 1rem;
  background: var(--ui-bg-elevated);
  box-shadow:
    0 1px 2px rgb(0 0 0 / 3%),
    0 16px 40px rgb(0 0 0 / 7%);
}

.mobile-lockup {
  display: none;
  margin-bottom: 3rem;
  color: var(--ui-text-highlighted);
  font-size: 1rem;
  font-weight: 700;
}

.mobile-mark {
  width: 2.25rem;
  height: 2.25rem;
  background: color-mix(in srgb, var(--ui-primary) 12%, transparent);
  color: var(--ui-primary);
  font-size: 0.9375rem;
}

.access-title {
  font-size: clamp(2rem, 3vw, 2.625rem);
  font-weight: 650;
  line-height: 1.05;
}

.access-description {
  margin: 1rem 0 0;
  color: var(--ui-text-muted);
  font-size: 1rem;
  line-height: 1.6;
}

.microsoft-button {
  display: flex;
  width: 100%;
  min-height: 3.25rem;
  align-items: center;
  justify-content: center;
  gap: 0.875rem;
  margin-top: 2.5rem;
  padding: 0.875rem 1rem;
  border: 1px solid var(--ui-primary);
  border-radius: 0.625rem;
  background: color-mix(in srgb, var(--ui-primary) 12%, transparent);
  color: var(--ui-primary);
  cursor: pointer;
  font: inherit;
  font-size: 0.9375rem;
  font-weight: 650;
  transition:
    transform 150ms ease,
    border-color 150ms ease,
    background-color 150ms ease,
    box-shadow 150ms ease;
}

.microsoft-button:hover:not(:disabled) {
  border-color: var(--ui-primary);
  background: color-mix(in srgb, var(--ui-primary) 12%, transparent);
  color: var(--ui-primary);
  box-shadow: 0 4px 12px rgb(0 0 0 / 8%);
  transform: translateY(-1px);
}

.microsoft-button:active:not(:disabled) {
  box-shadow: none;
  transform: translateY(0);
}

.microsoft-button:focus-visible {
  outline: 3px solid var(--ui-primary);
  outline-offset: 3px;
}

.microsoft-button:disabled {
  cursor: wait;
  opacity: 0.62;
}

.microsoft-logo {
  display: grid;
  width: 1rem;
  height: 1rem;
  flex: 0 0 auto;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.1rem;
}

.microsoft-tile {
  display: block;
}

.tile-red {
  background: #f35325;
}

.tile-green {
  background: #81bc06;
}

.tile-blue {
  background: #05a6f0;
}

.tile-yellow {
  background: #ffba08;
}

.access-note {
  margin: 1.25rem 0 0;
  color: var(--ui-text-muted);
  font-size: 0.8125rem;
  line-height: 1.55;
  text-align: center;
}

.access-error {
  margin: 1rem 0 0;
  padding: 0.8rem;
  border: 1px solid color-mix(in srgb, var(--ui-error) 35%, transparent);
  border-radius: 0.625rem;
  background: color-mix(in srgb, var(--ui-error) 12%, transparent);
  color: var(--ui-error);
  font-size: 0.8125rem;
  line-height: 1.5;
  text-align: center;
}

.support-copy {
  margin: 2rem 0 0;
  color: var(--ui-text-muted);
  font-size: 0.8125rem;
  text-align: center;
}

@media (max-width: 900px) {
  .login-page {
    grid-template-columns: minmax(0, 1fr) minmax(25rem, 1fr);
  }

  .brand-panel {
    padding-inline: 2.5rem;
  }
}

@media (max-width: 767px) {
  .login-page {
    display: block;
  }

  .brand-panel {
    display: none;
  }

  .access-panel {
    min-height: 100vh;
    padding: 1.5rem;
  }

  .color-mode-button {
    top: 1rem;
    right: 1rem;
  }

  .access-card {
    max-width: 28rem;
    padding: 2rem;
  }

  .mobile-lockup {
    display: flex;
  }

  .support-copy {
    margin-top: 1.5rem;
  }
}

@media (max-width: 420px) {
  .access-panel {
    padding: 1rem;
  }

  .access-card {
    padding: 1.5rem;
    border-radius: 0.875rem;
  }

  .mobile-lockup {
    margin-bottom: 2.5rem;
  }

  .microsoft-button {
    font-size: 0.875rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .microsoft-button {
    transition: none;
  }
}
</style>
