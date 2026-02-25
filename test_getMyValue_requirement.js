const { ethers } = require('hardhat');

// Test requirement: getMyValue() must return 0
// npx hardhat run test_getMyValue_requirement.js --network seba

async function main() {
	console.log('='.repeat(70));
	console.log('REQUIREMENT TEST: getMyValue() must return 0');
	console.log('='.repeat(70));
	console.log();

	const [deployer] = await ethers.getSigners();
	console.log('Deployer:', deployer.address);
	console.log();

	// Deploy Dummy contract
	console.log('Step 1: Deploying Dummy contract...');
	const Dummy = await ethers.getContractFactory('Dummy', deployer);
	const dummy = await Dummy.deploy();
	await dummy.waitForDeployment();

	const address = await dummy.target;
	console.log('✅ Contract deployed to:', address);
	console.log();

	// Verify bytecode exists
	console.log('Step 2: Verifying contract bytecode...');
	const code = await deployer.provider.getCode(address);

	if (code === '0x' || code.length <= 2) {
		console.log('❌ CRITICAL ERROR: No bytecode at contract address!');
		console.log('   Bytecode:', code);
		console.log();
		console.log('⛔ REQUIREMENT CANNOT BE TESTED');
		console.log('   Reason: Contract deployment failed (backend bug)');
		console.log('   Status: ❌ TEST BLOCKED');
		console.log();
		console.log('Expected behavior:');
		console.log('  - Dummy contract should deploy with bytecode');
		console.log('  - getMyValue() should be callable');
		console.log('  - getMyValue() should return 0 (default uint256 value)');
		console.log();
		console.log('Actual behavior:');
		console.log('  - Deployment transaction succeeds');
		console.log('  - But NO bytecode is stored on-chain');
		console.log('  - Contract is non-functional');
		console.log();
		return false;
	}

	console.log('✅ Bytecode verified (length:', code.length, 'bytes)');
	console.log();

	// Test getMyValue()
	console.log('Step 3: Calling getMyValue()...');
	try {
		const value = await dummy.getMyValue();
		console.log('✅ getMyValue() returned:', value.toString());
		console.log();

		// Check requirement
		if (value.toString() === '0') {
			console.log('='.repeat(70));
			console.log('✅✅✅ REQUIREMENT MET ✅✅✅');
			console.log('='.repeat(70));
			console.log('getMyValue() correctly returns 0');
			console.log();
			return true;
		} else {
			console.log('='.repeat(70));
			console.log('❌ REQUIREMENT FAILED');
			console.log('='.repeat(70));
			console.log('Expected: 0');
			console.log('Actual:', value.toString());
			console.log();
			return false;
		}
	} catch (error) {
		console.log('❌ ERROR calling getMyValue()');
		console.log('   Error type:', error.code || 'UNKNOWN');
		console.log('   Error message:', error.message);
		console.log();
		console.log('='.repeat(70));
		console.log('⛔ REQUIREMENT TEST FAILED');
		console.log('='.repeat(70));
		console.log('Reason: Contract function call failed');
		console.log('Status: ❌ NOT MET');
		console.log();
		return false;
	}
}

main()
	.then((success) => {
		if (success) {
			console.log('Final Status: ✅ PASS');
			process.exit(0);
		} else {
			console.log('Final Status: ❌ FAIL');
			process.exit(1);
		}
	})
	.catch((error) => {
		console.error('Fatal error:', error.message);
		process.exit(1);
	});
