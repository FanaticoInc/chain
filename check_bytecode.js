const { ethers } = require('hardhat');

async function main() {
	const provider = new ethers.JsonRpcProvider('http://paratime.fanati.co:8545');

	const contractAddress = '0xbCF26943C0197d2eE0E5D05c716Be60cc2761508';

	console.log('Checking deployed bytecode for:', contractAddress);
	console.log();

	const code = await provider.getCode(contractAddress);

	console.log('Bytecode length:', code.length, 'characters');
	console.log('Bytecode (first 200 chars):', code.substring(0, 200) + '...');
	console.log();

	if (code === '0x' || code.length <= 2) {
		console.log('❌ NO BYTECODE - Contract not deployed or deployment failed');
	} else {
		console.log('✅ Bytecode exists - Contract deployed successfully');
		console.log('   Full bytecode:', code);
	}
}

main()
	.then(() => process.exit(0))
	.catch((error) => {
		console.error(error);
		process.exit(1);
	});
