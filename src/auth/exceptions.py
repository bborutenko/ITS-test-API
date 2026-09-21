from fastapi import HTTPException, status

USER_EXIST = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="User is already exist"
)
USER_DOES_NOT_EXIST = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not exist"
)
USER_NOT_AUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not authorized"
)

NOT_VALID_PASS = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Password is not valid"
)

SESSION_EXPIRED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Confirmation link is invalid or expired",
)

TOKEN_TIME_NOT_VALID = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token time is not valid"
)
TOKEN_ID_NOT_VALID = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token id is not valid"
)
TOKEN_EMAIL_NOT_VALID = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token email is not valid"
)
