from ably import AblyRealtime
import os
from dotenv import load_dotenv
from fastapi import HTTPException
import asyncio

from ..schemas import AblyMessage

load_dotenv()
ABLY_API_KEY = os.getenv("ABLY_API_KEY")
ably_client = AblyRealtime(ABLY_API_KEY, client_id="my-first-client")

async def send_message(msg: AblyMessage,):
    try:
        channel = ably_client.channels.get(msg.channel)
        # await channel.publish("register", msg.content)
        await asyncio.to_thread(channel.publish, msg.publisher, msg.content)
        print("Ably send successfully")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
