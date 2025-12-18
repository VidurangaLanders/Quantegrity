"""
Privacy Amplification using Universal Hash Functions
Ref: Bennett et al. (1995)

Reduces Eve's information about the key through compression
Uses Toeplitz matrix hashing for efficiency
"""

import numpy as np
import hashlib
from typing import Tuple

def calculate_security_parameter(lambda_sec: int = 128) -> int:
    """
    Calculate security parameter

    Standard: λ = 128 bits (provides 2^128 security)
    Can be increased to 256 for higher security
    """
    return lambda_sec

def estimate_information_leaked(ber: float, key_length: int) -> int:
    """
    Estimate upper bound on Eve's information

    Conservative estimate:
    I(Eve) ≈ key_length * h(ber)
    where h(x) is binary entropy function
    """
    if ber <= 0 or ber >= 1:
        return 0

    # Binary entropy function
    h = -ber * np.log2(ber) - (1-ber) * np.log2(1-ber)

    return int(key_length * h)

def calculate_final_key_length(original_length: int,
                              information_leaked: int,
                              security_parameter: int) -> int:
    """
    Calculate secure final key length

    Formula: l_final = l_original - I(Eve) - λ

    Where:
    - l_original: original key length
    - I(Eve): information leaked to Eve
    - λ: security parameter
    """
    final_length = original_length - information_leaked - security_parameter

    if final_length <= 0:
        raise ValueError("Key too short for secure amplification")

    return final_length

def generate_toeplitz_matrix(output_size: int, input_size: int) -> np.ndarray:
    """
    Generate random Toeplitz matrix for universal hashing

    Toeplitz matrix properties:
    - Each descending diagonal has same value
    - Random bits: output_size + input_size - 1
    - Multiplication is O(n log n) using FFT

    Args:
        output_size: Size of compressed key
        input_size: Size of original key

    Returns:
        Binary Toeplitz matrix
    """
    # Generate random bits for diagonals
    random_bits = np.random.randint(0, 2, output_size + input_size - 1)

    # Construct Toeplitz matrix
    matrix = np.zeros((output_size, input_size), dtype=int)

    for i in range(output_size):
        for j in range(input_size):
            # Diagonal index
            diag_idx = (input_size - 1) - j + i
            matrix[i, j] = random_bits[diag_idx]

    return matrix

def toeplitz_hash(key: str, matrix: np.ndarray) -> str:
    """
    Apply Toeplitz hash to key

    Operation: result = matrix · key (mod 2)

    Args:
        key: Binary string to hash
        matrix: Toeplitz matrix

    Returns:
        Compressed binary string
    """
    # Convert key to numpy array
    key_array = np.array([int(b) for b in key])

    # Matrix multiplication mod 2
    result = (matrix @ key_array) % 2

    # Convert back to string
    return ''.join(str(b) for b in result)

def privacy_amplification(reconciled_key: str,
                         ber: float,
                         security_parameter: int = 128) -> Tuple[str, dict]:
    """
    Perform privacy amplification on reconciled key

    Args:
        reconciled_key: Error-corrected key (Alice and Bob share this)
        ber: Bit error rate (before correction)
        security_parameter: Security level (default 128 bits)

    Returns:
        Tuple of (compressed secure key, statistics dict)

    Example:
        >>> key = "10110101" * 4  # 32-bit key
        >>> ber = 0.05  # 5% error rate
        >>> secure_key, stats = privacy_amplification(key, ber)
        >>> len(secure_key) < len(key)  # Compressed
        True
    """
    original_length = len(reconciled_key)

    # Estimate Eve's information
    info_leaked = estimate_information_leaked(ber, original_length)

    # Calculate final key length
    try:
        final_length = calculate_final_key_length(
            original_length,
            info_leaked,
            security_parameter
        )
    except ValueError as e:
        # Key too short for secure amplification
        return "", {
            'success': False,
            'error': str(e),
            'original_length': original_length,
            'info_leaked': info_leaked,
            'security_parameter': security_parameter,
            'required_length': info_leaked + security_parameter
        }

    # Generate Toeplitz matrix
    hash_matrix = generate_toeplitz_matrix(final_length, original_length)

    # Apply hash function
    amplified_key = toeplitz_hash(reconciled_key, hash_matrix)

    # Statistics
    stats = {
        'success': True,
        'original_length': original_length,
        'final_length': final_length,
        'info_leaked': info_leaked,
        'security_parameter': security_parameter,
        'compression_ratio': final_length / original_length,
        'bits_removed': original_length - final_length,
        'ber': ber
    }

    return amplified_key, stats

def adaptive_privacy_amplification(reconciled_key: str,
                                   ber: float,
                                   target_length: int = None) -> Tuple[str, dict]:
    """
    Adaptive privacy amplification that adjusts security parameter

    If the key is too short for standard security parameter (128 bits),
    this function will reduce the security parameter to produce a valid key.

    Args:
        reconciled_key: Error-corrected key
        ber: Bit error rate
        target_length: Desired output length (optional)

    Returns:
        Tuple of (compressed key, statistics)
    """
    original_length = len(reconciled_key)
    info_leaked = estimate_information_leaked(ber, original_length)

    # Try standard security parameter first
    security_params = [128, 64, 32, 16]

    for sec_param in security_params:
        final_length = original_length - info_leaked - sec_param

        if target_length and final_length != target_length:
            continue

        if final_length > 0:
            hash_matrix = generate_toeplitz_matrix(final_length, original_length)
            amplified_key = toeplitz_hash(reconciled_key, hash_matrix)

            stats = {
                'success': True,
                'original_length': original_length,
                'final_length': final_length,
                'info_leaked': info_leaked,
                'security_parameter': sec_param,
                'compression_ratio': final_length / original_length,
                'bits_removed': original_length - final_length,
                'ber': ber,
                'adaptive': True
            }

            return amplified_key, stats

    # If all attempts failed
    return "", {
        'success': False,
        'error': 'Key too short even with minimum security parameter',
        'original_length': original_length,
        'info_leaked': info_leaked,
        'min_required_length': info_leaked + 16
    }


# Example usage and testing
if __name__ == "__main__":
    print("=== Privacy Amplification Module Test ===\n")

    # Test 1: Standard privacy amplification (128-bit key)
    print("Test 1: Standard Privacy Amplification")
    key1 = "10110101" * 16  # 128-bit key
    ber1 = 0.05  # 5% error rate

    print(f"Original key length: {len(key1)} bits")
    print(f"BER: {ber1:.2%}")

    amplified1, stats1 = privacy_amplification(key1, ber1, security_parameter=128)

    if stats1['success']:
        print(f"\n[SUCCESS] Privacy amplification completed")
        print(f"Final key length: {stats1['final_length']} bits")
        print(f"Information leaked: {stats1['info_leaked']} bits")
        print(f"Security parameter: {stats1['security_parameter']} bits")
        print(f"Compression ratio: {stats1['compression_ratio']:.2%}")
        print(f"Bits removed: {stats1['bits_removed']} bits")
        print(f"Amplified key (first 32 bits): {amplified1[:32]}...\n")
    else:
        print(f"\n[FAILED] {stats1['error']}\n")

    # Test 2: Larger key (256-bit)
    print("Test 2: Large Key Privacy Amplification")
    key2 = "10110101" * 32  # 256-bit key
    ber2 = 0.03  # 3% error rate

    print(f"Original key length: {len(key2)} bits")
    print(f"BER: {ber2:.2%}")

    amplified2, stats2 = privacy_amplification(key2, ber2, security_parameter=128)

    if stats2['success']:
        print(f"\n[SUCCESS] Privacy amplification completed")
        print(f"Final key length: {stats2['final_length']} bits")
        print(f"Compression ratio: {stats2['compression_ratio']:.2%}")
        print(f"Amplified key (first 64 bits): {amplified2[:64]}...\n")
    else:
        print(f"\n[FAILED] {stats2['error']}\n")

    # Test 3: Short key with adaptive amplification
    print("Test 3: Adaptive Privacy Amplification (Short Key)")
    key3 = "10110101" * 4  # 32-bit key (too short for standard)
    ber3 = 0.05  # 5% error rate

    print(f"Original key length: {len(key3)} bits")
    print(f"BER: {ber3:.2%}")

    amplified3, stats3 = adaptive_privacy_amplification(key3, ber3)

    if stats3['success']:
        print(f"\n[SUCCESS] Adaptive amplification completed")
        print(f"Final key length: {stats3['final_length']} bits")
        print(f"Security parameter (adapted): {stats3['security_parameter']} bits")
        print(f"Compression ratio: {stats3['compression_ratio']:.2%}")
        print(f"Amplified key: {amplified3}\n")
    else:
        print(f"\n[FAILED] {stats3['error']}")
        print(f"Minimum required length: {stats3['min_required_length']} bits\n")

    # Test 4: Excellent quality (very low BER)
    print("Test 4: Excellent Quality (Low BER)")
    key4 = "10110101" * 16  # 128-bit key
    ber4 = 0.001  # 0.1% error rate (excellent)

    print(f"Original key length: {len(key4)} bits")
    print(f"BER: {ber4:.2%}")

    amplified4, stats4 = privacy_amplification(key4, ber4, security_parameter=128)

    if stats4['success']:
        print(f"\n[SUCCESS] Privacy amplification completed")
        print(f"Final key length: {stats4['final_length']} bits")
        print(f"Information leaked: {stats4['info_leaked']} bits (very low!)")
        print(f"Compression ratio: {stats4['compression_ratio']:.2%}")
        print(f"Note: Low BER means less compression needed!\n")
    else:
        print(f"\n[FAILED] {stats4['error']}\n")

    print("=== All Tests Completed ===")
