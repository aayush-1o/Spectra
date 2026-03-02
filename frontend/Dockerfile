# Spectra Frontend — Multi-Stage Dockerfile
# Phase 5 optimisation: Vite build runs in Node stage; only the
# compiled /dist is shipped into an nginx:alpine runtime image.
#
# Final image ≈ 25MB (versus ~500MB with node_modules included).

# ── Stage 1: build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy manifests first — npm ci is cached until package-lock.json changes
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copy source and build
COPY . .
RUN npm run build


# ── Stage 2: serve ────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

# Remove default nginx placeholder
RUN rm -rf /usr/share/nginx/html/*

# Copy compiled assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx config: enable HTML5 history-mode routing (React Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
