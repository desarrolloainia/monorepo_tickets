<template>
  <header class="border-b border-default">
    <UContainer class="flex h-16 items-center justify-between">
      <NuxtLink to="/" class="font-semibold text-highlighted">Tickets</NuxtLink>
      <nav class="flex gap-2" aria-label="Navegación principal">
        <UButton to="/" color="neutral" variant="ghost">Resumen</UButton>
        <UButton to="/tickets" color="neutral" variant="ghost">Tickets</UButton>
      </nav>
    </UContainer>
  </header>
</template>