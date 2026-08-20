package routes

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"time"

	"biblioteca/autenticacion-ms/internal/controller"
)

func New(auth *controller.AuthController, logger *slog.Logger) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", auth.Health)
	mux.HandleFunc("POST /api/v1/auth/register", auth.Register)
	mux.HandleFunc("POST /api/v1/auth/login", auth.Login)
	return recoverMiddleware(logger, loggingMiddleware(logger, mux))
}

func loggingMiddleware(logger *slog.Logger, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		started := time.Now()
		next.ServeHTTP(w, r)
		logger.Info("peticion HTTP", "metodo", r.Method, "ruta", r.URL.Path, "duracion", time.Since(started))
	})
}

func recoverMiddleware(logger *slog.Logger, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if recovered := recover(); recovered != nil {
				logger.Error("panic recuperado", "error", recovered)
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusInternalServerError)
				_ = json.NewEncoder(w).Encode(map[string]any{
					"error": map[string]string{"codigo": "ERROR_INTERNO", "mensaje": "ocurrio un error inesperado"},
				})
			}
		}()
		next.ServeHTTP(w, r)
	})
}
