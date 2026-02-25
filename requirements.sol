// SPDX-License-Identifier: none
pragma solidity ^0.8.19;

/**
 * @title Sapphire
 * @dev Convenient wrapper methods for Sapphire's cryptographic primitives.
 */
library Sapphire {
	// Oasis-specific, confidential precompiles
	address internal constant RANDOM_BYTES = 0x0100000000000000000000000000000000000001;
	address internal constant DERIVE_KEY = 0x0100000000000000000000000000000000000002;
	address internal constant ENCRYPT = 0x0100000000000000000000000000000000000003;
	address internal constant DECRYPT = 0x0100000000000000000000000000000000000004;
	address internal constant GENERATE_SIGNING_KEYPAIR = 0x0100000000000000000000000000000000000005;
	address internal constant SIGN_DIGEST = 0x0100000000000000000000000000000000000006;
	address internal constant VERIFY_DIGEST = 0x0100000000000000000000000000000000000007;
	address internal constant CURVE25519_PUBLIC_KEY = 0x0100000000000000000000000000000000000008;
	address internal constant GAS_USED = 0x0100000000000000000000000000000000000009;
	address internal constant PAD_GAS = 0x010000000000000000000000000000000000000a;

	// Oasis-specific, general precompiles
	address internal constant SHA512_256 = 0x0100000000000000000000000000000000000101;
	address internal constant SHA512 = 0x0100000000000000000000000000000000000102;
	address internal constant SHA384 = 0x0100000000000000000000000000000000000104;

	type Curve25519PublicKey is bytes32;
	type Curve25519SecretKey is bytes32;

	enum SigningAlg {
		// Ed25519 signature over the provided message using SHA-512/265 with a domain separator.
		// Can be used to sign transactions for the Oasis consensus layer and SDK paratimes.
		Ed25519Oasis,
		// Ed25519 signature over the provided message.
		Ed25519Pure,
		// Ed25519 signature over the provided prehashed SHA-512 digest.
		Ed25519PrehashedSha512,
		// Secp256k1 signature over the provided message using SHA-512/256 with a domain separator.
		// Can be used to sign transactions for the Oasis consensus layer and SDK paratimes.
		Secp256k1Oasis,
		// Secp256k1 over the provided Keccak256 digest.
		// Can be used to sign transactions for Ethereum-compatible networks.
		Secp256k1PrehashedKeccak256,
		// Secp256k1 signature over the provided SHA-256 digest.
		Secp256k1PrehashedSha256,
		// Sr25519 signature over the provided message.
		Sr25519,
		// Secp256r1 signature over the provided SHA-256 digest.
		Secp256r1PrehashedSha256,
		// Secp384r1 signature over the provided SHA-384 digest.
		Secp384r1PrehashedSha384
	}

	/**
	 * @dev Returns cryptographically secure random bytes.
	 * @param numBytes The number of bytes to return.
	 * @param pers An optional personalization string to increase domain separation.
	 * @return The random bytes. If the number of bytes requested is too large (over 1024), a smaller amount (1024) will be returned.
	 */
	function randomBytes(uint256 numBytes, bytes memory pers) internal view returns (bytes memory) {
		(bool success, bytes memory entropy) = RANDOM_BYTES.staticcall(abi.encode(numBytes, pers));
		require(success, 'randomBytes: failed');
		return entropy;
	}

	/**
	 * @dev Generates a Curve25519 keypair.
	 * @param pers An optional personalization string used to add domain separation.
	 * @return pk The Curve25519 public key. Useful for key exchange.
	 * @return sk The Curve25519 secret key. Pairs well with {`deriveSymmetricKey`}.
	 */
	function generateCurve25519KeyPair(bytes memory pers) internal view returns (Curve25519PublicKey pk, Curve25519SecretKey sk) {
		bytes memory scalar = randomBytes(32, pers);
		// Twiddle some bits, as per RFC 7748 §5.
		scalar[0] &= 0xf8; // Make it a multiple of 8 to avoid small subgroup attacks.
		scalar[31] &= 0x7f; // Clamp to < 2^255 - 19
		scalar[31] |= 0x40; // Clamp to >= 2^254
		(bool success, bytes memory pkBytes) = CURVE25519_PUBLIC_KEY.staticcall(scalar);
		require(success, 'gen curve25519 pk: failed');
		return (Curve25519PublicKey.wrap(bytes32(pkBytes)), Curve25519SecretKey.wrap(bytes32(scalar)));
	}

	/**
	 * @dev Derive a symmetric key from a pair of keys using x25519.
	 * @param peerPublicKey The peer's public key.
	 * @param secretKey Your secret key.
	 * @return A derived symmetric key.
	 */
	function deriveSymmetricKey(Curve25519PublicKey peerPublicKey, Curve25519SecretKey secretKey) internal view returns (bytes32) {
		(bool success, bytes memory symmetric) = DERIVE_KEY.staticcall(abi.encode(peerPublicKey, secretKey));
		require(success, 'deriveSymmetricKey: failed');
		return bytes32(symmetric);
	}

	/**
	 * @dev Encrypt and authenticate the plaintext and additional data using DeoxysII.
	 * @param key The key to use for encryption.
	 * @param nonce The nonce. Note that only the first 15 bytes of this parameter are used.
	 * @param plaintext The plaintext to encrypt and authenticate.
	 * @param additionalData The additional data to authenticate.
	 * @return The ciphertext with appended auth tag.
	 */
	function encrypt(bytes32 key, bytes32 nonce, bytes memory plaintext, bytes memory additionalData) internal view returns (bytes memory) {
		(bool success, bytes memory ciphertext) = ENCRYPT.staticcall(abi.encode(key, nonce, plaintext, additionalData));
		require(success, 'encrypt: failed');
		return ciphertext;
	}

	/**
	 * @dev Decrypt and authenticate the ciphertext and additional data using DeoxysII. Reverts if the auth tag is incorrect.
	 * @param key The key to use for decryption.
	 * @param nonce The nonce. Note that only the first 15 bytes of this parameter are used.
	 * @param ciphertext The ciphertext with tag to decrypt and authenticate.
	 * @param additionalData The additional data to authenticate against the ciphertext.
	 * @return The original plaintext.
	 */
	function decrypt(bytes32 key, bytes32 nonce, bytes memory ciphertext, bytes memory additionalData) internal view returns (bytes memory) {
		(bool success, bytes memory plaintext) = DECRYPT.staticcall(abi.encode(key, nonce, ciphertext, additionalData));
		require(success, 'decrypt: failed');
		return plaintext;
	}

	/**
	 * @dev Generate a public/private key pair using the specified method and seed.
	 * @param alg The signing alg for which to generate a keypair.
	 * @param seed The seed to use for generating the key pair. You can use the `randomBytes` method if you don't already have a seed.
	 * @return publicKey The public half of the keypair.
	 * @return secretKey The secret half of the keypair.
	 */
	function generateSigningKeyPair(SigningAlg alg, bytes memory seed) internal view returns (bytes memory publicKey, bytes memory secretKey) {
		(bool success, bytes memory keypair) = GENERATE_SIGNING_KEYPAIR.staticcall(abi.encode(alg, seed));
		require(success, 'gen signing keypair: failed');
		return abi.decode(keypair, (bytes, bytes));
	}

	/**
	 * @dev Sign a message within the provided context using the specified algorithm, and return the signature.
	 * @param alg The signing algorithm to use.
	 * @param secretKey The secret key to use for signing. The key must be valid for use with the requested algorithm.
	 * @param contextOrHash Domain-Separator Context, or precomputed hash bytes
	 * @param message Message to sign, should be zero-length if precomputed hash given
	 * @return signature The resulting signature.
	 * @custom:see @oasisprotocol/oasis-sdk :: precompile/confidential.rs :: call_sign
	 */
	function sign(SigningAlg alg, bytes memory secretKey, bytes memory contextOrHash, bytes memory message) internal view returns (bytes memory signature) {
		(bool success, bytes memory sig) = SIGN_DIGEST.staticcall(abi.encode(alg, secretKey, contextOrHash, message));
		require(success, 'sign: failed');
		return sig;
	}

	/**
	 * @dev Verifies that the provided digest was signed with using the secret key corresponding to the provided private key and the specified signing algorithm.
	 * @param alg The signing algorithm by which the signature was generated.
	 * @param publicKey The public key against which to check the signature.
	 * @param contextOrHash Domain-Separator Context, or precomputed hash bytes
	 * @param message The hash of the message that was signed, should be zero-length if precomputed hash was given
	 * @param signature The signature to check.
	 * @return verified Whether the signature is valid for the given parameters.
	 * @custom:see @oasisprotocol/oasis-sdk :: precompile/confidential.rs :: call_verify
	 */
	function verify(SigningAlg alg, bytes memory publicKey, bytes memory contextOrHash, bytes memory message, bytes memory signature) internal view returns (bool verified) {
		(bool success, bytes memory v) = VERIFY_DIGEST.staticcall(abi.encode(alg, publicKey, contextOrHash, message, signature));
		require(success, 'verify: failed');
		return abi.decode(v, (bool));
	}

	/**
	 * @dev Set the current transactions gas usage to a specific amount
	 * @param toAmount Gas usage will be set to this amount
	 * @custom:see @oasisprotocol/oasis-sdk :: precompile/gas.rs :: call_pad_gas
	 *
	 * Will cause a reversion if the current usage is more than the amount
	 */
	function padGas(uint128 toAmount) internal view {
		(bool success, ) = PAD_GAS.staticcall(abi.encode(toAmount));
		require(success, 'verify: failed');
	}

	/**
	 * @dev Returns the amount of gas currently used by the transaction
	 * @custom:see @oasisprotocol/oasis-sdk :: precompile/gas.rs :: call_gas_used
	 */
	function gasUsed() internal view returns (uint64) {
		(bool success, bytes memory v) = GAS_USED.staticcall('');
		require(success, 'gasused: failed');
		return abi.decode(v, (uint64));
	}
}

/**
 * Hash the input data with SHA-512/256
 *
 * SHA-512 is vulnerable to length-extension attacks, which are relevant if you
 * are computing the hash of a secret message. The SHA-512/256 variant is
 * **not** vulnerable to length-extension attacks.
 *
 * @custom:standard https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf
 * @custom:see @oasisprotocol/oasis-sdk :: precompile/sha2.rs :: call_sha512_256
 * @param input Bytes to hash
 * @return result 32 byte digest
 */
function sha512_256(bytes memory input) view returns (bytes32 result) {
	(bool success, bytes memory output) = Sapphire.SHA512_256.staticcall(input);

	require(success, 'sha512_256');

	return bytes32(output);
}

/**
 * Hash the input data with SHA-512
 *
 * @custom:standard https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf
 * @custom:see @oasisprotocol/oasis-sdk :: precompile/sha2.rs :: call_sha512
 * @param input Bytes to hash
 * @return output 64 byte digest
 */
function sha512(bytes memory input) view returns (bytes memory output) {
	bool success;

	(success, output) = Sapphire.SHA512.staticcall(input);

	require(success, 'sha512');
}

/**
 * Hash the input data with SHA-384
 *
 * @custom:standard https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf
 * @custom:see @oasisprotocol/oasis-sdk :: precompile/sha2.rs :: call_sha384
 * @param input Bytes to hash
 * @return output 48 byte digest
 */
function sha384(bytes memory input) view returns (bytes memory output) {
	bool success;

	(success, output) = Sapphire.SHA384.staticcall(input);

	require(success, 'sha384');
}

struct SignatureRSV {
	bytes32 r;
	bytes32 s;
	uint256 v;
}

library EthereumUtils {
	uint256 internal constant K256_P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f;

	// (p+1)//4
	uint256 internal constant K256_P_PLUS_1_OVER_4 = 0x3fffffffffffffffffffffffffffffffffffffffffffffffffffffffbfffff0c;

	address internal constant PRECOMPILE_BIGMODEXP = address(0x5);

	error expmod_Error();

	function expmod(uint256 base, uint256 exponent, uint256 modulus) internal view returns (uint256 out) {
		(bool success, bytes memory result) = PRECOMPILE_BIGMODEXP.staticcall(
			abi.encodePacked(
				uint256(0x20), // length of base
				uint256(0x20), // length of exponent
				uint256(0x20), // length of modulus
				base,
				exponent,
				modulus
			)
		);

		if (!success) revert expmod_Error();

		out = uint256(bytes32(result));
	}

	error k256DeriveY_Invalid_Prefix_Error();

	/**
	 * Recover Y coordinate from X coordinate and sign bit
	 * @param prefix 0x02 or 0x03 indicates sign bit of compressed point
	 * @param x X coordinate
	 */
	function k256DeriveY(uint8 prefix, uint256 x) internal view returns (uint256 y) {
		if (prefix != 0x02 && prefix != 0x03) revert k256DeriveY_Invalid_Prefix_Error();

		// x^3 + ax + b, where a=0, b=7
		y = addmod(mulmod(x, mulmod(x, x, K256_P), K256_P), 7, K256_P);

		// find square root of quadratic residue
		y = expmod(y, K256_P_PLUS_1_OVER_4, K256_P);

		// negate y if indicated by sign bit
		if ((y + prefix) % 2 != 0) {
			y = K256_P - y;
		}
	}

	error k256Decompress_Invalid_Length_Error();

	/**
	 * Decompress SEC P256 k1 point
	 * @param pk 33 byte compressed public key
	 * @return x coordinate
	 * @return y coordinate
	 */
	function k256Decompress(bytes memory pk) internal view returns (uint256 x, uint256 y) {
		if (pk.length != 33) revert k256Decompress_Invalid_Length_Error();
		assembly {
			// skip 32 byte length prefix, plus one byte sign prefix
			x := mload(add(pk, 33))
		}
		y = k256DeriveY(uint8(pk[0]), x);
	}

	function k256PubkeyToEthereumAddress(bytes memory pubkey) internal view returns (address) {
		(uint256 x, uint256 y) = k256Decompress(pubkey);
		return toEthereumAddress(x, y);
	}

	/**
	 * Convert SEC P256 k1 curve point to Ethereum address
	 * @param x coordinate
	 * @param y coordinate
	 * @custom:see https://gavwood.com/paper.pdf (212)
	 */
	function toEthereumAddress(uint256 x, uint256 y) internal pure returns (address) {
		bytes32 digest = keccak256(abi.encodePacked(x, y));

		return address(uint160((uint256(digest) << 96) >> 96));
	}

	error DER_Split_Error();

	/**
	 * Extracts the `r` and `s` parameters from a DER encoded ECDSA signature.
	 *
	 * The signature is an ASN1 encoded SEQUENCE of the variable length `r` and `s` INTEGERs.
	 *
	 * | 0x30 | len(z) | 0x02 | len(r) |  r   | 0x02 | len(s) |  s   | = hex value
	 * |  1   |   1    |   1  |   1    | 1-33 |  1   |   1    | 1-33 | = byte length
	 *
	 * If the highest bit of either `r` or `s` is set, it will be prefix padded with a zero byte
	 * There is exponentially decreasing probability that either `r` or `s` will be below 32 bytes.
	 * There is a very high probability that either `r` or `s` will be 33 bytes.
	 * This function only works if either `r` or `s` are 256bits or lower.
	 *
	 * @param der DER encoded ECDSA signature
	 * @return rsv ECDSA R point X coordinate, and S scalar
	 * @custom:see https://bitcoin.stackexchange.com/questions/58853/how-do-you-figure-out-the-r-and-s-out-of-a-signature-using-python
	 */
	function splitDERSignature(bytes memory der) internal pure returns (SignatureRSV memory rsv) {
		if (der.length < 8) revert DER_Split_Error();
		if (der[0] != 0x30) revert DER_Split_Error();
		if (der[2] != 0x02) revert DER_Split_Error();

		uint256 zLen = uint8(der[1]);
		uint256 rLen = uint8(der[3]);
		if (rLen > 33) revert DER_Split_Error();

		uint256 sOffset = 4 + rLen;
		uint256 sLen = uint8(der[sOffset + 1]);
		if (sLen > 33) revert DER_Split_Error();
		if (der[sOffset] != 0x02) revert DER_Split_Error();

		if (rLen + sLen + 4 != zLen) revert DER_Split_Error();
		if (der.length != zLen + 2) revert DER_Split_Error();

		sOffset += 2;
		uint256 rOffset = 4;

		if (rLen == 33) {
			if (der[4] != 0x00) revert DER_Split_Error();
			rOffset += 1;
			rLen -= 1;
		}

		if (sLen == 33) {
			if (der[sOffset] != 0x00) revert DER_Split_Error();
			sOffset += 1;
			sLen -= 1;
		}

		bytes32 r;
		bytes32 s;

		assembly {
			r := mload(add(der, add(32, rOffset)))
			s := mload(add(der, add(32, sOffset)))
		}

		// When length of either `r` or `s` is below 32 bytes
		// the 32 byte `mload` will suffix it with unknown stuff
		// shift right to remove the unknown stuff, prefixing with zeros instead

		if (rLen < 32) {
			r >>= 8 * (32 - rLen);
		}

		if (sLen < 32) {
			s >>= 8 * (32 - sLen);
		}

		rsv.r = r;
		rsv.s = s;
	}

	error recoverV_Error();

	function recoverV(address pubkeyAddr, bytes32 digest, SignatureRSV memory rsv) internal pure {
		rsv.v = 27;

		if (ecrecover(digest, uint8(rsv.v), rsv.r, rsv.s) != pubkeyAddr) {
			rsv.v = 28;

			if (ecrecover(digest, uint8(rsv.v), rsv.r, rsv.s) != pubkeyAddr) {
				revert recoverV_Error();
			}
		}
	}

	/**
	 * Convert a Secp256k1PrehashedKeccak256 signature to one accepted by ecrecover
	 * @param pubkey 33 byte compressed public key
	 * @param digest 32 byte pre-hashed message digest
	 * @param signature ASN.1 DER encoded signature, as returned from `Sapphire.sign`
	 * @return pubkeyAddr 20 byte Ethereum address
	 * @return rsv Ethereum EcDSA RSV signature values
	 * @custom:see https://gavwood.com/paper.pdf (206)
	 */
	function toEthereumSignature(bytes memory pubkey, bytes32 digest, bytes memory signature) internal view returns (address pubkeyAddr, SignatureRSV memory rsv) {
		pubkeyAddr = k256PubkeyToEthereumAddress(pubkey);

		rsv = splitDERSignature(signature);

		recoverV(pubkeyAddr, digest, rsv);
	}

	function sign(address pubkeyAddr, bytes32 secretKey, bytes32 digest) internal view returns (SignatureRSV memory rsv) {
		bytes memory signature = Sapphire.sign(Sapphire.SigningAlg.Secp256k1PrehashedKeccak256, abi.encodePacked(secretKey), abi.encodePacked(digest), '');

		rsv = splitDERSignature(signature);

		recoverV(pubkeyAddr, digest, rsv);
	}

	/**
	 * Generates an Ethereum compatible SEC P256 k1 keypair and corresponding public address
	 * @return pubkeyAddr Ethereum address
	 * @return secretKey Secret key used for signing
	 */
	function generateKeypair() internal view returns (address pubkeyAddr, bytes32 secretKey) {
		bytes memory randSeed = Sapphire.randomBytes(32, '');

		secretKey = bytes32(randSeed);

		(bytes memory pk, ) = Sapphire.generateSigningKeyPair(Sapphire.SigningAlg.Secp256k1PrehashedKeccak256, randSeed);

		pubkeyAddr = k256PubkeyToEthereumAddress(pk);
	}
}
library Math {
	enum Rounding {
		Down, // Toward negative infinity
		Up, // Toward infinity
		Zero // Toward zero
	}

	/**
	 * @dev Returns the largest of two numbers.
	 */
	function max(uint256 a, uint256 b) internal pure returns (uint256) {
		return a > b ? a : b;
	}

	/**
	 * @dev Returns the smallest of two numbers.
	 */
	function min(uint256 a, uint256 b) internal pure returns (uint256) {
		return a < b ? a : b;
	}

	/**
	 * @dev Returns the average of two numbers. The result is rounded towards
	 * zero.
	 */
	function average(uint256 a, uint256 b) internal pure returns (uint256) {
		// (a + b) / 2 can overflow.
		return (a & b) + (a ^ b) / 2;
	}

	/**
	 * @dev Returns the ceiling of the division of two numbers.
	 *
	 * This differs from standard division with `/` in that it rounds up instead
	 * of rounding down.
	 */
	function ceilDiv(uint256 a, uint256 b) internal pure returns (uint256) {
		// (a + b - 1) / b can overflow on addition, so we distribute.
		return a == 0 ? 0 : (a - 1) / b + 1;
	}

	/**
	 * @notice Calculates floor(x * y / denominator) with full precision. Throws if result overflows a uint256 or denominator == 0
	 * @dev Original credit to Remco Bloemen under MIT license (https://xn--2-umb.com/21/muldiv)
	 * with further edits by Uniswap Labs also under MIT license.
	 */
	function mulDiv(uint256 x, uint256 y, uint256 denominator) internal pure returns (uint256 result) {
		unchecked {
			// 512-bit multiply [prod1 prod0] = x * y. Compute the product mod 2^256 and mod 2^256 - 1, then use
			// use the Chinese Remainder Theorem to reconstruct the 512 bit result. The result is stored in two 256
			// variables such that product = prod1 * 2^256 + prod0.
			uint256 prod0; // Least significant 256 bits of the product
			uint256 prod1; // Most significant 256 bits of the product
			assembly {
				let mm := mulmod(x, y, not(0))
				prod0 := mul(x, y)
				prod1 := sub(sub(mm, prod0), lt(mm, prod0))
			}

			// Handle non-overflow cases, 256 by 256 division.
			if (prod1 == 0) {
				return prod0 / denominator;
			}

			// Make sure the result is less than 2^256. Also prevents denominator == 0.
			require(denominator > prod1);

			///////////////////////////////////////////////
			// 512 by 256 division.
			///////////////////////////////////////////////

			// Make division exact by subtracting the remainder from [prod1 prod0].
			uint256 remainder;
			assembly {
				// Compute remainder using mulmod.
				remainder := mulmod(x, y, denominator)

				// Subtract 256 bit number from 512 bit number.
				prod1 := sub(prod1, gt(remainder, prod0))
				prod0 := sub(prod0, remainder)
			}

			// Factor powers of two out of denominator and compute largest power of two divisor of denominator. Always >= 1.
			// See https://cs.stackexchange.com/q/138556/92363.

			// Does not overflow because the denominator cannot be zero at this stage in the function.
			uint256 twos = denominator & (~denominator + 1);
			assembly {
				// Divide denominator by twos.
				denominator := div(denominator, twos)

				// Divide [prod1 prod0] by twos.
				prod0 := div(prod0, twos)

				// Flip twos such that it is 2^256 / twos. If twos is zero, then it becomes one.
				twos := add(div(sub(0, twos), twos), 1)
			}

			// Shift in bits from prod1 into prod0.
			prod0 |= prod1 * twos;

			// Invert denominator mod 2^256. Now that denominator is an odd number, it has an inverse modulo 2^256 such
			// that denominator * inv = 1 mod 2^256. Compute the inverse by starting with a seed that is correct for
			// four bits. That is, denominator * inv = 1 mod 2^4.
			uint256 inverse = (3 * denominator) ^ 2;

			// Use the Newton-Raphson iteration to improve the precision. Thanks to Hensel's lifting lemma, this also works
			// in modular arithmetic, doubling the correct bits in each step.
			inverse *= 2 - denominator * inverse; // inverse mod 2^8
			inverse *= 2 - denominator * inverse; // inverse mod 2^16
			inverse *= 2 - denominator * inverse; // inverse mod 2^32
			inverse *= 2 - denominator * inverse; // inverse mod 2^64
			inverse *= 2 - denominator * inverse; // inverse mod 2^128
			inverse *= 2 - denominator * inverse; // inverse mod 2^256

			// Because the division is now exact we can divide by multiplying with the modular inverse of denominator.
			// This will give us the correct result modulo 2^256. Since the preconditions guarantee that the outcome is
			// less than 2^256, this is the final result. We don't need to compute the high bits of the result and prod1
			// is no longer required.
			result = prod0 * inverse;
			return result;
		}
	}

	/**
	 * @notice Calculates x * y / denominator with full precision, following the selected rounding direction.
	 */
	function mulDiv(uint256 x, uint256 y, uint256 denominator, Rounding rounding) internal pure returns (uint256) {
		uint256 result = mulDiv(x, y, denominator);
		if (rounding == Rounding.Up && mulmod(x, y, denominator) > 0) {
			result += 1;
		}
		return result;
	}

	/**
	 * @dev Returns the square root of a number. If the number is not a perfect square, the value is rounded down.
	 *
	 * Inspired by Henry S. Warren, Jr.'s "Hacker's Delight" (Chapter 11).
	 */
	function sqrt(uint256 a) internal pure returns (uint256) {
		if (a == 0) {
			return 0;
		}

		// For our first guess, we get the biggest power of 2 which is smaller than the square root of the target.
		//
		// We know that the "msb" (most significant bit) of our target number `a` is a power of 2 such that we have
		// `msb(a) <= a < 2*msb(a)`. This value can be written `msb(a)=2**k` with `k=log2(a)`.
		//
		// This can be rewritten `2**log2(a) <= a < 2**(log2(a) + 1)`
		// → `sqrt(2**k) <= sqrt(a) < sqrt(2**(k+1))`
		// → `2**(k/2) <= sqrt(a) < 2**((k+1)/2) <= 2**(k/2 + 1)`
		//
		// Consequently, `2**(log2(a) / 2)` is a good first approximation of `sqrt(a)` with at least 1 correct bit.
		uint256 result = 1 << (log2(a) >> 1);

		// At this point `result` is an estimation with one bit of precision. We know the true value is a uint128,
		// since it is the square root of a uint256. Newton's method converges quadratically (precision doubles at
		// every iteration). We thus need at most 7 iteration to turn our partial result with one bit of precision
		// into the expected uint128 result.
		unchecked {
			result = (result + a / result) >> 1;
			result = (result + a / result) >> 1;
			result = (result + a / result) >> 1;
			result = (result + a / result) >> 1;
			result = (result + a / result) >> 1;
			result = (result + a / result) >> 1;
			result = (result + a / result) >> 1;
			return min(result, a / result);
		}
	}

	/**
	 * @notice Calculates sqrt(a), following the selected rounding direction.
	 */
	function sqrt(uint256 a, Rounding rounding) internal pure returns (uint256) {
		unchecked {
			uint256 result = sqrt(a);
			return result + (rounding == Rounding.Up && result * result < a ? 1 : 0);
		}
	}

	/**
	 * @dev Return the log in base 2, rounded down, of a positive value.
	 * Returns 0 if given 0.
	 */
	function log2(uint256 value) internal pure returns (uint256) {
		uint256 result = 0;
		unchecked {
			if (value >> 128 > 0) {
				value >>= 128;
				result += 128;
			}
			if (value >> 64 > 0) {
				value >>= 64;
				result += 64;
			}
			if (value >> 32 > 0) {
				value >>= 32;
				result += 32;
			}
			if (value >> 16 > 0) {
				value >>= 16;
				result += 16;
			}
			if (value >> 8 > 0) {
				value >>= 8;
				result += 8;
			}
			if (value >> 4 > 0) {
				value >>= 4;
				result += 4;
			}
			if (value >> 2 > 0) {
				value >>= 2;
				result += 2;
			}
			if (value >> 1 > 0) {
				result += 1;
			}
		}
		return result;
	}

	/**
	 * @dev Return the log in base 2, following the selected rounding direction, of a positive value.
	 * Returns 0 if given 0.
	 */
	function log2(uint256 value, Rounding rounding) internal pure returns (uint256) {
		unchecked {
			uint256 result = log2(value);
			return result + (rounding == Rounding.Up && 1 << result < value ? 1 : 0);
		}
	}

	/**
	 * @dev Return the log in base 10, rounded down, of a positive value.
	 * Returns 0 if given 0.
	 */
	function log10(uint256 value) internal pure returns (uint256) {
		uint256 result = 0;
		unchecked {
			if (value >= 10 ** 64) {
				value /= 10 ** 64;
				result += 64;
			}
			if (value >= 10 ** 32) {
				value /= 10 ** 32;
				result += 32;
			}
			if (value >= 10 ** 16) {
				value /= 10 ** 16;
				result += 16;
			}
			if (value >= 10 ** 8) {
				value /= 10 ** 8;
				result += 8;
			}
			if (value >= 10 ** 4) {
				value /= 10 ** 4;
				result += 4;
			}
			if (value >= 10 ** 2) {
				value /= 10 ** 2;
				result += 2;
			}
			if (value >= 10 ** 1) {
				result += 1;
			}
		}
		return result;
	}

	/**
	 * @dev Return the log in base 10, following the selected rounding direction, of a positive value.
	 * Returns 0 if given 0.
	 */
	function log10(uint256 value, Rounding rounding) internal pure returns (uint256) {
		unchecked {
			uint256 result = log10(value);
			return result + (rounding == Rounding.Up && 10 ** result < value ? 1 : 0);
		}
	}

	/**
	 * @dev Return the log in base 256, rounded down, of a positive value.
	 * Returns 0 if given 0.
	 *
	 * Adding one to the result gives the number of pairs of hex symbols needed to represent `value` as a hex string.
	 */
	function log256(uint256 value) internal pure returns (uint256) {
		uint256 result = 0;
		unchecked {
			if (value >> 128 > 0) {
				value >>= 128;
				result += 16;
			}
			if (value >> 64 > 0) {
				value >>= 64;
				result += 8;
			}
			if (value >> 32 > 0) {
				value >>= 32;
				result += 4;
			}
			if (value >> 16 > 0) {
				value >>= 16;
				result += 2;
			}
			if (value >> 8 > 0) {
				result += 1;
			}
		}
		return result;
	}

	/**
	 * @dev Return the log in base 10, following the selected rounding direction, of a positive value.
	 * Returns 0 if given 0.
	 */
	function log256(uint256 value, Rounding rounding) internal pure returns (uint256) {
		unchecked {
			uint256 result = log256(value);
			return result + (rounding == Rounding.Up && 1 << (result * 8) < value ? 1 : 0);
		}
	}
}
library Strings {
	bytes16 private constant _SYMBOLS = '0123456789abcdef';
	uint8 private constant _ADDRESS_LENGTH = 20;

	/**
	 * @dev Converts a `uint256` to its ASCII `string` decimal representation.
	 */
	function toString(uint256 value) internal pure returns (string memory) {
		unchecked {
			uint256 length = Math.log10(value) + 1;
			string memory buffer = new string(length);
			uint256 ptr;
			/// @solidity memory-safe-assembly
			assembly {
				ptr := add(buffer, add(32, length))
			}
			while (true) {
				ptr--;
				/// @solidity memory-safe-assembly
				assembly {
					mstore8(ptr, byte(mod(value, 10), _SYMBOLS))
				}
				value /= 10;
				if (value == 0) break;
			}
			return buffer;
		}
	}

	/**
	 * @dev Converts a `uint256` to its ASCII `string` hexadecimal representation.
	 */
	function toHexString(uint256 value) internal pure returns (string memory) {
		unchecked {
			return toHexString(value, Math.log256(value) + 1);
		}
	}

	/**
	 * @dev Converts a `uint256` to its ASCII `string` hexadecimal representation with fixed length.
	 */
	function toHexString(uint256 value, uint256 length) internal pure returns (string memory) {
		bytes memory buffer = new bytes(2 * length + 2);
		buffer[0] = '0';
		buffer[1] = 'x';
		for (uint256 i = 2 * length + 1; i > 1; --i) {
			buffer[i] = _SYMBOLS[value & 0xf];
			value >>= 4;
		}
		require(value == 0, 'Strings: hex length insufficient');
		return string(buffer);
	}

	/**
	 * @dev Converts an `address` with fixed length of 20 bytes to its not checksummed ASCII `string` hexadecimal representation.
	 */
	function toHexString(address addr) internal pure returns (string memory) {
		return toHexString(uint256(uint160(addr)), _ADDRESS_LENGTH);
	}
}
library ECDSA {
	enum RecoverError {
		NoError,
		InvalidSignature,
		InvalidSignatureLength,
		InvalidSignatureS,
		InvalidSignatureV // Deprecated in v4.8
	}

	function _throwError(RecoverError error) private pure {
		if (error == RecoverError.NoError) {
			return; // no error: do nothing
		} else if (error == RecoverError.InvalidSignature) {
			revert('ECDSA: invalid signature');
		} else if (error == RecoverError.InvalidSignatureLength) {
			revert('ECDSA: invalid signature length');
		} else if (error == RecoverError.InvalidSignatureS) {
			revert("ECDSA: invalid signature 's' value");
		}
	}

	/**
	 * @dev Returns the address that signed a hashed message (`hash`) with
	 * `signature` or error string. This address can then be used for verification purposes.
	 *
	 * The `ecrecover` EVM opcode allows for malleable (non-unique) signatures:
	 * this function rejects them by requiring the `s` value to be in the lower
	 * half order, and the `v` value to be either 27 or 28.
	 *
	 * IMPORTANT: `hash` _must_ be the result of a hash operation for the
	 * verification to be secure: it is possible to craft signatures that
	 * recover to arbitrary addresses for non-hashed data. A safe way to ensure
	 * this is by receiving a hash of the original message (which may otherwise
	 * be too long), and then calling {toEthSignedMessageHash} on it.
	 *
	 * Documentation for signature generation:
	 * - with https://web3js.readthedocs.io/en/v1.3.4/web3-eth-accounts.html#sign[Web3.js]
	 * - with https://docs.ethers.io/v5/api/signer/#Signer-signMessage[ethers]
	 *
	 * _Available since v4.3._
	 */
	function tryRecover(bytes32 hash, bytes memory signature) internal pure returns (address, RecoverError) {
		if (signature.length == 65) {
			bytes32 r;
			bytes32 s;
			uint8 v;
			// ecrecover takes the signature parameters, and the only way to get them
			// currently is to use assembly.
			/// @solidity memory-safe-assembly
			assembly {
				r := mload(add(signature, 0x20))
				s := mload(add(signature, 0x40))
				v := byte(0, mload(add(signature, 0x60)))
			}
			return tryRecover(hash, v, r, s);
		} else {
			return (address(0), RecoverError.InvalidSignatureLength);
		}
	}

	/**
	 * @dev Returns the address that signed a hashed message (`hash`) with
	 * `signature`. This address can then be used for verification purposes.
	 *
	 * The `ecrecover` EVM opcode allows for malleable (non-unique) signatures:
	 * this function rejects them by requiring the `s` value to be in the lower
	 * half order, and the `v` value to be either 27 or 28.
	 *
	 * IMPORTANT: `hash` _must_ be the result of a hash operation for the
	 * verification to be secure: it is possible to craft signatures that
	 * recover to arbitrary addresses for non-hashed data. A safe way to ensure
	 * this is by receiving a hash of the original message (which may otherwise
	 * be too long), and then calling {toEthSignedMessageHash} on it.
	 */
	function recover(bytes32 hash, bytes memory signature) internal pure returns (address) {
		(address recovered, RecoverError error) = tryRecover(hash, signature);
		_throwError(error);
		return recovered;
	}

	/**
	 * @dev Overload of {ECDSA-tryRecover} that receives the `r` and `vs` short-signature fields separately.
	 *
	 * See https://eips.ethereum.org/EIPS/eip-2098[EIP-2098 short signatures]
	 *
	 * _Available since v4.3._
	 */
	function tryRecover(bytes32 hash, bytes32 r, bytes32 vs) internal pure returns (address, RecoverError) {
		bytes32 s = vs & bytes32(0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff);
		uint8 v = uint8((uint256(vs) >> 255) + 27);
		return tryRecover(hash, v, r, s);
	}

	/**
	 * @dev Overload of {ECDSA-recover} that receives the `r and `vs` short-signature fields separately.
	 *
	 * _Available since v4.2._
	 */
	function recover(bytes32 hash, bytes32 r, bytes32 vs) internal pure returns (address) {
		(address recovered, RecoverError error) = tryRecover(hash, r, vs);
		_throwError(error);
		return recovered;
	}

	/**
	 * @dev Overload of {ECDSA-tryRecover} that receives the `v`,
	 * `r` and `s` signature fields separately.
	 *
	 * _Available since v4.3._
	 */
	function tryRecover(bytes32 hash, uint8 v, bytes32 r, bytes32 s) internal pure returns (address, RecoverError) {
		// EIP-2 still allows signature malleability for ecrecover(). Remove this possibility and make the signature
		// unique. Appendix F in the Ethereum Yellow paper (https://ethereum.github.io/yellowpaper/paper.pdf), defines
		// the valid range for s in (301): 0 < s < secp256k1n ÷ 2 + 1, and for v in (302): v ∈ {27, 28}. Most
		// signatures from current libraries generate a unique signature with an s-value in the lower half order.
		//
		// If your library generates malleable signatures, such as s-values in the upper range, calculate a new s-value
		// with 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 - s1 and flip v from 27 to 28 or
		// vice versa. If your library also generates signatures with 0/1 for v instead 27/28, add 27 to v to accept
		// these malleable signatures as well.
		if (uint256(s) > 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0) {
			return (address(0), RecoverError.InvalidSignatureS);
		}

		// If the signature is valid (and not malleable), return the signer address
		address signer = ecrecover(hash, v, r, s);
		if (signer == address(0)) {
			return (address(0), RecoverError.InvalidSignature);
		}

		return (signer, RecoverError.NoError);
	}

	/**
	 * @dev Overload of {ECDSA-recover} that receives the `v`,
	 * `r` and `s` signature fields separately.
	 */
	function recover(bytes32 hash, uint8 v, bytes32 r, bytes32 s) internal pure returns (address) {
		(address recovered, RecoverError error) = tryRecover(hash, v, r, s);
		_throwError(error);
		return recovered;
	}

	/**
	 * @dev Returns an Ethereum Signed Message, created from a `hash`. This
	 * produces hash corresponding to the one signed with the
	 * https://eth.wiki/json-rpc/API#eth_sign[`eth_sign`]
	 * JSON-RPC method as part of EIP-191.
	 *
	 * See {recover}.
	 */
	function toEthSignedMessageHash(bytes32 hash) internal pure returns (bytes32) {
		// 32 is the length in bytes of hash,
		// enforced by the type signature above
		return keccak256(abi.encodePacked('\x19Ethereum Signed Message:\n32', hash));
	}

	/**
	 * @dev Returns an Ethereum Signed Message, created from `s`. This
	 * produces hash corresponding to the one signed with the
	 * https://eth.wiki/json-rpc/API#eth_sign[`eth_sign`]
	 * JSON-RPC method as part of EIP-191.
	 *
	 * See {recover}.
	 */
	function toEthSignedMessageHash(bytes memory s) internal pure returns (bytes32) {
		return keccak256(abi.encodePacked('\x19Ethereum Signed Message:\n', Strings.toString(s.length), s));
	}

	/**
	 * @dev Returns an Ethereum Signed Typed Data, created from a
	 * `domainSeparator` and a `structHash`. This produces hash corresponding
	 * to the one signed with the
	 * https://eips.ethereum.org/EIPS/eip-712[`eth_signTypedData`]
	 * JSON-RPC method as part of EIP-712.
	 *
	 * See {recover}.
	 */
	function toTypedDataHash(bytes32 domainSeparator, bytes32 structHash) internal pure returns (bytes32) {
		return keccak256(abi.encodePacked('\x19\x01', domainSeparator, structHash));
	}
}
contract Dummy {
	uint256 private myValue = 12345;
	Sapphire.Curve25519PublicKey public publicKey;
	Sapphire.Curve25519SecretKey private privateKey;

	constructor() {
		(Sapphire.Curve25519PublicKey publicKey_, Sapphire.Curve25519SecretKey privateKey_) = Sapphire.generateCurve25519KeyPair(abi.encodePacked(block.timestamp, msg.sender));
		publicKey = publicKey_;
		privateKey = privateKey_;
	}

	// Add getter function for external reading
	function getMyValue() public view returns (uint256) {
		return myValue;
	}

	function getBlockTimestamp() public view returns (uint256) {
		return block.timestamp;
	}

	function getMulti() public view returns (uint256, uint256) {
		return (block.timestamp, myValue);
	}

	function getPublicKey() public view returns (bytes32) {
		return Sapphire.Curve25519PublicKey.unwrap(publicKey);
	}

	function getSharedKey(bytes32 clientPub) public view returns (bytes32) {
		return Sapphire.deriveSymmetricKey(Sapphire.Curve25519PublicKey.wrap(clientPub), privateKey);
	}
}
