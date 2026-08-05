import { computed, shallowRef, watch } from 'vue'

import {
  fetchSpending,
  fetchTicketPrice,
  fetchUserSpending,
  updateTicketPrice
} from '../api/spending'
import type { UserSpending } from '../api/spending'

export function useSpending(managePrice = false) {
  const now = new Date()
  const scope = shallowRef<'month' | 'year'>('month')
  const month = shallowRef(now.getMonth() + 1)
  const year = shallowRef(now.getFullYear())
  const search = shallowRef('')
  const selectedUser = shallowRef<UserSpending>()
  const detail = shallowRef<Awaited<ReturnType<typeof fetchUserSpending>>>()
  const detailLoading = shallowRef(false)
  const detailError = shallowRef(false)
  const modalOpen = shallowRef(false)
  const config = useRuntimeConfig()
  const router = useRouter()
  const requestHeaders = useRequestHeaders(['cookie'])
  const period = computed(() => scope.value === 'year'
    ? String(year.value)
    : `${year.value}-${String(month.value).padStart(2, '0')}`)
  const apiOptions = { baseURL: config.public.apiBase, headers: requestHeaders }

  const { data: report, error, refresh, status } = useAsyncData(
    'spending-report',
    () => fetchSpending(period.value, apiOptions),
    { watch: [period] }
  )
  const {
    data: priceOverview,
    error: priceLoadError,
    refresh: refreshPrice,
    status: priceStatus
  } = useAsyncData(
    'ticket-price',
    () => managePrice ? fetchTicketPrice(apiOptions) : Promise.resolve(null)
  )
  const priceSaving = shallowRef(false)
  const priceMessage = shallowRef('')
  const priceMutationError = shallowRef('')

  const users = computed(() => {
    const query = search.value.trim().toLocaleLowerCase('es')
    if (!query) return report.value?.usuarios ?? []
    return (report.value?.usuarios ?? []).filter(user =>
      `${user.nombre} ${user.email}`.toLocaleLowerCase('es').includes(query)
    )
  })

  async function openDetail(user: UserSpending) {
    selectedUser.value = user
    detail.value = undefined
    detailError.value = false
    detailLoading.value = true
    modalOpen.value = true

    try {
      detail.value = await fetchUserSpending(user.user_id, period.value, apiOptions)
    } catch (cause) {
      if ((cause as { statusCode?: number }).statusCode === 401) return router.push('/login')
      detailError.value = true
    } finally {
      detailLoading.value = false
    }
  }

  watch(period, () => {
    modalOpen.value = false
  })

  async function savePrice(value: string) {
    priceMessage.value = ''
    priceMutationError.value = ''
    const normalized = value.trim().replace(',', '.')
    if (!/^\d+(?:\.\d{1,2})?$/.test(normalized) || Number(normalized) <= 0) {
      priceMutationError.value = 'Introduce un importe positivo con un máximo de dos decimales.'
      return false
    }

    priceSaving.value = true
    try {
      await updateTicketPrice(
        normalized,
        priceOverview.value?.current_configuration_id ?? null,
        apiOptions
      )
      await refreshPrice()
      priceMessage.value = 'La nueva tarifa se aplicará a las próximas aprobaciones.'
      return true
    } catch (cause) {
      const error = cause as { data?: { detail?: string }, statusCode?: number }
      if (error.statusCode === 401) {
        await router.push('/login')
        return false
      }
      priceMutationError.value = error.data?.detail ?? 'No se pudo actualizar la tarifa.'
      if (error.statusCode === 409) await refreshPrice()
      return false
    } finally {
      priceSaving.value = false
    }
  }

  return {
    detail,
    detailError,
    detailLoading,
    error,
    isLoading: computed(() => status.value === 'pending'),
    modalOpen,
    month,
    openDetail,
    period,
    priceLoadError,
    priceLoading: computed(() => priceStatus.value === 'pending'),
    priceMessage,
    priceMutationError,
    priceOverview,
    priceSaving,
    refresh,
    report,
    scope,
    search,
    savePrice,
    selectedUser,
    users,
    year
  }
}
