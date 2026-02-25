const { ethers } = require('ethers');

console.log('='.repeat(80));
console.log('v0.4.8 JavaScript/ethers.js Verification');
console.log('Testing await tx.wait() - THE critical feature');
console.log('='.repeat(80));
console.log();

async function testV048() {
    const provider = new ethers.JsonRpcProvider('http://paratime.fanati.co:8545');
    const privateKey = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const wallet = new ethers.Wallet(privateKey, provider);

    console.log(`Wallet address: ${wallet.address}`);

    // Test 1: Check chain ID
    const network = await provider.getNetwork();
    console.log(`Chain ID: ${network.chainId}`);
    console.log();

    // Test 2: Gas estimation
    console.log('='.repeat(80));
    console.log('TEST 1: Gas Estimation (eth_estimateGas)');
    console.log('Claim: NEW feature in v0.4.8');
    console.log('='.repeat(80));

    try {
        const gasEstimate = await provider.estimateGas({
            from: wallet.address,
            to: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
            value: ethers.parseEther('0.001')
        });
        console.log(`✅ Gas estimation WORKS: ${gasEstimate}`);
    } catch (error) {
        console.log(`❌ Gas estimation FAILED: ${error.message}`);
    }
    console.log();

    // Test 3: await tx.wait() - THE CRITICAL TEST
    console.log('='.repeat(80));
    console.log('TEST 2: await tx.wait() - THE CRITICAL FEATURE');
    console.log('Claim: Works perfectly in v0.4.8');
    console.log('='.repeat(80));

    try {
        console.log('Sending transaction...');
        const tx = await wallet.sendTransaction({
            to: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
            value: ethers.parseEther('0.001'),
            gasLimit: 21000
        });

        console.log(`✅ Transaction sent: ${tx.hash}`);
        console.log();
        console.log('🔴 CRITICAL TEST: Calling await tx.wait()...');

        const receipt = await tx.wait();

        console.log('🎉 SUCCESS! await tx.wait() WORKED!');
        console.log();
        console.log('📋 Receipt Details:');
        console.log(`   Block Number: ${receipt.blockNumber}`);
        console.log(`   Status: ${receipt.status}`);
        console.log(`   Transaction Index: ${receipt.index}`);
        console.log(`   Gas Used: ${receipt.gasUsed}`);
        console.log(`   Cumulative Gas: ${receipt.cumulativeGasUsed}`);

        // Check if required fields are present
        const hasIndex = receipt.index !== undefined && receipt.index !== null;
        const hasCumulativeGas = receipt.cumulativeGasUsed !== undefined;

        console.log();
        console.log('🔍 Field Validation:');
        console.log(`   ${hasIndex ? '✅' : '❌'} transactionIndex (receipt.index)`);
        console.log(`   ${hasCumulativeGas ? '✅' : '❌'} cumulativeGasUsed`);

        if (hasIndex && hasCumulativeGas) {
            console.log();
            console.log('✅ v0.4.8 VERIFIED: All required fields present!');
        } else {
            console.log();
            console.log('⚠️  v0.4.8 INCOMPLETE: Missing required fields');
        }

    } catch (error) {
        console.log(`❌ CRITICAL FAILURE: ${error.message}`);
        console.log();
        console.log('Error details:', error.code);

        if (error.message.includes('invalid value for value.index')) {
            console.log();
            console.log('🚨 ROOT CAUSE: Missing transactionIndex field in receipt');
            console.log('   This is the SAME error as v0.4.6 and v0.4.7');
            console.log('   v0.4.8 claim of "working" is FALSE');
        }
    }

    console.log();
    console.log('='.repeat(80));
    console.log('Assessment Complete');
    console.log('='.repeat(80));
}

testV048().catch(console.error);
