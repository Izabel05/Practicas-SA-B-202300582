FROM golang:1.23-alpine AS builder

WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/autenticacion-ms ./cmd/api

FROM alpine:3.21
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder /out/autenticacion-ms /usr/local/bin/autenticacion-ms
USER app
EXPOSE 8081
ENTRYPOINT ["/usr/local/bin/autenticacion-ms"]
