<script setup lang="ts">
import { useAuth } from '@/shared/auth'

definePageMeta({ middleware: 'auth' })

const { user } = useAuth()

await navigateTo(user.value?.role === 'approver' ? '/recepcion' : '/user', { replace: true })
</script>
