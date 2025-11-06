from ably import AblyRealtime
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
import asyncio
import json

from ..schemas import AblyMessage

load_dotenv()
ABLY_API_KEY = os.getenv("ABLY_API_KEY")
ably_client = AblyRealtime(ABLY_API_KEY, client_id="my-first-client")

async def send_message(msg: AblyMessage,):
    try:
        channel = ably_client.channels.get(msg.channel)
        print("Before publish")

        # Convertir le contenu en JSON avant envoi
        # content = (
        #     msg.content.model_dump() if hasattr(msg.content, "model_dump") else msg.content
        # )
        payload = jsonable_encoder(msg.content)
        print(payload)
        # Ably attend un texte ou un objet dict JSON-sérialisable
        # await channel.publish(msg.publisher, json.dumps(content))
        await channel.publish(msg.publisher, payload)

        # await channel.publish(msg.publisher, msg.content)
        # await asyncio.to_thread(channel.publish, msg.publisher, msg.content)
        print("Ably send successfully")
    except Exception as e:
        print(f"Error : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
