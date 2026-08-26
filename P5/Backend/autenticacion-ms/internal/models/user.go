package models

import (
	"errors"
	"time"
)

var (
	ErrInvalidCredentials = errors.New("correo o contrasena incorrectos")
	ErrEmailAlreadyExists = errors.New("el correo ya esta registrado")
	ErrInvalidInput       = errors.New("datos de entrada invalidos")
)

const DefaultRole = "LECTOR"

type User struct {
	ID           string    `json:"id_usuario"`
	FirstName    string    `json:"nombre"`
	LastName     string    `json:"apellido"`
	Email        string    `json:"correo"`
	PasswordHash string    `json:"-"`
	RoleID       int       `json:"-"`
	RoleName     string    `json:"rol"`
	Active       bool      `json:"activo"`
	CreatedAt    time.Time `json:"fecha_creacion"`
	UpdatedAt    time.Time `json:"actualizado_en"`
}
