const { ethers } = require('ethers');

async function testSimpleTransfer() {
    console.log('Testing v0.4.3 with ethers.js (simple transfer)...\n');

    const RPC_URL = 'http://paratime.fanati.co:8546';
    const PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const CHAIN_ID = 999999999;

    try {
        // Setup
        const provider = new ethers.JsonRpcProvider(RPC_URL);
        const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

        // Test 1: Connection
        console.log('Test 1: Connection');
        const network = await provider.getNetwork();
        console.log('✅ Connected - Chain ID:', network.chainId.toString());

        // Test 2: Get block (NEW in v0.4.3)
        console.log('\nTest 2: eth_getBlockByNumber (NEW)');
        const block = await provider.getBlock('latest');
        console.log('✅ Block retrieved:', {
            number: block.number,
            hash: block.hash,
            timestamp: block.timestamp
        });

        // Test 3: Balance
        console.log('\nTest 3: Balance query');
        const balance = await provider.getBalance(wallet.address);
        console.log('✅ Balance:', ethers.formatEther(balance), 'FCO');

        // Test 4: Simple transfer (legacy transaction)
        console.log('\nTest 4: Simple transfer (legacy tx)');
        const recipient = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC';

        const tx = {
            to: recipient,
            value: ethers.parseEther('0.001'),
            gasLimit: 21000,
            gasPrice: ethers.parseUnits('10', 'gwei'),
            nonce: await provider.getTransactionCount(wallet.address),
            chainId: CHAIN_ID,
            type: 0  // Legacy transaction
        };

        console.log('Transaction:', {
            to: tx.to,
            value: ethers.formatEther(tx.value),
            gasLimit: tx.gasLimit,
            gasPrice: ethers.formatUnits(tx.gasPrice, 'gwei'),
            nonce: tx.nonce,
            type: tx.type
        });

        const txResponse = await wallet.sendTransaction(tx);
        console.log('✅ Transaction sent:', txResponse.hash);

        console.log('\nWaiting for confirmation...');
        const receipt = await txResponse.wait();
        console.log('✅ Transaction confirmed!');
        console.log('Receipt:', {
            blockNumber: receipt.blockNumber,
            status: receipt.status,
            gasUsed: receipt.gasUsed.toString()
        });

        console.log('\n🎉 All tests passed!');

    } catch (error) {
        console.error('\n❌ Error:', error.code || 'unknown');
        console.error('Message:', error.message);
        if (error.error) {
            console.error('RPC Error:', error.error);
        }
        process.exit(1);
    }
}

testSimpleTransfer();
