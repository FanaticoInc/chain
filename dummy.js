const { ethers } = require('hardhat');

// npx hardhat run dummy.js --network seba
async function main() {
	const [deployer] = await ethers.getSigners();

	console.log('Deploying Dummy contract with account:', deployer.address);

	// Deploy Dummy contract
	const Dummy = await ethers.getContractFactory('Dummy', deployer);
	const dummy = await Dummy.deploy();

	// ✅ ethers v6 syntax: waitForDeployment() instead of deployed()
	await dummy.waitForDeployment();

	// ✅ ethers v6 syntax: target instead of address
	const dummyAddress = await dummy.target;
	console.log('Dummy deployed to:', dummyAddress);

	// Call getMyValue
	const getMyValue = await dummy.getMyValue();
	console.log('getMyValue:', getMyValue.toString());
}

main()
	.then(() => process.exit(0))
	.catch((error) => {
		console.error(error);
		process.exit(1);
	});
