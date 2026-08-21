package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"biblioteca/catalogo-ms/internal/config"
	"biblioteca/catalogo-ms/internal/controller"
	"biblioteca/catalogo-ms/internal/repository"
	"biblioteca/catalogo-ms/internal/routes"
	"biblioteca/catalogo-ms/internal/service"
	"github.com/jackc/pgx/v5/pgxpool"
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

	catalogRepository := repository.NewPostgresCatalogRepository(pool)
	catalogService := service.NewCatalogService(catalogRepository)
	graphqlController, err := controller.NewGraphQLController(catalogService)
	if err != nil {
		return err
	}
	restController := controller.NewRestController(catalogService)
	server := &http.Server{
		Addr: ":" + cfg.Port, Handler: routes.New(graphqlController, restController, logger),
		ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second,
		WriteTimeout: 15 * time.Second, IdleTimeout: 60 * time.Second,
	}

	serverErrors := make(chan error, 1)
	go func() {
		logger.Info("catalogo-ms iniciado", "puerto", cfg.Port)
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
