class UserError(AssertionError):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"User Error: {self.message}"


class InternalError(AssertionError):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Internal Error: {self.message}"


class ExternalAuthFailure(Exception):
    def __init__(self, auth_url) -> None:
        self.auth_url = auth_url

    def get_auth_url(self):
        return self.auth_url
