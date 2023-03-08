from fastapi import HTTPException, status

CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

COOKIE_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not get cookie",
    )

ALREADY_REGISTERED_EXCEPTION = HTTPException(
    status_code=400, 
    detail="Username already registered"
    )

DATABASE_EXCEPTION = HTTPException(
    status_code=500,
    detail="Database error"
)

KUBER_EXCEPTION = HTTPException(
    status_code=500,
    detail="Kuber error"
)

INCORRENT_USERNAME_EXCEPTION = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
        )

INCORRENT_PASSWORD_EXCEPTION = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password ",
        )