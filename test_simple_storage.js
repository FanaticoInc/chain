const { ethers } = require('hardhat');

// npx hardhat run test_simple_storage.js --network seba
async function main() {
	const [deployer] = await ethers.getSigners();

	console.log('Testing SimpleStorage deployment...');
	console.log('Deployer:', deployer.address);

	const SimpleStorage = await ethers.getContractFactory('SimpleStorage', deployer);
	const contract = await SimpleStorage.deploy();

	console.log('Deployment hash:', contract.deploymentTransaction().hash);
	await contract.waitForDeployment();

	const address = await contract.target;
	console.log('Contract address:', address);

	// Check bytecode
	const code = await deployer.provider.getCode(address);
	console.log('Bytecode exists:', code !== '0x');
	console.log('Bytecode length:', code.length);

	if (code === '0x') {
		console.log('❌ SimpleStorage also failed to deploy bytecode');
	} else {
		console.log('✅ SimpleStorage bytecode deployed successfully');

		// Try calling a function
		try {
			const value = await contract.get();
			console.log('Initial value:', value.toString());
		} catch (error) {
			console.log('Error calling get():', error.message);
		}
	}
}

main()
	.then(() => process.exit(0))
	.catch((error) => {
		console.error(error);
		process.exit(1);
	});
