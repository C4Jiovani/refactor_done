import os
from typing import Optional
from..schemas import EmailSchema
from ..models import TypeNotif, Document
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).parent

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER"),
    MAIL_PASSWORD=os.getenv("SMTP_PASS"),
    MAIL_FROM=os.getenv("SMTP_FROM"),
    MAIL_PORT=os.getenv("SMTP_PORT"),
    MAIL_SERVER=os.getenv("SMTP_HOST"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email_async(
        email_data: EmailSchema,
        background_tasks: BackgroundTasks,
        type_notif: TypeNotif,
        document: Document = None
):
    """
    Crée le message en utilisant un template HTML externe, le personnalise 
    et l'ajoute aux BackgroundTasks pour un envoi asynchrone.
    """
    template_path = BASE_DIR / "template_email.html"

    if not os.path.exists(template_path):
        print(f"ERREUR: Template file not found at: {template_path.resolve()}")
        return

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()
    except IOError as e:
        print(f"ERREUR: Impossible de lire le fichier template : {e}")
        return

    type_text = ""

    if type_notif.value == TypeNotif.REGISTER.value:
        # type_text = "Action Requise : Nouvelle Inscription en Attente de Validation"
        type_text = f"Nouvelle inscription en attente de validation. Un nouvel utilisateur est en attente d'approbation administrative. "
    elif type_notif.value == TypeNotif.REQUEST.value and document is not None:
        # type_text = f"Demande Étudiante Reçue : {document.categorie.designation}"
        type_text = f"Nouvelle demande de document à examiner (N°: {document.numero}, Categori : {document.categorie.designation})."
    elif type_notif.value == TypeNotif.VALIDATION.value and document is not None:
        # type_text = f"Votre Demande de Document (N°: {document.numero}) a été Validée"
        type_text = f"Votre Demande de Document (N°: {document.numero}) a été Validée"
    else :
        type_text = f"Notification speci[Numéro_Document]fique."

    html_template = html_template.replace("{{ sujet }}", type_text)
    html_template = html_template.replace("{{ type_notif }}", type_text)
    html_template = html_template.replace("{{ message }}", email_data.body)

    message = MessageSchema(
        subject = email_data.subject,
        recipients = [*email_data.receivers],
        body = html_template,
        subtype = MessageType.html
    )

    fm = FastMail(conf)

    background_tasks.add_task(fm.send_message, message)
    # try:
    #     await fm.send_message(message)
    #     print(f"DEBUG: Email envoyé avec succès à {email_data.destinataire}")
    # except Exception as e:
    #     # Si vous voyez cette erreur, c'est que la configuration SMTP est fausse.
    #     print(f"ERREUR CRITIQUE D'ENVOI SMTP : {e}")

