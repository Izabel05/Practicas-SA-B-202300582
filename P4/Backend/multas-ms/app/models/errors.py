class FineError(Exception):
    """Error base del dominio de multas."""


class InvalidInputError(FineError):
    pass


class NotFoundError(FineError):
    pass


class ConflictError(FineError):
    pass
