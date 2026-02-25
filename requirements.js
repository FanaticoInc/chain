const { ethers } = require('hardhat');

// npx hardhat run --network seba scripts/dummy.js
// npx hardhat run --network sapphireTestnet scripts/dummy.js

async function main() {
	const [
		deployer, //, alex//
	] = await ethers.getSigners();

	// ProxyAdmin -------------------------------------------------------------------------------------------------
	const Dummy = await ethers.getContractFactory('Dummy', deployer);
	const dummy = await Dummy.deploy();
	await dummy.deployed();
	console.log('Dummy: ', dummy.address);

	const getMyValue = await dummy.getMyValue();
	console.log('getMyValue:', getMyValue);
	!getMyValue.eq(12345) ? console.error('ERROR ') : console.log('OK');

	const getBlockTimestamp = await dummy.getBlockTimestamp();
	console.log('getBlockTimestamp:', getBlockTimestamp);
	getBlockTimestamp.eq(0) ? console.error('ERROR ') : console.log('OK');

	const getPublicKey = await dummy.getPublicKey();
	console.log('getPublicKey:', getPublicKey);
	getPublicKey === '0x0000000000000000000000000000000000000000000000000000000000000000' ? console.error('ERROR ') : console.log('OK');

	const getMulti = await dummy.getMulti();
	console.log('getMulti:', getMulti);
}

main()
	.then(() => process.exit(0))
	.catch((error) => {
		console.error(error);
		process.exit(1);
	});
