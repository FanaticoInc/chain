#!/usr/bin/env python3
"""
WebSocket Server for Fanatico L1 - v0.5.0.0
January 29, 2026

Implements Ethereum JSON-RPC WebSocket API:
- eth_subscribe: Subscribe to real-time events
- eth_unsubscribe: Unsubscribe from events

Subscription Types:
- newHeads: New block headers
- logs: Contract event logs (with filter)
- newPendingTransactions: Pending transaction hashes
- syncing: Sync status changes

Port: 8546 (standard Ethereum WebSocket port)
"""

import asyncio
import json
import logging
import uuid
import time
from typing import Dict, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import websockets
from websockets.server import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
WS_HOST = "0.0.0.0"
WS_PORT = 8546
MAX_CONNECTIONS = 1000
PING_INTERVAL = 30  # seconds
PING_TIMEOUT = 10  # seconds
MAX_SUBSCRIPTIONS_PER_CONNECTION = 100


@dataclass
class LogFilter:
    """Filter for log subscriptions"""
    address: Optional[str] = None
    addresses: list = field(default_factory=list)
    topics: list = field(default_factory=list)

    def matches(self, log: dict) -> bool:
        """Check if a log matches this filter"""
        # Address filter
        if self.address:
            if log.get('address', '').lower() != self.address.lower():
                return False
        if self.addresses:
            if log.get('address', '').lower() not in [a.lower() for a in self.addresses]:
                return False

        # Topics filter
        if self.topics:
            log_topics = log.get('topics', [])
            for i, topic in enumerate(self.topics):
                if topic is None:
                    continue
                if i >= len(log_topics):
                    return False
                if isinstance(topic, list):
                    if log_topics[i] not in topic:
                        return False
                elif log_topics[i] != topic:
                    return False

        return True


@dataclass
class Subscription:
    """Represents a single subscription"""
    id: str
    type: str  # 'newHeads', 'logs', 'newPendingTransactions', 'syncing'
    connection: WebSocketServerProtocol
    created_at: float = field(default_factory=time.time)
    filter: Optional[LogFilter] = None


class SubscriptionManager:
    """Manages all WebSocket subscriptions"""

    def __init__(self):
        self.subscriptions: Dict[str, Subscription] = {}
        self.connections: Dict[WebSocketServerProtocol, Set[str]] = defaultdict(set)
        self.type_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def add_subscription(
        self,
        sub_type: str,
        connection: WebSocketServerProtocol,
        filter_params: Optional[dict] = None
    ) -> str:
        """Add a new subscription and return subscription ID"""
        async with self._lock:
            # Check subscription limit per connection
            if len(self.connections[connection]) >= MAX_SUBSCRIPTIONS_PER_CONNECTION:
                raise ValueError(f"Maximum subscriptions ({MAX_SUBSCRIPTIONS_PER_CONNECTION}) reached")

            sub_id = "0x" + uuid.uuid4().hex[:32]

            # Create log filter if needed
            log_filter = None
            if sub_type == 'logs' and filter_params:
                log_filter = LogFilter(
                    address=filter_params.get('address'),
                    addresses=filter_params.get('addresses', []),
                    topics=filter_params.get('topics', [])
                )

            subscription = Subscription(
                id=sub_id,
                type=sub_type,
                connection=connection,
                filter=log_filter
            )

            self.subscriptions[sub_id] = subscription
            self.connections[connection].add(sub_id)
            self.type_subscriptions[sub_type].add(sub_id)

            logger.info(f"Added subscription {sub_id} type={sub_type}")
            return sub_id

    async def remove_subscription(self, sub_id: str) -> bool:
        """Remove a subscription by ID"""
        async with self._lock:
            if sub_id not in self.subscriptions:
                return False

            subscription = self.subscriptions[sub_id]
            self.connections[subscription.connection].discard(sub_id)
            self.type_subscriptions[subscription.type].discard(sub_id)
            del self.subscriptions[sub_id]

            logger.info(f"Removed subscription {sub_id}")
            return True

    async def remove_connection(self, connection: WebSocketServerProtocol):
        """Remove all subscriptions for a connection"""
        async with self._lock:
            sub_ids = list(self.connections.get(connection, set()))
            for sub_id in sub_ids:
                if sub_id in self.subscriptions:
                    subscription = self.subscriptions[sub_id]
                    self.type_subscriptions[subscription.type].discard(sub_id)
                    del self.subscriptions[sub_id]

            if connection in self.connections:
                del self.connections[connection]

            logger.info(f"Removed {len(sub_ids)} subscriptions for disconnected client")

    async def get_subscriptions_by_type(self, sub_type: str) -> list:
        """Get all subscriptions of a specific type"""
        async with self._lock:
            sub_ids = self.type_subscriptions.get(sub_type, set())
            return [self.subscriptions[sid] for sid in sub_ids if sid in self.subscriptions]

    def get_stats(self) -> dict:
        """Get subscription statistics"""
        return {
            "total_subscriptions": len(self.subscriptions),
            "total_connections": len(self.connections),
            "by_type": {t: len(subs) for t, subs in self.type_subscriptions.items()}
        }


class FanaticoWebSocketServer:
    """Main WebSocket server for Fanatico L1"""

    def __init__(self, blockchain_ref=None):
        self.subscription_manager = SubscriptionManager()
        self.blockchain = blockchain_ref
        self._server = None
        self._running = False
        self._broadcast_tasks: Set[asyncio.Task] = set()

    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new WebSocket connection"""
        client_addr = websocket.remote_address
        logger.info(f"New WebSocket connection from {client_addr}")

        try:
            async for message in websocket:
                try:
                    response = await self.handle_message(websocket, message)
                    if response:
                        await websocket.send(json.dumps(response))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
                    await websocket.send(json.dumps(error_response))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed from {client_addr}")
        finally:
            await self.subscription_manager.remove_connection(websocket)

    async def handle_message(self, websocket: WebSocketServerProtocol, message: str) -> Optional[dict]:
        """Handle incoming JSON-RPC message"""
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }

        request_id = data.get("id")
        method = data.get("method", "")
        params = data.get("params", [])

        # Route to appropriate handler
        if method == "eth_subscribe":
            return await self.handle_subscribe(request_id, params, websocket)
        elif method == "eth_unsubscribe":
            return await self.handle_unsubscribe(request_id, params)
        else:
            # Forward other methods to HTTP RPC (if available)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}. Use HTTP RPC on port 8545 for non-subscription methods."
                }
            }

    async def handle_subscribe(
        self,
        request_id: Any,
        params: list,
        websocket: WebSocketServerProtocol
    ) -> dict:
        """Handle eth_subscribe request"""
        if not params:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Invalid params: subscription type required"
                }
            }

        sub_type = params[0]
        filter_params = params[1] if len(params) > 1 else None

        # Validate subscription type
        valid_types = ['newHeads', 'logs', 'newPendingTransactions', 'syncing']
        if sub_type not in valid_types:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": f"Invalid subscription type: {sub_type}. Valid types: {valid_types}"
                }
            }

        try:
            sub_id = await self.subscription_manager.add_subscription(
                sub_type, websocket, filter_params
            )
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": sub_id
            }
        except ValueError as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }

    async def handle_unsubscribe(self, request_id: Any, params: list) -> dict:
        """Handle eth_unsubscribe request"""
        if not params:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Invalid params: subscription ID required"
                }
            }

        sub_id = params[0]
        success = await self.subscription_manager.remove_subscription(sub_id)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": success
        }

    async def broadcast_new_head(self, block: dict):
        """Broadcast new block header to all newHeads subscribers"""
        subscriptions = await self.subscription_manager.get_subscriptions_by_type('newHeads')

        # Format block header according to Ethereum spec
        header = {
            "difficulty": block.get("difficulty", "0x0"),
            "extraData": block.get("extraData", "0x"),
            "gasLimit": block.get("gasLimit", "0xe4e1c0"),
            "gasUsed": block.get("gasUsed", "0x0"),
            "hash": block.get("hash"),
            "logsBloom": block.get("logsBloom", "0x" + "0" * 512),
            "miner": block.get("miner", "0x0000000000000000000000000000000000000000"),
            "mixHash": block.get("mixHash", "0x" + "0" * 64),
            "nonce": block.get("nonce", "0x0000000000000000"),
            "number": block.get("number"),
            "parentHash": block.get("parentHash"),
            "receiptsRoot": block.get("receiptsRoot", "0x" + "0" * 64),
            "sha3Uncles": block.get("sha3Uncles", "0x" + "0" * 64),
            "stateRoot": block.get("stateRoot", "0x" + "0" * 64),
            "timestamp": block.get("timestamp"),
            "transactionsRoot": block.get("transactionsRoot", "0x" + "0" * 64),
            "baseFeePerGas": block.get("baseFeePerGas", "0x4a817c800"),  # 20 Gwei
        }

        for sub in subscriptions:
            notification = {
                "jsonrpc": "2.0",
                "method": "eth_subscription",
                "params": {
                    "subscription": sub.id,
                    "result": header
                }
            }
            try:
                await sub.connection.send(json.dumps(notification))
            except Exception as e:
                logger.error(f"Error sending newHead notification: {e}")

    async def broadcast_logs(self, logs: list):
        """Broadcast logs to matching log subscribers"""
        subscriptions = await self.subscription_manager.get_subscriptions_by_type('logs')

        for sub in subscriptions:
            matching_logs = []
            for log in logs:
                if sub.filter is None or sub.filter.matches(log):
                    matching_logs.append(log)

            if matching_logs:
                for log in matching_logs:
                    notification = {
                        "jsonrpc": "2.0",
                        "method": "eth_subscription",
                        "params": {
                            "subscription": sub.id,
                            "result": log
                        }
                    }
                    try:
                        await sub.connection.send(json.dumps(notification))
                    except Exception as e:
                        logger.error(f"Error sending log notification: {e}")

    async def broadcast_pending_transaction(self, tx_hash: str):
        """Broadcast pending transaction hash to subscribers"""
        subscriptions = await self.subscription_manager.get_subscriptions_by_type('newPendingTransactions')

        for sub in subscriptions:
            notification = {
                "jsonrpc": "2.0",
                "method": "eth_subscription",
                "params": {
                    "subscription": sub.id,
                    "result": tx_hash
                }
            }
            try:
                await sub.connection.send(json.dumps(notification))
            except Exception as e:
                logger.error(f"Error sending pending tx notification: {e}")

    async def broadcast_syncing(self, syncing_status: Any):
        """Broadcast syncing status changes"""
        subscriptions = await self.subscription_manager.get_subscriptions_by_type('syncing')

        for sub in subscriptions:
            notification = {
                "jsonrpc": "2.0",
                "method": "eth_subscription",
                "params": {
                    "subscription": sub.id,
                    "result": syncing_status
                }
            }
            try:
                await sub.connection.send(json.dumps(notification))
            except Exception as e:
                logger.error(f"Error sending syncing notification: {e}")

    async def start(self, host: str = WS_HOST, port: int = WS_PORT):
        """Start the WebSocket server"""
        self._running = True
        self._server = await websockets.serve(
            self.handle_connection,
            host,
            port,
            ping_interval=PING_INTERVAL,
            ping_timeout=PING_TIMEOUT,
            max_size=2**20,  # 1MB max message size
            max_queue=32
        )

        logger.info(f"""
        ╔═══════════════════════════════════════════════════════════════╗
        ║      FANATICO L1 WebSocket Server v0.5.0.0                    ║
        ╠═══════════════════════════════════════════════════════════════╣
        ║  WebSocket URL: ws://{host}:{port}
        ║  Max Connections: {MAX_CONNECTIONS}
        ║  Ping Interval: {PING_INTERVAL}s
        ║
        ║  Supported Methods:
        ║  - eth_subscribe
        ║  - eth_unsubscribe
        ║
        ║  Subscription Types:
        ║  - newHeads: New block headers
        ║  - logs: Contract event logs (with filter)
        ║  - newPendingTransactions: Pending tx hashes
        ║  - syncing: Sync status changes
        ╚═══════════════════════════════════════════════════════════════╝
        """)

        await self._server.wait_closed()

    async def stop(self):
        """Stop the WebSocket server"""
        self._running = False
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        # Cancel all broadcast tasks
        for task in self._broadcast_tasks:
            task.cancel()

        logger.info("WebSocket server stopped")

    def get_stats(self) -> dict:
        """Get server statistics"""
        return {
            "running": self._running,
            "subscriptions": self.subscription_manager.get_stats()
        }


# Event hook functions for integration with main blockchain
class WebSocketEventHooks:
    """
    Event hooks to integrate WebSocket server with main blockchain.
    Call these from the main Flask API when events occur.
    """

    _server: Optional[FanaticoWebSocketServer] = None
    _loop: Optional[asyncio.AbstractEventLoop] = None

    @classmethod
    def set_server(cls, server: FanaticoWebSocketServer, loop: asyncio.AbstractEventLoop):
        """Set the WebSocket server instance"""
        cls._server = server
        cls._loop = loop

    @classmethod
    def on_new_block(cls, block: dict):
        """Called when a new block is created"""
        if cls._server and cls._loop:
            asyncio.run_coroutine_threadsafe(
                cls._server.broadcast_new_head(block),
                cls._loop
            )

    @classmethod
    def on_logs(cls, logs: list):
        """Called when new logs are emitted"""
        if cls._server and cls._loop:
            asyncio.run_coroutine_threadsafe(
                cls._server.broadcast_logs(logs),
                cls._loop
            )

    @classmethod
    def on_pending_transaction(cls, tx_hash: str):
        """Called when a new pending transaction is received"""
        if cls._server and cls._loop:
            asyncio.run_coroutine_threadsafe(
                cls._server.broadcast_pending_transaction(tx_hash),
                cls._loop
            )

    @classmethod
    def on_syncing_change(cls, syncing_status: Any):
        """Called when sync status changes"""
        if cls._server and cls._loop:
            asyncio.run_coroutine_threadsafe(
                cls._server.broadcast_syncing(syncing_status),
                cls._loop
            )


async def main():
    """Main entry point for standalone WebSocket server"""
    server = FanaticoWebSocketServer()

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop()


if __name__ == '__main__':
    asyncio.run(main())
