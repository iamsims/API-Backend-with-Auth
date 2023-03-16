from fastapi import HTTPException, status

class PROVIDER_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Invalid provider"
        super().__init__(status_code=self.status_code, detail=self.detail)



class CREDENTIALS_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not validate credentials"
        super().__init__(status_code=self.status_code, detail=self.detail)


class SIGNUP_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not sign up"
        super().__init__(status_code=self.status_code, detail=self.detail)

class LOGIN_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not login"
        super().__init__(status_code=self.status_code, detail=self.detail)



class COOKIE_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Could not get cookie"
        super().__init__(status_code=self.status_code, detail=self.detail)

class ENDPOINT_DOES_NOT_EXIST_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "The endpoint doesn't exist in Kuber"
        super().__init__(status_code=self.status_code, detail=self.detail)



class CREDIT_NOT_ENOUGH_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "You don't have enough credit to perform this request"
        super().__init__(status_code=self.status_code, detail=self.detail)

class ALREADY_REGISTERED_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Username already registered"
        super().__init__(status_code=self.status_code, detail=self.detail)



class DATABASE_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = "Database error"
        super().__init__(status_code=self.status_code, detail=self.detail)



class KUBER_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = "Kuber error"
        super().__init__(status_code=self.status_code, detail=self.detail)

class INCORRECT_USERNAME_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Incorrect username"
        super().__init__(status_code=self.status_code, detail=self.detail)

class INCORRECT_PASSWORD_EXCEPTION(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Incorrect password"
        super().__init__(status_code=self.status_code, detail=self.detail)
