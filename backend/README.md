# Backend

API FastAPI del sistema de tickets. Contiene autenticacion Microsoft, usuarios y roles, solicitudes, aprobacion, emision, persistencia PostgreSQL y renderizado A4.

## Documentacion

- [Referencia completa de modulos](../docs/backend.md)
- [Arquitectura del sistema](../docs/architecture.md)
- [Guia general](../README.md)

## Inicio rapido

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --app-dir src --reload
```

La configuracion se copia desde `.env.example`. La API queda en `http://localhost:8000` y Swagger en `http://localhost:8000/docs`.

## Calidad

```bash
uv run pytest
uv run ruff check src
uv run basedpyright
```
