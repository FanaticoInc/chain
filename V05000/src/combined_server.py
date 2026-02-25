#!/usr/bin/env python3
"""
Combined HTTP + WebSocket Server for Fanatico L1 - v0.5.0.0
January 29, 2026

This module runs both:
- HTTP JSON-RPC server on port 8545
- WebSocket server on port 8546

Integrates event broadcasting from blockchain to WebSocket subscribers.
"""

import asyncio
import threading
import signal
import sys
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CombinedServer:
    """
    Runs HTTP (Flask) and WebSocket servers together.
    Provides event hooks for blockchain -> WebSocket notification.
    """

    def __init__(
        self,
        http_host: str = "0.0.0.0",
        http_port: int = 8545,
        ws_host: str = "0.0.0.0",
        ws_port: int = 8546
    ):
        self.http_host = http_host
        self.http_port = http_port
        self.ws_host = ws_host
        self.ws_port = ws_port

        self._ws_server = None
        self._ws_loop = None
        self._ws_thread = None
        self._http_thread = None
        self._running = False

    def _run_websocket_server(self):
        """Run WebSocket server in a separate thread with its own event loop"""
        from websocket_server import FanaticoWebSocketServer, WebSocketEventHooks

        self._ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._ws_loop)

        self._ws_server = FanaticoWebSocketServer()
        WebSocketEventHooks.set_server(self._ws_server, self._ws_loop)

        try:
            self._ws_loop.run_until_complete(
                self._ws_server.start(self.ws_host, self.ws_port)
            )
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
        finally:
            self._ws_loop.close()

    def _run_http_server(self, blockchain_module):
        """Run HTTP Flask server in a separate thread"""
        # Import the blockchain and Flask app
        app = blockchain_module.app
        blockchain_module.blockchain = blockchain_module.Blockchain()

        # Patch the blockchain to emit events to WebSocket
        self._patch_blockchain_events(blockchain_module.blockchain)

        app.run(
            host=self.http_host,
            port=self.http_port,
            debug=False,
            use_reloader=False,
            threaded=True
        )

    def _patch_blockchain_events(self, blockchain):
        """Patch blockchain to emit events to WebSocket subscribers"""
        from websocket_server import WebSocketEventHooks

        # Store original methods
        original_add_block = blockchain.add_block if hasattr(blockchain, 'add_block') else None
        original_add_transaction = blockchain.add_transaction if hasattr(blockchain, 'add_transaction') else None

        # Patch add_block to emit newHeads
        if original_add_block:
            def patched_add_block(*args, **kwargs):
                result = original_add_block(*args, **kwargs)
                if result:
                    block = blockchain.get_latest_block() if hasattr(blockchain, 'get_latest_block') else None
                    if block:
                        WebSocketEventHooks.on_new_block(block)
                return result
            blockchain.add_block = patched_add_block

        logger.info("Blockchain patched for WebSocket event emission")

    def start(self, blockchain_module):
        """Start both servers"""
        self._running = True

        # Start WebSocket server in background thread
        self._ws_thread = threading.Thread(
            target=self._run_websocket_server,
            daemon=True,
            name="WebSocket-Server"
        )
        self._ws_thread.start()

        logger.info(f"""
        ╔═══════════════════════════════════════════════════════════════╗
        ║           FANATICO L1 Combined Server v0.5.0.0                ║
        ╠═══════════════════════════════════════════════════════════════╣
        ║  HTTP  JSON-RPC: http://{self.http_host}:{self.http_port}
        ║  WebSocket RPC:  ws://{self.ws_host}:{self.ws_port}
        ║
        ║  Chain ID: 11111111111 (0x2964619c7)
        ║  Client: Fanatico/v0.5.0.0/python
        ╚═══════════════════════════════════════════════════════════════╝
        """)

        # Run HTTP server in main thread (blocking)
        try:
            self._run_http_server(blockchain_module)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop all servers"""
        self._running = False
        logger.info("Shutting down servers...")

        if self._ws_server and self._ws_loop:
            asyncio.run_coroutine_threadsafe(
                self._ws_server.stop(),
                self._ws_loop
            )

    def get_ws_stats(self) -> dict:
        """Get WebSocket server statistics"""
        if self._ws_server:
            return self._ws_server.get_stats()
        return {"running": False}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Fanatico L1 Combined Server')
    parser.add_argument('--http-host', default='0.0.0.0', help='HTTP server host')
    parser.add_argument('--http-port', type=int, default=8545, help='HTTP server port')
    parser.add_argument('--ws-host', default='0.0.0.0', help='WebSocket server host')
    parser.add_argument('--ws-port', type=int, default=8546, help='WebSocket server port')
    args = parser.parse_args()

    # Import the blockchain module
    import sys
    sys.path.insert(0, '/Users/sebastian/CODE/L1/V04998')
    import web3_api_v04998 as blockchain_module

    server = CombinedServer(
        http_host=args.http_host,
        http_port=args.http_port,
        ws_host=args.ws_host,
        ws_port=args.ws_port
    )

    # Handle signals
    def signal_handler(sig, frame):
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    server.start(blockchain_module)


if __name__ == '__main__':
    main()
