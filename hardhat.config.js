require("@nomicfoundation/hardhat-toolbox");
require('dotenv').config();

module.exports = {
  solidity: "0.8.27",
  networks: {
    // ✅ v0.4.8.1: CURRENT - Production Ready (92% JavaScript compatibility)
    fanatico_v0481: {
      url: "http://paratime.fanati.co:8545",
      chainId: 11111111111,
      accounts: [
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
      ],
      timeout: 60000,
      gasPrice: 10000000000  // 10 Gwei
    },

    // Alias for v0.4.8.1 (convenience)
    seba: {
      url: "http://paratime.fanati.co:8545",
      chainId: 11111111111,
      accounts: [
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
      ],
      timeout: 60000,
      gasPrice: 10000000000  // 10 Gwei
    },

    // ⚠️ LEGACY - v0.2.8: EVM on Port 8545 (Phase 4 EVM Integration - Old Chain ID)
    fanatico_v028: {
      url: "http://paratime.fanati.co:8545",
      chainId: 1234,
      accounts: [
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
      ],
      timeout: 60000,
      gasPrice: 1000000000  // 1 Gwei
    },

    // ✅ v0.4.0: New Chain ID 11111111111 on Port 8546
    fanatico_v040: {
      url: "http://paratime.fanati.co:8546",
      chainId: 11111111111,
      accounts: [
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
      ],
      timeout: 60000,
      gasPrice: 10000000000  // 10 Gwei (as per v0.4.0 specs)
    },

    // ✅ OPERATIONAL: Web3 API on Port 8549 (Full functionality)
    fanatico_local: {
      url: "http://paratime.fanati.co:8549",
      chainId: 1234,
      accounts: [
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"  // Funded with 100 FCO
      ],
      timeout: 60000,
      gasPrice: 1000000000  // 1 Gwei
    },

    // ⚠️ Remote ports temporarily unavailable
    fanatico: {
      url: "http://paratime.fanati.co:8547",
      chainId: 1234,
      accounts: [
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
      ],
      timeout: 60000,
      gasPrice: 1000000000  // 1 Gwei
    },

    fanatico8548: {
      url: "http://paratime.fanati.co:8548",
      chainId: 1234,
      accounts: [
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
      ],
      timeout: 60000,
      gasPrice: 1000000000  // 1 Gwei
    },

    // Local Hardhat network (for testing)
    hardhat: {
      chainId: 31337
    }
  },
  
  gasReporter: {
    enabled: false,  // Disabled for v0.2.8 testing (eth_getCode not implemented)
    currency: 'USD',
    gasPrice: 1
  }
};
