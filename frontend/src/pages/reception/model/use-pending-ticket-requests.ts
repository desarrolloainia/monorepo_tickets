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

    // ponytail: Chrome's native dialog owns printer discovery and selection.
    const printWindow = window.open('about:blank', '_blank')
    if (!printWindow) {
      toast.add({
        title: 'Chrome bloqueó la impresión',
        description: 'Permite las ventanas emergentes para aprobar e imprimir.',
        icon: 'i-lucide-panels-top-left',
        color: 'warning'
      })
      return
    }
    printWindow.opener = null

    approvingIds.value = new Set(approvingIds.value).add(id)

    try {
      await approveTicketRequest(config.public.apiBase, id)
      requests.value = requests.value.filter(request => request.id !== id)
      printWindow.location.href = new URL(`/tickets/${id}/print`, config.public.apiBase).toString()
      toast.add({
        title: 'Solicitud aprobada',
        description: 'Elige la impresora en la pestaña que acaba de abrirse.',
        icon: 'i-lucide-printer-check',
        color: 'success'
      })
    } catch (cause) {
      printWindow.close()
      const error = cause as { data?: { detail?: string }, statusCode?: number }
      const statusCode = error.statusCode

      if (statusCode === 401) {
        await navigateTo('/login')
        return
      }

      toast.add({
        title: 'No se pudo aprobar',
        description: error.data?.detail ?? 'Vuelve a intentarlo en unos segundos.',
        icon: 'i-lucide-circle-alert',
        color: 'error'
      })

      if (statusCode === 400 || statusCode === 409 || statusCode === 404) await refresh()
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
