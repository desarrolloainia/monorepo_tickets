import { computed, shallowRef } from 'vue'

import { approveTicketRequest, fetchPendingTicketRequests } from '../api/tickets'

export async function usePendingTicketRequests() {
  const config = useRuntimeConfig()
  const requestHeaders = useRequestHeaders(['cookie'])
  const toast = useToast()
  const approvingIds = shallowRef(new Set<string>())

  const {
    data: requests,
    error: loadError,
    refresh,
    status
  } = await useAsyncData(
    'pending-ticket-requests',
    () => fetchPendingTicketRequests({
      baseURL: config.public.apiBase,
      headers: requestHeaders
    }),
    { default: () => [] }
  )

  const sortedRequests = computed(() => [...requests.value].sort(
    (left, right) => Date.parse(left.fecha_creacion) - Date.parse(right.fecha_creacion)
  ))

  async function approve(id: string) {
    if (approvingIds.value.has(id)) return

    approvingIds.value = new Set(approvingIds.value).add(id)

    try {
      await approveTicketRequest(config.public.apiBase, id)
      requests.value = requests.value.filter(request => request.id !== id)
      toast.add({
        title: 'Solicitud aprobada',
        description: 'El backend ha iniciado la impresión de los tickets.',
        icon: 'i-lucide-printer-check',
        color: 'success'
      })
    } catch (cause) {
      const statusCode = (cause as { statusCode?: number }).statusCode

      if (statusCode === 401) {
        await navigateTo('/login')
        return
      }

      toast.add({
        title: 'No se pudo aprobar',
        description: statusCode === 409
          ? 'Esta solicitud ya no está pendiente.'
          : 'Vuelve a intentarlo en unos segundos.',
        icon: 'i-lucide-circle-alert',
        color: 'error'
      })

      if (statusCode === 409 || statusCode === 404) await refresh()
    } finally {
      const nextIds = new Set(approvingIds.value)
      nextIds.delete(id)
      approvingIds.value = nextIds
    }
  }

  return {
    approve,
    approvingIds,
    isLoading: computed(() => status.value === 'pending'),
    loadError,
    refresh,
    sortedRequests
  }
}
