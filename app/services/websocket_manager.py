from typing import Dict, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """Gère les connexions WebSocket pour les notifications en temps réel"""
    
    def __init__(self):
        # Dictionnaire pour stocker les connexions : {user_id: {websocket1, websocket2, ...}}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connecte un utilisateur via WebSocket"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Déconnecte un utilisateur"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Envoie un message à un utilisateur spécifique"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Nettoyer les connexions déconnectées
            for connection in disconnected:
                self.disconnect(connection, user_id)
    
    async def broadcast_to_admins(self, message: dict):
        """Envoie un message à tous les administrateurs connectés"""
        # Pour simplifier, on peut envoyer à tous les utilisateurs
        # ou maintenir une liste séparée d'admins
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


# Instance globale du gestionnaire de connexions
manager = ConnectionManager()


