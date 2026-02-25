const { ethers } = require('ethers');

async function main() {
    // Configuration
    const RPC_URL = 'http://paratime.fanati.co:8546';
    const PRIVATE_KEY = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const CHAIN_ID = 999999999;

    // SimpleStorage bytecode
    const BYTECODE = '0x608060405234801561000f575f80fd5b50602a5f5560bb806100205f395ff3fe6080604052348015600e575f80fd5b50600436106030575f3560e01c80636d4ce63c146034578063e5c19b2d14604c575b5f80fd5b603a6056565b60405190815260200160405180910390f35b6054605e565b005b5f5f54905090565b602a5f8190555056fea2646970667358221220c85b4c6f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f8f64736f6c63430008140033';

    console.log('Setting up provider and wallet...');
    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

    // Check connection
    const network = await provider.getNetwork();
    console.log('✅ RPC connected:', {
        chainId: network.chainId.toString(),
        name: network.name || 'unknown'
    });

    // Get deployer info
    const deployer = await wallet.getAddress();
    const balance = await provider.getBalance(deployer);

    console.log('Deployer:', deployer);
    console.log('Balance:', ethers.formatEther(balance));

    // Create deployment transaction
    const tx = {
        to: null,
        value: ethers.parseEther('0.00001'),
        gasLimit: 21000,
        gasPrice: ethers.parseUnits('2630755759', 'wei'),
        nonce: 0,
        chainId: CHAIN_ID,
        data: BYTECODE
    };

    console.log('TX:', {
        to: tx.to,
        value: tx.value.toString(),
        gasLimit: tx.gasLimit,
        gasPrice: tx.gasPrice.toString(),
        nonce: tx.nonce,
        chainId: tx.chainId
    });

    try {
        console.log('Sending transaction...');
        const txResponse = await wallet.sendTransaction(tx);
        console.log('Transaction hash:', txResponse.hash);

        console.log('Waiting for confirmation...');
        const receipt = await txResponse.wait();
        console.log('Receipt:', receipt);
    } catch (error) {
        console.error('Error:', error.code || 'unknown');
        console.error('Message:', error.message);

        if (error.error) {
            console.error('RPC Error:', error.error);
        }
    }
}

main().catch(console.error);
