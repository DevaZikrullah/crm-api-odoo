class MissingFormDataError(Exception):
    status_code = 400

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def to_dict(self):
        return {'error': self.message}
