class ExternalAuthFailure(Exception):
    def __init__(self, auth_url) -> None:
        self.__auth_url = auth_url

    @property
    def auth_url(self):
        return self.__auth_url

    @auth_url.setter
    def auth_url(self, auth_url):
        self.__auth_url = auth_url
