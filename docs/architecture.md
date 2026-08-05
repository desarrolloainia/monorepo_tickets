# Arquitectura del sistema

## Objetivo

El sistema separa la experiencia web de las reglas de negocio. Nuxt presenta dos portales segun el rol; FastAPI autentica, autoriza y ejecuta los casos de uso; PostgreSQL conserva el estado y garantiza la unicidad de los codigos.

## Contexto

```mermaid
flowchart LR
    Employee[Empleado] -->|Solicita y previsualiza| System[Sistema de tickets]
    Approver[Recepcion] -->|Aprueba e imprime| System
    System -->|OAuth 2.0| Microsoft[Microsoft Identity Platform]
    Approver -->|Dialogo de Chrome| Printer[Impresora de Windows]
```

## Contenedores

```mermaid
flowchart TB
    subgraph Client[Equipo del usuario]
        Browser[Chrome]
        Nuxt[Nuxt 4 / Vue 3]
        PrintDialog[Dialogo nativo de impresion]
    end

    subgraph Server[Servidor de aplicacion]
        FastAPI[FastAPI]
        Jinja[Jinja2 + plantilla A4]
    end

    DB[(PostgreSQL)]
    Entra[Microsoft Entra ID]
    Graph[Microsoft Graph]
    CDN[JsBarcode en jsDelivr]

    Browser --> Nuxt
    Nuxt -->|JSON y cookie HttpOnly| FastAPI
    FastAPI --> DB
    FastAPI --> Entra
    FastAPI -->|User.Read.All| Graph
    FastAPI --> Jinja
    Jinja -->|HTML| Browser
    Browser --> CDN
    Browser --> PrintDialog
```

## Responsabilidades

| Capa | Responsabilidad | No debe decidir |
|---|---|---|
| Nuxt | Rutas, formularios, modales, paginacion, mensajes y navegacion | Permisos finales, codigos o transacciones |
| FastAPI API | Contrato HTTP, autenticacion, autorizacion y traduccion de errores | Detalles visuales de las paginas Nuxt |
| Aplicacion | Casos de uso y orden de operaciones | SQL o componentes Vue |
| Dominio | Entidades, estados y puertos | FastAPI, salvo el puerto HTML actual |
| Infraestructura | SQLAlchemy, MSAL, JWT, Jinja2 y PostgreSQL | Flujos de interfaz |
| PostgreSQL | Persistencia, relaciones, unicidad y asignacion atomica de secuencias | Presentacion |

## Dependencias internas

```mermaid
flowchart LR
    UI[Nuxt pages/ui] --> Models[Nuxt pages/model]
    Models --> APIs[Nuxt pages/api]
    APIs --> HTTP[FastAPI routers]
    UI --> Shared[Nuxt shared]
    Models --> Shared

    HTTP --> UseCases[Application use cases]
    HTTP --> Dependencies[Auth dependencies]
    UseCases --> Ports[Domain ports]
    UseCases --> Entities[Domain entities]
    Dependencies --> UoW[UnitOfWork]
    UoW --> Repositories[SQLAlchemy repositories]
    Repositories --> PostgreSQL[(PostgreSQL)]
    UseCases --> PrinterPort[TicketPrinter]
    PrinterPort --> HtmlPrinter[HtmlTicketPrinter]
```

El frontend sigue una variante pequena de Feature-Sliced Design: `app` compone, `pages` contiene funcionalidades y `shared` contiene capacidades transversales. El backend agrupa por modulo y dentro de cada modulo separa API, aplicacion, dominio e infraestructura.

## Autenticacion y autorizacion

```mermaid
sequenceDiagram
    actor Browser
    participant API as Auth Router
    participant Microsoft
    participant Users as User Repository
    participant JWT as TokenService

    Browser->>API: GET /auth/microsoft/login
    API-->>Browser: 302 Microsoft + cookie oauth_state
    Browser->>Microsoft: Autorizacion
    Microsoft-->>Browser: Callback con code y state
    Browser->>API: GET /auth/microsoft/callback
    API->>Microsoft: Intercambia code
    Microsoft-->>API: id_token_claims
    API->>Users: Crea o sincroniza usuario
    API->>JWT: Firma token interno HS256
    API-->>Browser: 302 frontend + cookie access_token HttpOnly
```

El JWT solo contiene el ID del usuario. Cada peticion protegida vuelve a consultar PostgreSQL, por lo que un cambio de rol o una eliminacion se aplica inmediatamente.

RRHH puede bloquear una identidad del directorio por su OID estable. El callback OAuth y
`current_user` consultan la tabla local de bloqueos, por lo que no se crea una nueva sesion y las
sesiones existentes dejan de acceder sin depender de Graph. El bloqueo conserva usuarios,
historial y solicitudes pendientes.

```mermaid
flowchart TD
    Request[Peticion protegida] --> Cookie{Cookie access_token?}
    Cookie -->|No| Unauthorized[401]
    Cookie -->|Si| Decode[Verificar firma, exp, iss y aud]
    Decode -->|Invalido| Unauthorized
    Decode --> User[Buscar usuario actual]
    User -->|No existe| Unauthorized
    User --> Role{Endpoint de aprobador?}
    Role -->|No| Endpoint[Ejecutar endpoint]
    Role -->|Si y role=approver| Endpoint
    Role -->|Si y otro rol| Forbidden[403]
```

## Ciclo de una solicitud

```mermaid
stateDiagram-v2
    [*] --> pending: Empleado crea solicitud
    pending --> approved: Recepcion aprueba
    approved --> [*]
    rejected: Modelado, sin flujo actual
```

Cantidades aceptadas por la API: 11 o 22. La restriccion vive en el DTO de entrada, no en la base de datos.

## Creacion

```mermaid
sequenceDiagram
    actor Employee as Empleado
    participant UI as TicketRequestForm
    participant Model as useTicketRequests
    participant API as POST /tickets/
    participant App as CreateTicketRequest
    participant DB as PostgreSQL

    Employee->>UI: Selecciona 11 o 22
    UI->>Model: submit
    Model->>API: cantidad
    API->>App: create(cantidad, user.id)
    App->>DB: INSERT pending
    App->>DB: COMMIT
    API-->>Model: TicketRequestDTO
    Model->>UI: Inserta solicitud en historial
```

## Aprobacion y emision

```mermaid
sequenceDiagram
    actor Approver as Recepcion
    participant API as POST /tickets/{id}/approve
    participant App as ApproveTicketRequest
    participant Repo as TicketRepository
    participant DB as PostgreSQL

    Approver->>API: Confirmar aprobacion
    API->>App: approve(id, approver.id)
    App->>Repo: find_by_id(for_update=true)
    Repo->>DB: SELECT FOR UPDATE
    App->>Repo: current_price()
    alt Precio configurado
        Repo-->>App: Ultimo precio
    else Tabla vacia
        App->>App: Usar 5.50 temporalmente
    end
    loop Por cada ticket
        App->>DB: UPSERT contador YYMM y RETURNING
        App->>App: Crear codigo YYMM-NNNNNN
    end
    App->>DB: UPDATE solicitud + INSERT tickets emitidos
    App->>DB: COMMIT
    API-->>Approver: Solicitud approved
```

El bloqueo de fila evita aprobar dos veces la misma solicitud. El `UPSERT` del contador evita repetir secuencias cuando se aprueban solicitudes concurrentemente.

## Previsualizacion e impresion

```mermaid
sequenceDiagram
    actor Requester
    participant Web as Nuxt
    participant API as GET /tickets/{id}/print
    participant App as PrintTicketRequest
    participant Template as HTML A4
    participant Chrome

    Requester->>Web: Abre documento
    Web->>API: Cookie de sesion
    API->>App: render(id, current_user)
    App->>App: Autorizar propietario o approver
    App->>Template: Tickets en grupos de 11
    Template-->>Chrome: A4 3x4 + JsBarcode
    Chrome->>Chrome: Inicializar CODE128
    alt Rol user
        Chrome-->>Web: Mostrar en iframe fullscreen
    else Rol approver
        Chrome->>Chrome: window.print()
    end
```

La celda 12 de cada hoja se reserva para firma. Por eso 11 tickets producen una hoja y 22 producen dos.

## Modelo de datos

```mermaid
erDiagram
    USERS {
        UUID id PK
        string microsoft_oid UK
        string email
        string name
        string role
        datetime created_at
        datetime updated_at
    }

    TICKET_REQUESTS {
        UUID id PK
        int cantidad
        UUID created_by_id FK
        datetime fecha_creacion
        string status
        UUID approved_by_id FK
        datetime approved_at
    }

    ISSUED_TICKETS {
        UUID id PK
        UUID ticket_request_id FK
        string codigo UK
        datetime fecha_emision
        decimal precio_unitario
    }

    TICKET_CODE_COUNTERS {
        string period PK
        int last_sequence
    }

    TICKET_PRICE_CONFIGURATIONS {
        UUID id PK
        decimal precio_unitario
        UUID updated_by_id FK
        datetime updated_at
    }

    BLOCKED_USERS {
        string microsoft_oid PK
        string email
        string name
        datetime blocked_at
    }

    USERS ||--o{ TICKET_REQUESTS : creates
    USERS |o--o{ TICKET_REQUESTS : approves
    USERS ||--o{ TICKET_PRICE_CONFIGURATIONS : updates
    TICKET_REQUESTS ||--o{ ISSUED_TICKETS : contains
```

El precio se copia al ticket emitido. Un cambio posterior de tarifa no altera tickets historicos.

## Rutas y roles

```mermaid
flowchart TD
    Root["/"] --> Role{Rol autenticado}
    Role -->|user| UserRoute["/user"]
    Role -->|approver| ReceptionRoute["/recepcion"]
    Login["/login"] --> Microsoft[Microsoft OAuth]
    UserRoute --> Form[Solicitud]
    UserRoute --> History[Historial y previsualizacion]
    ReceptionRoute --> Queue[Cola pendiente]
    Queue --> Approval[Modal de aprobacion]
    Approval --> NativePrint[Chrome / Windows]
```

| Ruta web | Rol | Finalidad |
|---|---|---|
| `/login` | Publica | Iniciar sesion |
| `/` | Autenticado | Redirigir segun rol |
| `/user` | `user` | Solicitar y consultar tickets propios |
| `/recepcion` | `approver` | Aprobar e imprimir solicitudes |

## Limites deliberados

- Chrome gestiona las impresoras; la web no las enumera ni confirma impresion fisica.
- No existe cola persistente de trabajos de impresion.
- La previsualizacion usa HTML A4, no un archivo PDF.
- El precio `5.50` es un respaldo temporal hasta implementar administracion.
- `rejected` existe en el modelo, pero no hay transicion implementada.
- JsBarcode se descarga de un CDN al abrir el documento.
- El CORS actual solo contempla el entorno local.

## Extension segura

Cuando se agregue funcionalidad, el punto de entrada recomendado es:

1. Definir o ampliar entidad y puerto del dominio.
2. Implementar un caso de uso pequeno.
3. Adaptar persistencia si hace falta.
4. Exponerlo en el router y OpenAPI.
5. Regenerar `frontend/src/shared/api/openapi.ts`.
6. Consumirlo desde `pages/*/api`, no directamente desde componentes.
7. Añadir la prueba minima que proteja la nueva regla.
