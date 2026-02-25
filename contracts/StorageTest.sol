// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title StorageTest
 * @notice Comprehensive storage testing contract for FCO Chain v0.4.9.6.2
 * @dev Tests all storage operations, state persistence, and data retrieval
 *
 * Purpose: Diagnose storage-issue.jpg problem where:
 * - getMyValue() returns 0 instead of stored value
 * - getBlockTimestamp() returns 0
 * - getPublicKey() returns zeros
 * - getMulti() throws CALL_EXCEPTION
 */
contract StorageTest {
    // ============= STATE VARIABLES =============

    // Simple storage slots
    uint256 public myValue;
    uint256 public blockTimestamp;
    address public deployer;
    bytes32 public publicKey;

    // Complex storage
    uint256[] public dynamicArray;
    mapping(uint256 => uint256) public storageMap;
    mapping(address => uint256) public balances;

    // Struct storage
    struct TestData {
        uint256 number;
        address addr;
        bool flag;
        string text;
    }
    TestData public testStruct;

    // Multiple values for batch testing
    uint256 public value1;
    uint256 public value2;
    uint256 public value3;

    // Event for testing logs
    event ValueSet(uint256 indexed oldValue, uint256 indexed newValue, address indexed setter);
    event MultipleValuesSet(uint256 v1, uint256 v2, uint256 v3);
    event StorageTest(string message, uint256 value);

    // ============= CONSTRUCTOR =============

    constructor() {
        deployer = msg.sender;
        myValue = 42;
        blockTimestamp = block.timestamp;
        publicKey = blockhash(block.number - 1);

        // Initialize multiple values
        value1 = 100;
        value2 = 200;
        value3 = 300;

        // Initialize struct
        testStruct = TestData({
            number: 999,
            addr: msg.sender,
            flag: true,
            text: "initialized"
        });

        // Initialize array
        dynamicArray.push(1);
        dynamicArray.push(2);
        dynamicArray.push(3);

        // Initialize mappings
        storageMap[0] = 111;
        storageMap[1] = 222;
        storageMap[2] = 333;
        balances[msg.sender] = 1000;

        emit StorageTest("Constructor executed", myValue);
    }

    // ============= SIMPLE GETTERS (Testing basic storage reads) =============

    function getMyValue() public view returns (uint256) {
        return myValue;
    }

    function getBlockTimestamp() public view returns (uint256) {
        return blockTimestamp;
    }

    function getPublicKey() public view returns (bytes32) {
        return publicKey;
    }

    function getDeployer() public view returns (address) {
        return deployer;
    }

    // ============= MULTIPLE RETURN VALUES =============

    function getMulti() public view returns (
        uint256 val,
        uint256 timestamp,
        address dep
    ) {
        return (myValue, blockTimestamp, deployer);
    }

    function getThreeValues() public view returns (
        uint256 v1,
        uint256 v2,
        uint256 v3
    ) {
        return (value1, value2, value3);
    }

    function getAllValues() public view returns (
        uint256 _myValue,
        uint256 _timestamp,
        address _deployer,
        bytes32 _publicKey,
        uint256 _v1,
        uint256 _v2,
        uint256 _v3
    ) {
        return (
            myValue,
            blockTimestamp,
            deployer,
            publicKey,
            value1,
            value2,
            value3
        );
    }

    // ============= SETTERS (Testing storage writes) =============

    function setMyValue(uint256 newValue) public {
        uint256 oldValue = myValue;
        myValue = newValue;
        emit ValueSet(oldValue, newValue, msg.sender);
    }

    function setMultipleValues(uint256 v1, uint256 v2, uint256 v3) public {
        value1 = v1;
        value2 = v2;
        value3 = v3;
        emit MultipleValuesSet(v1, v2, v3);
    }

    function updateTimestamp() public {
        blockTimestamp = block.timestamp;
    }

    // ============= COMPLEX STORAGE TESTS =============

    function getArrayLength() public view returns (uint256) {
        return dynamicArray.length;
    }

    function getArrayElement(uint256 index) public view returns (uint256) {
        require(index < dynamicArray.length, "Index out of bounds");
        return dynamicArray[index];
    }

    function pushToArray(uint256 value) public {
        dynamicArray.push(value);
    }

    function getMapValue(uint256 key) public view returns (uint256) {
        return storageMap[key];
    }

    function setMapValue(uint256 key, uint256 value) public {
        storageMap[key] = value;
    }

    function getBalance(address account) public view returns (uint256) {
        return balances[account];
    }

    function setBalance(address account, uint256 amount) public {
        balances[account] = amount;
    }

    // ============= STRUCT OPERATIONS =============

    function getStruct() public view returns (
        uint256 number,
        address addr,
        bool flag,
        string memory text
    ) {
        return (
            testStruct.number,
            testStruct.addr,
            testStruct.flag,
            testStruct.text
        );
    }

    function setStruct(
        uint256 number,
        address addr,
        bool flag,
        string memory text
    ) public {
        testStruct = TestData({
            number: number,
            addr: addr,
            flag: flag,
            text: text
        });
    }

    // ============= STORAGE SLOT TESTS =============

    function testStorageSlot0() public view returns (uint256) {
        // myValue is in slot 0
        return myValue;
    }

    function testStorageSlot1() public view returns (uint256) {
        // blockTimestamp is in slot 1
        return blockTimestamp;
    }

    function testStorageSlot2() public view returns (address) {
        // deployer is in slot 2
        return deployer;
    }

    function testStorageSlot3() public view returns (bytes32) {
        // publicKey is in slot 3
        return publicKey;
    }

    // ============= COMPREHENSIVE STORAGE CHECK =============

    function checkAllStorage() public view returns (
        bool allOk,
        string memory message
    ) {
        if (myValue == 0) return (false, "myValue is zero");
        if (blockTimestamp == 0) return (false, "blockTimestamp is zero");
        if (deployer == address(0)) return (false, "deployer is zero address");
        if (value1 == 0) return (false, "value1 is zero");
        if (value2 == 0) return (false, "value2 is zero");
        if (value3 == 0) return (false, "value3 is zero");
        if (dynamicArray.length == 0) return (false, "array is empty");
        if (storageMap[0] == 0) return (false, "map[0] is zero");
        if (balances[deployer] == 0) return (false, "deployer balance is zero");
        if (testStruct.number == 0) return (false, "struct.number is zero");

        return (true, "All storage slots OK");
    }

    // ============= DIAGNOSTIC FUNCTIONS =============

    function getCurrentBlockNumber() public view returns (uint256) {
        return block.number;
    }

    function getCurrentTimestamp() public view returns (uint256) {
        return block.timestamp;
    }

    function getMsgSender() public view returns (address) {
        return msg.sender;
    }

    function getChainId() public view returns (uint256) {
        return block.chainid;
    }

    function testRevert() public pure {
        revert("Intentional revert for testing");
    }

    function testAssert() public pure returns (bool) {
        assert(1 + 1 == 2);
        return true;
    }

    function testRequire(uint256 value) public pure returns (uint256) {
        require(value > 0, "Value must be positive");
        return value * 2;
    }

    // ============= BATCH OPERATIONS =============

    function batchSetValues(uint256[] memory values) public {
        require(values.length >= 3, "Need at least 3 values");
        value1 = values[0];
        value2 = values[1];
        value3 = values[2];
    }

    function batchGetValues() public view returns (uint256[] memory) {
        uint256[] memory result = new uint256[](3);
        result[0] = value1;
        result[1] = value2;
        result[2] = value3;
        return result;
    }

    // ============= STORAGE STATISTICS =============

    function getStorageStats() public view returns (
        uint256 simpleVarCount,
        uint256 arrayLength,
        uint256 structFieldCount,
        uint256 totalStorageSlots
    ) {
        return (
            7,  // myValue, blockTimestamp, deployer, publicKey, v1, v2, v3
            dynamicArray.length,
            4,  // testStruct has 4 fields
            7 + dynamicArray.length + 4  // approximate total
        );
    }

    // ============= DEBUGGING HELPERS =============

    function debugStorageValues() public view returns (
        uint256 _myValue,
        uint256 _blockTimestamp,
        address _deployer,
        bytes32 _publicKey,
        bool deployerIsZero,
        bool myValueIsZero,
        bool timestampIsZero
    ) {
        return (
            myValue,
            blockTimestamp,
            deployer,
            publicKey,
            deployer == address(0),
            myValue == 0,
            blockTimestamp == 0
        );
    }

    // ============= EMERGENCY FUNCTIONS =============

    function reset() public {
        myValue = 42;
        blockTimestamp = block.timestamp;
        value1 = 100;
        value2 = 200;
        value3 = 300;
        emit StorageTest("Storage reset", myValue);
    }

    function forceSetAll(
        uint256 _myValue,
        uint256 _timestamp,
        address _deployer
    ) public {
        myValue = _myValue;
        blockTimestamp = _timestamp;
        deployer = _deployer;
        emit StorageTest("Force set completed", _myValue);
    }
}
