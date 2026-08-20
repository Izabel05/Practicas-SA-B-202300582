package repository

import (
	"context"

	"biblioteca/autenticacion-ms/internal/models"
)

type UserRepositoryContract interface {
	Create(ctx context.Context, user models.User, roleName string) (models.User, error)
	FindByEmail(ctx context.Context, email string) (models.User, error)
}

type PasswordHasher interface {
	Hash(password string) (string, error)
	Compare(hash, password string) error
}

type TokenGenerator interface {
	Generate(user models.User) (string, error)
}
