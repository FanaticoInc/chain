const { ethers } = require('ethers');

async function assessTestAccounts() {
    console.log('='.repeat(80));
    console.log('Test Account Balance Assessment - v0.4.8.1');
    console.log('Chain ID: 999999999');
    console.log('Endpoint: http://paratime.fanati.co:8545');
    console.log('='.repeat(80));
    console.log();

    const provider = new ethers.JsonRpcProvider('http://paratime.fanati.co:8545');

    // Standard Hardhat test accounts (first 10)
    const testAccounts = [
        { name: 'Account #0', address: '0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266' },
        { name: 'Account #1', address: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8' },
        { name: 'Account #2', address: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC' },
        { name: 'Account #3', address: '0x90F79bf6EB2c4f870365E785982E1f101E93b906' },
        { name: 'Account #4', address: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65' },
        { name: 'Account #5', address: '0x9965507D1a55bcC2695C58ba16FB37d819B0A4dc' },
        { name: 'Account #6', address: '0x976EA74026E726554dB657fA54763abd0C3a0aa9' },
        { name: 'Account #7', address: '0x14dC79964da2C08b23698B3D3cc7Ca32193d9955' },
        { name: 'Account #8', address: '0x23618e81E3f5cdF7f54C3d65f7FBc0aBf5B21E8f' },
        { name: 'Account #9', address: '0xa0Ee7A142d267C1f36714E4a8F75612F20a79720' }
    ];

    let totalBalance = 0n;
    const balances = [];

    console.log('Checking balances...\n');

    for (const account of testAccounts) {
        try {
            const balance = await provider.getBalance(account.address);
            const balanceFCO = ethers.formatEther(balance);

            balances.push({
                ...account,
                balance: balance,
                balanceFCO: balanceFCO
            });

            totalBalance += balance;

            const status = balance > 0n ? '✅' : '⚠️';
            console.log(`${status} ${account.name.padEnd(12)} ${account.address}`);
            console.log(`   Balance: ${balanceFCO} FCO`);
            console.log();
        } catch (error) {
            console.log(`❌ ${account.name.padEnd(12)} ${account.address}`);
            console.log(`   Error: ${error.message}`);
            console.log();
        }
    }

    // Summary
    console.log('='.repeat(80));
    console.log('SUMMARY');
    console.log('='.repeat(80));
    console.log();

    const accountsWithBalance = balances.filter(a => a.balance > 0n).length;
    const accountsWithoutBalance = balances.filter(a => a.balance === 0n).length;

    console.log(`Total Accounts: ${testAccounts.length}`);
    console.log(`Accounts with balance: ${accountsWithBalance}`);
    console.log(`Accounts without balance: ${accountsWithoutBalance}`);
    console.log();

    console.log(`Total Balance: ${ethers.formatEther(totalBalance)} FCO`);
    console.log();

    // Top 3 accounts by balance
    const sorted = [...balances].sort((a, b) =>
        a.balance > b.balance ? -1 : a.balance < b.balance ? 1 : 0
    );

    console.log('Top 3 Accounts by Balance:');
    for (let i = 0; i < Math.min(3, sorted.length); i++) {
        const acc = sorted[i];
        if (acc.balance > 0n) {
            console.log(`  ${i + 1}. ${acc.name}: ${acc.balanceFCO} FCO`);
        }
    }
    console.log();

    // Transaction count check for active accounts
    console.log('Transaction Count (Nonce) for Active Accounts:');
    for (const acc of balances.filter(a => a.balance > 0n)) {
        try {
            const txCount = await provider.getTransactionCount(acc.address);
            console.log(`  ${acc.name}: ${txCount} transactions`);
        } catch (error) {
            console.log(`  ${acc.name}: Error getting tx count`);
        }
    }
    console.log();

    console.log('='.repeat(80));
    console.log('Assessment Complete');
    console.log('='.repeat(80));
}

assessTestAccounts().catch(console.error);
