class LoanError(Exception):
    """Error base del dominio de préstamos."""


class InvalidInputError(LoanError):
    pass


class NotFoundError(LoanError):
    pass


class ConflictError(LoanError):
    pass


class ExternalServiceError(LoanError):
    pass
