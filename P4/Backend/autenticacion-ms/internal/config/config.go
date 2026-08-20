package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	Port        string
	DatabaseURL string
	JWTSecret   string
	JWTDuration time.Duration
}

func Load() (Config, error) {
	durationMinutes, err := strconv.Atoi(valueOrDefault("JWT_DURATION_MINUTES", "60"))
	if err != nil || durationMinutes <= 0 {
		return Config{}, fmt.Errorf("JWT_DURATION_MINUTES debe ser un entero positivo")
	}
	config := Config{
		Port: valueOrDefault("PORT", "8081"), DatabaseURL: os.Getenv("DATABASE_URL"),
		JWTSecret: os.Getenv("JWT_SECRET"), JWTDuration: time.Duration(durationMinutes) * time.Minute,
	}
	if config.DatabaseURL == "" || len(config.JWTSecret) < 32 {
		return Config{}, fmt.Errorf("DATABASE_URL y JWT_SECRET (minimo 32 caracteres) son obligatorios")
	}
	return config, nil
}

func valueOrDefault(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
