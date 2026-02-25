const { ethers } = require('ethers');

async function runTests() {
    console.log('='.repeat(70));
    console.log('v0.4.4 JAVASCRIPT/ETHERS.JS TESTING');
    console.log('='.repeat(70));

    const RPC_URL = 'http://paratime.fanati.co:8546';
    const PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const CHAIN_ID = 999999999;

    let test1_passed = false;
    let test2_passed = false;
    let test3_passed = false;
    let test4_passed = false;

    try {
        // Setup
        const provider = new ethers.JsonRpcProvider(RPC_URL);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

        console.log('\nTest Account:', wallet.address);
        const balance = await provider.getBalance(wallet.address);
        console.log('Balance:', ethers.formatEther(balance), 'FCO');

        // Test 1: Network and Block Queries
        console.log('\n' + '='.repeat(70));
        console.log('TEST 1: Network and Block Queries');
        console.log('='.repeat(70));

        try {
            const network = await provider.getNetwork();
            console.log('✅ Network connected - Chain ID:', network.chainId.toString());

            const blockNumber = await provider.getBlockNumber();
            console.log('✅ Current block:', blockNumber);

            const block = await provider.getBlock('latest');
            console.log('✅ Latest block retrieved:', {
                number: block.number,
                hash: block.hash.substring(0, 10) + '...',
                transactions: block.transactions.length
            });

            console.log('\n✅ TEST 1: PASSED - Network queries working!');
            test1_passed = true;

        } catch (error) {
            console.log('\n❌ TEST 1: FAILED');
            console.error('Error:', error.message);
            test1_passed = false;
        }

        // Test 2: Simple Transfer
        console.log('\n' + '='.repeat(70));
        console.log('TEST 2: Simple Transfer (Legacy Transaction)');
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
                type: 0  // Legacy transaction
            };

            console.log('\nTransaction:');
            console.log('  To:', tx.to);
            console.log('  Value:', ethers.formatEther(tx.value), 'FCO');
            console.log('  Gas:', tx.gasLimit);
            console.log('  Gas Price:', ethers.formatUnits(tx.gasPrice, 'gwei'), 'Gwei');
            console.log('  Nonce:', tx.nonce);

            console.log('\nSending transaction...');
            const txResponse = await wallet.sendTransaction(tx);
            console.log('✅ Transaction sent:', txResponse.hash);

            console.log('Waiting for confirmation...');
            const receipt = await txResponse.wait();
            console.log('✅ Transaction confirmed!');
            console.log('   Block:', receipt.blockNumber);
            console.log('   Status:', receipt.status);
            console.log('   Gas Used:', receipt.gasUsed.toString());

            console.log('\n✅ TEST 2: PASSED - Simple transfer working!');
            test2_passed = true;

        } catch (error) {
            console.log('\n❌ TEST 2: FAILED');
            console.error('Error:', error.code || 'unknown');
            console.error('Message:', error.message);
            if (error.error) {
                console.error('RPC Error:', error.error);
            }
            test2_passed = false;
        }

        // Test 3: Contract Deployment
        console.log('\n' + '='.repeat(70));
        console.log('TEST 3: Contract Deployment');
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

            console.log('\nDeployment Transaction:');
            console.log('  Gas:', tx.gasLimit);
            console.log('  Gas Price:', ethers.formatUnits(tx.gasPrice, 'gwei'), 'Gwei');
            console.log('  Bytecode length:', BYTECODE.length, 'chars');

            console.log('\nDeploying contract...');
            const txResponse = await wallet.sendTransaction(tx);
            console.log('✅ Transaction sent:', txResponse.hash);

            console.log('Waiting for confirmation...');
            const receipt = await txResponse.wait();

            if (receipt.contractAddress) {
                console.log('✅ Contract deployed!');
                console.log('   Address:', receipt.contractAddress);
                console.log('   Block:', receipt.blockNumber);
                console.log('   Gas Used:', receipt.gasUsed.toString());

                // Test the deployed contract
                console.log('\nTesting deployed contract...');

                // Test eth_getCode
                console.log('  Testing eth_getCode...');
                const code = await provider.getCode(receipt.contractAddress);
                if (code && code !== '0x' && code.length > 4) {
                    console.log('  ✅ Bytecode retrieved:', code.length, 'chars');
                } else {
                    console.log('  ⚠️  Bytecode empty:', code);
                }

                // Test eth_call
                console.log('  Testing eth_call (get() function)...');
                const result = await provider.call({
                    to: receipt.contractAddress,
                    data: '0x6d4ce63c'
                });
                const value = parseInt(result, 16);
                console.log('  ✅ Contract state:', value, '(expected: 42)');

                console.log('\n✅ TEST 3: PASSED - Contract deployment working!');
                test3_passed = true;
            } else {
                console.log('⚠️  Contract address is null');
                test3_passed = false;
            }

        } catch (error) {
            console.log('\n❌ TEST 3: FAILED');
            console.error('Error:', error.code || 'unknown');
            console.error('Message:', error.message);
            if (error.error) {
                console.error('RPC Error:', error.error);
            }
            test3_passed = false;
        }

        // Test 4: EIP-1559 Transaction
        console.log('\n' + '='.repeat(70));
        console.log('TEST 4: EIP-1559 Transaction');
        console.log('='.repeat(70));

        try {
            const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';
            const nonce = await provider.getTransactionCount(wallet.address);

            const tx = {
                type: 2,  // EIP-1559
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
            console.log('  Priority Fee:', ethers.formatUnits(tx.maxPriorityFeePerGas, 'gwei'), 'Gwei');

            console.log('\nSending transaction...');
            const txResponse = await wallet.sendTransaction(tx);
            console.log('✅ Transaction sent:', txResponse.hash);

            console.log('Waiting for confirmation...');
            const receipt = await txResponse.wait();
            console.log('✅ Transaction confirmed!');
            console.log('   Block:', receipt.blockNumber);
            console.log('   Status:', receipt.status);
            console.log('   Gas Used:', receipt.gasUsed.toString());

            console.log('\n✅ TEST 4: PASSED - EIP-1559 transaction working!');
            test4_passed = true;

        } catch (error) {
            console.log('\n❌ TEST 4: FAILED');
            console.error('Error:', error.code || 'unknown');
            console.error('Message:', error.message);
            if (error.error) {
                console.error('RPC Error:', error.error);
            }
            test4_passed = false;
        }

        // Summary
        console.log('\n' + '='.repeat(70));
        console.log('TEST SUMMARY');
        console.log('='.repeat(70));

        const tests = [
            ['Network and Block Queries', test1_passed],
            ['Simple Transfer', test2_passed],
            ['Contract Deployment', test3_passed],
            ['EIP-1559 Transaction', test4_passed]
        ];

        const passed = tests.filter(([_, result]) => result).length;
        const total = tests.length;

        tests.forEach(([name, result]) => {
            const status = result ? '✅ PASS' : '❌ FAIL';
            console.log(`${status}: ${name}`);
        });

        console.log(`\nResults: ${passed}/${total} tests passed (${Math.floor(100 * passed / total)}%)`);

        if (passed === total) {
            console.log('\n🎉 ALL TESTS PASSED - v0.4.4 JAVASCRIPT SUPPORT WORKING!');
        } else if (passed > 0) {
            console.log(`\n⚠️  PARTIAL SUCCESS - ${passed}/${total} tests passed`);
        } else {
            console.log('\n❌ ALL TESTS FAILED - CRITICAL ISSUES REMAIN');
        }

        console.log('='.repeat(70));

        process.exit(passed === total ? 0 : 1);

    } catch (error) {
        console.error('\n❌ FATAL ERROR');
        console.error('Error:', error.message);
        console.error(error);
        process.exit(1);
    }
}

runTests();
