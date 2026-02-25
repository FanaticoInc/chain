const { ethers } = require('ethers');

async function testV047CompleteValidation() {
    console.log('='.repeat(70));
    console.log('v0.4.7 COMPLETE VALIDATION - 100% ethers.js Compatibility Test');
    console.log('='.repeat(70));
    console.log('\n🎯 GOAL: Verify 100% ethers.js compatibility');
    console.log('🔍 TESTING: Receipt fields (transactionIndex, v, r, s)');
    console.log('✅ CRITICAL: await tx.wait() must work without workarounds\n');

    const RPC_URL = 'http://paratime.fanati.co:8546';
    const PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const CHAIN_ID = 999999999;

    const results = {
        network: false,
        hashValidation: false,
        simpleTransferSubmit: false,
        simpleTransferWait: false,
        contractDeploySubmit: false,
        contractDeployWait: false,
        contractInteraction: false,
        eip1559Submit: false,
        eip1559Wait: false,
        receiptFields: false
    };

    try {
        // Setup
        const provider = new ethers.JsonRpcProvider(RPC_URL);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

        console.log('Test Account:', wallet.address);
        const balance = await provider.getBalance(wallet.address);
        console.log('Balance:', ethers.formatEther(balance), 'FCO\n');

        // Test 1: Network & Basic Queries (Regression Test)
        console.log('='.repeat(70));
        console.log('TEST 1: Network Connection & Basic Queries');
        console.log('Regression test from v0.4.6');
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
            console.log('\n✅ TEST 1 PASSED\n');
        } catch (error) {
            console.log('\n❌ TEST 1 FAILED:', error.message, '\n');
        }

        // Test 2: Hash Validation (Regression Test from v0.4.6)
        console.log('='.repeat(70));
        console.log('TEST 2: Transaction Hash Validation');
        console.log('Regression test: Ensure Keccak-256 fix maintained');
        console.log('='.repeat(70));

        try {
            const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';
            const nonce = await provider.getTransactionCount(wallet.address);

            const txRequest = {
                to: recipient,
                value: ethers.parseEther('0.001'),
                gasLimit: 21000,
                gasPrice: ethers.parseUnits('10', 'gwei'),
                nonce: nonce,
                chainId: CHAIN_ID,
                type: 0
            };

            console.log('\nSigning transaction locally...');
            const signedTx = await wallet.signTransaction(txRequest);
            const localHash = ethers.keccak256(signedTx);
            console.log('Local hash (ethers.js):', localHash);

            console.log('\nSending to backend...');
            const remoteHash = await provider.send('eth_sendRawTransaction', [signedTx]);
            console.log('Remote hash (backend):', remoteHash);

            console.log('\nComparing hashes...');
            if (localHash === remoteHash) {
                console.log('✅ HASHES MATCH! Keccak-256 fix maintained!');
                results.hashValidation = true;
            } else {
                console.log('❌ HASHES MISMATCH! Regression detected!');
                console.log('   Local:  ', localHash);
                console.log('   Remote: ', remoteHash);
            }

            console.log('\n' + (results.hashValidation ? '✅' : '❌') + ' TEST 2 ' + (results.hashValidation ? 'PASSED' : 'FAILED') + '\n');
        } catch (error) {
            console.log('\n❌ TEST 2 FAILED');
            console.log('Error:', error.message, '\n');
        }

        // Test 3: Simple Transfer with await tx.wait() (THE CRITICAL TEST!)
        console.log('='.repeat(70));
        console.log('TEST 3: Simple Transfer with await tx.wait()');
        console.log('🔴 CRITICAL: This is the v0.4.7 fix - tx.wait() must work!');
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
                type: 0
            };

            console.log('\nTransaction Details:');
            console.log('  To:', tx.to);
            console.log('  Value:', ethers.formatEther(tx.value), 'FCO');
            console.log('  Gas:', tx.gasLimit);
            console.log('  Nonce:', tx.nonce);

            console.log('\nSending transaction...');
            const txResponse = await wallet.sendTransaction(tx);
            console.log('✅ Transaction accepted! Hash:', txResponse.hash);
            results.simpleTransferSubmit = true;

            console.log('\n🔴 CRITICAL TEST: Calling await tx.wait()...');
            console.log('This failed in v0.4.6, must work in v0.4.7!');

            try {
                const receipt = await txResponse.wait();
                console.log('✅ tx.wait() SUCCEEDED! No error thrown!');
                console.log('✅ Transaction confirmed!');
                console.log('   Block:', receipt.blockNumber);
                console.log('   Status:', receipt.status === 1 ? 'SUCCESS' : 'FAILED');
                console.log('   Gas Used:', receipt.gasUsed.toString());

                // Check for new fields
                console.log('\n  Checking v0.4.7 new fields:');
                if (receipt.index !== undefined || receipt.transactionIndex !== undefined) {
                    const txIndex = receipt.index ?? receipt.transactionIndex;
                    console.log('  ✅ transactionIndex:', txIndex);
                } else {
                    console.log('  ⚠️  transactionIndex: missing');
                }

                results.simpleTransferWait = true;
                console.log('\n🎉 TEST 3 PASSED - tx.wait() works! v0.4.7 fix VERIFIED!\n');

            } catch (waitError) {
                console.log('❌ tx.wait() FAILED!');
                console.log('Error:', waitError.code || 'unknown');
                console.log('Message:', waitError.message);
                console.log('🔴 CRITICAL: v0.4.7 fix NOT working - receipt fields still missing!');
                console.log('');
            }

        } catch (error) {
            console.log('\n❌ TEST 3 FAILED');
            console.log('Error Code:', error.code || 'unknown');
            console.log('Error Message:', error.message);
            console.log('');
        }

        // Test 4: Contract Deployment with await contract.waitForDeployment()
        console.log('='.repeat(70));
        console.log('TEST 4: Contract Deployment with waitForDeployment()');
        console.log('🔴 CRITICAL: Standard ethers.js deployment pattern');
        console.log('='.repeat(70));

        try {
            // SimpleStorage contract bytecode
            const BYTECODE = '0x608060405234801561000f575f80fd5b50602a5f5560bb806100205f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c80636d4ce63c146034578063e5c19b2d14604c575b5f80fd5b603a6056565b60405190815260200160405180910390f35b6054605e565b005b5f5f54905090565b602a5f8190555056fea2646970667358221220c85b4c6f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f64736f6c63430008140033';
            const ABI = [
                "function get() view returns (uint256)",
                "function set() public"
            ];

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
            results.contractDeploySubmit = true;

            console.log('\n🔴 CRITICAL TEST: Calling await txResponse.wait()...');

            try {
                const receipt = await txResponse.wait();
                console.log('✅ tx.wait() SUCCEEDED for deployment!');
                results.contractDeployWait = true;

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

                    results.contractInteraction = (value === 42);
                    console.log('\n🎉 TEST 4 PASSED - Contract deployment with tx.wait() works!\n');
                } else {
                    console.log('⚠️  Contract address is null in receipt\n');
                }

            } catch (waitError) {
                console.log('❌ tx.wait() FAILED for deployment!');
                console.log('Error:', waitError.message);
                console.log('');
            }

        } catch (error) {
            console.log('\n❌ TEST 4 FAILED');
            console.log('Error Code:', error.code || 'unknown');
            console.log('Error Message:', error.message);
            console.log('');
        }

        // Test 5: EIP-1559 Transaction with tx.wait()
        console.log('='.repeat(70));
        console.log('TEST 5: EIP-1559 Transaction with tx.wait()');
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
            results.eip1559Submit = true;

            console.log('\nCalling await tx.wait()...');

            try {
                const receipt = await txResponse.wait();
                console.log('✅ tx.wait() SUCCEEDED!');
                console.log('✅ Transaction confirmed!');
                console.log('   Block:', receipt.blockNumber);
                console.log('   Status:', receipt.status === 1 ? 'SUCCESS' : 'FAILED');
                console.log('   Gas Used:', receipt.gasUsed.toString());

                results.eip1559Wait = true;
                console.log('\n✅ TEST 5 PASSED\n');

            } catch (waitError) {
                console.log('❌ tx.wait() FAILED!');
                console.log('Error:', waitError.message);
                console.log('');
            }

        } catch (error) {
            console.log('\n❌ TEST 5 FAILED');
            console.log('Error Code:', error.code || 'unknown');
            console.log('Error Message:', error.message);
            console.log('');
        }

        // Test 6: Receipt Fields Validation
        console.log('='.repeat(70));
        console.log('TEST 6: Receipt Fields Validation');
        console.log('Verify v0.4.7 new fields present');
        console.log('='.repeat(70));

        try {
            // Send a simple transaction and get receipt directly
            const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';
            const nonce = await provider.getTransactionCount(wallet.address);

            const tx = await wallet.sendTransaction({
                to: recipient,
                value: ethers.parseEther('0.001'),
                gasLimit: 21000,
                gasPrice: ethers.parseUnits('10', 'gwei'),
                nonce: nonce
            });

            console.log('\nTransaction sent:', tx.hash);
            console.log('Getting receipt...');

            const receipt = await tx.wait();

            console.log('\nChecking receipt fields:');

            // Required standard fields
            console.log('  ✅ transactionHash:', receipt.hash ? 'present' : 'missing');
            console.log('  ✅ blockHash:', receipt.blockHash ? 'present' : 'missing');
            console.log('  ✅ blockNumber:', receipt.blockNumber ? 'present' : 'missing');
            console.log('  ✅ from:', receipt.from ? 'present' : 'missing');
            console.log('  ✅ to:', receipt.to ? 'present' : 'missing');
            console.log('  ✅ gasUsed:', receipt.gasUsed ? 'present' : 'missing');
            console.log('  ✅ status:', receipt.status !== undefined ? 'present' : 'missing');

            // NEW in v0.4.7
            console.log('\n  🆕 v0.4.7 new fields:');
            const hasTransactionIndex = receipt.index !== undefined || receipt.transactionIndex !== undefined;
            console.log('  ' + (hasTransactionIndex ? '✅' : '❌') + ' transactionIndex:', hasTransactionIndex ? 'present' : 'MISSING');

            // Signature fields (optional but helpful)
            console.log('  ' + (receipt.v !== undefined ? '✅' : '⚠️ ') + ' v (signature):', receipt.v !== undefined ? 'present' : 'optional/missing');
            console.log('  ' + (receipt.r !== undefined ? '✅' : '⚠️ ') + ' r (signature):', receipt.r !== undefined ? 'present' : 'optional/missing');
            console.log('  ' + (receipt.s !== undefined ? '✅' : '⚠️ ') + ' s (signature):', receipt.s !== undefined ? 'present' : 'optional/missing');

            results.receiptFields = hasTransactionIndex;

            if (results.receiptFields) {
                console.log('\n✅ TEST 6 PASSED - Receipt fields complete!\n');
            } else {
                console.log('\n⚠️  TEST 6 PARTIAL - transactionIndex missing\n');
            }

        } catch (error) {
            console.log('\n❌ TEST 6 FAILED');
            console.log('Error:', error.message);
            console.log('');
        }

        // Summary
        console.log('='.repeat(70));
        console.log('COMPLETE VALIDATION SUMMARY - v0.4.7');
        console.log('='.repeat(70));

        const tests = [
            ['Network & Queries', results.network, 'Regression'],
            ['Hash Validation (Keccak-256)', results.hashValidation, 'Regression'],
            ['Simple Transfer Submit', results.simpleTransferSubmit, 'Regression'],
            ['Simple Transfer tx.wait()', results.simpleTransferWait, 'v0.4.7 Fix'],
            ['Contract Deploy Submit', results.contractDeploySubmit, 'Regression'],
            ['Contract Deploy tx.wait()', results.contractDeployWait, 'v0.4.7 Fix'],
            ['Contract Interaction', results.contractInteraction, 'Regression'],
            ['EIP-1559 Submit', results.eip1559Submit, 'Regression'],
            ['EIP-1559 tx.wait()', results.eip1559Wait, 'v0.4.7 Fix'],
            ['Receipt Fields Complete', results.receiptFields, 'v0.4.7 Fix']
        ];

        let passed = 0;
        let critical_passed = 0;
        let critical_total = 0;

        tests.forEach(([name, result, category]) => {
            const icon = result ? '✅' : '❌';
            const isCritical = category === 'v0.4.7 Fix';
            const label = isCritical ? ' 🔴 CRITICAL' : '';
            console.log(`${icon} ${name}${label}`);
            if (result) passed++;
            if (isCritical) {
                critical_total++;
                if (result) critical_passed++;
            }
        });

        const total = tests.length;
        const percentage = Math.floor((passed / total) * 100);
        const critical_percentage = critical_total > 0 ? Math.floor((critical_passed / critical_total) * 100) : 0;

        console.log(`\nResults: ${passed}/${total} tests passed (${percentage}%)`);
        console.log(`Critical (v0.4.7 fixes): ${critical_passed}/${critical_total} passed (${critical_percentage}%)`);

        // Critical assessment
        console.log('\n' + '='.repeat(70));

        const allCriticalPass = critical_passed === critical_total && critical_total > 0;
        const noRegression = results.network && results.hashValidation;

        if (allCriticalPass && noRegression) {
            console.log('🎉 100% ethers.js COMPATIBILITY ACHIEVED!');
            console.log('   ✅ v0.4.7 fix VERIFIED: tx.wait() works!');
            console.log('   ✅ Receipt fields complete: transactionIndex present');
            console.log('   ✅ No workarounds needed anymore!');
            console.log('   ✅ All regression tests passed');
            console.log('   ✅ Keccak-256 fix maintained from v0.4.6');
            console.log('\n🟢 PRODUCTION READY - v0.4.7 delivers 100% as claimed!');
        } else if (critical_passed > 0) {
            console.log('⚠️  PARTIAL SUCCESS');
            console.log('   Some v0.4.7 fixes working');
            console.log('   ' + (allCriticalPass ? '✅' : '⚠️') + ' Critical fixes: ' + critical_passed + '/' + critical_total);
            console.log('   ' + (noRegression ? '✅' : '⚠️') + ' Regression tests: ' + (noRegression ? 'passing' : 'failing'));
        } else {
            console.log('❌ v0.4.7 FIX NOT WORKING');
            console.log('   🔴 tx.wait() still failing');
            console.log('   🔴 Receipt fields incomplete');
            console.log('   🔴 Claims not verified');
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

testV047CompleteValidation();
