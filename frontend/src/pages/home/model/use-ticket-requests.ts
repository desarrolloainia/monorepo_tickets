import { computed, shallowRef } from 'vue'

import { createTicketRequest, fetchTicketRequests, type TicketAmount } from '../api/tickets'

export function useTicketRequests() {
  const config = useRuntimeConfig()
  const router = useRouter()
  const requestHeaders = useRequestHeaders(['cookie'])
  const selectedAmount = shallowRef<TicketAmount>(11)
  const isSubmitting = shallowRef(false)
  const submitError = shallowRef<string | null>(null)
  const submitSuccess = shallowRef<string | null>(null)

  const {
    data: requests,
    error: loadError,
    refresh,
    status
  } = useAsyncData(
    'ticket-requests',
    () => fetchTicketRequests({
      baseURL: config.public.apiBase,
      headers: requestHeaders
    }),
    { default: () => [] }
  )

  const sortedRequests = computed(() => [...requests.value].sort(
    (left, right) => Date.parse(right.fecha_creacion) - Date.parse(left.fecha_creacion)
  ))

  async function submit() {
    if (isSubmitting.value) return

    isSubmitting.value = true
    submitError.value = null
    submitSuccess.value = null

    try {
      const created = await createTicketRequest(config.public.apiBase, selectedAmount.value)
      requests.value = [created, ...requests.value]
      submitSuccess.value = `Solicitud de ${created.cantidad} tickets enviada.`
    } catch (cause) {
      const statusCode = (cause as { statusCode?: number }).statusCode

      if (statusCode === 401) {
        await router.push('/login')
        return
      }

      submitError.value = statusCode === 422
        ? 'La cantidad debe ser 11 o 22.'
        : 'No se pudo enviar la solicitud. Inténtalo de nuevo.'
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    isLoading: computed(() => status.value === 'pending'),
    isSubmitting,
    loadError,
    printBaseUrl: config.public.apiBase,
    refresh,
    selectedAmount,
    sortedRequests,
    submit,
    submitError,
    submitSuccess
  }
}
