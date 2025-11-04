from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Nullable
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ETUDIANT = "etudiant"
    SCO = "sco"

class CategoriType(str, enum.Enum):
    ATTESTATION = "att"
    CERTIFICAT = "crt"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATE = "validate"
    REFUSE = "refuse"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4(), unique=True, nullable=False)
    matricule = Column(String, unique=True, index=True, nullable=False)  # Identifiant unique
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nom = Column(String, nullable=False)  # Nom de famille
    prenom = Column(String, nullable=False)  # Prénom
    date_et_lieu_naissance = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    fonction = Column(String, nullable=True)  # Poste/fonction de l'utilisateur
    type = Column(String, default=UserRole.ETUDIANT.value, nullable=False)  # admin/etudiant/sco
    niveau_id = Column(Integer, ForeignKey("niveau.id"), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)  # Soft delete
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    documents = relationship("Document", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    # niveau = relationship("Niveau", back_populates="user")

    @hybrid_property
    def full_name(self):
        """Retourne le nom complet (nom + prénom)"""
        return f"{self.prenom} {self.nom}" if self.prenom and self.nom else ""

    @full_name.setter
    def full_name(self, value):
        """Permet de définir full_name en le séparant en nom et prénom"""
        if value:
            parts = value.split(maxsplit=1)
            if len(parts) >= 2:
                self.prenom = parts[0]
                self.nom = parts[1]
            elif len(parts) == 1:
                self.prenom = parts[0]
                self.nom = ""

    # Alias pour compatibilité avec l'ancien code
    @hybrid_property
    def role(self):
        """Retourne le type de l'utilisateur (alias pour compatibilité)"""
        return self.type

    @role.setter
    def role(self, value):
        """Définit le type (alias pour compatibilité)"""
        self.type = value


class Niveau(Base):
    __tablename__ = "niveau"

    id = Column(Integer, primary_key=True, index=True)
    designation = Column(String, nullable=False)

    # Relations
    documents = relationship("Document", back_populates="niveau")
    # users = relationship("User", back_populates="niveau")


class AnneeUniv(Base):
    __tablename__ = "annee_univ"

    annee = Column(String, primary_key=True, index=True)  # ex: "2024-2025"

    # Relations
    documents = relationship("Document", back_populates="annee_univ")


class Categori(Base):
    __tablename__ = "categori"

    id = Column(Integer, primary_key=True, index=True)
    designation = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=False, nullable=True)
    type = Column(String, nullable=True)  # att/crt or null
    montant = Column(Float, nullable=False)
    contenu_notif = Column(String, nullable=True)
    is_visible = Column(Boolean, default=True)

    # Relations
    documents = relationship("Document", back_populates="categorie")


class Document(Base):
    __tablename__ = "document"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True, nullable=True)
    date_de_demande = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_de_validation = Column(DateTime(timezone=True), nullable=True)

    # Clés étrangères
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    niveau_id = Column(Integer, ForeignKey("niveau.id"), nullable=True)
    annee_univ_id = Column(String, ForeignKey("annee_univ.annee"), nullable=True)
    categorie_id = Column(Integer, ForeignKey("categori.id"), nullable=False)

    # Champs spécifiques
    pere = Column(String, nullable=True)
    mere = Column(String, nullable=True)

    status = Column(String, default=DocumentStatus.PENDING.value, nullable=False)
    est_paye = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="documents")
    niveau = relationship("Niveau", back_populates="documents")
    annee_univ = relationship("AnneeUniv", back_populates="documents", foreign_keys=[annee_univ_id])
    categorie = relationship("Categori", back_populates="documents")
    notifications = relationship("Notification", back_populates="document")
    infosupps = relationship("Infosupp", back_populates="document")

    @hybrid_property
    def document_type(self):
        """Retourne le type de document (designation de la catégorie)"""
        return self.categorie.designation if self.categorie else ""

class Infosupp(Base):
    __tablename__ = "infosupp"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    niveau = Column(String(10), nullable=True)
    annee_univ = Column(String(20), nullable=True)

    # Relationship
    document_id = Column(Integer, ForeignKey("document.id"), nullable=True)
    document = relationship("Document", back_populates="infosupps")

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("document.id"), nullable=True)
    date_de_notification = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    vue = Column(Boolean, default=False, nullable=False)
    contenu = Column(String, nullable=False)
    type_notif = Column(String, nullable=True)

    # Relations
    user = relationship("User", back_populates="notifications")
    document = relationship("Document", back_populates="notifications")


############### Extra relationship to avoid mapping error from creating elements before other
User.niveau = relationship("Niveau", back_populates="users")
Niveau.users = relationship("User", back_populates="niveau")