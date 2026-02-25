/**
 * FCO Token Metrics API for Fanatico L1
 * Provides token metrics endpoints similar to secret-token.com
 *
 * Endpoints:
 * - GET /api/info/prices - Price aggregation
 * - GET /api/info/stat/metrics - All token metrics
 * - GET /api/info/stat/metrics/total-supply
 * - GET /api/info/stat/metrics/total-circulation
 * - GET /api/info/stat/metrics/max-supply
 *
 * @version 1.0.0
 * @date February 2026
 */

const express = require('express');
const { ethers } = require('ethers');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Configuration
const CONFIG = {
  RPC_URL: process.env.RPC_URL || 'http://paratime.fanati.co:8545',
  AUTHORITY_ADDRESS: process.env.AUTHORITY_ADDRESS || '0xed4E6CA376FaA5c1EB37fF8Fc053875A6F327EB2',
  FCO_ADDRESS: process.env.FCO_ADDRESS || '0xd6F8Ff0036D8B2088107902102f9415330868109',
  PORT: process.env.PORT || 3001,

  // External price sources (for price aggregation)
  LBANK_API: 'https://api.lbank.com/v2/ticker/24hr.do?symbol=fco_usdt',
  COINGECKO_API: 'https://api.coingecko.com/api/v3/simple/price?ids=fanatico&vs_currencies=usd'
};

// Contract ABIs
const FCO_ABI = [
  'function name() view returns (string)',
  'function symbol() view returns (string)',
  'function decimals() view returns (uint8)',
  'function totalSupply() view returns (uint40)',
  'function epochDuration() view returns (uint40)',
  'function lockDuration() view returns (uint40)',
  'function currentEpoch() view returns (uint40)',
  'function ethReserve() view returns (uint256)'
];

const AUTHORITY_ABI = [
  'function chainId() view returns (uint40)',
  'function admin() view returns (address)',
  'function fco() view returns (address)'
];

// Initialize provider and contracts
let provider, fcoContract, authorityContract;

async function initContracts() {
  provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
  fcoContract = new ethers.Contract(CONFIG.FCO_ADDRESS, FCO_ABI, provider);
  authorityContract = new ethers.Contract(CONFIG.AUTHORITY_ADDRESS, AUTHORITY_ABI, provider);

  console.log('Contracts initialized');
  console.log('  FCO:', CONFIG.FCO_ADDRESS);
  console.log('  Authority:', CONFIG.AUTHORITY_ADDRESS);
}

// Cache for metrics (refresh every 60 seconds)
let metricsCache = null;
let cacheTimestamp = 0;
const CACHE_TTL = 60000; // 60 seconds

async function getMetrics() {
  const now = Date.now();
  if (metricsCache && (now - cacheTimestamp) < CACHE_TTL) {
    return metricsCache;
  }

  try {
    const [
      name,
      symbol,
      decimals,
      totalSupply,
      epochDuration,
      lockDuration,
      currentEpoch,
      ethReserve,
      chainId
    ] = await Promise.all([
      fcoContract.name(),
      fcoContract.symbol(),
      fcoContract.decimals(),
      fcoContract.totalSupply(),
      fcoContract.epochDuration(),
      fcoContract.lockDuration(),
      fcoContract.currentEpoch(),
      fcoContract.ethReserve(),
      authorityContract.chainId()
    ]);

    metricsCache = {
      token: {
        name,
        symbol,
        decimals: Number(decimals),
        address: CONFIG.FCO_ADDRESS
      },
      supply: {
        total: Number(totalSupply),
        max: 20000000000, // 20 billion max supply (from tokenomics)
        circulation: Number(totalSupply), // For now, all minted = circulating
        burned: 0 // Track burn events separately
      },
      epoch: {
        current: Number(currentEpoch),
        duration: Number(epochDuration),
        lockDuration: Number(lockDuration)
      },
      chain: {
        id: Number(chainId),
        rpc: CONFIG.RPC_URL,
        ethReserve: ethReserve.toString()
      },
      timestamp: new Date().toISOString()
    };

    cacheTimestamp = now;
    return metricsCache;
  } catch (error) {
    console.error('Error fetching metrics:', error.message);
    throw error;
  }
}

// Fetch external prices (best effort)
async function getPrices() {
  const prices = {
    usd_fco_l1: 0,
    usd_fco_cex_lbank: 0,
    usdt_fco_dex_uniswap: 0,
    timestamp: new Date().toISOString()
  };

  try {
    // Try LBank
    const lbankResponse = await fetch(CONFIG.LBANK_API);
    if (lbankResponse.ok) {
      const data = await lbankResponse.json();
      if (data.data && data.data[0]) {
        prices.usd_fco_cex_lbank = parseFloat(data.data[0].ticker.latest) || 0;
      }
    }
  } catch (e) {
    console.log('LBank price fetch failed:', e.message);
  }

  try {
    // Try CoinGecko
    const cgResponse = await fetch(CONFIG.COINGECKO_API);
    if (cgResponse.ok) {
      const data = await cgResponse.json();
      if (data.fanatico) {
        prices.usd_fco_l1 = data.fanatico.usd || 0;
      }
    }
  } catch (e) {
    console.log('CoinGecko price fetch failed:', e.message);
  }

  return prices;
}

// API Routes

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Price aggregation (compatible with secret-token.com)
app.get('/api/info/prices', async (req, res) => {
  try {
    const prices = await getPrices();
    res.json(prices);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// All metrics
app.get('/api/info/stat/metrics', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.json(metrics);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Individual metric endpoints
app.get('/api/info/stat/metrics/total-supply', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.json({ totalSupply: metrics.supply.total });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/info/stat/metrics/max-supply', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.json({ maxSupply: metrics.supply.max });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/info/stat/metrics/total-circulation', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.json({ circulation: metrics.supply.circulation });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/info/stat/metrics/total-mint', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.json({ totalMint: metrics.supply.total });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/info/stat/metrics/total-burn', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.json({ totalBurn: metrics.supply.burned });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Contract info
app.get('/api/info/contract', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.json({
      fco: CONFIG.FCO_ADDRESS,
      authority: CONFIG.AUTHORITY_ADDRESS,
      chainId: metrics.chain.id,
      rpc: CONFIG.RPC_URL
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start server
async function start() {
  await initContracts();

  app.listen(CONFIG.PORT, () => {
    console.log(`\nFCO Metrics API running on port ${CONFIG.PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET /health`);
    console.log(`  GET /api/info/prices`);
    console.log(`  GET /api/info/stat/metrics`);
    console.log(`  GET /api/info/stat/metrics/total-supply`);
    console.log(`  GET /api/info/stat/metrics/total-circulation`);
    console.log(`  GET /api/info/stat/metrics/max-supply`);
    console.log(`  GET /api/info/contract`);
  });
}

start().catch(console.error);
