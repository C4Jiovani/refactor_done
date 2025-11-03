from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# Schémas pour User
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None  # Optionnel pour rétrocompatibilité
    matricule: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    phone: Optional[str] = None
    fonction: Optional[str] = None
    date_et_lieu_naissance: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    matricule: str
    nom: str
    prenom: str
    full_name: str  # Propriété calculée
    is_active: bool
    role: str
    type: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    phone: Optional[str] = None
    fonction: Optional[str] = None
    is_active: Optional[bool] = None


# Schémas pour Auth
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Schémas pour Document (alias pour compatibilité)
class DocumentRequestBase(BaseModel):
    document_type: str


class DocumentRequestCreate(DocumentRequestBase):
    pass


class DocumentRequestResponse(DocumentRequestBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class DocumentRequestUpdate(BaseModel):
    status: Optional[str] = None


# Schéma pour créer plusieurs demandes en une fois
class MultipleRequestsCreate(BaseModel):
    document_types: List[str]


# Alias pour compatibilité avec le modèle Document
DocumentBase = DocumentRequestBase
DocumentCreate = DocumentRequestCreate
DocumentResponse = DocumentRequestResponse
DocumentUpdate = DocumentRequestUpdate


class NotificationMessage(BaseModel):
    type: str  # "account_validated", "account_rejected", "request_status_changed"
    message: str
    data: Optional[dict] = None


