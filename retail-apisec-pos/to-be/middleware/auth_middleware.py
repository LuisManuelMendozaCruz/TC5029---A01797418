from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Any

security = HTTPBearer()
JWT_SECRET = "SUPER_SECRET_APITOKEN_KEY_FOR_LOCAL_POC"
JWT_ALGORITHM = "HS256"

def validate_token_claims(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        claims = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["exp", "sub", "store_id", "scope"]}
        )
        return claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token criptográficamente inválido.")

def check_scope(required_scope: str):
    def validator(claims: Dict[str, Any] = Security(validate_token_claims)):
        user_scopes = claims.get("scope", "").split()
        if required_scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso insuficiente. Se requiere scope: {required_scope}"
            )
        return claims
    return validator