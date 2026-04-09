"""Custom exception hierarchy."""


class AnalyzerError(Exception):
    """Base error."""


class InvalidUploadError(AnalyzerError):
    """Uploaded file failed validation."""


class SessionNotFoundError(AnalyzerError):
    """Requested session id does not exist."""


class AnalysisNotReadyError(AnalyzerError):
    """Analysis is still processing."""


class ParseError(AnalyzerError):
    """Parser failed to extract any messages."""
