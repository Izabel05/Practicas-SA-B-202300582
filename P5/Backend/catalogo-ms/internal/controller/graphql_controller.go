package controller

import (
	"encoding/json"
	"net/http"

	"biblioteca/catalogo-ms/internal/models"
	"biblioteca/catalogo-ms/internal/service"
	"github.com/graphql-go/graphql"
)

type GraphQLController struct{ schema graphql.Schema }

func NewGraphQLController(catalog *service.CatalogService) (*GraphQLController, error) {
	categoryType := graphql.NewObject(graphql.ObjectConfig{Name: "Categoria", Fields: graphql.Fields{
		"id_categoria": &graphql.Field{Type: graphql.NewNonNull(graphql.ID), Resolve: field(func(value models.Category) any { return value.ID })},
		"nombre":       &graphql.Field{Type: graphql.NewNonNull(graphql.String), Resolve: field(func(value models.Category) any { return value.Name })},
		"descripcion":  &graphql.Field{Type: graphql.String, Resolve: field(func(value models.Category) any { return value.Description })},
	}})
	authorType := graphql.NewObject(graphql.ObjectConfig{Name: "Autor", Fields: graphql.Fields{
		"id_autor": &graphql.Field{Type: graphql.NewNonNull(graphql.ID), Resolve: field(func(value models.Author) any { return value.ID })},
		"nombre":   &graphql.Field{Type: graphql.NewNonNull(graphql.String), Resolve: field(func(value models.Author) any { return value.FirstName })},
		"apellido": &graphql.Field{Type: graphql.NewNonNull(graphql.String), Resolve: field(func(value models.Author) any { return value.LastName })},
	}})
	copyType := graphql.NewObject(graphql.ObjectConfig{Name: "Ejemplar", Fields: graphql.Fields{
		"id_ejemplar":       &graphql.Field{Type: graphql.NewNonNull(graphql.ID), Resolve: field(func(value models.Copy) any { return value.ID })},
		"id_libro":          &graphql.Field{Type: graphql.NewNonNull(graphql.ID), Resolve: field(func(value models.Copy) any { return value.BookID })},
		"codigo_inventario": &graphql.Field{Type: graphql.NewNonNull(graphql.String), Resolve: field(func(value models.Copy) any { return value.InventoryCode })},
		"estado":            &graphql.Field{Type: graphql.NewNonNull(graphql.String), Resolve: field(func(value models.Copy) any { return value.Status })},
		"fecha_creacion":    &graphql.Field{Type: graphql.NewNonNull(graphql.DateTime), Resolve: field(func(value models.Copy) any { return value.CreatedAt })},
		"actualizado_en":    &graphql.Field{Type: graphql.NewNonNull(graphql.DateTime), Resolve: field(func(value models.Copy) any { return value.UpdatedAt })},
	}})
	bookType := graphql.NewObject(graphql.ObjectConfig{Name: "Libro", Fields: graphql.Fields{
		"id_libro":         &graphql.Field{Type: graphql.NewNonNull(graphql.ID), Resolve: field(func(value models.Book) any { return value.ID })},
		"titulo":           &graphql.Field{Type: graphql.NewNonNull(graphql.String), Resolve: field(func(value models.Book) any { return value.Title })},
		"editorial":        &graphql.Field{Type: graphql.NewNonNull(graphql.String), Resolve: field(func(value models.Book) any { return value.Publisher })},
		"anio_publicacion": &graphql.Field{Type: graphql.NewNonNull(graphql.Int), Resolve: field(func(value models.Book) any { return value.PublicationYear })},
		"activo":           &graphql.Field{Type: graphql.NewNonNull(graphql.Boolean), Resolve: field(func(value models.Book) any { return value.Active })},
		"categoria":        &graphql.Field{Type: graphql.NewNonNull(categoryType), Resolve: field(func(value models.Book) any { return value.Category })},
		"autores":          &graphql.Field{Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(authorType))), Resolve: field(func(value models.Book) any { return value.Authors })},
		"ejemplares":       &graphql.Field{Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(copyType))), Resolve: field(func(value models.Book) any { return value.Copies })},
	}})

	query := graphql.NewObject(graphql.ObjectConfig{Name: "Query", Fields: graphql.Fields{
		"categorias": &graphql.Field{Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(categoryType))), Resolve: func(params graphql.ResolveParams) (any, error) { return catalog.ListCategories(params.Context) }},
		"autores":    &graphql.Field{Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(authorType))), Resolve: func(params graphql.ResolveParams) (any, error) { return catalog.ListAuthors(params.Context) }},
		"libros":     &graphql.Field{Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(bookType))), Resolve: func(params graphql.ResolveParams) (any, error) { return catalog.ListBooks(params.Context) }},
		"libro": &graphql.Field{Type: bookType, Args: graphql.FieldConfigArgument{
			"id": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.ID)},
		}, Resolve: func(params graphql.ResolveParams) (any, error) {
			return catalog.FindBook(params.Context, params.Args["id"].(string))
		}},
	}})
	mutation := graphql.NewObject(graphql.ObjectConfig{Name: "Mutation", Fields: graphql.Fields{
		"crearCategoria": &graphql.Field{Type: categoryType, Args: graphql.FieldConfigArgument{
			"nombre": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.String)}, "descripcion": &graphql.ArgumentConfig{Type: graphql.String},
		}, Resolve: func(params graphql.ResolveParams) (any, error) {
			return catalog.CreateCategory(params.Context, params.Args["nombre"].(string), optionalString(params.Args, "descripcion"))
		}},
		"crearAutor": &graphql.Field{Type: authorType, Args: graphql.FieldConfigArgument{
			"nombre": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.String)}, "apellido": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.String)},
		}, Resolve: func(params graphql.ResolveParams) (any, error) {
			return catalog.CreateAuthor(params.Context, params.Args["nombre"].(string), params.Args["apellido"].(string))
		}},
		"crearLibro": &graphql.Field{Type: bookType, Args: graphql.FieldConfigArgument{
			"titulo": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.String)}, "editorial": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.String)},
			"anio_publicacion": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.Int)}, "id_categoria": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.ID)},
			"ids_autores": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.NewList(graphql.NewNonNull(graphql.ID)))},
		}, Resolve: func(params graphql.ResolveParams) (any, error) {
			return catalog.CreateBook(params.Context, service.CreateBookInput{
				Title: params.Args["titulo"].(string), Publisher: params.Args["editorial"].(string), PublicationYear: params.Args["anio_publicacion"].(int),
				CategoryID: params.Args["id_categoria"].(string), AuthorIDs: stringSlice(params.Args["ids_autores"].([]any)),
			})
		}},
		"crearEjemplar": &graphql.Field{Type: copyType, Args: graphql.FieldConfigArgument{
			"id_libro": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.ID)}, "codigo_inventario": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.String)},
		}, Resolve: func(params graphql.ResolveParams) (any, error) {
			return catalog.CreateCopy(params.Context, params.Args["id_libro"].(string), params.Args["codigo_inventario"].(string))
		}},
		"actualizarEstadoEjemplar": &graphql.Field{Type: copyType, Args: graphql.FieldConfigArgument{
			"id": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.ID)}, "estado": &graphql.ArgumentConfig{Type: graphql.NewNonNull(graphql.String)},
		}, Resolve: func(params graphql.ResolveParams) (any, error) {
			return catalog.UpdateCopyStatus(params.Context, params.Args["id"].(string), params.Args["estado"].(string))
		}},
	}})
	schema, err := graphql.NewSchema(graphql.SchemaConfig{Query: query, Mutation: mutation})
	if err != nil {
		return nil, err
	}
	return &GraphQLController{schema: schema}, nil
}

func (c *GraphQLController) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	var request struct {
		Query         string         `json:"query"`
		Variables     map[string]any `json:"variables"`
		OperationName string         `json:"operationName"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20)).Decode(&request); err != nil {
		writeError(w, http.StatusBadRequest, "JSON_INVALIDO", err.Error())
		return
	}
	result := graphql.Do(graphql.Params{Schema: c.schema, RequestString: request.Query, VariableValues: request.Variables, OperationName: request.OperationName, Context: r.Context()})
	writeJSON(w, http.StatusOK, result)
}

func field[T any](resolver func(T) any) graphql.FieldResolveFn {
	return func(params graphql.ResolveParams) (any, error) { return resolver(params.Source.(T)), nil }
}

func optionalString(arguments map[string]any, key string) string {
	value, _ := arguments[key].(string)
	return value
}

func stringSlice(values []any) []string {
	result := make([]string, 0, len(values))
	for _, value := range values {
		result = append(result, value.(string))
	}
	return result
}
