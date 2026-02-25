#!/usr/bin/env python3
"""
Fanatico L1 Metrics Exporter for Prometheus
v0.5.0.0 - January 29, 2026

Exports blockchain-specific metrics:
- Block height and production rate
- Transaction counts and pending pool
- RPC request metrics
- Account balances (optional)
- Chain health indicators

Port: 9546 (default)
"""

import argparse
import json
import logging
import time
import threading
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
RPC_URL = "http://localhost:8545"
METRICS_PORT = 9546
SCRAPE_INTERVAL = 15  # seconds
CHAIN_ID = 11111111111


class FanaticoMetrics:
    """Collects and stores Fanatico blockchain metrics."""

    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._request_id = 0

    def _rpc_call(self, method: str, params: list = None) -> Optional[Dict]:
        """Make an RPC call to the Fanatico node."""
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": self._request_id
        }

        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"RPC call failed: {method} - {e}")
            return None

    def collect(self):
        """Collect all metrics from the Fanatico node."""
        start_time = time.time()
        metrics = {}

        # Node status
        metrics['fanatico_up'] = 1

        # Chain ID
        result = self._rpc_call("eth_chainId")
        if result and "result" in result:
            chain_id = int(result["result"], 16)
            metrics['fanatico_chain_id'] = chain_id
            if chain_id != CHAIN_ID:
                logger.warning(f"Unexpected chain ID: {chain_id}")
        else:
            metrics['fanatico_up'] = 0

        # Block number
        result = self._rpc_call("eth_blockNumber")
        if result and "result" in result:
            block_number = int(result["result"], 16)
            metrics['fanatico_block_number'] = block_number

            # Get block details
            block_result = self._rpc_call("eth_getBlockByNumber", [result["result"], False])
            if block_result and "result" in block_result and block_result["result"]:
                block = block_result["result"]
                metrics['fanatico_block_timestamp'] = int(block.get("timestamp", "0x0"), 16)
                metrics['fanatico_block_gas_used'] = int(block.get("gasUsed", "0x0"), 16)
                metrics['fanatico_block_gas_limit'] = int(block.get("gasLimit", "0x0"), 16)
                metrics['fanatico_block_transaction_count'] = len(block.get("transactions", []))

        # Gas price
        result = self._rpc_call("eth_gasPrice")
        if result and "result" in result:
            gas_price = int(result["result"], 16)
            metrics['fanatico_gas_price_wei'] = gas_price
            metrics['fanatico_gas_price_gwei'] = gas_price / 1e9

        # Syncing status
        result = self._rpc_call("eth_syncing")
        if result and "result" in result:
            syncing = result["result"]
            if syncing is False:
                metrics['fanatico_syncing'] = 0
            else:
                metrics['fanatico_syncing'] = 1
                if isinstance(syncing, dict):
                    metrics['fanatico_sync_current_block'] = int(syncing.get("currentBlock", "0x0"), 16)
                    metrics['fanatico_sync_highest_block'] = int(syncing.get("highestBlock", "0x0"), 16)

        # Peer count
        result = self._rpc_call("net_peerCount")
        if result and "result" in result:
            metrics['fanatico_peer_count'] = int(result["result"], 16)

        # Mining status
        result = self._rpc_call("eth_mining")
        if result and "result" in result:
            metrics['fanatico_mining'] = 1 if result["result"] else 0

        # Client version
        result = self._rpc_call("web3_clientVersion")
        if result and "result" in result:
            version = result["result"]
            # Extract version number (e.g., "Fanatico/v0.5.0.0/python" -> "0.5.0.0")
            if "/" in version:
                parts = version.split("/")
                if len(parts) >= 2:
                    version_str = parts[1].lstrip("v")
                    # Store as info metric
                    metrics['fanatico_client_version_info'] = {
                        'version': version_str,
                        'client': parts[0],
                        'platform': parts[2] if len(parts) > 2 else 'unknown'
                    }

        # Collection time
        metrics['fanatico_metrics_collection_duration_seconds'] = time.time() - start_time
        metrics['fanatico_metrics_last_collection_timestamp'] = int(time.time())

        # Update stored metrics
        with self._lock:
            self.metrics = metrics

        logger.debug(f"Collected {len(metrics)} metrics in {metrics['fanatico_metrics_collection_duration_seconds']:.3f}s")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        with self._lock:
            return self.metrics.copy()


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint."""

    collector: FanaticoMetrics = None

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)

        if parsed.path == '/metrics':
            self.send_metrics()
        elif parsed.path == '/health':
            self.send_health()
        else:
            self.send_error(404)

    def send_metrics(self):
        """Send Prometheus metrics."""
        metrics = self.collector.get_metrics()
        output = self.format_prometheus(metrics)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(output.encode('utf-8'))

    def send_health(self):
        """Send health check response."""
        metrics = self.collector.get_metrics()
        healthy = metrics.get('fanatico_up', 0) == 1

        self.send_response(200 if healthy else 503)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'healthy' if healthy else 'unhealthy',
            'block_number': metrics.get('fanatico_block_number', 0)
        }).encode('utf-8'))

    def format_prometheus(self, metrics: Dict[str, Any]) -> str:
        """Format metrics in Prometheus exposition format."""
        lines = []

        # Add HELP and TYPE comments
        metric_info = {
            'fanatico_up': ('gauge', 'Whether the Fanatico node is up'),
            'fanatico_chain_id': ('gauge', 'Chain ID of the Fanatico network'),
            'fanatico_block_number': ('gauge', 'Current block number'),
            'fanatico_block_timestamp': ('gauge', 'Timestamp of the latest block'),
            'fanatico_block_gas_used': ('gauge', 'Gas used in the latest block'),
            'fanatico_block_gas_limit': ('gauge', 'Gas limit of the latest block'),
            'fanatico_block_transaction_count': ('gauge', 'Number of transactions in the latest block'),
            'fanatico_gas_price_wei': ('gauge', 'Current gas price in wei'),
            'fanatico_gas_price_gwei': ('gauge', 'Current gas price in gwei'),
            'fanatico_syncing': ('gauge', 'Whether the node is syncing (1) or not (0)'),
            'fanatico_sync_current_block': ('gauge', 'Current block during sync'),
            'fanatico_sync_highest_block': ('gauge', 'Highest known block during sync'),
            'fanatico_peer_count': ('gauge', 'Number of connected peers'),
            'fanatico_mining': ('gauge', 'Whether the node is mining'),
            'fanatico_metrics_collection_duration_seconds': ('gauge', 'Time taken to collect metrics'),
            'fanatico_metrics_last_collection_timestamp': ('gauge', 'Unix timestamp of last metrics collection'),
        }

        for metric_name, value in metrics.items():
            if metric_name == 'fanatico_client_version_info':
                # Handle info metric
                info = value
                labels = ','.join([f'{k}="{v}"' for k, v in info.items()])
                lines.append(f'# HELP fanatico_client_info Fanatico client version information')
                lines.append(f'# TYPE fanatico_client_info gauge')
                lines.append(f'fanatico_client_info{{{labels}}} 1')
            elif isinstance(value, (int, float)):
                if metric_name in metric_info:
                    metric_type, help_text = metric_info[metric_name]
                    lines.append(f'# HELP {metric_name} {help_text}')
                    lines.append(f'# TYPE {metric_name} {metric_type}')
                lines.append(f'{metric_name} {value}')

        return '\n'.join(lines) + '\n'


def collection_loop(collector: FanaticoMetrics, interval: int):
    """Background thread for periodic metric collection."""
    while True:
        try:
            collector.collect()
        except Exception as e:
            logger.error(f"Collection error: {e}")
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description='Fanatico L1 Metrics Exporter')
    parser.add_argument('--rpc-url', default=RPC_URL, help='RPC endpoint URL')
    parser.add_argument('--port', type=int, default=METRICS_PORT, help='Metrics server port')
    parser.add_argument('--interval', type=int, default=SCRAPE_INTERVAL, help='Collection interval (seconds)')
    args = parser.parse_args()

    # Create collector
    collector = FanaticoMetrics(args.rpc_url)

    # Initial collection
    logger.info(f"Connecting to Fanatico node at {args.rpc_url}")
    collector.collect()

    # Start collection thread
    collection_thread = threading.Thread(
        target=collection_loop,
        args=(collector, args.interval),
        daemon=True
    )
    collection_thread.start()

    # Start HTTP server
    MetricsHandler.collector = collector
    server = HTTPServer(('0.0.0.0', args.port), MetricsHandler)

    logger.info(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║       Fanatico L1 Metrics Exporter v0.5.0.0                   ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║  Metrics URL: http://0.0.0.0:{args.port}/metrics
    ║  Health URL:  http://0.0.0.0:{args.port}/health
    ║  RPC URL:     {args.rpc_url}
    ║  Interval:    {args.interval}s
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
