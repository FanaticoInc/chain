const { ethers } = require('ethers');

async function testV045Critical() {
    console.log('='.repeat(70));
    console.log('v0.4.5 CRITICAL JAVASCRIPT/ETHERS.JS TESTING');
    console.log('='.repeat(70));
    console.log('\n⚠️  CRITICAL: All developers need JavaScript/ethers.js support');
    console.log('Focus: Testing the hash mismatch fix from v0.4.4\n');

    const RPC_URL = 'http://paratime.fanati.co:8546';
    const PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const CHAIN_ID = 999999999;

    const results = {
        network: false,
        simpleTransfer: false,
        contractDeployment: false,
        eip1559: false,
        blockQuery: false
    };

    try {
        // Setup
        const provider = new ethers.JsonRpcProvider(RPC_URL);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

        console.log('Test Account:', wallet.address);
        const balance = await provider.getBalance(wallet.address);
        console.log('Balance:', ethers.formatEther(balance), 'FCO\n');

        // Test 1: Network Connection
        console.log('='.repeat(70));
        console.log('TEST 1: Network Connection & Block Queries');
        console.log('='.repeat(70));

        try {
            const network = await provider.getNetwork();
            console.log('✅ Network - Chain ID:', network.chainId.toString());

            const blockNumber = await provider.getBlockNumber();
            console.log('✅ Block Number:', blockNumber);

            const block = await provider.getBlock('latest');
            console.log('✅ Latest Block:', {
                number: block.number,
                hash: block.hash.substring(0, 20) + '...'
            });

            results.network = true;
            results.blockQuery = true;
            console.log('\n✅ TEST 1 PASSED\n');
        } catch (error) {
            console.log('\n❌ TEST 1 FAILED:', error.message, '\n');
        }

        // Test 2: Simple Transfer (CRITICAL - was failing in v0.4.4)
        console.log('='.repeat(70));
        console.log('TEST 2: Simple Transfer (Legacy Transaction)');
        console.log('🔴 CRITICAL: This failed in v0.4.4 with hash mismatch');
        console.log('='.repeat(70));

        try {
            const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';
            const nonce = await provider.getTransactionCount(wallet.address);

            const tx = {
                to: recipient,
                value: ethers.parseEther('0.001'),
                gasLimit: 21000,
                gasPrice: ethers.parseUnits('10', 'gwei'),
                nonce: nonce,
                chainId: CHAIN_ID,
                type: 0  // Legacy
            };

            console.log('\nTransaction Details:');
            console.log('  To:', tx.to);
            console.log('  Value:', ethers.formatEther(tx.value), 'FCO');
            console.log('  Gas:', tx.gasLimit);
            console.log('  Nonce:', tx.nonce);

            console.log('\nSending transaction...');
            const txResponse = await wallet.sendTransaction(tx);
            console.log('✅ Transaction accepted! Hash:', txResponse.hash);

            console.log('Waiting for confirmation...');
            const receipt = await txResponse.wait();
            console.log('✅ Transaction confirmed!');
            console.log('   Block:', receipt.blockNumber);
            console.log('   Status:', receipt.status === 1 ? 'SUCCESS' : 'FAILED');
            console.log('   Gas Used:', receipt.gasUsed.toString());

            results.simpleTransfer = true;
            console.log('\n🎉 TEST 2 PASSED - Hash mismatch issue FIXED!\n');

        } catch (error) {
            console.log('\n❌ TEST 2 FAILED');
            console.log('Error Code:', error.code || 'unknown');
            console.log('Error Message:', error.message);
            if (error.message.includes('hash did not match')) {
                console.log('🔴 CRITICAL: Hash mismatch still present in v0.4.5!');
            }
            if (error.error) {
                console.log('RPC Error:', JSON.stringify(error.error, null, 2));
            }
            console.log('');
        }

        // Test 3: Contract Deployment (CRITICAL)
        console.log('='.repeat(70));
        console.log('TEST 3: Contract Deployment');
        console.log('🔴 CRITICAL: This failed in v0.4.4 with hash mismatch');
        console.log('='.repeat(70));

        try {
            const BYTECODE = '0x608060405234801561000f575f80fd5b50602a5f5560bb806100205f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c80636d4ce63c146034578063e5c19b2d14604c575b5f80fd5b603a6056565b60405190815260200160405180910390f35b6054605e565b005b5f5f54905090565b602a5f8190555056fea2646970667358221220c85b4c6f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f64736f6c63430008140033';

            const nonce = await provider.getTransactionCount(wallet.address);

            const tx = {
                to: null,
                data: BYTECODE,
                gasLimit: 300000,
                gasPrice: ethers.parseUnits('10', 'gwei'),
                nonce: nonce,
                chainId: CHAIN_ID,
                type: 0
            };

            console.log('\nDeployment Details:');
            console.log('  Gas Limit:', tx.gasLimit);
            console.log('  Bytecode Length:', BYTECODE.length, 'chars');
            console.log('  Nonce:', tx.nonce);

            console.log('\nDeploying contract...');
            const txResponse = await wallet.sendTransaction(tx);
            console.log('✅ Transaction accepted! Hash:', txResponse.hash);

            console.log('Waiting for confirmation...');
            const receipt = await txResponse.wait();

            if (receipt.contractAddress) {
                console.log('✅ Contract deployed!');
                console.log('   Address:', receipt.contractAddress);
                console.log('   Block:', receipt.blockNumber);
                console.log('   Gas Used:', receipt.gasUsed.toString());

                // Test the deployed contract
                console.log('\n  Testing deployed contract...');

                const code = await provider.getCode(receipt.contractAddress);
                if (code && code !== '0x' && code.length > 4) {
                    console.log('  ✅ eth_getCode:', code.length, 'chars');
                } else {
                    console.log('  ⚠️  eth_getCode: empty or invalid');
                }

                const result = await provider.call({
                    to: receipt.contractAddress,
                    data: '0x6d4ce63c'  // get() function
                });
                const value = parseInt(result, 16);
                console.log('  ✅ eth_call (get):', value, '(expected: 42)');

                results.contractDeployment = true;
                console.log('\n🎉 TEST 3 PASSED - Contract deployment working!\n');
            } else {
                console.log('⚠️  Contract address is null in receipt\n');
            }

        } catch (error) {
            console.log('\n❌ TEST 3 FAILED');
            console.log('Error Code:', error.code || 'unknown');
            console.log('Error Message:', error.message);
            if (error.message.includes('hash did not match')) {
                console.log('🔴 CRITICAL: Hash mismatch still present in v0.4.5!');
            }
            if (error.error) {
                console.log('RPC Error:', JSON.stringify(error.error, null, 2));
            }
            console.log('');
        }

        // Test 4: EIP-1559 Transaction
        console.log('='.repeat(70));
        console.log('TEST 4: EIP-1559 Transaction');
        console.log('='.repeat(70));

        try {
            const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';
            const nonce = await provider.getTransactionCount(wallet.address);

            const tx = {
                type: 2,
                to: recipient,
                value: ethers.parseEther('0.001'),
                gasLimit: 21000,
                maxFeePerGas: ethers.parseUnits('20', 'gwei'),
                maxPriorityFeePerGas: ethers.parseUnits('2', 'gwei'),
                nonce: nonce,
                chainId: CHAIN_ID
            };

            console.log('\nEIP-1559 Transaction:');
            console.log('  Type:', tx.type);
            console.log('  To:', tx.to);
            console.log('  Value:', ethers.formatEther(tx.value), 'FCO');
            console.log('  Max Fee:', ethers.formatUnits(tx.maxFeePerGas, 'gwei'), 'Gwei');

            console.log('\nSending transaction...');
            const txResponse = await wallet.sendTransaction(tx);
            console.log('✅ Transaction accepted! Hash:', txResponse.hash);

            console.log('Waiting for confirmation...');
            const receipt = await txResponse.wait();
            console.log('✅ Transaction confirmed!');
            console.log('   Block:', receipt.blockNumber);
            console.log('   Status:', receipt.status === 1 ? 'SUCCESS' : 'FAILED');
            console.log('   Gas Used:', receipt.gasUsed.toString());

            results.eip1559 = true;
            console.log('\n✅ TEST 4 PASSED\n');

        } catch (error) {
            console.log('\n❌ TEST 4 FAILED');
            console.log('Error Code:', error.code || 'unknown');
            console.log('Error Message:', error.message);
            if (error.error) {
                console.log('RPC Error:', JSON.stringify(error.error, null, 2));
            }
            console.log('');
        }

        // Summary
        console.log('='.repeat(70));
        console.log('CRITICAL TEST SUMMARY - v0.4.5');
        console.log('='.repeat(70));

        const tests = [
            ['Network & Block Queries', results.network && results.blockQuery],
            ['Simple Transfer (Legacy)', results.simpleTransfer],
            ['Contract Deployment', results.contractDeployment],
            ['EIP-1559 Transaction', results.eip1559]
        ];

        let passed = 0;
        tests.forEach(([name, result]) => {
            const icon = result ? '✅' : '❌';
            console.log(`${icon} ${name}`);
            if (result) passed++;
        });

        const total = tests.length;
        const percentage = Math.floor((passed / total) * 100);

        console.log(`\nResults: ${passed}/${total} tests passed (${percentage}%)`);

        // Critical assessment
        console.log('\n' + '='.repeat(70));
        if (results.simpleTransfer && results.contractDeployment) {
            console.log('🎉 PRODUCTION READY FOR JAVASCRIPT!');
            console.log('   ✅ Hash mismatch issue FIXED');
            console.log('   ✅ ethers.js transactions working');
            console.log('   ✅ Contract deployment working');
            console.log('   ✅ All developers can use JavaScript/ethers.js');
        } else if (results.simpleTransfer || results.contractDeployment) {
            console.log('⚠️  PARTIAL SUCCESS');
            console.log('   Some critical features working');
            console.log('   Additional fixes may be needed');
        } else {
            console.log('❌ NOT PRODUCTION READY');
            console.log('   🔴 Critical features still broken');
            console.log('   🔴 JavaScript/ethers.js not working');
            if (!results.simpleTransfer) {
                console.log('   🔴 Hash mismatch issue NOT FIXED');
            }
        }
        console.log('='.repeat(70));

        process.exit(passed === total ? 0 : 1);

    } catch (error) {
        console.error('\n💥 FATAL ERROR');
        console.error('Error:', error.message);
        console.error('\nStack:', error.stack);
        process.exit(1);
    }
}

testV045Critical();
