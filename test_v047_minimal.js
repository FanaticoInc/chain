const { ethers } = require('ethers');

async function minimalTest() {
    console.log('======================================================================');
    console.log('v0.4.7 MINIMAL FIX VERIFICATION');
    console.log('Testing if transactionIndex and cumulativeGasUsed fields are present');
    console.log('======================================================================\n');

    const RPC_URL = 'http://paratime.fanati.co:8545';
    const PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';

    try {
        const provider = new ethers.JsonRpcProvider(RPC_URL);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

        console.log('Test Account:', wallet.address);
        console.log('RPC URL:', RPC_URL, '\n');

        // Test 1: Send a simple transaction
        console.log('='.repeat(70));
        console.log('TEST 1: Send Transaction');
        console.log('='.repeat(70));

        const nonce = await provider.send('eth_getTransactionCount', [wallet.address, 'latest']);
        console.log('Account nonce:', parseInt(nonce, 16));

        const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';
        
        const tx = await wallet.sendTransaction({
            to: recipient,
            value: ethers.parseEther('0.001'),
            gasLimit: 21000,
            gasPrice: ethers.parseUnits('10', 'gwei'),
            nonce: parseInt(nonce, 16)
        });

        console.log('✅ Transaction sent:', tx.hash);

        // Test 2: THE CRITICAL TEST - await tx.wait()
        console.log('\n' + '='.repeat(70));
        console.log('TEST 2: CRITICAL - await tx.wait()');
        console.log('🔴 This is THE fix from v0.4.7 - MUST work!');
        console.log('='.repeat(70));

        console.log('\n🔴 CRITICAL: Calling await tx.wait()...');
        console.log('This is the make-or-break test for v0.4.7!\n');

        const receipt = await tx.wait();

        console.log('🎉 SUCCESS! await tx.wait() WORKED!');
        console.log('✅ Receipt received!\n');

        // Test 3: Check receipt structure
        console.log('='.repeat(70));
        console.log('TEST 3: Receipt Field Validation');
        console.log('='.repeat(70));

        console.log('\n📋 Receipt Structure:');
        console.log('  Transaction Hash:', receipt.hash);
        console.log('  Block Number:', receipt.blockNumber);
        console.log('  Status:', receipt.status === 1 ? 'SUCCESS' : 'FAILED');
        console.log('  Gas Used:', receipt.gasUsed.toString());

        console.log('\n🔍 Checking Required Fields:');

        // Check transactionIndex
        const hasIndex = receipt.index !== undefined && receipt.index !== null;
        console.log('  ' + (hasIndex ? '✅' : '❌') + ' transactionIndex:', hasIndex ? receipt.index : 'MISSING');

        // Check cumulativeGasUsed
        const hasCumulativeGas = receipt.cumulativeGasUsed !== undefined && receipt.cumulativeGasUsed !== null;
        console.log('  ' + (hasCumulativeGas ? '✅' : '❌') + ' cumulativeGasUsed:', hasCumulativeGas ? receipt.cumulativeGasUsed.toString() : 'MISSING');

        // Check signatures
        const hasV = receipt.v !== undefined && receipt.v !== null;
        const hasR = receipt.r !== undefined && receipt.r !== null;
        const hasS = receipt.s !== undefined && receipt.s !== null;
        const hasSignatures = hasV && hasR && hasS;
        console.log('  ' + (hasSignatures ? '✅' : '⚠️ ') + ' Signature fields (v,r,s):', hasSignatures ? 'PRESENT' : 'optional/missing');

        // Overall verdict
        console.log('\n' + '='.repeat(70));
        console.log('VERDICT');
        console.log('='.repeat(70));

        if (hasIndex && hasCumulativeGas) {
            console.log('🎉 v0.4.7 FIX VERIFIED!');
            console.log('   ✅ await tx.wait() WORKS!');
            console.log('   ✅ transactionIndex PRESENT!');
            console.log('   ✅ cumulativeGasUsed PRESENT!');
            if (hasSignatures) {
                console.log('   ✅ Signature fields PRESENT!');
            }
            console.log('\n🟢 CLAIMS CONFIRMED - Fix was actually applied!');
            process.exit(0);
        } else {
            console.log('❌ v0.4.7 FIX NOT VERIFIED');
            if (!hasIndex) console.log('   🔴 transactionIndex MISSING');
            if (!hasCumulativeGas) console.log('   🔴 cumulativeGasUsed MISSING');
            console.log('\n🔴 CLAIMS NOT CONFIRMED - Fix not fully applied');
            process.exit(1);
        }

    } catch (error) {
        console.log('\n❌ TEST FAILED');
        console.log('Error:', error.message);
        if (error.message.includes('index')) {
            console.log('🔴 Still has index field issue - fix NOT working!');
        }
        if (error.message.includes('cumulativeGasUsed')) {
            console.log('🔴 Missing cumulativeGasUsed field!');
        }
        console.log('\n' + '='.repeat(70));
        console.log('VERDICT: Fix NOT applied or not working');
        console.log('='.repeat(70));
        process.exit(1);
    }
}

minimalTest();
