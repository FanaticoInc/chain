const { ethers } = require('ethers');

console.log('='.repeat(80));
console.log('v0.4.8.1 JavaScript/ethers.js CRITICAL VERIFICATION');
console.log('Testing THE critical feature: await tx.wait()');
console.log('='.repeat(80));
console.log();

async function testV0481() {
    const provider = new ethers.JsonRpcProvider('http://paratime.fanati.co:8545');
    const privateKey = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const wallet = new ethers.Wallet(privateKey, provider);

    console.log(`Wallet address: ${wallet.address}`);

    // Test 1: Check chain ID
    try {
        const network = await provider.getNetwork();
        console.log(`✅ Chain ID: ${network.chainId}`);
    } catch (error) {
        console.log(`⚠️  Chain ID detection: ${error.message}`);
    }
    console.log();

    // Test 2: Gas estimation - THE NEW FEATURE
    console.log('='.repeat(80));
    console.log('TEST 1: Gas Estimation (NEW in v0.4.8.1)');
    console.log('Claim: eth_estimateGas implemented');
    console.log('='.repeat(80));

    try {
        const gasEstimate = await provider.estimateGas({
            from: wallet.address,
            to: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
            value: ethers.parseEther('0.001')
        });
        console.log(`✅ Gas estimation WORKS: ${gasEstimate}`);

        if (gasEstimate === 21000n) {
            console.log('   ✅ CORRECT value (21000 for simple transfer)');
        } else {
            console.log(`   ⚠️  Expected 21000, got ${gasEstimate}`);
        }
    } catch (error) {
        console.log(`❌ Gas estimation FAILED: ${error.message}`);
    }
    console.log();

    // Test 3: await tx.wait() - THE MOST CRITICAL TEST
    console.log('='.repeat(80));
    console.log('TEST 2: await tx.wait() - THE CRITICAL FEATURE');
    console.log('This is THE feature that has been broken since v0.4.6');
    console.log('='.repeat(80));

    try {
        console.log('Sending transaction...');
        const tx = await wallet.sendTransaction({
            to: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
            value: ethers.parseEther('0.001')
        });

        console.log(`✅ Transaction sent: ${tx.hash}`);
        console.log();
        console.log('🔴 CRITICAL TEST: Calling await tx.wait()...');
        console.log('   This has FAILED in v0.4.6, v0.4.7, and v0.4.8');
        console.log();

        const receipt = await tx.wait();

        console.log('🎉🎉🎉 SUCCESS! await tx.wait() WORKED! 🎉🎉🎉');
        console.log();
        console.log('📋 Receipt Details:');
        console.log(`   Block Number: ${receipt.blockNumber}`);
        console.log(`   Status: ${receipt.status === 1 ? 'SUCCESS' : 'FAILED'}`);
        console.log(`   Transaction Index: ${receipt.index}`);
        console.log(`   Gas Used: ${receipt.gasUsed}`);
        console.log(`   Cumulative Gas: ${receipt.cumulativeGasUsed}`);
        console.log();

        // Check if required fields are present
        const hasIndex = receipt.index !== undefined && receipt.index !== null;
        const hasCumulativeGas = receipt.cumulativeGasUsed !== undefined;

        console.log('🔍 Field Validation:');
        console.log(`   ${hasIndex ? '✅' : '❌'} transactionIndex (receipt.index): ${receipt.index}`);
        console.log(`   ${hasCumulativeGas ? '✅' : '❌'} cumulativeGasUsed: ${receipt.cumulativeGasUsed}`);

        if (hasIndex && hasCumulativeGas) {
            console.log();
            console.log('✅✅✅ v0.4.8.1 COMPLETELY VERIFIED! ✅✅✅');
            console.log();
            console.log('ALL required fields present:');
            console.log('   ✅ transactionIndex field exists');
            console.log('   ✅ cumulativeGasUsed field exists');
            console.log('   ✅ await tx.wait() works without errors');
            console.log('   ✅ Receipt fully parsed by ethers.js');
            console.log();
            console.log('🚀 THIS IS A MAJOR BREAKTHROUGH!');
            console.log('   JavaScript/ethers.js dApp development is now fully supported!');
        }

    } catch (error) {
        console.log(`❌ CRITICAL FAILURE: ${error.message}`);
        console.log();
        console.log('Error code:', error.code);

        if (error.message.includes('invalid value for value.index')) {
            console.log();
            console.log('🚨 ROOT CAUSE: Missing transactionIndex field in receipt');
            console.log('   This is the SAME error as v0.4.6, v0.4.7, and v0.4.8');
            console.log('   v0.4.8.1 claim of "working" would be FALSE');
        } else {
            console.log();
            console.log('Full error:', error);
        }
    }

    console.log();
    console.log('='.repeat(80));
    console.log('Assessment Complete');
    console.log('='.repeat(80));
}

testV0481().catch(console.error);
