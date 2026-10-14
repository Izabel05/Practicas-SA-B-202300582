FROM golang:1.26-alpine AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /api-gateway .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /api-gateway /api-gateway
EXPOSE 8080
ENTRYPOINT ["/api-gateway"]
