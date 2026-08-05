# Sistema de tickets de comida

Aplicacion interna para solicitar, aprobar, previsualizar e imprimir tickets de comida. El repositorio contiene un frontend Nuxt y una API FastAPI que comparten el contrato mediante OpenAPI.

## Funcionalidad

- Inicio de sesion con Microsoft OAuth.
- Busqueda de empleados con Microsoft Graph y bloqueo de acceso por RRHH.
- Roles `user` y `approver`.
- Solicitudes de 11 o 22 tickets.
- Cola de aprobacion ordenada por antiguedad.
- Codigos mensuales unicos con formato `YYMM-NNNNNN`.
- Previsualizacion A4 dentro de la web para empleados.
- Impresion desde recepcion mediante el dialogo nativo de Chrome.
- Historial y colas paginadas.

## Arquitectura

```mermaid
flowchart LR
    Browser[Chrome] --> Nuxt[Frontend Nuxt 4]
    Nuxt -->|HTTP + cookie| API[API FastAPI]
    API --> PostgreSQL[(PostgreSQL)]
    API --> Microsoft[Microsoft Identity Platform]
    API --> Template[Jinja2 A4]
    Template --> Browser
    Browser -->|Recepcion| Printer[Dialogo de impresion de Windows]
```

El frontend gestiona navegacion, estado de interfaz y presentacion. El backend es la autoridad sobre autenticacion, permisos, estados, precios, codigos y persistencia.

## Estructura

```text
.
|-- backend/          API FastAPI, dominio, persistencia y migraciones
|-- frontend/         Aplicacion Nuxt, paginas y componentes
|-- docs/             Arquitectura y referencia de modulos
|-- Makefile          Comandos comunes
`-- README.md
```

## Documentacion

- [Arquitectura del sistema](docs/architecture.md)
- [Modulos del backend](docs/backend.md)
- [Modulos del frontend](docs/frontend.md)
- [README del backend](backend/README.md)
- [README del frontend](frontend/README.md)

## Requisitos

- Python 3.14
- [uv](https://docs.astral.sh/uv/)
- Node.js compatible con Nuxt 4
- [pnpm](https://pnpm.io/)
- PostgreSQL
- Una aplicacion registrada en Microsoft Entra ID
- GNU Make opcional; debajo de cada comando se documenta su equivalente directo

## Instalacion

Desde la raiz:

```bash
make install
```

Equivalente sin Make:

```bash
pnpm --dir frontend install
uv sync --directory backend
```

## Configuracion

Crear los archivos locales a partir de los ejemplos:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

Backend, `backend/.env`:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tickets
MICROSOFT_TENANT_ID=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/microsoft/callback
AUTH_COOKIE_SECRET=
AUTH_SUCCESS_REDIRECT_URL=http://localhost:3000
AUTH_COOKIE_SECURE=false
```

Frontend, `frontend/.env`:

```dotenv
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

Notas:

- `AUTH_COOKIE_SECRET` debe ser un secreto aleatorio y no debe versionarse.
- En produccion se debe usar HTTPS y `AUTH_COOKIE_SECURE=true`.
- El origen frontend permitido por CORS esta actualmente fijado a `http://localhost:3000` en `backend/src/main.py`.
- Si no existe una configuracion de precio, el backend usa temporalmente `5.50` euros.
- La aplicacion de Entra necesita el permiso de aplicacion Microsoft Graph `User.Read.All`
  con consentimiento de administrador. Se reutilizan el tenant, client ID y secret existentes.

## Base de datos

Crear la base de datos y ejecutar la migracion:

```bash
uv run --directory backend alembic upgrade head
```

La migracion crea usuarios, solicitudes, tickets emitidos, contadores mensuales y configuraciones de precio.

## Desarrollo

Terminal 1, API:

```bash
make api
```

Terminal 2, frontend:

```bash
make dev
```

Servicios locales:

| Servicio | URL |
|---|---|
| Frontend | `http://localhost:3000` |
| API | `http://localhost:8000` |
| OpenAPI | `http://localhost:8000/docs` |

## Flujo principal

```mermaid
sequenceDiagram
    actor Employee as Empleado
    actor Approver as Recepcion
    participant Web as Nuxt
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Chrome

    Employee->>Web: Solicita 11 o 22 tickets
    Web->>API: POST /tickets/
    API->>DB: Guarda solicitud pending
    Approver->>Web: Abre cola de recepcion
    Web->>API: GET /tickets/pending
    Approver->>Web: Confirma aprobar e imprimir
    Web->>API: POST /tickets/{id}/approve
    API->>DB: Genera codigos y marca approved
    Web->>API: GET /tickets/{id}/print
    API-->>Chrome: HTML A4
    Chrome->>Chrome: Genera codigos de barras
    Chrome->>Approver: Dialogo nativo de impresion
    Employee->>Web: Previsualiza desde su historial
    Web->>API: GET /tickets/{id}/print
    API-->>Web: HTML A4 sin impresion automatica
```

## Calidad

Backend:

```bash
uv run --directory backend pytest
uv run --directory backend ruff check src
uv run --directory backend basedpyright
```

Frontend:

```bash
pnpm --dir frontend typecheck
pnpm --dir frontend lint:fsd
pnpm --dir frontend build
```

Regenerar tipos OpenAPI con la API en ejecucion:

```bash
pnpm --dir frontend generate:api
```

## Impresion

Una pagina web normal no puede enumerar ni seleccionar impresoras de Windows. El sistema delega esa operacion al dialogo nativo de Chrome:

- El empleado recibe una previsualizacion dentro de un modal, sin impresion automatica.
- El aprobador abre el mismo documento y Chrome muestra el dialogo de impresion.
- La aplicacion no puede confirmar que el papel haya salido ni impedir `Ctrl+P` en el navegador.

No existe agente local, extension de Chrome ni cola de trabajos de impresion.

## Estado actual

- El estado `rejected` esta modelado, pero no tiene caso de uso ni endpoint.
- La configuracion de precio esta modelada, pero no tiene API de administracion.
- Los codigos de barras dependen de JsBarcode servido por jsDelivr.
- Las pruebas frontend son comprobaciones de tipos, arquitectura y build; no hay suite de componentes o E2E.
