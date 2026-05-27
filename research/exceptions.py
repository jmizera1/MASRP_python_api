from exceptions import Exception


class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, http_status_code: int, detail: str):
        self.http_status_code = http_status_code
        self.detail = detail
        super().__init__(f"HTTP {http_status_code}: {detail}")
