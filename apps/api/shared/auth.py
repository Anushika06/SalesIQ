from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

firebase_admin_available = False
try:
    from firebase_admin import auth, credentials
    import firebase_admin
    
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if creds_path and os.path.exists(creds_path):
        cred = credentials.Certificate(creds_path)
    else:
        cred = credentials.ApplicationDefault()
        
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass  # already initialized
    firebase_admin_available = True
except Exception as e:
    print(f"firebase_admin init failed: {e}")

security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase ID token."""
    # No credentials at all - use dev-mode
    if credentials is None:
        return {"uid": "dev-user", "email": "dev@example.com"}
        
    token = credentials.credentials
    
    # DEV MODE BYPASS
    if token == "dev-token" or not token:
        return {"uid": "dev-user", "email": "dev@example.com"}
    
    # Try real Firebase verification if firebase_admin is available
    if firebase_admin_available:
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Fallback: if firebase_admin failed to init, allow through in dev
    return {"uid": "dev-user", "email": "dev@example.com"}
