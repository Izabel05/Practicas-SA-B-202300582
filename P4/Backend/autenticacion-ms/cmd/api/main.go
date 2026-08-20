package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"biblioteca/autenticacion-ms/internal/config"
	"biblioteca/autenticacion-ms/internal/controller"
	"biblioteca/autenticacion-ms/internal/repository"
	"biblioteca/autenticacion-ms/internal/routes"
	"biblioteca/autenticacion-ms/internal/security"
	"biblioteca/autenticacion-ms/internal/service"
	"github.com/jackc/pgx/v5/pgxpool"
	"golang.org/x/crypto/bcrypt"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	if err := run(logger); err != nil {
		logger.Error("servicio finalizado", "error", err)
		os.Exit(1)
	}
}

func run(logger *slog.Logger) error {
	cfg, err := config.Load()
	if err != nil {
		return err
	}
	pool, err := pgxpool.New(context.Background(), cfg.DatabaseURL)
	if err != nil {
		return err
	}
	defer pool.Close()
	if err := pool.Ping(context.Background()); err != nil {
		return err
	}

	users := repository.NewUserRepository(pool)
	hasher := security.NewBcryptHasher(bcrypt.DefaultCost)
	tokens := security.NewJWTGenerator(cfg.JWTSecret, cfg.JWTDuration)
	authService := service.NewAuthService(users, hasher, tokens)
	authController := controller.NewAuthController(authService, logger)

	server := &http.Server{
		Addr: ":" + cfg.Port, Handler: routes.New(authController, logger),
		ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second,
		WriteTimeout: 10 * time.Second, IdleTimeout: 60 * time.Second,
	}

	serverErrors := make(chan error, 1)
	go func() {
		logger.Info("autenticacion-ms iniciado", "puerto", cfg.Port)
		serverErrors <- server.ListenAndServe()
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	select {
	case <-stop:
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		return server.Shutdown(ctx)
	case err := <-serverErrors:
		return err
	}
}
