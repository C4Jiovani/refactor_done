from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.database import get_db, engine, Base
from app.models import User, Document
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, Token, LoginRequest,
    DocumentRequestCreate, DocumentRequestResponse, DocumentRequestUpdate,
    MultipleRequestsCreate, NotificationMessage
)
from app.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_current_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.crud import (
    create_user, get_user_by_email, get_user_by_id, get_all_users,
    get_pending_users, update_user, delete_user,
    create_document_request, create_multiple_document_requests,
    get_document_request_by_id, get_all_document_requests,
    get_user_document_requests, update_document_request, delete_document_request
)
from app.services.websocket_manager import manager

# Créer les tables de la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Gestion Documents Étudiants",
    description="API pour la gestion des demandes de documents administratifs",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ROUTES D'AUTHENTIFICATION ====================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur (compte non actif par défaut)"""
    # Vérifier si l'email existe déjà
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = create_user(db=db, user=user)
    return new_user


@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Please wait for admin approval."
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== ROUTES POUR UTILISATEURS ====================

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user


@app.get("/users", response_model=List[UserResponse])
async def read_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère tous les utilisateurs (admin seulement)"""
    users = get_all_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/pending", response_model=List[UserResponse])
async def read_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère les utilisateurs en attente de validation (admin seulement)"""
    users = get_pending_users(db)
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère un utilisateur par son ID (admin seulement)"""
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Met à jour un utilisateur (admin seulement)"""
    db_user = update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Envoyer une notification si le statut is_active change
    if user_update.is_active is not None:
        notification_type = "account_validated" if user_update.is_active else "account_rejected"
        notification_message = {
            "type": notification_type,
            "message": f"Votre compte a été {'validé' if user_update.is_active else 'refusé'}",
            "data": {"user_id": user_id, "is_active": user_update.is_active}
        }
        await manager.send_personal_message(notification_message, user_id)
    
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime un utilisateur (admin seulement)"""
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


# ==================== ROUTES POUR DEMANDES DE DOCUMENTS ====================

@app.post("/requests", response_model=List[DocumentRequestResponse], status_code=status.HTTP_201_CREATED)
async def create_requests(
    requests_data: MultipleRequestsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crée une ou plusieurs demandes de documents en une seule requête"""
    if not requests_data.document_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one document type is required"
        )
    
    db_requests = create_multiple_document_requests(
        db=db,
        document_types=requests_data.document_types,
        user_id=current_user.id
    )
    
    return db_requests


@app.get("/requests", response_model=List[DocumentRequestResponse])
async def read_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère les demandes de documents"""
    # Si admin, retourner toutes les demandes, sinon seulement celles de l'utilisateur
    if current_user.role == "admin":
        requests = get_all_document_requests(db, skip=skip, limit=limit)
    else:
        requests = get_user_document_requests(db, user_id=current_user.id)
    return requests


@app.get("/requests/{request_id}", response_model=DocumentRequestResponse)
async def read_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère une demande par son ID"""
    db_request = get_document_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Vérifier que l'utilisateur peut accéder à cette demande
    if current_user.role != "admin" and db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return db_request


@app.put("/requests/{request_id}", response_model=DocumentRequestResponse)
async def update_request(
    request_id: int,
    request_update: DocumentRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Met à jour le statut d'une demande (admin seulement)"""
    db_request = get_document_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    
    old_status = db_request.status
    updated_request = update_document_request(db, request_id=request_id, request_update=request_update)
    
    # Envoyer une notification si le statut a changé
    if request_update.status and request_update.status != old_status:
        notification_message = {
            "type": "request_status_changed",
            "message": f"Le statut de votre demande a changé: {request_update.status}",
            "data": {
                "request_id": request_id,
                "old_status": old_status,
                "new_status": request_update.status,
                "document_type": updated_request.document_type
            }
        }
        await manager.send_personal_message(notification_message, updated_request.user_id)
    
    return updated_request


@app.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime une demande (admin seulement)"""
    success = delete_document_request(db, request_id=request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")


# ==================== ROUTES WEBSOCKET ====================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Endpoint WebSocket pour les notifications en temps réel"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Écouter les messages (optionnel, pour le ping/pong)
            data = await websocket.receive_text()
            # On peut répondre avec un pong si nécessaire
            await websocket.send_json({"type": "pong", "message": "Connection alive"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "API Gestion Documents Étudiants",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from app.database import get_db, engine, Base
from app.models import User, Document
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, Token, LoginRequest,
    DocumentRequestCreate, DocumentRequestResponse, DocumentRequestUpdate,
    MultipleRequestsCreate, NotificationMessage
)
from app.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_current_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.crud import (
    create_user, get_user_by_email, get_user_by_id, get_all_users,
    get_pending_users, update_user, delete_user,
    create_document_request, create_multiple_document_requests,
    get_document_request_by_id, get_all_document_requests,
    get_user_document_requests, update_document_request, delete_document_request
)
from app.services.websocket_manager import manager

# Créer les tables de la base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Gestion Documents Étudiants",
    description="API pour la gestion des demandes de documents administratifs",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ROUTES D'AUTHENTIFICATION ====================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur (compte non actif par défaut)"""
    # Vérifier si l'email existe déjà
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = create_user(db=db, user=user)
    return new_user


@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Connexion d'un utilisateur"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Please wait for admin approval."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== ROUTES POUR UTILISATEURS ====================

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user


@app.get("/users", response_model=List[UserResponse])
async def read_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère tous les utilisateurs (admin seulement)"""
    users = get_all_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/pending", response_model=List[UserResponse])
async def read_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère les utilisateurs en attente de validation (admin seulement)"""
    users = get_pending_users(db)
    return users


@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère un utilisateur par son ID (admin seulement)"""
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Met à jour un utilisateur (admin seulement)"""
    db_user = update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Envoyer une notification si le statut is_active change
    if user_update.is_active is not None:
        notification_type = "account_validated" if user_update.is_active else "account_rejected"
        notification_message = {
            "type": notification_type,
            "message": f"Votre compte a été {'validé' if user_update.is_active else 'refusé'}",
            "data": {"user_id": user_id, "is_active": user_update.is_active}
        }
        await manager.send_personal_message(notification_message, user_id)

    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime un utilisateur (admin seulement)"""
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


# ==================== ROUTES POUR DEMANDES DE DOCUMENTS ====================

@app.post("/requests", response_model=List[DocumentRequestResponse], status_code=status.HTTP_201_CREATED)
async def create_requests(
    requests_data: MultipleRequestsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crée une ou plusieurs demandes de documents en une seule requête"""
    if not requests_data.document_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one document type is required"
        )

    db_requests = create_multiple_document_requests(
        db=db,
        document_types=requests_data.document_types,
        user_id=current_user.id
    )

    return db_requests


@app.get("/requests", response_model=List[DocumentRequestResponse])
async def read_requests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère les demandes de documents"""
    # Si admin, retourner toutes les demandes, sinon seulement celles de l'utilisateur
    if current_user.role == "admin":
        requests = get_all_document_requests(db, skip=skip, limit=limit)
    else:
        requests = get_user_document_requests(db, user_id=current_user.id)
    return requests


@app.get("/requests/{request_id}", response_model=DocumentRequestResponse)
async def read_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère une demande par son ID"""
    db_request = get_document_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    # Vérifier que l'utilisateur peut accéder à cette demande
    if current_user.role != "admin" and db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return db_request


@app.put("/requests/{request_id}", response_model=DocumentRequestResponse)
async def update_request(
    request_id: int,
    request_update: DocumentRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Met à jour le statut d'une demande (admin seulement)"""
    db_request = get_document_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = db_request.status
    updated_request = update_document_request(db, request_id=request_id, request_update=request_update)

    # Envoyer une notification si le statut a changé
    if request_update.status and request_update.status != old_status:
        notification_message = {
            "type": "request_status_changed",
            "message": f"Le statut de votre demande a changé: {request_update.status}",
            "data": {
                "request_id": request_id,
                "old_status": old_status,
                "new_status": request_update.status,
                "document_type": updated_request.document_type
            }
        }
        await manager.send_personal_message(notification_message, updated_request.user_id)

    return updated_request


@app.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime une demande (admin seulement)"""
    success = delete_document_request(db, request_id=request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")


# ==================== ROUTES WEBSOCKET ====================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Endpoint WebSocket pour les notifications en temps réel"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Écouter les messages (optionnel, pour le ping/pong)
            data = await websocket.receive_text()
            # On peut répondre avec un pong si nécessaire
            await websocket.send_json({"type": "pong", "message": "Connection alive"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "API Gestion Documents Étudiants",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


