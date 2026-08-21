package controller

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"biblioteca/catalogo-ms/internal/models"
	"biblioteca/catalogo-ms/internal/service"
)

type graphqlRepository struct{}

func (graphqlRepository) ListCategories(context.Context) ([]models.Category, error) {
	return []models.Category{{ID: "category-1", Name: "Software", Description: "Ingenieria"}}, nil
}
func (graphqlRepository) CreateCategory(_ context.Context, value models.Category) (models.Category, error) {
	return value, nil
}
func (graphqlRepository) ListAuthors(context.Context) ([]models.Author, error) {
	return []models.Author{}, nil
}
func (graphqlRepository) CreateAuthor(_ context.Context, value models.Author) (models.Author, error) {
	return value, nil
}
func (graphqlRepository) ListBooks(context.Context) ([]models.Book, error) {
	return []models.Book{}, nil
}
func (graphqlRepository) FindBookByID(context.Context, string) (models.Book, error) {
	return models.Book{}, models.ErrNotFound
}
func (graphqlRepository) CreateBook(_ context.Context, value models.Book, _ []string) (models.Book, error) {
	return value, nil
}
func (graphqlRepository) CreateCopy(_ context.Context, value models.Copy) (models.Copy, error) {
	return value, nil
}
func (graphqlRepository) UpdateCopyStatus(_ context.Context, _, _ string) (models.Copy, error) {
	return models.Copy{}, nil
}

func TestGraphQLCategoriesQuery(t *testing.T) {
	service := service.NewCatalogService(graphqlRepository{})
	controller, err := NewGraphQLController(service)
	if err != nil {
		t.Fatalf("NewGraphQLController() error = %v", err)
	}
	server := httptest.NewServer(controller)
	defer server.Close()

	body, _ := json.Marshal(map[string]string{"query": `{ categorias { id_categoria nombre } }`})
	response, err := http.Post(server.URL, "application/json", bytes.NewReader(body))
	if err != nil {
		t.Fatalf("POST GraphQL: %v", err)
	}
	defer response.Body.Close()
	var payload struct {
		Data struct {
			Categories []models.Category `json:"categorias"`
		} `json:"data"`
		Errors []any `json:"errors"`
	}
	if err := json.NewDecoder(response.Body).Decode(&payload); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if len(payload.Errors) != 0 || len(payload.Data.Categories) != 1 || payload.Data.Categories[0].Name != "Software" {
		t.Fatalf("respuesta inesperada: %+v", payload)
	}
}
