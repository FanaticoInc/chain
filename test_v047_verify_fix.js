const { ethers } = require('ethers');

async function verifyV047Fix() {
    console.log('='.repeat(70));
    console.log('v0.4.7 FIX VERIFICATION TEST');
    console.log('Testing claims from V047_FIX_APPLIED_SUCCESS.md');
    console.log('='.repeat(70));
    console.log('\n🎯 GOAL: Verify await tx.wait() works');
    console.log('🔍 TESTING: Mining, receipt fields, transaction index\n');

    const RPC_URL = 'http://paratime.fanati.co:8545';
    const PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const CHAIN_ID = 1234;  // Actual chain ID on port 8545

    const results = {
        connection: false,
        txSend: false,
        txWait: false,
        receiptFields: false,
        transactionIndex: false,
        cumulativeGasUsed: false,
        signatures: false
    };

    try {
        const provider = new ethers.JsonRpcProvider(RPC_URL);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

        console.log('Test Account:', wallet.address);
        const balance = await provider.getBalance(wallet.address);
        console.log('Balance:', ethers.formatEther(balance), 'FCO\n');

        // Test 1: Connection
        console.log('='.repeat(70));
        console.log('TEST 1: Basic Connection');
        console.log('='.repeat(70));

        try {
            const chainId = (await provider.getNetwork()).chainId;
            console.log('✅ Chain ID:', chainId.toString());
            const blockNumber = await provider.getBlockNumber();
            console.log('✅ Block Number:', blockNumber);
            results.connection = true;
            console.log('\n✅ TEST 1 PASSED\n');
        } catch (error) {
            console.log('\n❌ TEST 1 FAILED:', error.message, '\n');
        }

        // Test 2: THE CRITICAL TEST - await tx.wait()
        console.log('='.repeat(70));
        console.log('TEST 2: CRITICAL - await tx.wait()');
        console.log('🔴 This is THE fix from v0.4.7 - MUST work!');
        console.log('='.repeat(70));

        try {
            const nonce = await provider.getTransactionCount(wallet.address);
            const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';

            console.log('\nSending transaction...');
            const tx = await wallet.sendTransaction({
                to: recipient,
                value: ethers.parseEther('0.001'),
                gasLimit: 21000,
                gasPrice: ethers.parseUnits('10', 'gwei'),
                nonce: nonce
            });

            console.log('✅ Transaction sent:', tx.hash);
            results.txSend = true;

            console.log('\n🔴 CRITICAL: Calling await tx.wait()...');
            console.log('This is the make-or-break test for v0.4.7!');

            const receipt = await tx.wait();

            console.log('🎉 SUCCESS! await tx.wait() WORKED!');
            console.log('✅ Receipt received!');
            results.txWait = true;

            // Check receipt structure
            console.log('\n📋 Receipt Structure:');
            console.log('  Transaction Hash:', receipt.hash);
            console.log('  Block Number:', receipt.blockNumber);
            console.log('  Status:', receipt.status === 1 ? 'SUCCESS' : 'FAILED');
            console.log('  Gas Used:', receipt.gasUsed.toString());

            // Check for required fields
            console.log('\n🔍 Checking Required Fields:');

            // transactionIndex
            const hasIndex = receipt.index !== undefined && receipt.index !== null;
            console.log('  ' + (hasIndex ? '✅' : '❌') + ' transactionIndex:', hasIndex ? receipt.index : 'MISSING');
            results.transactionIndex = hasIndex;

            // cumulativeGasUsed
            const hasCumulativeGas = receipt.cumulativeGasUsed !== undefined && receipt.cumulativeGasUsed !== null;
            console.log('  ' + (hasCumulativeGas ? '✅' : '❌') + ' cumulativeGasUsed:', hasCumulativeGas ? receipt.cumulativeGasUsed.toString() : 'MISSING');
            results.cumulativeGasUsed = hasCumulativeGas;

            // Signature fields (optional but nice to have)
            const hasV = receipt.v !== undefined && receipt.v !== null;
            const hasR = receipt.r !== undefined && receipt.r !== null;
            const hasS = receipt.s !== undefined && receipt.s !== null;
            const hasSignatures = hasV && hasR && hasS;
            console.log('  ' + (hasSignatures ? '✅' : '⚠️ ') + ' Signature fields (v,r,s):', hasSignatures ? 'PRESENT' : 'optional/missing');
            results.signatures = hasSignatures;

            // Overall receipt validity
            const hasAllRequired = hasIndex && hasCumulativeGas;
            results.receiptFields = hasAllRequired;

            if (hasAllRequired) {
                console.log('\n🎉 TEST 2 PASSED - All required fields present!\n');
            } else {
                console.log('\n⚠️  TEST 2 PARTIAL - Some fields missing\n');
            }

        } catch (error) {
            console.log('\n❌ TEST 2 FAILED');
            console.log('Error Code:', error.code || 'unknown');
            console.log('Error Message:', error.message);
            if (error.message.includes('index')) {
                console.log('🔴 Still has index field issue - fix NOT working!');
            }
            if (error.message.includes('cumulativeGasUsed')) {
                console.log('🔴 Missing cumulativeGasUsed field!');
            }
            console.log('');
        }

        // Test 3: Direct Receipt Query
        console.log('='.repeat(70));
        console.log('TEST 3: Direct Receipt Query');
        console.log('Query receipt via eth_getTransactionReceipt');
        console.log('='.repeat(70));

        try {
            // Send another transaction to get a fresh hash
            const nonce2 = await provider.getTransactionCount(wallet.address);
            const tx2 = await wallet.sendTransaction({
                to: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
                value: ethers.parseEther('0.001'),
                gasLimit: 21000,
                gasPrice: ethers.parseUnits('10', 'gwei'),
                nonce: nonce2
            });

            console.log('\nTransaction sent:', tx2.hash);
            console.log('Waiting for receipt...');

            // Wait a bit for mining
            await new Promise(r => setTimeout(r, 6000));

            // Query receipt directly
            const receipt2 = await provider.getTransactionReceipt(tx2.hash);

            if (receipt2) {
                console.log('✅ Receipt found!');
                console.log('\nRaw Receipt Fields:');
                console.log('  transactionIndex:', receipt2.index ?? 'missing');
                console.log('  cumulativeGasUsed:', receipt2.cumulativeGasUsed?.toString() ?? 'missing');
                console.log('  v:', receipt2.v ?? 'missing');
                console.log('  r:', receipt2.r ?? 'missing');
                console.log('  s:', receipt2.s ?? 'missing');
                console.log('\n✅ TEST 3 PASSED\n');
            } else {
                console.log('⚠️  Receipt not yet available\n');
            }

        } catch (error) {
            console.log('\n❌ TEST 3 FAILED:', error.message, '\n');
        }

        // Summary
        console.log('='.repeat(70));
        console.log('VERIFICATION SUMMARY - v0.4.7 FIX');
        console.log('='.repeat(70));

        const tests = [
            ['Basic Connection', results.connection],
            ['Transaction Send', results.txSend],
            ['await tx.wait() Works', results.txWait, '🔴 CRITICAL'],
            ['Receipt Fields Complete', results.receiptFields, '🔴 CRITICAL'],
            ['transactionIndex Present', results.transactionIndex, '🔴 CRITICAL'],
            ['cumulativeGasUsed Present', results.cumulativeGasUsed, '🔴 CRITICAL'],
            ['Signature Fields Present', results.signatures, '⚠️  Optional']
        ];

        let passed = 0;
        let critical_passed = 0;
        let critical_total = 0;

        tests.forEach(([name, result, level]) => {
            const icon = result ? '✅' : '❌';
            const label = level ? ' ' + level : '';
            console.log(`${icon} ${name}${label}`);
            if (result) passed++;
            if (level && level.includes('CRITICAL')) {
                critical_total++;
                if (result) critical_passed++;
            }
        });

        const total = tests.length;
        const percentage = Math.floor((passed / total) * 100);
        const critical_percentage = critical_total > 0 ? Math.floor((critical_passed / critical_total) * 100) : 0;

        console.log(`\nResults: ${passed}/${total} tests passed (${percentage}%)`);
        console.log(`Critical tests: ${critical_passed}/${critical_total} passed (${critical_percentage}%)`);

        console.log('\n' + '='.repeat(70));

        if (results.txWait && results.receiptFields) {
            console.log('🎉 v0.4.7 FIX VERIFIED!');
            console.log('   ✅ await tx.wait() WORKS!');
            console.log('   ✅ Receipt fields COMPLETE!');
            console.log('   ✅ transactionIndex PRESENT!');
            console.log('   ✅ cumulativeGasUsed PRESENT!');
            console.log('\n🟢 CLAIMS CONFIRMED - Fix was actually applied!');
        } else if (results.txWait) {
            console.log('⚠️  PARTIAL SUCCESS');
            console.log('   ✅ await tx.wait() works');
            console.log('   ⚠️  Some receipt fields incomplete');
        } else {
            console.log('❌ FIX NOT VERIFIED');
            console.log('   🔴 await tx.wait() still failing');
            console.log('   🔴 Claims not confirmed');
        }

        console.log('='.repeat(70));

        process.exit(critical_passed === critical_total ? 0 : 1);

    } catch (error) {
        console.error('\n💥 FATAL ERROR');
        console.error('Error:', error.message);
        console.error('\nStack:', error.stack);
        process.exit(1);
    }
}

verifyV047Fix();
