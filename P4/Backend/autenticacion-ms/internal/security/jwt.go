package security

import (
	"time"

	"biblioteca/autenticacion-ms/internal/models"
	"github.com/golang-jwt/jwt/v5"
)

type JWTGenerator struct {
	secret   []byte
	duration time.Duration
	issuer   string
}

func NewJWTGenerator(secret string, duration time.Duration) JWTGenerator {
	return JWTGenerator{secret: []byte(secret), duration: duration, issuer: "autenticacion-ms"}
}

func (g JWTGenerator) Generate(user models.User) (string, error) {
	now := time.Now().UTC()
	claims := jwt.MapClaims{
		"sub": user.ID, "correo": user.Email, "rol": user.RoleName,
		"iss": g.issuer, "iat": now.Unix(), "exp": now.Add(g.duration).Unix(),
	}
	return jwt.NewWithClaims(jwt.SigningMethodHS256, claims).SignedString(g.secret)
}
