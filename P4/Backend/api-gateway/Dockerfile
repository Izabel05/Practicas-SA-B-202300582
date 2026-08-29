FROM alpine:3.21 AS config-builder

WORKDIR /config
COPY nginx.conf ./nginx.conf

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime

COPY --from=config-builder /config/nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080
