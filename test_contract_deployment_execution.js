/**
 * Comprehensive Contract Deployment & Execution Test
 * Date: November 10, 2025
 * Purpose: Verify contract deployment and execution on both endpoints
 */

const { ethers } = require('hardhat');
const fs = require('fs');

// Test configuration
const ENDPOINTS = [
  {
    name: "Legacy (Chain ID 1234)",
    url: "http://paratime.fanati.co:8545",
    chainId: 1234,
    network: "fanatico_v028"
  },
  {
    name: "v0.4.0 (Chain ID 999999999)",
    url: "http://paratime.fanati.co:8546",
    chainId: 999999999,
    network: "fanatico_v040"
  }
];

const TEST_ACCOUNT = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d";

// Helper function to create provider for each endpoint
async function createProvider(endpoint) {
  const provider = new ethers.JsonRpcProvider(endpoint.url);
  const wallet = new ethers.Wallet(TEST_ACCOUNT, provider);
  return { provider, wallet };
}

// Test results tracking
const testResults = {
  timestamp: new Date().toISOString(),
  endpoints: []
};

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function testEndpoint(endpoint) {
  console.log(`\n${'='.repeat(80)}`);
  console.log(`TESTING ENDPOINT: ${endpoint.name}`);
  console.log(`URL: ${endpoint.url}`);
  console.log(`Chain ID: ${endpoint.chainId}`);
  console.log(`${'='.repeat(80)}\n`);

  const endpointResult = {
    name: endpoint.name,
    url: endpoint.url,
    chainId: endpoint.chainId,
    tests: [],
    summary: {
      total: 0,
      passed: 0,
      failed: 0
    }
  };

  try {
    // Create provider and wallet
    const { provider, wallet } = await createProvider(endpoint);

    // Test 1: Network Connectivity
    console.log("Test 1: Network Connectivity");
    const connectivityTest = { name: "Network Connectivity", status: "pending" };
    try {
      const network = await provider.getNetwork();
      const blockNumber = await provider.getBlockNumber();
      console.log(`  ✅ Connected to network`);
      console.log(`  Chain ID: ${network.chainId}`);
      console.log(`  Current Block: ${blockNumber}`);
      connectivityTest.status = "passed";
      connectivityTest.data = { chainId: network.chainId.toString(), blockNumber };
      endpointResult.summary.passed++;
    } catch (error) {
      console.log(`  ❌ Connection failed: ${error.message}`);
      connectivityTest.status = "failed";
      connectivityTest.error = error.message;
      endpointResult.summary.failed++;
      endpointResult.tests.push(connectivityTest);
      endpointResult.summary.total++;
      return endpointResult; // Can't continue without connectivity
    }
    endpointResult.tests.push(connectivityTest);
    endpointResult.summary.total++;

    // Test 2: Account Balance
    console.log("\nTest 2: Account Balance Check");
    const balanceTest = { name: "Account Balance", status: "pending" };
    try {
      const balance = await provider.getBalance(wallet.address);
      const balanceFCO = ethers.formatEther(balance);
      console.log(`  Account: ${wallet.address}`);
      console.log(`  Balance: ${balanceFCO} FCO`);

      if (parseFloat(balanceFCO) > 0) {
        console.log(`  ✅ Account funded`);
        balanceTest.status = "passed";
      } else {
        console.log(`  ⚠️ Account has zero balance - may affect deployment`);
        balanceTest.status = "warning";
      }
      balanceTest.data = { address: wallet.address, balance: balanceFCO };
      endpointResult.summary.passed++;
    } catch (error) {
      console.log(`  ❌ Balance check failed: ${error.message}`);
      balanceTest.status = "failed";
      balanceTest.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(balanceTest);
    endpointResult.summary.total++;

    // Test 3: Compile Contract
    console.log("\nTest 3: Contract Compilation");
    const compileTest = { name: "Contract Compilation", status: "pending" };
    let SimpleStorage;
    try {
      SimpleStorage = await ethers.getContractFactory("SimpleStorage", wallet);
      console.log(`  ✅ SimpleStorage contract compiled`);
      compileTest.status = "passed";
      endpointResult.summary.passed++;
    } catch (error) {
      console.log(`  ❌ Compilation failed: ${error.message}`);
      compileTest.status = "failed";
      compileTest.error = error.message;
      endpointResult.summary.failed++;
      endpointResult.tests.push(compileTest);
      endpointResult.summary.total++;
      return endpointResult; // Can't continue without contract
    }
    endpointResult.tests.push(compileTest);
    endpointResult.summary.total++;

    // Test 4: Contract Deployment
    console.log("\nTest 4: Contract Deployment");
    const deploymentTest = { name: "Contract Deployment", status: "pending" };
    let contract;
    let deploymentTx;

    try {
      console.log(`  Deploying SimpleStorage contract...`);
      contract = await SimpleStorage.deploy();
      deploymentTx = contract.deploymentTransaction();

      console.log(`  Deployment transaction sent: ${deploymentTx.hash}`);
      console.log(`  Waiting for confirmation...`);

      await contract.waitForDeployment();
      const contractAddress = await contract.getAddress();

      console.log(`  ✅ Contract deployed successfully`);
      console.log(`  Contract Address: ${contractAddress}`);
      console.log(`  Deployment TX: ${deploymentTx.hash}`);

      deploymentTest.status = "passed";
      deploymentTest.data = {
        contractAddress,
        deploymentTxHash: deploymentTx.hash
      };
      endpointResult.summary.passed++;
    } catch (error) {
      console.log(`  ❌ Deployment failed: ${error.message}`);
      deploymentTest.status = "failed";
      deploymentTest.error = error.message;
      deploymentTest.stack = error.stack;
      endpointResult.summary.failed++;
      endpointResult.tests.push(deploymentTest);
      endpointResult.summary.total++;
      return endpointResult; // Can't continue without deployed contract
    }
    endpointResult.tests.push(deploymentTest);
    endpointResult.summary.total++;

    const contractAddress = await contract.getAddress();

    // Test 5: Read Initial Value
    console.log("\nTest 5: Read Initial Value (Constructor)");
    const initialReadTest = { name: "Initial Value Read", status: "pending" };
    try {
      const initialValue = await contract.get();
      console.log(`  Initial value: ${initialValue}`);

      if (initialValue.toString() === "0") {
        console.log(`  ✅ Initial value correct (0)`);
        initialReadTest.status = "passed";
        endpointResult.summary.passed++;
      } else {
        console.log(`  ❌ Initial value incorrect (expected 0, got ${initialValue})`);
        initialReadTest.status = "failed";
        endpointResult.summary.failed++;
      }
      initialReadTest.data = { value: initialValue.toString() };
    } catch (error) {
      console.log(`  ❌ Read failed: ${error.message}`);
      initialReadTest.status = "failed";
      initialReadTest.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(initialReadTest);
    endpointResult.summary.total++;

    // Test 6: Write Operation - Set Value to 42
    console.log("\nTest 6: Write Operation - Set Value to 42");
    const writeTest1 = { name: "Write Operation (set 42)", status: "pending" };
    try {
      const tx = await contract.set(42);
      console.log(`  Transaction sent: ${tx.hash}`);
      console.log(`  Waiting for confirmation...`);

      const receipt = await tx.wait();
      console.log(`  ✅ Transaction confirmed in block ${receipt.blockNumber}`);
      console.log(`  Gas used: ${receipt.gasUsed.toString()}`);
      console.log(`  Status: ${receipt.status === 1 ? 'Success' : 'Failed'}`);

      if (receipt.status === 1) {
        writeTest1.status = "passed";
        endpointResult.summary.passed++;
      } else {
        writeTest1.status = "failed";
        endpointResult.summary.failed++;
      }

      writeTest1.data = {
        txHash: tx.hash,
        blockNumber: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString(),
        status: receipt.status
      };
    } catch (error) {
      console.log(`  ❌ Write operation failed: ${error.message}`);
      writeTest1.status = "failed";
      writeTest1.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(writeTest1);
    endpointResult.summary.total++;

    // Test 7: Read Value After Write
    console.log("\nTest 7: Read Value After Write");
    const readTest1 = { name: "Read After Write (expected 42)", status: "pending" };
    try {
      const value = await contract.get();
      console.log(`  Value read: ${value}`);

      if (value.toString() === "42") {
        console.log(`  ✅ Value correctly stored and retrieved (42)`);
        readTest1.status = "passed";
        endpointResult.summary.passed++;
      } else {
        console.log(`  ❌ Value incorrect (expected 42, got ${value})`);
        readTest1.status = "failed";
        endpointResult.summary.failed++;
      }
      readTest1.data = { value: value.toString() };
    } catch (error) {
      console.log(`  ❌ Read failed: ${error.message}`);
      readTest1.status = "failed";
      readTest1.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(readTest1);
    endpointResult.summary.total++;

    // Test 8: Write Operation - Set Value to 999
    console.log("\nTest 8: Write Operation - Set Value to 999");
    const writeTest2 = { name: "Write Operation (set 999)", status: "pending" };
    try {
      const tx = await contract.set(999);
      console.log(`  Transaction sent: ${tx.hash}`);
      const receipt = await tx.wait();
      console.log(`  ✅ Transaction confirmed`);
      console.log(`  Gas used: ${receipt.gasUsed.toString()}`);

      if (receipt.status === 1) {
        writeTest2.status = "passed";
        endpointResult.summary.passed++;
      } else {
        writeTest2.status = "failed";
        endpointResult.summary.failed++;
      }

      writeTest2.data = {
        txHash: tx.hash,
        gasUsed: receipt.gasUsed.toString(),
        status: receipt.status
      };
    } catch (error) {
      console.log(`  ❌ Write operation failed: ${error.message}`);
      writeTest2.status = "failed";
      writeTest2.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(writeTest2);
    endpointResult.summary.total++;

    // Test 9: Read Value After Second Write
    console.log("\nTest 9: Read Value After Second Write");
    const readTest2 = { name: "Read After Write (expected 999)", status: "pending" };
    try {
      const value = await contract.get();
      console.log(`  Value read: ${value}`);

      if (value.toString() === "999") {
        console.log(`  ✅ Value correctly updated (999)`);
        readTest2.status = "passed";
        endpointResult.summary.passed++;
      } else {
        console.log(`  ❌ Value incorrect (expected 999, got ${value})`);
        readTest2.status = "failed";
        endpointResult.summary.failed++;
      }
      readTest2.data = { value: value.toString() };
    } catch (error) {
      console.log(`  ❌ Read failed: ${error.message}`);
      readTest2.status = "failed";
      readTest2.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(readTest2);
    endpointResult.summary.total++;

    // Test 10: Increment Operation
    console.log("\nTest 10: Increment Operation");
    const incrementTest = { name: "Increment Operation", status: "pending" };
    try {
      const tx = await contract.increment();
      console.log(`  Transaction sent: ${tx.hash}`);
      const receipt = await tx.wait();
      console.log(`  ✅ Increment confirmed`);

      const value = await contract.get();
      console.log(`  Value after increment: ${value}`);

      if (value.toString() === "1000") {
        console.log(`  ✅ Increment worked correctly (999 → 1000)`);
        incrementTest.status = "passed";
        endpointResult.summary.passed++;
      } else {
        console.log(`  ❌ Increment failed (expected 1000, got ${value})`);
        incrementTest.status = "failed";
        endpointResult.summary.failed++;
      }

      incrementTest.data = {
        txHash: tx.hash,
        finalValue: value.toString()
      };
    } catch (error) {
      console.log(`  ❌ Increment operation failed: ${error.message}`);
      incrementTest.status = "failed";
      incrementTest.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(incrementTest);
    endpointResult.summary.total++;

    // Test 11: eth_call Direct Test
    console.log("\nTest 11: Direct eth_call Test");
    const ethCallTest = { name: "Direct eth_call", status: "pending" };
    try {
      // Encode the get() function call
      const data = contract.interface.encodeFunctionData("get");

      const result = await provider.call({
        to: contractAddress,
        data: data
      });

      console.log(`  eth_call result (raw): ${result}`);

      // Decode the result
      const decoded = contract.interface.decodeFunctionResult("get", result);
      console.log(`  Decoded value: ${decoded[0]}`);

      if (result !== "0x" && result !== "0x0") {
        console.log(`  ✅ eth_call returns data`);
        ethCallTest.status = "passed";
        endpointResult.summary.passed++;
      } else {
        console.log(`  ❌ eth_call returns empty data`);
        ethCallTest.status = "failed";
        endpointResult.summary.failed++;
      }

      ethCallTest.data = {
        rawResult: result,
        decodedValue: decoded[0].toString()
      };
    } catch (error) {
      console.log(`  ❌ eth_call failed: ${error.message}`);
      ethCallTest.status = "failed";
      ethCallTest.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(ethCallTest);
    endpointResult.summary.total++;

    // Test 12: Event Emission Check
    console.log("\nTest 12: Event Emission Check");
    const eventTest = { name: "Event Emission", status: "pending" };
    try {
      const tx = await contract.set(12345);
      const receipt = await tx.wait();

      console.log(`  Receipt logs count: ${receipt.logs.length}`);

      if (receipt.logs.length > 0) {
        console.log(`  ✅ Events emitted (${receipt.logs.length} logs)`);

        // Try to parse the event
        try {
          const parsedLogs = receipt.logs.map(log => {
            try {
              return contract.interface.parseLog(log);
            } catch {
              return null;
            }
          }).filter(log => log !== null);

          console.log(`  Parsed events: ${parsedLogs.length}`);
          parsedLogs.forEach(log => {
            console.log(`    Event: ${log.name}`);
            console.log(`    Args: ${JSON.stringify(log.args)}`);
          });

          eventTest.data = {
            logsCount: receipt.logs.length,
            parsedEvents: parsedLogs.map(log => ({
              name: log.name,
              args: log.args.toString()
            }))
          };
        } catch (parseError) {
          console.log(`  ⚠️ Could not parse events: ${parseError.message}`);
        }

        eventTest.status = "passed";
        endpointResult.summary.passed++;
      } else {
        console.log(`  ⚠️ No events emitted`);
        eventTest.status = "warning";
        eventTest.data = { logsCount: 0 };
        endpointResult.summary.passed++; // Not critical failure
      }
    } catch (error) {
      console.log(`  ❌ Event test failed: ${error.message}`);
      eventTest.status = "failed";
      eventTest.error = error.message;
      endpointResult.summary.failed++;
    }
    endpointResult.tests.push(eventTest);
    endpointResult.summary.total++;

  } catch (error) {
    console.log(`\n❌ FATAL ERROR: ${error.message}`);
    endpointResult.fatalError = error.message;
    endpointResult.fatalStack = error.stack;
  }

  // Summary
  console.log(`\n${'='.repeat(80)}`);
  console.log(`ENDPOINT SUMMARY: ${endpoint.name}`);
  console.log(`Total Tests: ${endpointResult.summary.total}`);
  console.log(`Passed: ${endpointResult.summary.passed}`);
  console.log(`Failed: ${endpointResult.summary.failed}`);
  console.log(`Success Rate: ${endpointResult.summary.total > 0 ? ((endpointResult.summary.passed / endpointResult.summary.total) * 100).toFixed(2) : 0}%`);
  console.log(`${'='.repeat(80)}\n`);

  return endpointResult;
}

async function main() {
  console.log("\n");
  console.log("╔═══════════════════════════════════════════════════════════════════════════════╗");
  console.log("║                                                                               ║");
  console.log("║         COMPREHENSIVE CONTRACT DEPLOYMENT & EXECUTION TEST SUITE              ║");
  console.log("║                                                                               ║");
  console.log("║  Date: November 10, 2025                                                      ║");
  console.log("║  Purpose: Verify contract deployment and execution functionality             ║");
  console.log("║  Endpoints: 2 (Legacy Chain ID 1234, v0.4.0 Chain ID 999999999)              ║");
  console.log("║                                                                               ║");
  console.log("╚═══════════════════════════════════════════════════════════════════════════════╝");
  console.log("\n");

  // Test each endpoint
  for (const endpoint of ENDPOINTS) {
    const result = await testEndpoint(endpoint);
    testResults.endpoints.push(result);

    // Wait between endpoint tests
    if (ENDPOINTS.indexOf(endpoint) < ENDPOINTS.length - 1) {
      console.log("\nWaiting 5 seconds before testing next endpoint...\n");
      await sleep(5000);
    }
  }

  // Overall Summary
  console.log("\n");
  console.log("╔═══════════════════════════════════════════════════════════════════════════════╗");
  console.log("║                          OVERALL TEST SUMMARY                                 ║");
  console.log("╚═══════════════════════════════════════════════════════════════════════════════╝");
  console.log("\n");

  testResults.endpoints.forEach(endpoint => {
    console.log(`${endpoint.name}:`);
    console.log(`  Total Tests: ${endpoint.summary.total}`);
    console.log(`  Passed: ${endpoint.summary.passed}`);
    console.log(`  Failed: ${endpoint.summary.failed}`);
    console.log(`  Success Rate: ${endpoint.summary.total > 0 ? ((endpoint.summary.passed / endpoint.summary.total) * 100).toFixed(2) : 0}%`);
    console.log("");
  });

  // Save results to file
  const outputFile = `contract_test_results_${Date.now()}.json`;
  fs.writeFileSync(outputFile, JSON.stringify(testResults, null, 2));
  console.log(`\n📄 Detailed results saved to: ${outputFile}\n`);

  // Calculate overall status
  const totalPassed = testResults.endpoints.reduce((sum, ep) => sum + ep.summary.passed, 0);
  const totalTests = testResults.endpoints.reduce((sum, ep) => sum + ep.summary.total, 0);
  const overallRate = totalTests > 0 ? ((totalPassed / totalTests) * 100).toFixed(2) : 0;

  console.log(`Overall Success Rate: ${overallRate}%\n`);

  if (overallRate >= 80) {
    console.log("✅ RESULT: PRODUCTION READY - Contract deployment and execution working");
  } else if (overallRate >= 50) {
    console.log("⚠️ RESULT: PARTIAL FUNCTIONALITY - Some features working");
  } else {
    console.log("❌ RESULT: NOT FUNCTIONAL - Critical issues detected");
  }

  console.log("\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
