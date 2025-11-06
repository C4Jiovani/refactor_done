from fastapi import BackgroundTasks
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, select, func, any_, cast, String, update, extract
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from app.models import User, Document, UserRole, DocumentStatus, Categori, Niveau, Infosupp, Notification, TypeNotif
from app.schemas import (
    UserCreate, UserUpdate, DocumentRequestCreate, DocumentRequestUpdate, DocumentRequestFilter,
    DocumentCreateSchema, DocumentRequestCLientUpdate,
    NiveauCreateRequest, AblyMessage,
    CategoriCreateRequest, PaginationMeta,
    NotificationSeenSchema, EmailSchema, UserRequestFilter, NotificationResponseSchema
)
from .services.mail_service import send_email_async
from .services.ably_service import send_message

from app.auth import get_password_hash
from typing import List, Optional
import secrets
import math
from datetime import datetime, timedelta


# --- FONCTION UTILITAIRE DE NOTIFICATION ---
def get_admin_emails(db:Session) -> List[str]:
    target_users_stmt = select(User.email).where(User.type == "admin")
    target_user_emails = db.scalars(target_users_stmt).all()

    if not target_user_emails:
        print("Aucun utilisateur cible trouvé pour recevoir la notification par email.")
        return []

    # 2. Créer les objets Notification
    admin_emails = []
    for admin in target_user_emails:
        admin_emails.append(admin)

    return admin_emails


def create_notifications_for_roles(
        db: Session,
        document: Document,
        notif_type: TypeNotif,
        content: str,
        excluded_role: Optional[str] = "etudiant",
        specific_user_id: Optional[str] = None,
) -> List[Notification]:
    """
    Crée une notification pour tous les utilisateurs n'ayant pas le rôle spécifié.
    Utilisé ici pour les notifications de type REQUEST.
    """

    # 1. Trouver les IDs des utilisateurs ciblés (tous sauf les étudiants)
    target_users_stmt = select(User.id).where(User.type != excluded_role)
    target_user_ids = db.scalars(target_users_stmt).all()

    if not target_user_ids:
        print("Aucun utilisateur cible trouvé pour recevoir la notification.")
        return []

    # 2. Créer les objets Notification
    new_notifications = []
    for user_id in target_user_ids:
        new_notif = Notification(
            user_id=user_id,
            document_id=document.id,
            contenu=content,
            type_notif=notif_type.value,
            vue=False
        )
        new_notifications.append(new_notif)
        db.add(new_notif)
        db.commit()

    return new_notifications

def create_notifications_for_user(
        db: Session,
        document: Document,
        notif_type: TypeNotif,
        # content: str,
) -> Notification:
    """
    Crée une notification pour tous les utilisateurs n'ayant pas le rôle spécifié.
    Utilisé ici pour les notifications de type REQUEST.
    """

    new_notif = Notification(
        user_id=document.user_id,
        document_id=document.id,
        contenu=document.categorie.contenu_notif,
        type_notif=notif_type.value,
        vue=False
    )

    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)

    return new_notif

def create_notifications_for_register(
        db: Session,
        new_user_id: User,
        notif_type: TypeNotif,
) -> List[Notification]:
    """
    Crée une notification pour tous les utilisateurs n'ayant pas le rôle spécifié.
    Utilisé ici pour les notifications de type REQUEST.
    """

    # 1. Trouver les IDs des utilisateurs ciblés (tous sauf les étudiants)
    target_users_stmt = select(User.id).where(User.type == "admin")
    target_user_ids = db.scalars(target_users_stmt).all()

    if not target_user_ids:
        print("Aucun utilisateur cible trouvé pour recevoir la notification.")
        return []

    # 2. Créer les objets Notification
    new_notifications = []
    for user_id in target_user_ids:
        new_notif = Notification(
            user_id=user_id,
            contenu= f"Nouvelle inscription en attente de validation. Un nouvel utilisateur est en attente d'approbation administrative. "
                     f"\n Etudiant: {new_user_id.full_name}",
            type_notif=notif_type.value,
            vue=False
        )
        new_notifications.append(new_notif)
        db.add(new_notif)
        db.commit()

    return new_notifications




# CRUD pour User
async def create_user(db: Session, user: UserCreate, background_task: BackgroundTasks) -> User:
    """Crée un nouvel utilisateur (non actif par défaut)"""
    hashed_password = get_password_hash(user.password)
    
    # Gérer matricule si non fourni
    # matricule = user.matricule if user.matricule else f"STU{secrets.token_hex(4).upper()}"
    
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
        matricule=user.matricule,
        email=user.email,
        hashed_password=hashed_password,
        nom=nom,
        prenom=prenom,
        phone=user.phone,
        niveau_id=user.niveau_id,
        fonction=user.fonction,
        date_et_lieu_naissance=user.date_et_lieu_naissance,
        is_active=False,  # Pas actif par défaut
        type=UserRole.ETUDIANT.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    notifs = create_notifications_for_register(db, db_user, TypeNotif.REGISTER)
    if len(notifs) > 0:
        notification_schema = NotificationResponseSchema(
            id=notifs[0].id,
            user=notifs[0].user,
            document=notifs[0].document,
            contenu=notifs[0].contenu,
            type_notif=notifs[0].type_notif
        )

        msg = AblyMessage(
            channel=f"admin_sco",
            publisher="register",
            content=notification_schema
        )
        await send_message(msg)


    # -------- Email preparation -----------
    admin_emails = get_admin_emails(db)

    if len(admin_emails) != 0:
        email_data = EmailSchema(
            receivers=admin_emails,
            subject="Action Requise : Nouvelle Inscription en Attente de Validation",
            body=f"Bonjour, L'utilisateur {db_user.full_name} (Matricule/Email : {db_user.matricule if db_user.matricule else db_user.email}) s'est inscrit et son compte est actuellement en attente. Votre validation est nécessaire pour lui donner accès à la plateforme.",
            optional_input=None
        )
        await send_email_async(
            email_data=email_data,
            background_tasks=background_task,
            type_notif=TypeNotif.REGISTER,
            document=None
        )
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Récupère un utilisateur par son email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_matricule(db: Session, matricule: str) -> Optional[User]:
    """Récupère un utilisateur par son matricule"""
    return db.query(User).filter(User.matricule == matricule).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Récupère un utilisateur par son ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session, filter: UserRequestFilter) -> tuple[List[User], PaginationMeta]:
    """Récupère tous les utilisateurs"""
    stmt = select(User).options(
        joinedload(User.niveau)
    )

    conditions = []
    if filter.type:
        conditions.append(User.type == filter.type)
    if filter.status:
        conditions.append(User.is_active == filter.status)
    if filter.search_term :
        search_like = f"%{filter.search_term}%"
        search_condition = (
            User.matricule.ilike(search_like)) | (
            User.nom.ilike(search_like)) | (
            User.prenom.ilike(search_like)
        )

    if conditions:
        stmt = stmt.where(and_(*conditions))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_items = db.execute(count_stmt).scalar_one()

    # --- Application de la Pagination ---
    per_page = filter.per_page
    # Calcul du nombre total de pages
    if total_items > 0:
        page_total = math.ceil(total_items / per_page)
    else:
        page_total = 0
    # S'assurer que la page demandée n'est pas hors limite
    page = filter.page
    if page > page_total and page_total > 0:
        page = page_total  # Ramener à la dernière page
    # Calcul de l'offset (skip)
    skip = (page - 1) * per_page

    stmt_final = stmt.order_by(User.id.desc())
    # Gérer le cas 'all=True' (Admin seulement)
    if filter.all is False:
        stmt_final = stmt_final.offset(skip).limit(per_page)

    result = db.execute(stmt_final)
    users = result.scalars().all()

    # Création des métadonnées de pagination
    pagination_meta = PaginationMeta(
        page=page,
        page_total=page_total,
        per_page=per_page,
        total_items=total_items
    )

    return users, pagination_meta


def get_pending_users(db: Session) -> List[User]:
    """Récupère les utilisateurs en attente de validation"""
    return db.query(User).filter(User.is_active == False, User.is_deleted == False).all()


def update_user(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
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


def delete_user(db: Session, user_id: str) -> bool:
    """Soft delete d'un utilisateur"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    db_user.is_deleted = True
    db.commit()
    return True



# CRUD pour Document (DocumentRequest est un alias)
async def create_document_request(
        db: Session,
        request: DocumentCreateSchema,
        user_id: str,
        background_task: BackgroundTasks
) -> Document:
    """Crée une nouvelle demande de document"""
    # 1.1 Créer l'objet Document
    db_request = Document(
        user_id=UUID(user_id),  # Assurez-vous de convertir l'ID utilisateur en UUID si nécessaire
        pere=request.pere,
        mere=request.mere,
        categorie_id=request.categorie_id
        # Les champs 'status' et 'est_paye' sont gérés par défaut/modèle
    )
    db.add(db_request)

    if request.infosupps:
        infosupps_to_create = []
        for info_data in request.infosupps:
            # Crée un objet Infosupp à partir des données Pydantic
            # Nous n'avons pas besoin d'associer document_id ici, SQLAlchemy le fera
            # automatiquement via la relation lors de l'ajout à la liste
            new_infosupp = Infosupp(
                niveau=info_data.niveau,
                annee_univ=info_data.annee_univ
                # L'association db_request.infosupps gère la clé étrangère
            )
            infosupps_to_create.append(new_infosupp)

        # 3.2 Ajouter les Infosupps au document (ceci définit automatiquement document_id)
        db_request.infosupps.extend(infosupps_to_create)

    # --- 4. Exécution et Retour ---
    try:
        # Exécuter l'insertion du Document, des InfoSupps et des entrées d'association
        db.commit()
        # Rafraîchir l'objet pour obtenir l'ID généré et les relations chargées
        db.refresh(db_request)
    except Exception as e:
        db.rollback()
        # Log l'erreur détaillée si possible
        print(f"Erreur lors de la création du document et de ses relations : {e}")
        raise e

    # --- 5. Création des Notifications (Après le Commit) ---
    notif_content = f"Nouvelle demande de document à examiner N°: {db_request.numero}, Categori : {db_request.categorie.designation})."

    # Créer une notification pour tous les utilisateurs sauf "student"
    notifs = create_notifications_for_roles(
        db=db,
        document=db_request,
        notif_type=TypeNotif.REQUEST,
        content=notif_content,
        excluded_role="etudiant"
    )

    if len(notifs) > 0:
        notification_schema = NotificationResponseSchema(
            id=notifs[0].id,
            user=notifs[0].user,
            document=notifs[0].document,
            contenu=notifs[0].contenu,
            type_notif=notifs[0].type_notif
        )

        msg = AblyMessage(
            channel=f"admin_sco",
            publisher="request",
            content=notification_schema
        )
        await send_message(msg)

    # Il est crucial de faire un second commit pour les notifications.
    # On pourrait aussi envelopper tout dans une seule transaction,
    # mais un commit séparé est acceptable si le système de notification est secondaire.
    try:
        db.commit()
        # pass
    except Exception as e:
        # La création du document a réussi, mais la notification a échoué.
        # On pourrait logguer ceci sans faire un rollback du document.
        print(f"Erreur lors du commit des notifications : {e}")
        db.rollback()

    # -------- Email preparation -----------
    admin_emails = get_admin_emails(db)
    if len(admin_emails) != 0:
        email_data = EmailSchema(
            receivers=admin_emails,
            subject=f"Demande Étudiante Reçue : {db_request.categorie.designation}",
            body=f"Une nouvelle demande de document vient d'être soumise par l'étudiant {db_request.user.full_name} (Matricule : {db_request.user.matricule}). La demande concerne : {db_request.categorie.designation}. Veuillez examiner cette demande depuis le tableau de bord.",
            optional_input=None
        )
        await send_email_async(
            email_data=email_data,
            background_tasks=background_task,
            type_notif=TypeNotif.REQUEST,
            document=db_request
        )

    return db_request

# CRUD pour Document (DocumentRequest est un alias)
def update_document_client_request(db: Session, request: DocumentRequestCLientUpdate, document_id: int) -> Document:
    """Crée une nouvelle demande de document"""
    # 1.1 Recuperer le document en question
    db_request = db.get(Document, document_id)
    if not db_request:
        raise ValueError(f"Document with ID {document_id} not found.")

    if request.pere is not None :
        db_request.pere = request.pere
    if request.mere is not None:
        db_request.pere = request.mere
    if request.categorie_id is not None:
        db_request.categorie_id = request.categorie_id

    print(db_request.categorie.with_info)

    if request.infosupps is not None and db_request.categorie.with_info:
        for info in db_request.infosupps:
            db.delete(info)
        db_request.infosupps = [] # Puis réinitialiser la collection

        new_infosupps = []
        for info_data in request.infosupps:
            new_infosupp = Infosupp(
                niveau=info_data.niveau,
                annee_univ=info_data.annee_univ
            )
            new_infosupps.append(new_infosupp)

        db_request.infosupps.extend(new_infosupps)
    try:
        # Un seul commit est nécessaire pour tout enregistrer (Document, suppressions, ajouts)
        db.commit()
        db.refresh(db_request)
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la mise à jour du document : {e}")
        raise e

    return db_request


def get_document_request_by_id(db: Session, request_id: int) -> Optional[Document]:
    """Récupère une demande par son ID"""
    result = db.query(Document).options(
        selectinload(Document.infosupps)
    ).filter(Document.id == request_id).first()

    # Vérifiez si les données existent
    if result:
        print(f"Nombre d'infosupp: {len(result.infosupps)}")
        for info in result.infosupps:
            print(f"Infosupp: {info.niveau}, {info.annee_univ}")
    else :
        print(f"Aucun info supp trouver")

    result = db.query(Document).options(
        # joinedload(Document.categorie),
        # joinedload(Document.user),
        # joinedload(Document.infosupps)
        selectinload(Document.categorie),
        selectinload(Document.user),
        selectinload(Document.infosupps)
    ).filter(Document.id == request_id).first()

    return result


def get_all_document_requests(db: Session, skip: int = 0, limit: int = 100) -> List[Document]:
    """Récupère toutes les demandes"""
    return db.query(Document).options(joinedload(Document.categorie), joinedload(Document.user)).offset(skip).limit(limit).all()


def get_user_document_requests(db: Session, user_id: int) -> List[Document]:
    """Récupère toutes les demandes d'un utilisateur"""
    return db.query(Document).options(joinedload(Document.categorie)).filter(Document.user_id == user_id).all()


def get_document_requests_filtered(
        db: Session,
        filters: DocumentRequestFilter,
        current_user: User,
) -> tuple[List[Document], PaginationMeta]:
    # --- 1. Requête de base ---
    # Démarre la sélection des Documents avec jointures pour éviter les requêtes N+1
    stmt = select(Document).options(
        selectinload(Document.categorie),
        selectinload(Document.user),
        selectinload(Document.infosupps)
    )

    # --- 2. Construction de la clause WHERE ---

    # Filtre spécifique à l'utilisateur (obligatoire si ce n'est pas un admin)
    if current_user.role != "admin":
        stmt = stmt.where(Document.user_id == current_user.id)

    conditions = []
    # Filtre par statut
    if filters.status:
        conditions.append(Document.status == filters.status)
    if filters.categorie_id is not None:
        conditions.append(Document.categorie_id == filters.categorie_id)
        # conditions.append(Document.categories.any(Categori.id.in_(filters.categorie_id)))
    if filters.start_date:
        conditions.append(Document.date_de_demande >= filters.start_date)
    if filters.end_date:
        conditions.append(Document.date_de_demande <= filters.end_date)

    # Filtre de Recherche Libre (Nom, Matricule, Numéro de document)
    if filters.search_term:
        search_like = f"%{filters.search_term}%"
        search_condition = (
           User.nom.ilike(search_like)) | (
           User.matricule.ilike(search_like)) | (
           cast(Document.numero, String).ilike(search_like)
        )
        # Pour rechercher sur les champs utilisateur, il faut joindre la table User
        # SQLAlchemy est suffisamment intelligent pour ne joindre qu'une seule fois.
        stmt = stmt.join(Document.user)
        conditions.append(search_condition)

    # Application de tous les filtres à la requête
    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Ajout de la pagination et exécution
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_items = db.execute(count_stmt).scalar_one()

    # --- Application de la Pagination ---
    per_page = filters.per_page
    # Calcul du nombre total de pages
    if total_items > 0:
        page_total = math.ceil(total_items / per_page)
    else:
        page_total = 0

    # S'assurer que la page demandée n'est pas hors limite
    page = filters.page
    if page > page_total and page_total > 0:
        page = page_total  # Ramener à la dernière page
    # Calcul de l'offset (skip)
    skip = (page - 1) * per_page

    # Création du statement final avec LIMIT et OFFSET
    stmt_final = stmt.order_by(Document.date_de_demande.desc())

    # Gérer le cas 'all=True' (Admin seulement)
    if filters.all is False:
        stmt_final = stmt_final.offset(skip).limit(per_page)

    result = db.execute(stmt_final)
    documents = result.scalars().all()

    # Création des métadonnées de pagination
    pagination_meta = PaginationMeta(
        page=page,
        page_total=page_total,
        per_page=per_page,
        total_items=total_items
    )

    return documents, pagination_meta




async def update_document_request(
    db: Session,
    request_id: int,
    request_update: DocumentRequestUpdate,
    background_task: BackgroundTasks,
) -> Optional[Document]:
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
                # 'en attente': DocumentStatus.PENDING.value,
                'pending': DocumentStatus.PENDING.value,
                # 'validée': DocumentStatus.VALIDATE.value,
                'validate': DocumentStatus.VALIDATE.value,
                # 'refusée': DocumentStatus.REFUSE.value,
                'refused': DocumentStatus.REFUSE.value
            }
            value = status_mapping.get(value.lower(), value)
        setattr(db_request, field, value)

    db_request.updated_at = datetime.now()
    notifiation_schema = None
    # Si le statut passe à validé, mettre à jour date_de_validation
    if update_data.get('status') == DocumentStatus.VALIDATE.value:
        db_request.date_de_validation = datetime.now()


        # --- 5. Création des Notifications (Après le Commit) ---
        notif = create_notifications_for_user(
            db=db,
            document=db_request,
            notif_type=TypeNotif.VALIDATION,
        )
        notification_schema = NotificationResponseSchema(
            id=notif.id,
            user=notif.user,
            document=notif.document,
            contenu=notif.contenu,
            type_notif=notif.type_notif
        )

        msg = AblyMessage(
            channel=f"client-{notif.user.id}",
            publisher="validation",
            content=notification_schema
        )
        await send_message(msg)

    try:
        db.commit()
        db.refresh(db_request)
    except Exception as e:
        print(f"Erreur lors du commit des notifications : {e}")
        db.rollback()



    # ----------------- EMAIL FUNCTION ----------------

    email_data = EmailSchema(
        receivers=[db_request.user.email],
        subject=f"Votre Demande de Document (N°: {db_request.numero}) a été Validée",
        body=f"Nous avons le plaisir de vous informer que votre demande (N°: {db_request.numero}) concernant {db_request.categorie.designation} a été examinée et approuvée par nos services. Vous pouvez désormais la retirer auprès de la scolarité.",
        optional_input=None
    )
    await send_email_async(
        email_data=email_data,
        background_tasks=background_task,
        type_notif=TypeNotif.VALIDATION,
        document=db_request
    )

    return db_request


def delete_document_request(db: Session, request_id: int) -> bool:
    """Supprime une demande"""
    db_request = db.query(Document).filter(Document.id == request_id).first()
    if not db_request:
        return False

    db_request.is_deleted = True
    # db.delete(db_request)
    # db.commit()
    db.commit()
    db.refresh(db_request)
    return True


# Alias pour compatibilité
DocumentRequest = Document

# ==================== FUNCTION NIVEAU (CRUD) ====================
def get_all_niveau(db:Session) -> List[Niveau]:
    stmt = select(Niveau)
    result = db.execute(stmt)
    niveaux = result.scalars().all()
    return niveaux

def get_a_niveau(db:Session, niveau_id: int) -> Niveau|None:
    stmt = select(Niveau).where(Niveau.id == niveau_id)
    result = db.execute(stmt)
    niveaux = result.scalar_one_or_none()
    return niveaux

def create_niveau(db:Session, request: NiveauCreateRequest) -> Niveau | None:
    try:
        db_request = Niveau(designation=request.designation)
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except IntegrityError:
        db.rollback()
        return None


def update_niveau(db:Session, request: NiveauCreateRequest, niveau_id: int) -> Niveau | None:
    try:
        niveau = get_a_niveau(db, niveau_id)
        if niveau is None:
            return None

        niveau.designation = request.designation
        db.commit()
        db.refresh(niveau)
        return niveau
    except IntegrityError:
        db.rollback()
        return None

def delete_niveau(db: Session, niveau_id: int) -> bool:
    """Supprime une demande"""
    db_request = db.query(Niveau).filter(Niveau.id == niveau_id).first()
    if not db_request:
        return False
    db.delete(db_request)
    db.commit()
    return True

# ==================== FUNCTION NIVEAU (CRUD) ====================
def get_all_categori(db:Session) -> List[Categori]:
    stmt = select(Categori)
    result = db.execute(stmt)
    categories = result.scalars().all()
    return categories

def get_a_categori(db:Session, categori_id: int) -> Categori|None:
    stmt = select(Categori).where(Categori.id == categori_id)
    result = db.execute(stmt)
    categories = result.scalar_one_or_none()
    return categories

def create_categori(db:Session, request: CategoriCreateRequest) -> Categori | None:
    try:
        db_request = Categori(
            designation=request.designation,
            slug=request.slug,
            type=request.type,
            icon=request.icon,
            path=request.path,
            montant=request.montant,
            contenu_notif=request.contenu_notif,
            is_visible=True,
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request
    except IntegrityError:
        db.rollback()
        return None

def update_categori(db:Session, request: CategoriCreateRequest, categori_id: int) -> Categori | None:
    try:
        categori = get_a_categori(db, categori_id)
        if categori is None:
            return None

        categori.designation = request.designation
        categori.slug = request.slug
        categori.type = request.type
        categori.icon = request.icon
        categori.path = request.path
        categori.montant = request.montant
        categori.contenu_notif = request.contenu_notif
        categori.is_visible = request.is_visible

        db.commit()
        db.refresh(categori)
        return categori
    except IntegrityError:
        db.rollback()
        return None

def delete_categori(db: Session, categori_id: int) -> bool:
    """Supprime une demande"""
    db_request = db.query(Categori).filter(Categori.id == categori_id).first()
    if not db_request:
        return False
    db.delete(db_request)
    db.commit()
    return True


# ==================== FUNCTION NOTIFICATION (CRUD) ====================
def get_notification_for_active_user(db: Session, user_id) -> List[Notification]:
    stmt = select(Notification).where(
        Notification.user_id == user_id
    ).order_by(
        Notification.date_de_notification.desc()
    )
    result = db.execute(stmt).scalars().all()
    return result

def mark_as_seen(db: Session, notif_ids: List[int], user_uuid: UUID):
    if not notif_ids:
        return 0

    try:
        # On utilise 'update()' avec DEUX conditions dans le where :
        stmt = update(Notification).where(
            Notification.id.in_(notif_ids),
            # Condition de sécurité essentielle : la notification doit appartenir à l'utilisateur
            Notification.user_id == user_uuid
        ).values(
            vue=True
        )

        result = db.execute(stmt)
        db.commit()

        return result.rowcount

    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la mise à jour des notifications comme vues : {e}")
        raise e

async def get_all_stats_for_dashboard(db:Session):
    current_month = datetime.now().month
    current_year = datetime.now().year
    twelve_months_ago = datetime.now() - timedelta(days=365)

    # === 1️⃣ Indicateurs généraux ===
    total_docs = db.query(func.count(Document.id)).scalar()
    total_pending = db.query(func.count()).filter(Document.status == DocumentStatus.PENDING).scalar()
    total_validated = db.query(func.count()).filter(Document.status == DocumentStatus.VALIDATE).scalar()
    total_refused = db.query(func.count()).filter(Document.status == DocumentStatus.REFUSE).scalar()
    total_paid = db.query(func.count()).filter(Document.est_paye == True).scalar()

    total_students = db.query(func.count()).filter(User.type == "etudiant").scalar()
    total_students_pending = (db.query(func.count(User.id))
          .filter(User.type == "etudiant", User.is_active == False).scalar())

    # Montant total encaissé
    total_revenue = (
        db.query(func.sum(Categori.montant))
        .join(Document, Document.categorie_id == Categori.id)
        .filter(Document.est_paye == True)
        .scalar()
    ) or 0.0

    # === 2️⃣ Statistiques temporelles ===
    dmd_this_month = (
        db.query(func.count(Document.id))
        .filter(extract("month", Document.date_de_demande) == current_month)
        .scalar()
    )
    validated_this_month = (
        db.query(func.count(Document.id))
        .filter(
            Document.status == DocumentStatus.VALIDATE,
            extract("month", Document.date_de_validation) == current_month
        )
        .scalar()
    )

    # === 3️⃣ Répartition par catégorie ===
    docs_by_category = (
        db.query(Categori.designation, func.count(Document.id))
        .join(Document, Document.categorie_id == Categori.id)
        .filter(Document.date_de_demande >= twelve_months_ago)
        .group_by(Categori.designation)
        .all()
    )

    # === 4️⃣ Répartition par niveau ===
    docs_by_level = (
        db.query(Niveau.designation, func.count(Document.id))
        .join(Document, Document.niveau_id == Niveau.id)
        .group_by(Niveau.designation)
        .all()
    )

    return {
        "global": {
            "total_documents": total_docs,
            "pending": total_pending,
            "validated": total_validated,
            "refused": total_refused,
            "paid": total_paid,
            "students": total_students,
            "students_pending": total_students_pending,
            "total_revenue": total_revenue,
            # "average_validation_delay_h": avg_validation_delay or 0
        },
        "monthly": {
            "documents_this_month": dmd_this_month,
            "validated_this_month": validated_this_month,
        },
        "by_category": [
            {"category": cat, "count": count} for cat, count in docs_by_category
        ],
        # "by_level": [
        #     {"level": lvl, "count": count} for lvl, count in docs_by_level
        # ],
        # "notifications": {
        #     "total": total_notifications,
        #     "unread": total_unread
        # }
    }








