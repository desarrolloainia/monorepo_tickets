# Frontend

Aplicacion Nuxt 4 del sistema de tickets. Incluye login Microsoft, portal del empleado, historial paginado, visor A4 y cola de recepcion con aprobacion e impresion.

## Documentacion

- [Referencia completa de modulos](../docs/frontend.md)
- [Arquitectura del sistema](../docs/architecture.md)
- [Guia general](../README.md)

## Inicio rapido

```bash
pnpm install
pnpm dev
```

La configuracion se copia desde `.env.example`. La web queda en `http://localhost:3000`.

## Calidad

```bash
pnpm typecheck
pnpm lint:fsd
pnpm build
```

Con la API en ejecucion, regenerar el contrato con:

```bash
pnpm generate:api
```
