<script setup lang="ts">
import { useAuth } from '@/shared/auth'

definePageMeta({ middleware: 'auth' })

const { user } = useAuth()

const landingByRole = {
  accountant: '/contabilidad',
  approver: '/recepcion',
  rrhh: '/gasto',
  user: '/user'
} as const

await navigateTo(landingByRole[user.value!.role], { replace: true })
</script>
