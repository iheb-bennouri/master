from master.exceptions import Error


class DataBaseError(Error):
    pass


class DatabaseSessionError(DataBaseError):
    pass


class AccessError(DataBaseError):
    pass
