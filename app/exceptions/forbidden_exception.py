class ForbiddenException(Exception):
    """
    Exception class for not found errors.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
