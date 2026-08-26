"""
WebSocket Manager - Manejo de conexiones WebSocket para progreso en tiempo real.

Responsabilidades:
- Gestionar conexiones WebSocket activas
- Enviar actualizaciones de progreso
- Manejar desconexiones
"""

import json
from typing import Dict, Optional

from fastapi import WebSocket


class ConnectionManager:
    """
    Maneja conexiones WebSocket para el progreso en tiempo real.

    Permite enviar actualizaciones de procesamiento a clientes conectados.
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """
        Acepta una conexión WebSocket.

        Args:
            websocket: Conexión WebSocket
            client_id: ID único del cliente
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: str) -> None:
        """
        Cierra una conexión WebSocket.

        Args:
            client_id: ID único del cliente
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_progress(self, client_id: str, message: dict) -> bool:
        """
        Envía un mensaje de progreso a un cliente.

        Args:
            client_id: ID único del cliente
            message: Diccionario con el mensaje

        Returns:
            True si se envió correctamente, False si no
        """
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                return True
            except Exception:
                await self.disconnect(client_id)
                return False
        return False

    async def broadcast(self, message: dict) -> int:
        """
        Envía un mensaje a todos los clientes conectados.

        Args:
            message: Diccionario con el mensaje

        Returns:
            Cantidad de clientes que recibieron el mensaje
        """
        sent_count = 0
        disconnected = []

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
                sent_count += 1
            except Exception:
                disconnected.append(client_id)

        # Limpiar conexiones fallidas
        for client_id in disconnected:
            await self.disconnect(client_id)

        return sent_count

    def get_connection_count(self) -> int:
        """
        Obtiene la cantidad de conexiones activas.

        Returns:
            Cantidad de conexiones
        """
        return len(self.active_connections)

    def is_connected(self, client_id: str) -> bool:
        """
        Verifica si un cliente está conectado.

        Args:
            client_id: ID único del cliente

        Returns:
            True si está conectado
        """
        return client_id in self.active_connections
