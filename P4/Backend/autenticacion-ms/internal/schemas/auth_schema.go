package schemas

type RegisterRequest struct {
	FirstName string `json:"nombre"`
	LastName  string `json:"apellido"`
	Email     string `json:"correo"`
	Password  string `json:"password"`
}

type LoginRequest struct {
	Email    string `json:"correo"`
	Password string `json:"password"`
}
