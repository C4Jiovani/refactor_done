from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models import User, Document, UserRole, DocumentStatus, Categori
from app.schemas import UserCreate, UserUpdate, DocumentRequestCreate, DocumentRequestUpdate
from app.auth import get_password_hash
from typing import List, Optional
import secrets


# CRUD pour User
def create_user(db: Session, user: UserCreate) -> User:
    """Crée un nouvel utilisateur (non actif par défaut)"""
    hashed_password = get_password_hash(user.password)
    
    # Gérer matricule si non fourni
    matricule = user.matricule if user.matricule else f"STU{secrets.token_hex(4).upper()}"
    
    # Gérer nom et prénom
    if user.full_name and not (user.nom and user.prenom):
        # Si full_name est fourni, le diviser
        parts = user.full_name.split(maxsplit=1)
        nom = parts[1] if len(parts) > 1 else ""
        prenom = parts[0] if len(parts) > 0 else ""
    else:
        nom = user.nom or ""
        prenom = user.prenom or ""
    
    db_user = User(
        matricule=matricule,
        email=user.email,
        hashed_password=hashed_password,
        nom=nom,
        prenom=prenom,
        phone=user.phone,
        fonction=user.fonction,
        date_et_lieu_naissance=user.date_et_lieu_naissance,
        is_active=False,  # Pas actif par défaut
        type=UserRole.ETUDIANT.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Récupère un utilisateur par son email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_matricule(db: Session, matricule: str) -> Optional[User]:
    """Récupère un utilisateur par son matricule"""
    return db.query(User).filter(User.matricule == matricule).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Récupère un utilisateur par son ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Récupère tous les utilisateurs"""
    return db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()


def get_pending_users(db: Session) -> List[User]:
    """Récupère les utilisateurs en attente de validation"""
    return db.query(User).filter(User.is_active == False, User.is_deleted == False).all()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Met à jour un utilisateur"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Gérer full_name si fourni
    if 'full_name' in update_data:
        full_name = update_data.pop('full_name')
        if full_name:
            parts = full_name.split(maxsplit=1)
            db_user.prenom = parts[0] if len(parts) > 0 else ""
            db_user.nom = parts[1] if len(parts) > 1 else ""
    
    for field, value in update_data.items():
        if hasattr(db_user, field):
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Soft delete d'un utilisateur"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    db_user.is_deleted = True
    db.commit()
    return True


# CRUD pour Document (DocumentRequest est un alias)
def create_document_request(db: Session, request: DocumentRequestCreate, user_id: int) -> Document:
    """Crée une nouvelle demande de document"""
    # Mapper document_type vers categorie_id
    # Pour l'instant, chercher une catégorie par designation
    categorie = db.query(Categori).filter(Categori.designation.ilike(f"%{request.document_type}%")).first()
    
    if not categorie:
        # Catégorie par défaut si non trouvée
        categorie = db.query(Categori).first()
    
    if not categorie:
        raise ValueError("Aucune catégorie de document trouvée")
    
    db_request = Document(
        user_id=user_id,
        categorie_id=categorie.id,
        status=DocumentStatus.PENDING.value,
        est_paye=False
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def create_multiple_document_requests(db: Session, document_types: List[str], user_id: int) -> List[Document]:
    """Crée plusieurs demandes de documents en une seule fois"""
    db_requests = []
    for doc_type in document_types:
        # Mapper document_type vers categorie_id
        categorie = db.query(Categori).filter(Categori.designation.ilike(f"%{doc_type}%")).first()
        
        if not categorie:
            # Catégorie par défaut si non trouvée
            categorie = db.query(Categori).first()
        
        if categorie:
            db_request = Document(
                user_id=user_id,
                categorie_id=categorie.id,
                status=DocumentStatus.PENDING.value,
                est_paye=False
            )
            db.add(db_request)
            db_requests.append(db_request)
    
    db.commit()
    for db_request in db_requests:
        db.refresh(db_request)
    return db_requests


def get_document_request_by_id(db: Session, request_id: int) -> Optional[Document]:
    """Récupère une demande par son ID"""
    return db.query(Document).options(joinedload(Document.categorie), joinedload(Document.user)).filter(Document.id == request_id).first()


def get_all_document_requests(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    """Récupère toutes les demandes"""
    return db.query(Document).options(joinedload(Document.categorie), joinedload(Document.user)).offset(skip).limit(limit).all()


def get_user_document_requests(db: Session, user_id: int) -> List[Document]:
    """Récupère toutes les demandes d'un utilisateur"""
    return db.query(Document).options(joinedload(Document.categorie)).filter(Document.user_id == user_id).all()


def update_document_request(db: Session, request_id: int, request_update: DocumentRequestUpdate) -> Optional[Document]:
    """Met à jour une demande"""
    db_request = db.query(Document).options(joinedload(Document.categorie), joinedload(Document.user)).filter(Document.id == request_id).first()
    if not db_request:
        return None
    
    update_data = request_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Mapper status vers les valeurs du modèle
        if field == 'status' and value:
            # Convertir les anciennes valeurs vers les nouvelles
            status_mapping = {
                'en attente': DocumentStatus.PENDING.value,
                'pending': DocumentStatus.PENDING.value,
                'validée': DocumentStatus.VALIDATE.value,
                'validate': DocumentStatus.VALIDATE.value,
                'refusée': DocumentStatus.REFUSE.value,
                'refuse': DocumentStatus.REFUSE.value
            }
            value = status_mapping.get(value.lower(), value)
        setattr(db_request, field, value)
    
    from datetime import datetime
    db_request.updated_at = datetime.utcnow()
    
    # Si le statut passe à validé, mettre à jour date_de_validation
    if update_data.get('status') == DocumentStatus.VALIDATE.value:
        db_request.date_de_validation = datetime.utcnow()
    
    db.commit()
    db.refresh(db_request)
    return db_request


def delete_document_request(db: Session, request_id: int) -> bool:
    """Supprime une demande"""
    db_request = db.query(Document).filter(Document.id == request_id).first()
    if not db_request:
        return False
    db.delete(db_request)
    db.commit()
    return True


# Alias pour compatibilité
DocumentRequest = Document


