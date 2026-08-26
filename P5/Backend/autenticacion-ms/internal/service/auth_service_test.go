package service

import (
	"context"
	"errors"
	"testing"

	"biblioteca/autenticacion-ms/internal/models"
)

type fakeUsers struct {
	created models.User
	found   models.User
	err     error
}

func (f *fakeUsers) Create(_ context.Context, user models.User, role string) (models.User, error) {
	if f.err != nil {
		return models.User{}, f.err
	}
	user.ID, user.RoleName = "user-1", role
	f.created = user
	return user, nil
}

func (f *fakeUsers) FindByEmail(_ context.Context, _ string) (models.User, error) {
	return f.found, f.err
}

type fakeHasher struct{ compareErr error }

func (f fakeHasher) Hash(password string) (string, error) { return "hash:" + password, nil }
func (f fakeHasher) Compare(_, _ string) error            { return f.compareErr }

type fakeTokens struct{}

func (fakeTokens) Generate(models.User) (string, error) { return "jwt-token", nil }

func TestRegisterCreatesReaderAndReturnsToken(t *testing.T) {
	repository := &fakeUsers{}
	service := NewAuthService(repository, fakeHasher{}, fakeTokens{})

	result, err := service.Register(context.Background(), RegisterInput{
		FirstName: " Ana ", LastName: " López ", Email: " ANA@EXAMPLE.COM ", Password: "Clave123",
	})
	if err != nil {
		t.Fatalf("Register() error = %v", err)
	}
	if result.Token != "jwt-token" || result.User.RoleName != models.DefaultRole {
		t.Fatalf("resultado inesperado: %+v", result)
	}
	if repository.created.Email != "ana@example.com" || repository.created.PasswordHash == "Clave123" {
		t.Fatalf("usuario no fue normalizado o protegido: %+v", repository.created)
	}
}

func TestRegisterRejectsShortPassword(t *testing.T) {
	service := NewAuthService(&fakeUsers{}, fakeHasher{}, fakeTokens{})
	_, err := service.Register(context.Background(), RegisterInput{
		FirstName: "Ana", LastName: "López", Email: "ana@example.com", Password: "123",
	})
	if !errors.Is(err, models.ErrInvalidInput) {
		t.Fatalf("se esperaba ErrInvalidInput, se obtuvo %v", err)
	}
}

func TestLoginRejectsInactiveUser(t *testing.T) {
	repository := &fakeUsers{found: models.User{ID: "user-1", Active: false, PasswordHash: "hash"}}
	service := NewAuthService(repository, fakeHasher{}, fakeTokens{})
	_, err := service.Login(context.Background(), LoginInput{Email: "ana@example.com", Password: "Clave123"})
	if !errors.Is(err, models.ErrInvalidCredentials) {
		t.Fatalf("se esperaba ErrInvalidCredentials, se obtuvo %v", err)
	}
}
