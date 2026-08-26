package repository

import (
	"context"

	"biblioteca/catalogo-ms/internal/models"
)

type CatalogRepositoryContract interface {
	ListCategories(ctx context.Context) ([]models.Category, error)
	CreateCategory(ctx context.Context, category models.Category) (models.Category, error)
	ListAuthors(ctx context.Context) ([]models.Author, error)
	CreateAuthor(ctx context.Context, author models.Author) (models.Author, error)
	ListBooks(ctx context.Context) ([]models.Book, error)
	FindBookByID(ctx context.Context, id string) (models.Book, error)
	CreateBook(ctx context.Context, book models.Book, authorIDs []string) (models.Book, error)
	CreateCopy(ctx context.Context, copy models.Copy) (models.Copy, error)
	UpdateCopyStatus(ctx context.Context, id, status string) (models.Copy, error)
}
