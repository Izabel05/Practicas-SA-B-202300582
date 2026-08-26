package service

import (
	"context"
	"errors"
	"testing"

	"biblioteca/catalogo-ms/internal/models"
)

type fakeCatalogRepository struct {
	categories []models.Category
	copy       models.Copy
}

func (f *fakeCatalogRepository) ListCategories(context.Context) ([]models.Category, error) {
	return f.categories, nil
}
func (f *fakeCatalogRepository) CreateCategory(_ context.Context, value models.Category) (models.Category, error) {
	value.ID = "category-1"
	return value, nil
}
func (f *fakeCatalogRepository) ListAuthors(context.Context) ([]models.Author, error) {
	return []models.Author{}, nil
}
func (f *fakeCatalogRepository) CreateAuthor(_ context.Context, value models.Author) (models.Author, error) {
	return value, nil
}
func (f *fakeCatalogRepository) ListBooks(context.Context) ([]models.Book, error) {
	return []models.Book{}, nil
}
func (f *fakeCatalogRepository) FindBookByID(context.Context, string) (models.Book, error) {
	return models.Book{}, models.ErrNotFound
}
func (f *fakeCatalogRepository) CreateBook(_ context.Context, value models.Book, _ []string) (models.Book, error) {
	return value, nil
}
func (f *fakeCatalogRepository) CreateCopy(_ context.Context, value models.Copy) (models.Copy, error) {
	return value, nil
}
func (f *fakeCatalogRepository) UpdateCopyStatus(_ context.Context, id, status string) (models.Copy, error) {
	f.copy = models.Copy{ID: id, Status: status}
	return f.copy, nil
}

func TestCreateCategoryTrimsInput(t *testing.T) {
	service := NewCatalogService(&fakeCatalogRepository{})
	category, err := service.CreateCategory(context.Background(), " Arquitectura ", " Software ")
	if err != nil {
		t.Fatalf("CreateCategory() error = %v", err)
	}
	if category.Name != "Arquitectura" || category.Description != "Software" {
		t.Fatalf("categoria no normalizada: %+v", category)
	}
}

func TestUpdateCopyStatusRejectsUnknownStatus(t *testing.T) {
	service := NewCatalogService(&fakeCatalogRepository{})
	_, err := service.UpdateCopyStatus(context.Background(), "copy-1", "PERDIDO")
	if !errors.Is(err, models.ErrInvalidInput) {
		t.Fatalf("se esperaba ErrInvalidInput, se obtuvo %v", err)
	}
}

func TestUpdateCopyStatusNormalizesValue(t *testing.T) {
	repository := &fakeCatalogRepository{}
	service := NewCatalogService(repository)
	copy, err := service.UpdateCopyStatus(context.Background(), "copy-1", " prestado ")
	if err != nil {
		t.Fatalf("UpdateCopyStatus() error = %v", err)
	}
	if copy.Status != models.CopyLoaned {
		t.Fatalf("estado = %s", copy.Status)
	}
}
