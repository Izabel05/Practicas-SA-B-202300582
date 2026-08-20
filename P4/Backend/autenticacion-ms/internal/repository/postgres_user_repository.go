package repository

import (
	"context"
	"errors"

	"biblioteca/autenticacion-ms/internal/models"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

type UserRepository struct{ pool *pgxpool.Pool }

func NewUserRepository(pool *pgxpool.Pool) *UserRepository { return &UserRepository{pool: pool} }

func (r *UserRepository) Create(ctx context.Context, user models.User, roleName string) (models.User, error) {
	const query = `
		INSERT INTO usuarios (nombre, apellido, correo, password_hash, id_rol, activo)
		SELECT $1, $2, $3, $4, id_rol, TRUE FROM roles WHERE nombre = $5
		RETURNING id_usuario, id_rol, fecha_creacion, actualizado_en`
	err := r.pool.QueryRow(ctx, query, user.FirstName, user.LastName, user.Email, user.PasswordHash, roleName).
		Scan(&user.ID, &user.RoleID, &user.CreatedAt, &user.UpdatedAt)
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) && pgErr.Code == "23505" {
			return models.User{}, models.ErrEmailAlreadyExists
		}
		return models.User{}, err
	}
	user.RoleName = roleName
	return user, nil
}

func (r *UserRepository) FindByEmail(ctx context.Context, email string) (models.User, error) {
	const query = `
		SELECT u.id_usuario, u.nombre, u.apellido, u.correo, u.password_hash,
		       u.id_rol, r.nombre, u.activo, u.fecha_creacion, u.actualizado_en
		FROM usuarios u JOIN roles r ON r.id_rol = u.id_rol
		WHERE LOWER(u.correo) = LOWER($1)`
	var user models.User
	err := r.pool.QueryRow(ctx, query, email).Scan(
		&user.ID, &user.FirstName, &user.LastName, &user.Email, &user.PasswordHash,
		&user.RoleID, &user.RoleName, &user.Active, &user.CreatedAt, &user.UpdatedAt,
	)
	if errors.Is(err, pgx.ErrNoRows) {
		return models.User{}, models.ErrInvalidCredentials
	}
	return user, err
}
