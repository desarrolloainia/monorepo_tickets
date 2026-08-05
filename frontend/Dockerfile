FROM node:24-alpine AS dependencies

ENV PNPM_HOME="/pnpm" \
    PATH="/pnpm:${PATH}"

WORKDIR /app

RUN corepack enable \
    && corepack prepare pnpm@11.12.0 --activate

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm install --frozen-lockfile


FROM dependencies AS builder

COPY . .

RUN pnpm build


FROM node:24-bookworm-slim AS runtime

ENV NODE_ENV="production" \
    HOST="0.0.0.0" \
    PORT="3000" \
    NITRO_HOST="0.0.0.0" \
    NITRO_PORT="3000"

WORKDIR /app

COPY --from=builder \
    --chown=65532:65532 \
    /app/.output \
    /app/.output

USER 65532:65532

EXPOSE 3000

CMD ["node", "/app/.output/server/index.mjs"]
