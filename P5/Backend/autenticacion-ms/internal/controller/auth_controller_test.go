package controller_test

import (
	"bytes"
	"context"
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"

	"biblioteca/autenticacion-ms/internal/controller"
	"biblioteca/autenticacion-ms/internal/models"
	"biblioteca/autenticacion-ms/internal/routes"
	"biblioteca/autenticacion-ms/internal/service"
)

type testUsers struct{}

func (testUsers) Create(_ context.Context, user models.User, role string) (models.User, error) {
	user.ID = "8eeb5650-1e88-4692-b42a-66f59b477cc8"
	user.RoleName = role
	return user, nil
}

func (testUsers) FindByEmail(context.Context, string) (models.User, error) {
	return models.User{}, models.ErrInvalidCredentials
}

type testHasher struct{}

func (testHasher) Hash(string) (string, error)  { return "bcrypt-hash", nil }
func (testHasher) Compare(string, string) error { return nil }

type testTokens struct{}

func (testTokens) Generate(models.User) (string, error) { return "jwt-token", nil }

func TestRegisterEndpoint(t *testing.T) {
	authService := service.NewAuthService(testUsers{}, testHasher{}, testTokens{})
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))
	authController := controller.NewAuthController(authService, logger)
	server := httptest.NewServer(routes.New(authController, logger))
	defer server.Close()

	body := []byte(`{"nombre":"Ana","apellido":"Lopez","correo":"ana@example.com","password":"Clave123"}`)
	response, err := http.Post(server.URL+"/api/v1/auth/register", "application/json", bytes.NewReader(body))
	if err != nil {
		t.Fatalf("POST register: %v", err)
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusCreated {
		payload, _ := io.ReadAll(response.Body)
		t.Fatalf("status = %d, body = %s", response.StatusCode, payload)
	}
}
