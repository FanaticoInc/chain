const { ethers } = require('ethers');

async function transfer10FCO() {
    console.log('='.repeat(70));
    console.log('Transfer 10 FCO');
    console.log('='.repeat(70));
    console.log();

    // Setup
    const provider = new ethers.JsonRpcProvider('http://paratime.fanati.co:8545');
    const privateKey = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d';
    const wallet = new ethers.Wallet(privateKey, provider);

    const recipient = '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266';

    console.log(`From: ${wallet.address}`);
    console.log(`To: ${recipient}`);
    console.log(`Amount: 10 FCO`);
    console.log();

    // Check balance before
    const balanceBefore = await provider.getBalance(wallet.address);
    console.log(`Sender balance before: ${ethers.formatEther(balanceBefore)} FCO`);

    const recipientBalanceBefore = await provider.getBalance(recipient);
    console.log(`Recipient balance before: ${ethers.formatEther(recipientBalanceBefore)} FCO`);
    console.log();

    // Send transaction
    console.log('Sending transaction...');
    const tx = await wallet.sendTransaction({
        to: recipient,
        value: ethers.parseEther('10.0')
    });

    console.log(`Transaction hash: ${tx.hash}`);
    console.log();

    // Wait for confirmation
    console.log('Waiting for confirmation...');
    const receipt = await tx.wait();

    console.log(`✅ Transaction confirmed in block ${receipt.blockNumber}`);
    console.log(`   Gas used: ${receipt.gasUsed.toString()}`);
    console.log(`   Status: ${receipt.status === 1 ? 'SUCCESS' : 'FAILED'}`);
    console.log();

    // Check balance after
    const balanceAfter = await provider.getBalance(wallet.address);
    console.log(`Sender balance after: ${ethers.formatEther(balanceAfter)} FCO`);

    const recipientBalanceAfter = await provider.getBalance(recipient);
    console.log(`Recipient balance after: ${ethers.formatEther(recipientBalanceAfter)} FCO`);
    console.log();

    console.log('='.repeat(70));
    console.log('Transfer complete!');
    console.log('='.repeat(70));
}

transfer10FCO().catch(console.error);
