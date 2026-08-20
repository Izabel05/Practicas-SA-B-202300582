package service

import (
	"context"
	"errors"
	"net/mail"
	"strings"

	"biblioteca/autenticacion-ms/internal/models"
	"biblioteca/autenticacion-ms/internal/repository"
)

type RegisterInput struct {
	FirstName string
	LastName  string
	Email     string
	Password  string
}

type LoginInput struct {
	Email    string
	Password string
}

type AuthResult struct {
	Token string      `json:"token"`
	User  models.User `json:"usuario"`
}

type AuthService struct {
	users  repository.UserRepositoryContract
	hasher repository.PasswordHasher
	tokens repository.TokenGenerator
}

func NewAuthService(users repository.UserRepositoryContract, hasher repository.PasswordHasher, tokens repository.TokenGenerator) *AuthService {
	return &AuthService{users: users, hasher: hasher, tokens: tokens}
}

func (s *AuthService) Register(ctx context.Context, input RegisterInput) (AuthResult, error) {
	input.FirstName = strings.TrimSpace(input.FirstName)
	input.LastName = strings.TrimSpace(input.LastName)
	input.Email = normalizeEmail(input.Email)
	if input.FirstName == "" || input.LastName == "" || !validEmail(input.Email) || len(input.Password) < 8 {
		return AuthResult{}, models.ErrInvalidInput
	}

	hash, err := s.hasher.Hash(input.Password)
	if err != nil {
		return AuthResult{}, err
	}
	user, err := s.users.Create(ctx, models.User{
		FirstName: input.FirstName, LastName: input.LastName, Email: input.Email,
		PasswordHash: hash, Active: true,
	}, models.DefaultRole)
	if err != nil {
		return AuthResult{}, err
	}
	return s.resultFor(user)
}

func (s *AuthService) Login(ctx context.Context, input LoginInput) (AuthResult, error) {
	user, err := s.users.FindByEmail(ctx, normalizeEmail(input.Email))
	if err != nil {
		return AuthResult{}, models.ErrInvalidCredentials
	}
	if !user.Active || s.hasher.Compare(user.PasswordHash, input.Password) != nil {
		return AuthResult{}, models.ErrInvalidCredentials
	}
	return s.resultFor(user)
}

func (s *AuthService) resultFor(user models.User) (AuthResult, error) {
	token, err := s.tokens.Generate(user)
	if err != nil {
		return AuthResult{}, err
	}
	return AuthResult{Token: token, User: user}, nil
}

func normalizeEmail(email string) string { return strings.ToLower(strings.TrimSpace(email)) }

func validEmail(email string) bool {
	parsed, err := mail.ParseAddress(email)
	return err == nil && parsed.Address == email
}

func IsClientError(err error) bool {
	return errors.Is(err, models.ErrInvalidInput) || errors.Is(err, models.ErrInvalidCredentials) || errors.Is(err, models.ErrEmailAlreadyExists)
}
