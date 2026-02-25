const { ethers } = require('hardhat');

// npx hardhat run dummy_debug.js --network seba
async function main() {
	const [deployer] = await ethers.getSigners();

	console.log('Deploying Dummy contract with account:', deployer.address);
	console.log('Account balance:', ethers.formatEther(await deployer.provider.getBalance(deployer.address)), 'FCO');

	// Deploy Dummy contract
	const Dummy = await ethers.getContractFactory('Dummy', deployer);

	console.log('\n📤 Sending deployment transaction...');
	const dummy = await Dummy.deploy();

	console.log('⏳ Waiting for deployment...');
	console.log('Deployment transaction hash:', dummy.deploymentTransaction().hash);

	// Wait for deployment
	await dummy.waitForDeployment();

	const dummyAddress = await dummy.target;
	console.log('✅ Contract deployed to:', dummyAddress);

	// Get deployment receipt
	const deployTx = dummy.deploymentTransaction();
	const receipt = await deployer.provider.getTransactionReceipt(deployTx.hash);

	console.log('\n📋 Deployment Receipt:');
	console.log('  Block:', receipt.blockNumber);
	console.log('  Gas Used:', receipt.gasUsed.toString());
	console.log('  Status:', receipt.status === 1 ? 'SUCCESS' : 'FAILED');
	console.log('  Contract Address:', receipt.contractAddress);

	// Check if bytecode exists
	console.log('\n🔍 Checking deployed bytecode...');
	const code = await deployer.provider.getCode(dummyAddress);
	console.log('  Bytecode length:', code.length);
	console.log('  Bytecode (first 100 chars):', code.substring(0, 100));

	if (code === '0x') {
		console.log('\n❌ ERROR: No bytecode deployed! Contract deployment failed.');
		return;
	}

	// Try calling getMyValue
	console.log('\n📞 Calling getMyValue()...');
	try {
		const getMyValue = await dummy.getMyValue();
		console.log('✅ getMyValue:', getMyValue.toString());
	} catch (error) {
		console.log('❌ Error calling getMyValue:', error.message);
	}
}

main()
	.then(() => process.exit(0))
	.catch((error) => {
		console.error(error);
		process.exit(1);
	});
