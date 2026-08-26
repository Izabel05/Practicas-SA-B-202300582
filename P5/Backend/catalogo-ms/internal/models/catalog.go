package models

import (
	"errors"
	"time"
)

var (
	ErrInvalidInput = errors.New("datos de entrada invalidos")
	ErrNotFound     = errors.New("recurso no encontrado")
	ErrConflict     = errors.New("el recurso ya existe")
)

type Category struct {
	ID          string `json:"id_categoria"`
	Name        string `json:"nombre"`
	Description string `json:"descripcion"`
}

type Author struct {
	ID        string `json:"id_autor"`
	FirstName string `json:"nombre"`
	LastName  string `json:"apellido"`
}

type Book struct {
	ID              string    `json:"id_libro"`
	Title           string    `json:"titulo"`
	Publisher       string    `json:"editorial"`
	PublicationYear int       `json:"anio_publicacion"`
	CategoryID      string    `json:"id_categoria"`
	Category        Category  `json:"categoria"`
	Authors         []Author  `json:"autores"`
	Copies          []Copy    `json:"ejemplares"`
	Active          bool      `json:"activo"`
	CreatedAt       time.Time `json:"fecha_creacion"`
	UpdatedAt       time.Time `json:"actualizado_en"`
}

type Copy struct {
	ID            string    `json:"id_ejemplar"`
	BookID        string    `json:"id_libro"`
	InventoryCode string    `json:"codigo_inventario"`
	Status        string    `json:"estado"`
	CreatedAt     time.Time `json:"fecha_creacion"`
	UpdatedAt     time.Time `json:"actualizado_en"`
}

const (
	CopyAvailable   = "DISPONIBLE"
	CopyLoaned      = "PRESTADO"
	CopyMaintenance = "MANTENIMIENTO"
)
