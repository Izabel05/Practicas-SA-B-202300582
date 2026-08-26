package controller

import (
	"encoding/json"
	"errors"
	"io"
	"log/slog"
	"net/http"

	"biblioteca/autenticacion-ms/internal/models"
	"biblioteca/autenticacion-ms/internal/schemas"
	"biblioteca/autenticacion-ms/internal/service"
)

const maxRequestBody = 1 << 20

type AuthController struct {
	auth   *service.AuthService
	logger *slog.Logger
}

func NewAuthController(auth *service.AuthService, logger *slog.Logger) *AuthController {
	return &AuthController{auth: auth, logger: logger}
}

func (h *AuthController) Health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok", "servicio": "autenticacion-ms"})
}

func (h *AuthController) Register(w http.ResponseWriter, r *http.Request) {
	var request schemas.RegisterRequest
	if err := decodeJSON(w, r, &request); err != nil {
		writeError(w, http.StatusBadRequest, "JSON_INVALIDO", err.Error())
		return
	}
	result, err := h.auth.Register(r.Context(), service.RegisterInput{
		FirstName: request.FirstName, LastName: request.LastName,
		Email: request.Email, Password: request.Password,
	})
	if err != nil {
		h.handleServiceError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, result)
}

func (h *AuthController) Login(w http.ResponseWriter, r *http.Request) {
	var request schemas.LoginRequest
	if err := decodeJSON(w, r, &request); err != nil {
		writeError(w, http.StatusBadRequest, "JSON_INVALIDO", err.Error())
		return
	}
	result, err := h.auth.Login(r.Context(), service.LoginInput{Email: request.Email, Password: request.Password})
	if err != nil {
		h.handleServiceError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, result)
}

func (h *AuthController) handleServiceError(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, models.ErrInvalidInput):
		writeError(w, http.StatusBadRequest, "DATOS_INVALIDOS", "nombre, apellido, correo valido y password de al menos 8 caracteres son obligatorios")
	case errors.Is(err, models.ErrEmailAlreadyExists):
		writeError(w, http.StatusConflict, "CORREO_EXISTENTE", err.Error())
	case errors.Is(err, models.ErrInvalidCredentials):
		writeError(w, http.StatusUnauthorized, "CREDENCIALES_INVALIDAS", err.Error())
	default:
		h.logger.Error("error interno", "error", err)
		writeError(w, http.StatusInternalServerError, "ERROR_INTERNO", "ocurrio un error inesperado")
	}
}

func decodeJSON(w http.ResponseWriter, r *http.Request, destination any) error {
	r.Body = http.MaxBytesReader(w, r.Body, maxRequestBody)
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(destination); err != nil {
		return err
	}
	if err := decoder.Decode(&struct{}{}); err != io.EOF {
		return errors.New("el cuerpo debe contener un solo objeto JSON")
	}
	return nil
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, status int, code, message string) {
	writeJSON(w, status, map[string]any{"error": map[string]string{"codigo": code, "mensaje": message}})
}
