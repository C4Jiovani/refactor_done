from pydantic import BaseModel, EmailStr, UUID4, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, List

class PaginationMeta(BaseModel):
    page: int
    page_total: int
    per_page: int
    total_items: int

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
    niveau_id: int

class UserRequestFilter(BaseModel):
    """Schéma Pydantic pour les paramètres de filtrage des demandes de documents."""

    search_term: Optional[str] = Field(None, description="Terme de recherche libre: Nom, Matricule, nom, prenom, de document.")
    type: Optional[str] = Field(None, description="Chercher le type de compte (etudiant, admin, sco)")
    status: Optional[bool] = Field(None, description="Etat d'activation du compte")

    # --- Nouveaux Paramètres de Pagination ---
    page: int = Field(1, ge=1, description="Numéro de la page à retourner (doit être >= 1).")
    per_page: int = Field(10, ge=1, le=100, description="Nombre d'éléments par page (entre 1 et 100).")
    all: bool = Field(False, description="Si True, ignore la pagination et retourne tous les résultats (admin seulement).")

class NiveauSchema(BaseModel):
    id:int
    designation: str
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: UUID4
    matricule: Optional[str] = None
    nom: str
    prenom: str
    full_name: str  # Propriété calculée
    is_active: bool
    role: str
    type: str
    niveau: Optional[NiveauSchema] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedUserRequestResponse(BaseModel):
    """Schéma de réponse complet incluant les données et les informations de pagination."""
    data: List[UserResponse]
    pagination: PaginationMeta


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    phone: Optional[str] = None
    fonction: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None



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
    # document_type: List[str]
    document_type: str


class DocumentRequestCreate(DocumentRequestBase):
    pass


class InfoSuppSchema(BaseModel):
    niveau: str
    annee_univ: str

    class Config:
        from_attributes = True

# ==================== SCHEMAS CATEGORI (CRUD) ====================
class CategoriResponseSchema(BaseModel):
    id: int
    designation : str
    slug: Optional[str] = None
    type: Optional[str] = None
    icon: Optional[str] = None
    path: Optional[str] = None
    montant: float
    contenu_notif: Optional[str] = None
    is_visible: bool
    with_parent: bool
    with_info: bool

    class Config:
        from_attributes = True

class CategoriCreateRequest(BaseModel):
    designation: str
    slug: str
    type: str
    icon: str
    path: str
    montant: float
    contenu_notif: str
    is_visible: bool
    with_parent: Optional[bool] = None
    with_info: Optional[bool] = None

# ==================== SCHEMAS DEMANDE (CRUD) ====================
class DocumentCreateSchema(BaseModel):
    """Schéma Pydantic pour la création d'une seule demande de document."""
    pere: Optional[str] = None
    mere: Optional[str] = None
    categorie_id: int
    infosupps: Optional[List[InfoSuppSchema]] = None  # Pour la création des InfoSupps

    # user_id: UUID4
    # numero: Optional[str] = None
    # date_de_demande: datetime
    # date_de_validation: Optional[datetime] = None
    # status: str
    # est_paye: bool
    # created_at: datetime
    # updated_at: Optional[datetime] = None
    # user: Optional[UserResponse] = None
    # infosupps: Optional[List[InfoSuppSchema]] = None
    # categorie: Optional[CategoriResponseSchema] = None
    # --- NOUVEAU CHAMP POUR M2M ---
    # Le frontend envoie une liste d'IDs


# Mise à jour du Schéma de Filtre
class DocumentRequestFilter(BaseModel):
    """Schéma Pydantic pour les paramètres de filtrage des demandes de documents."""

    search_term: Optional[str] = Field(None, description="Terme de recherche libre: Nom, Matricule, ou Numéro de document.")
    status: Optional[str] = Field(None, description="Filtrer par statut du document (ex: PENDING, APPROVED).")
    categorie_id: Optional[int] = Field(None, description="Filtrer par ID de catégorie du document.")
    start_date: Optional[date] = Field(None, description="Date de début pour le filtre de période (inclusif).")
    end_date: Optional[date] = Field(None, description="Date de fin pour le filtre de période (inclusif).")

    # --- Nouveaux Paramètres de Pagination ---
    page: int = Field(1, ge=1, description="Numéro de la page à retourner (doit être >= 1).")
    per_page: int = Field(10, ge=1, le=100, description="Nombre d'éléments par page (entre 1 et 100).")
    all: bool = Field(False, description="Si True, ignore la pagination et retourne tous les résultats (admin seulement).")


class DocumentRequestResponse(DocumentRequestBase):
    id: int
    user_id: UUID4
    numero: Optional[int] = None
    date_de_demande: datetime
    date_de_validation: Optional[datetime] = None
    pere: Optional[str] = None
    mere: Optional[str] = None
    status: str
    est_paye: bool
    is_deleted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[UserResponse] = None
    infosupps: Optional[List[InfoSuppSchema]] = None
    categorie: Optional[CategoriResponseSchema] = None

    class Config:
        from_attributes = True

class PaginatedDocumentRequestResponse(BaseModel):
    """Schéma de réponse complet incluant les données et les informations de pagination."""
    data: List[DocumentRequestResponse]
    pagination: PaginationMeta

class DocumentRequestUpdate(BaseModel):
    status: Optional[str] = None # pending, validate, refused
    est_paye: Optional[bool] = None


class DocumentRequestCLientUpdate(BaseModel):
    pere: Optional[str] = None # pending, validate, refused
    mere: Optional[str] = None
    categorie_id: Optional[int] = None
    infosupps: Optional[List[InfoSuppSchema]] = None


# Schéma pour créer plusieurs demandes en une fois
class MultipleRequestsCreate(BaseModel):
    # document_types: List[str]
    document_type: str


# Alias pour compatibilité avec le modèle Document
DocumentBase = DocumentRequestBase
DocumentCreate = DocumentRequestCreate
DocumentResponse = DocumentRequestResponse
DocumentUpdate = DocumentRequestUpdate


class NotificationMessage(BaseModel):
    type: str  # "account_validated", "account_rejected", "request_status_changed"
    message: str
    data: Optional[dict] = None

# ==================== SCHEMAS NIVEAU (CRUD) ====================
class NiveauResponseSchema(BaseModel):
    id: int
    designation : str

class NiveauCreateRequest(BaseModel):
    designation : str


# ==================== SCHEMAS NOTIFICATION (CRUD) ====================
class NotificationResponseSchema(BaseModel):
    id: int
    user: Optional[UserResponse] = None
    document: Optional[DocumentRequestResponse] = None
    contenu: Optional[str] = None
    type_notif: str
    vue: Optional[bool] = None

class NotificationSeenSchema(BaseModel):
    notif_ids: List[int]

class EmailSchema(BaseModel):
    receivers: List[EmailStr]
    subject: str
    body: str
    optional_input: Optional[str] = None

# ==================== REALTIME CONTENT (CRUD) ====================
class AblyMessage(BaseModel):
    channel: str
    publisher: str
    content: NotificationResponseSchema | DocumentResponse

    # def to_payload(self):
    #     if isinstance(self.content, BaseModel):
    #         return self.content.model_dump()
    #     elif isinstance(self.content, dict):
    #         return self.content
    #     elif isinstance(self.content, str):
    #         return {"message": self.content}
    #     else:
    #         return {"message": str(self.content)}

class DashboardStatsResponse(BaseModel):
    pass
