package repository

import (
	"context"
	"errors"

	"biblioteca/catalogo-ms/internal/models"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

type PostgresCatalogRepository struct{ pool *pgxpool.Pool }

func NewPostgresCatalogRepository(pool *pgxpool.Pool) *PostgresCatalogRepository {
	return &PostgresCatalogRepository{pool: pool}
}

func (r *PostgresCatalogRepository) ListCategories(ctx context.Context) ([]models.Category, error) {
	rows, err := r.pool.Query(ctx, `SELECT id_categoria, nombre, descripcion FROM categorias ORDER BY nombre`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	categories := make([]models.Category, 0)
	for rows.Next() {
		var category models.Category
		if err := rows.Scan(&category.ID, &category.Name, &category.Description); err != nil {
			return nil, err
		}
		categories = append(categories, category)
	}
	return categories, rows.Err()
}

func (r *PostgresCatalogRepository) CreateCategory(ctx context.Context, category models.Category) (models.Category, error) {
	err := r.pool.QueryRow(ctx, `INSERT INTO categorias (nombre, descripcion) VALUES ($1, $2) RETURNING id_categoria`, category.Name, category.Description).Scan(&category.ID)
	return category, mapPostgresError(err)
}

func (r *PostgresCatalogRepository) ListAuthors(ctx context.Context) ([]models.Author, error) {
	rows, err := r.pool.Query(ctx, `SELECT id_autor, nombre, apellido FROM autores ORDER BY apellido, nombre`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	authors := make([]models.Author, 0)
	for rows.Next() {
		var author models.Author
		if err := rows.Scan(&author.ID, &author.FirstName, &author.LastName); err != nil {
			return nil, err
		}
		authors = append(authors, author)
	}
	return authors, rows.Err()
}

func (r *PostgresCatalogRepository) CreateAuthor(ctx context.Context, author models.Author) (models.Author, error) {
	err := r.pool.QueryRow(ctx, `INSERT INTO autores (nombre, apellido) VALUES ($1, $2) RETURNING id_autor`, author.FirstName, author.LastName).Scan(&author.ID)
	return author, mapPostgresError(err)
}

func (r *PostgresCatalogRepository) ListBooks(ctx context.Context) ([]models.Book, error) {
	rows, err := r.pool.Query(ctx, bookSelect+` ORDER BY l.titulo`)
	if err != nil {
		return nil, err
	}
	books := make([]models.Book, 0)
	for rows.Next() {
		book, err := scanBook(rows)
		if err != nil {
			rows.Close()
			return nil, err
		}
		books = append(books, book)
	}
	if err := rows.Err(); err != nil {
		rows.Close()
		return nil, err
	}
	rows.Close()
	for index := range books {
		if err := r.loadBookRelations(ctx, &books[index]); err != nil {
			return nil, err
		}
	}
	return books, nil
}

func (r *PostgresCatalogRepository) FindBookByID(ctx context.Context, id string) (models.Book, error) {
	book, err := scanBook(r.pool.QueryRow(ctx, bookSelect+` WHERE l.id_libro = $1`, id))
	if err != nil {
		return models.Book{}, mapPostgresError(err)
	}
	if err := r.loadBookRelations(ctx, &book); err != nil {
		return models.Book{}, err
	}
	return book, nil
}

func (r *PostgresCatalogRepository) CreateBook(ctx context.Context, book models.Book, authorIDs []string) (models.Book, error) {
	tx, err := r.pool.Begin(ctx)
	if err != nil {
		return models.Book{}, err
	}
	defer tx.Rollback(ctx)
	err = tx.QueryRow(ctx, `
		INSERT INTO libros (titulo, editorial, anio_publicacion, id_categoria, activo)
		VALUES ($1, $2, $3, $4, TRUE) RETURNING id_libro, fecha_creacion, actualizado_en`,
		book.Title, book.Publisher, book.PublicationYear, book.CategoryID,
	).Scan(&book.ID, &book.CreatedAt, &book.UpdatedAt)
	if err != nil {
		return models.Book{}, mapPostgresError(err)
	}
	for _, authorID := range authorIDs {
		if _, err := tx.Exec(ctx, `INSERT INTO libro_autores (id_libro, id_autor) VALUES ($1, $2)`, book.ID, authorID); err != nil {
			return models.Book{}, mapPostgresError(err)
		}
	}
	if err := tx.Commit(ctx); err != nil {
		return models.Book{}, err
	}
	return r.FindBookByID(ctx, book.ID)
}

func (r *PostgresCatalogRepository) CreateCopy(ctx context.Context, copy models.Copy) (models.Copy, error) {
	err := r.pool.QueryRow(ctx, `
		INSERT INTO ejemplares (id_libro, codigo_inventario, estado)
		VALUES ($1, $2, $3)
		RETURNING id_ejemplar, fecha_creacion, actualizado_en`,
		copy.BookID, copy.InventoryCode, copy.Status,
	).Scan(&copy.ID, &copy.CreatedAt, &copy.UpdatedAt)
	return copy, mapPostgresError(err)
}

func (r *PostgresCatalogRepository) UpdateCopyStatus(ctx context.Context, id, status string) (models.Copy, error) {
	var copy models.Copy
	err := r.pool.QueryRow(ctx, `
		UPDATE ejemplares SET estado = $2, actualizado_en = CURRENT_TIMESTAMP
		WHERE id_ejemplar = $1 AND (
			($2 = 'PRESTADO' AND estado = 'DISPONIBLE') OR
			($2 = 'DISPONIBLE' AND estado IN ('PRESTADO', 'MANTENIMIENTO')) OR
			($2 = 'MANTENIMIENTO' AND estado = 'DISPONIBLE')
		)
		RETURNING id_ejemplar, id_libro, codigo_inventario, estado, fecha_creacion, actualizado_en`,
		id, status,
	).Scan(&copy.ID, &copy.BookID, &copy.InventoryCode, &copy.Status, &copy.CreatedAt, &copy.UpdatedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		var exists bool
		if lookupErr := r.pool.QueryRow(ctx, `SELECT EXISTS(SELECT 1 FROM ejemplares WHERE id_ejemplar = $1)`, id).Scan(&exists); lookupErr != nil {
			return models.Copy{}, lookupErr
		}
		if exists {
			return models.Copy{}, models.ErrConflict
		}
		return models.Copy{}, models.ErrNotFound
	}
	return copy, mapPostgresError(err)
}

const bookSelect = `
	SELECT l.id_libro, l.titulo, l.editorial, l.anio_publicacion, l.id_categoria,
	       l.activo, l.fecha_creacion, l.actualizado_en,
	       c.id_categoria, c.nombre, c.descripcion
	FROM libros l JOIN categorias c ON c.id_categoria = l.id_categoria`

type scanner interface{ Scan(dest ...any) error }

func scanBook(row scanner) (models.Book, error) {
	var book models.Book
	err := row.Scan(
		&book.ID, &book.Title, &book.Publisher, &book.PublicationYear, &book.CategoryID,
		&book.Active, &book.CreatedAt, &book.UpdatedAt,
		&book.Category.ID, &book.Category.Name, &book.Category.Description,
	)
	return book, err
}

func (r *PostgresCatalogRepository) loadBookRelations(ctx context.Context, book *models.Book) error {
	authorRows, err := r.pool.Query(ctx, `
		SELECT a.id_autor, a.nombre, a.apellido
		FROM autores a JOIN libro_autores la ON la.id_autor = a.id_autor
		WHERE la.id_libro = $1 ORDER BY a.apellido, a.nombre`, book.ID)
	if err != nil {
		return err
	}
	book.Authors = make([]models.Author, 0)
	for authorRows.Next() {
		var author models.Author
		if err := authorRows.Scan(&author.ID, &author.FirstName, &author.LastName); err != nil {
			authorRows.Close()
			return err
		}
		book.Authors = append(book.Authors, author)
	}
	if err := authorRows.Err(); err != nil {
		authorRows.Close()
		return err
	}
	authorRows.Close()

	copyRows, err := r.pool.Query(ctx, `
		SELECT id_ejemplar, id_libro, codigo_inventario, estado, fecha_creacion, actualizado_en
		FROM ejemplares WHERE id_libro = $1 ORDER BY codigo_inventario`, book.ID)
	if err != nil {
		return err
	}
	defer copyRows.Close()
	book.Copies = make([]models.Copy, 0)
	for copyRows.Next() {
		var copy models.Copy
		if err := copyRows.Scan(&copy.ID, &copy.BookID, &copy.InventoryCode, &copy.Status, &copy.CreatedAt, &copy.UpdatedAt); err != nil {
			return err
		}
		book.Copies = append(book.Copies, copy)
	}
	return copyRows.Err()
}

func mapPostgresError(err error) error {
	if err == nil {
		return nil
	}
	if errors.Is(err, pgx.ErrNoRows) {
		return models.ErrNotFound
	}
	var pgErr *pgconn.PgError
	if errors.As(err, &pgErr) {
		switch pgErr.Code {
		case "23505":
			return models.ErrConflict
		case "23503", "22P02":
			return models.ErrInvalidInput
		}
	}
	return err
}
