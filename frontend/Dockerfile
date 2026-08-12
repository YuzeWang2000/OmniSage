FROM node:22-alpine AS build

WORKDIR /app
RUN corepack enable && corepack prepare pnpm@11.16.0 --activate

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
RUN pnpm install --frozen-lockfile

COPY index.html tsconfig.json tsconfig.app.json tsconfig.node.json vite.config.ts ./
COPY src ./src

ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN pnpm build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD wget -qO- http://127.0.0.1/healthz || exit 1
