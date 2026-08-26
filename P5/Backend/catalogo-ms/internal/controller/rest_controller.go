package controller

import (
	"encoding/json"
	"errors"
	"net/http"

	"biblioteca/catalogo-ms/internal/models"
	"biblioteca/catalogo-ms/internal/schemas"
	"biblioteca/catalogo-ms/internal/service"
)

type RestController struct{ catalog *service.CatalogService }

func NewRestController(catalog *service.CatalogService) *RestController {
	return &RestController{catalog: catalog}
}

func (c *RestController) Health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok", "servicio": "catalogo-ms"})
}

func (c *RestController) UpdateCopyStatus(w http.ResponseWriter, r *http.Request) {
	var request schemas.UpdateCopyStatusRequest
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20)).Decode(&request); err != nil {
		writeError(w, http.StatusBadRequest, "JSON_INVALIDO", err.Error())
		return
	}
	copy, err := c.catalog.UpdateCopyStatus(r.Context(), r.PathValue("id"), request.Status)
	if err != nil {
		switch {
		case errors.Is(err, models.ErrInvalidInput):
			writeError(w, http.StatusBadRequest, "DATOS_INVALIDOS", err.Error())
		case errors.Is(err, models.ErrNotFound):
			writeError(w, http.StatusNotFound, "NO_ENCONTRADO", err.Error())
		case errors.Is(err, models.ErrConflict):
			writeError(w, http.StatusConflict, "TRANSICION_INVALIDA", "el estado actual del ejemplar no permite la transición")
		default:
			writeError(w, http.StatusInternalServerError, "ERROR_INTERNO", "ocurrio un error inesperado")
		}
		return
	}
	writeJSON(w, http.StatusOK, copy)
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func writeError(w http.ResponseWriter, status int, code, message string) {
	writeJSON(w, status, map[string]any{"error": map[string]string{"codigo": code, "mensaje": message}})
}
