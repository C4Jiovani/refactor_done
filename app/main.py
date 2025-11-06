from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from app.database import get_db, engine, Base
from app.models import User, Document, Niveau, Notification
from app.schemas import (
    UserCreate, UserResponse, UserUpdate, Token, LoginRequest, UserRequestFilter,
    DocumentRequestCreate, DocumentRequestResponse, DocumentRequestUpdate, DocumentRequestCLientUpdate,
    DocumentRequestFilter, PaginatedDocumentRequestResponse, DocumentCreateSchema,
    MultipleRequestsCreate, NotificationMessage,
    NiveauResponseSchema, NiveauCreateRequest,
    CategoriCreateRequest, CategoriResponseSchema,
    NotificationResponseSchema, NotificationSeenSchema,
    PaginatedUserRequestResponse, AblyMessage,
)
from app.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_current_sco_or_admin_user, get_current_sco_user,
    get_current_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.crud import (
    create_user, get_user_by_email, get_user_by_id, get_all_users,
    get_pending_users, update_user, delete_user,
    create_document_request,
    get_document_request_by_id, get_all_document_requests, get_document_requests_filtered,
    get_user_document_requests, update_document_request, update_document_client_request, delete_document_request,
    get_all_niveau, create_niveau, update_niveau, delete_niveau, get_a_niveau,
    get_a_categori, get_all_categori, create_categori, update_categori, delete_categori,
    get_notification_for_active_user, mark_as_seen
)
from app.services.websocket_manager import manager
from app.services.ably_service import send_message

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
async def register(user: UserCreate, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur (compte non actif par défaut)"""
    # Vérifier si l'email existe déjà
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = await create_user(db=db, user=user, background_task=background_task)
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
        data={"sub": user.email, "id": str(user.id), "type": user.type}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== ROUTES POUR UTILISATEURS ====================

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return current_user


@app.get("/users", response_model=PaginatedUserRequestResponse)
async def read_all_users(
    data: UserRequestFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Récupère tous les utilisateurs (admin seulement)"""
    users, pagination_meta = get_all_users(db, data)
    result = PaginatedUserRequestResponse(
        data=users,
        pagination=pagination_meta
    )
    return result


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
    user_id: str,
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
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Met à jour un utilisateur (admin seulement)"""
    print(user_id)
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
    db_user.id = str(db_user.id)
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime un utilisateur (admin seulement)"""
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


# ==================== ROUTES POUR DEMANDES DE DOCUMENTS ====================

@app.get("/requests", response_model=PaginatedDocumentRequestResponse)
async def read_demand_all_requests(
    filters: DocumentRequestFilter = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère les demandes de documents avec support de pagination et de filtres.
    Retourne les données et les métadonnées de pagination.
    """

    documents, pagination_meta = get_document_requests_filtered(
        db,
        filters=filters,
        current_user=current_user
    )

    # Construction de la réponse finale
    return PaginatedDocumentRequestResponse(
        data=documents,
        pagination=pagination_meta
    )


@app.get("/requests/{request_id}", response_model=DocumentRequestResponse)
async def read_single_demand_request(
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


@app.post("/requests", response_model=DocumentRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_requests(
    requests_data: DocumentCreateSchema,
    background_task: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # requests_data: MultipleRequestsCreate,
    """Crée une ou plusieurs demandes de documents en une seule requête"""
    db_requests = await create_document_request(
        db=db,
        request=requests_data,
        user_id=str(current_user.id),
        background_task=background_task
    )
    return db_requests


@app.put("/requests/{request_id}", response_model=DocumentRequestResponse)
async def validate_request(
    request_id: int,
    request_update: DocumentRequestUpdate,
        background_task: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_sco_or_admin_user)
):
    """Met à jour le statut d'une demande (admin seulement)"""
    db_request = get_document_request_by_id(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = db_request.status
    updated_request = await update_document_request(db, request_id=request_id, request_update=request_update, background_task=background_task)

    # Envoyer une notification si le statut a changé
    if request_update.status and request_update.status != old_status:
        notification_message = {
            "type": "request_status_changed",
            "message": f"Le statut de votre demande a changé: {request_update.status}",
            "data": {
                "request_id": request_id,
                "est_paye": request_update.est_paye,
                "old_status": old_status,
                "new_status": request_update.status,
                "document_type": updated_request.document_type
            }
        }
        await manager.send_personal_message(notification_message, updated_request.user_id)
    return updated_request


@app.put("/requests/for_student/{request_id}", response_model=DocumentRequestResponse)
async def update_for_client_request(
    request_id: int,
    request_update: DocumentRequestCLientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Met à jour le statut d'une demande (admin seulement)"""
    db_requests = update_document_client_request(
        db=db,
        request=request_update,
        document_id=request_id
    )
    return db_requests


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



# ==================== ROUTES NIVEAU (CRUD) ====================
@app.get("/niveau", response_model=List[NiveauResponseSchema])
def read_requests(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    result = get_all_niveau(db)
    return result

@app.get("/niveau/{niveau_id}", response_model=NiveauResponseSchema)
def read_unique_requests(
    niveau_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    result = get_a_niveau(db, niveau_id)
    return result


@app.post("/niveau", response_model=NiveauResponseSchema, status_code=HTTP_201_CREATED)
def create_niveau_requests(
    request_data: NiveauCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = create_niveau(db, request_data)
    return result


@app.put("/niveau/{niveau_id}", response_model=NiveauResponseSchema, status_code=HTTP_200_OK)
def update_niveau_requests(
    niveau_id: int,
    request_data: NiveauCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = update_niveau(db, request_data, niveau_id)
    return result

@app.delete("/niveau/{niveau_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_niveau_request(
    niveau_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime une demande (admin seulement)"""
    success = delete_niveau(db, niveau_id)
    if not success:
        raise HTTPException(status_code=404, detail="Niveau not found")

# ==================== ROUTES CATEGORIES (CRUD) ====================
@app.get("/categori", response_model=List[CategoriResponseSchema])
def read_requests(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    result = get_all_categori(db)
    return result

@app.get("/categori/{categori_id}", response_model=CategoriResponseSchema)
def read_unique_requests(
    categori_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_active_user)
):
    result = get_a_categori(db, categori_id)
    return result


@app.post("/categori", response_model=CategoriResponseSchema, status_code=HTTP_201_CREATED)
def create_niveau_requests(
    request_data: CategoriCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = create_categori(db, request_data)
    return result

@app.put("/categori/{categori_id}", response_model=CategoriResponseSchema, status_code=HTTP_200_OK)
def update_categori_requests(
    categori_id: int,
    request_data: CategoriCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = update_categori(db, request_data, categori_id)
    return result

@app.delete("/categori/{categori_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categori_request(
    categori_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Supprime une demande (admin seulement)"""
    success = delete_categori(db, categori_id)
    if not success:
        raise HTTPException(status_code=404, detail="Categori not found")


# ==================== ROUTES NOTIFICATION =====================
@app.get("/notification", response_model=List[NotificationResponseSchema])
def notification_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = get_notification_for_active_user(db, current_user.id)
    return result

@app.put("/notification", status_code=HTTP_200_OK)
def notification_unseen_requests(
    data: NotificationSeenSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    rows_updated = mark_as_seen(db, data.notif_ids, current_user.id)
    return {"message": f"{rows_updated} notification(s) marquée(s) comme lue(s)."}

@app.put("/notification", status_code=HTTP_200_OK)
def notification_unseen_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_sco_or_admin_user)
):
    rows_updated = mark_as_seen(db, data.notif_ids, current_user.id)
    return {"message": f"{rows_updated} notification(s) marquée(s) comme lue(s)."}




















@app.get("/send", status_code=HTTP_200_OK)
async def test_realtime():
    msg = AblyMessage(
        channel="admin",
        publisher="register",
        content="Hello world"
    )
    await send_message(msg)

    return {"status": "success", "sent": True}















# ==================== ROUTES WEBSOCKET ====================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
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


