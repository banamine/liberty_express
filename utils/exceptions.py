cd liberty_express
cat > utils/exceptions.py << 'EOF'
"""
Custom exception hierarchy for Liberty Express
"""

class ContentHubError(Exception):
    """Base exception for all Content Hub errors"""
    pass

class NetworkError(ContentHubError):
    """Raised when network operations fail"""
    pass

class ExtractionError(ContentHubError):
    """Raised when content extraction fails"""
    pass

class FileOperationError(ContentHubError):
    """Raised when file operations fail"""
    pass

class ConfigurationError(ContentHubError):
    """Raised when configuration is invalid"""
    pass

class ValidationError(ContentHubError):
    """Raised when data validation fails"""
    pass
EOF
