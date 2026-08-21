package service

import (
	"context"
	"strings"
	"time"

	"biblioteca/catalogo-ms/internal/models"
	"biblioteca/catalogo-ms/internal/repository"
)

type CatalogService struct {
	repository repository.CatalogRepositoryContract
}

type CreateBookInput struct {
	Title           string
	Publisher       string
	PublicationYear int
	CategoryID      string
	AuthorIDs       []string
}

func NewCatalogService(repository repository.CatalogRepositoryContract) *CatalogService {
	return &CatalogService{repository: repository}
}

func (s *CatalogService) ListCategories(ctx context.Context) ([]models.Category, error) {
	return s.repository.ListCategories(ctx)
}

func (s *CatalogService) CreateCategory(ctx context.Context, name, description string) (models.Category, error) {
	name, description = strings.TrimSpace(name), strings.TrimSpace(description)
	if name == "" || len(name) > 50 || len(description) > 500 {
		return models.Category{}, models.ErrInvalidInput
	}
	return s.repository.CreateCategory(ctx, models.Category{Name: name, Description: description})
}

func (s *CatalogService) ListAuthors(ctx context.Context) ([]models.Author, error) {
	return s.repository.ListAuthors(ctx)
}

func (s *CatalogService) CreateAuthor(ctx context.Context, firstName, lastName string) (models.Author, error) {
	firstName, lastName = strings.TrimSpace(firstName), strings.TrimSpace(lastName)
	if firstName == "" || lastName == "" || len(firstName) > 50 || len(lastName) > 50 {
		return models.Author{}, models.ErrInvalidInput
	}
	return s.repository.CreateAuthor(ctx, models.Author{FirstName: firstName, LastName: lastName})
}

func (s *CatalogService) ListBooks(ctx context.Context) ([]models.Book, error) {
	return s.repository.ListBooks(ctx)
}

func (s *CatalogService) FindBook(ctx context.Context, id string) (models.Book, error) {
	if strings.TrimSpace(id) == "" {
		return models.Book{}, models.ErrInvalidInput
	}
	return s.repository.FindBookByID(ctx, id)
}

func (s *CatalogService) CreateBook(ctx context.Context, input CreateBookInput) (models.Book, error) {
	input.Title, input.Publisher, input.CategoryID = strings.TrimSpace(input.Title), strings.TrimSpace(input.Publisher), strings.TrimSpace(input.CategoryID)
	currentYear := time.Now().Year()
	if input.Title == "" || input.Publisher == "" || input.CategoryID == "" || len(input.AuthorIDs) == 0 || input.PublicationYear < 1450 || input.PublicationYear > currentYear {
		return models.Book{}, models.ErrInvalidInput
	}
	book := models.Book{Title: input.Title, Publisher: input.Publisher, PublicationYear: input.PublicationYear, CategoryID: input.CategoryID, Active: true}
	return s.repository.CreateBook(ctx, book, input.AuthorIDs)
}

func (s *CatalogService) CreateCopy(ctx context.Context, bookID, inventoryCode string) (models.Copy, error) {
	bookID, inventoryCode = strings.TrimSpace(bookID), strings.TrimSpace(inventoryCode)
	if bookID == "" || inventoryCode == "" || len(inventoryCode) > 50 {
		return models.Copy{}, models.ErrInvalidInput
	}
	return s.repository.CreateCopy(ctx, models.Copy{BookID: bookID, InventoryCode: inventoryCode, Status: models.CopyAvailable})
}

func (s *CatalogService) UpdateCopyStatus(ctx context.Context, id, status string) (models.Copy, error) {
	status = strings.ToUpper(strings.TrimSpace(status))
	if strings.TrimSpace(id) == "" || !validCopyStatus(status) {
		return models.Copy{}, models.ErrInvalidInput
	}
	return s.repository.UpdateCopyStatus(ctx, id, status)
}

func validCopyStatus(status string) bool {
	return status == models.CopyAvailable || status == models.CopyLoaned || status == models.CopyMaintenance
}
