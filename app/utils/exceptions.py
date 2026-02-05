"""
Custom exception classes for the application.
"""


class BaseAppException(Exception):
    """Base exception for application-specific errors."""
    pass


class DocumentProcessingError(BaseAppException):
    """Raised when document processing fails."""
    pass


class EmbeddingGenerationError(BaseAppException):
    """Raised when embedding generation fails."""
    pass


class VectorSearchError(BaseAppException):
    """Raised when vector search operations fail."""
    pass


class ConfigurationError(BaseAppException):
    """Raised when configuration is invalid."""
    pass
