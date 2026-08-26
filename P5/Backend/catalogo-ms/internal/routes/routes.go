package routes

import (
	"log/slog"
	"net/http"
	"time"

	"biblioteca/catalogo-ms/internal/controller"
)

func New(graphqlController *controller.GraphQLController, restController *controller.RestController, logger *slog.Logger) http.Handler {
	mux := http.NewServeMux()
	mux.Handle("POST /graphql", graphqlController)
	mux.HandleFunc("GET /health", restController.Health)
	mux.HandleFunc("PATCH /api/v1/ejemplares/{id}/estado", restController.UpdateCopyStatus)
	return loggingMiddleware(logger, mux)
}

func loggingMiddleware(logger *slog.Logger, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		started := time.Now()
		next.ServeHTTP(w, r)
		logger.Info("peticion HTTP", "metodo", r.Method, "ruta", r.URL.Path, "duracion", time.Since(started))
	})
}
