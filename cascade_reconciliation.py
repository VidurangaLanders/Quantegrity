"""
CASCADE Protocol for Quantum Key Reconciliation
Ref: Brassard & Salvail (1993)

Iteratively corrects errors through:
1. Parity checks on random blocks
2. Binary search for error locations
3. Multiple passes with increasing block sizes
"""

import random
import math
from typing import List, Tuple

def estimate_initial_block_size(error_rate: float, key_length: int) -> int:
    """
    Calculate optimal initial block size for CASCADE

    Formula: k0 = 0.73 / error_rate
    This balances efficiency with error correction capability
    """
    if error_rate <= 0:
        return key_length  # No errors expected
    return max(1, int(0.73 / error_rate))

def calculate_parity(bits: str) -> int:
    """Calculate parity (XOR of all bits) for a bit string"""
    return sum(int(b) for b in bits) % 2

def divide_into_blocks(bits: str, block_size: int) -> List[str]:
    """Divide bit string into blocks of specified size"""
    return [bits[i:i+block_size] for i in range(0, len(bits), block_size)]

def flip_bit(bits: str, position: int) -> str:
    """Flip bit at specified position"""
    bits_list = list(bits)
    bits_list[position] = '1' if bits_list[position] == '0' else '0'
    return ''.join(bits_list)

def binary_search_error(alice_block: str, bob_block: str) -> int:
    """
    Use binary search to find error position within a block

    Process:
    1. Divide block in half
    2. Compare parities
    3. Error is in half with different parity
    4. Recursively search that half

    Returns:
        Position of first error found (relative to block start)
    """
    if len(alice_block) == 1:
        return 0 if alice_block != bob_block else -1

    mid = len(alice_block) // 2
    alice_left, alice_right = alice_block[:mid], alice_block[mid:]
    bob_left, bob_right = bob_block[:mid], bob_block[mid:]

    if calculate_parity(alice_left) != calculate_parity(bob_left):
        # Error in left half
        return binary_search_error(alice_left, bob_left)
    else:
        # Error in right half
        result = binary_search_error(alice_right, bob_right)
        return mid + result if result != -1 else -1

def cascade_reconciliation(alice_key: str,
                          bob_key: str,
                          error_rate: float,
                          num_passes: int = 4) -> Tuple[str, str, dict]:
    """
    Perform CASCADE error reconciliation

    Args:
        alice_key: Alice's raw key
        bob_key: Bob's raw key (with errors)
        error_rate: Estimated bit error rate
        num_passes: Number of CASCADE passes (default 4)

    Returns:
        Tuple of (corrected_alice_key, corrected_bob_key, statistics)

    Algorithm:
    - Pass 1: Block size k0
    - Pass 2: Block size 2*k0
    - Pass 3: Block size 4*k0
    - Pass 4: Block size 8*k0

    Each pass:
    1. Divide keys into blocks
    2. Compare parity of each block pair
    3. If parity differs, use binary search to find error
    4. Correct error in Bob's key
    """
    n = len(alice_key)
    k0 = estimate_initial_block_size(error_rate, n)

    corrected_alice = alice_key
    corrected_bob = bob_key

    # Statistics tracking
    stats = {
        'initial_errors': sum(a != b for a, b in zip(alice_key, bob_key)),
        'passes': [],
        'total_corrections': 0
    }

    for pass_num in range(num_passes):
        block_size = k0 * (2 ** pass_num)

        if block_size > n:
            block_size = n

        pass_stats = {
            'pass_number': pass_num + 1,
            'block_size': block_size,
            'corrections': 0,
            'blocks_checked': 0
        }

        # Divide keys into blocks
        alice_blocks = divide_into_blocks(corrected_alice, block_size)
        bob_blocks = divide_into_blocks(corrected_bob, block_size)

        # Check each block
        for block_idx, (a_block, b_block) in enumerate(zip(alice_blocks, bob_blocks)):
            pass_stats['blocks_checked'] += 1

            if calculate_parity(a_block) != calculate_parity(b_block):
                # Parity mismatch - search for error
                error_pos_in_block = binary_search_error(a_block, b_block)

                if error_pos_in_block != -1:
                    # Calculate absolute position in key
                    absolute_pos = block_idx * block_size + error_pos_in_block

                    # Correct error in Bob's key
                    corrected_bob = flip_bit(corrected_bob, absolute_pos)
                    pass_stats['corrections'] += 1
                    stats['total_corrections'] += 1

        stats['passes'].append(pass_stats)

    # Final error count
    stats['final_errors'] = sum(a != b for a, b in zip(corrected_alice, corrected_bob))
    stats['success'] = stats['final_errors'] == 0

    return corrected_alice, corrected_bob, stats

def cascade_with_retry(alice_key: str,
                       bob_key: str,
                       error_rate: float,
                       max_retries: int = 3) -> Tuple[str, str, dict]:
    """
    Perform CASCADE with automatic retry if first attempt fails

    Args:
        alice_key: Alice's raw key
        bob_key: Bob's raw key (with errors)
        error_rate: Estimated bit error rate
        max_retries: Maximum number of retry attempts

    Returns:
        Tuple of (corrected_alice_key, corrected_bob_key, statistics)
    """
    for attempt in range(max_retries):
        corrected_alice, corrected_bob, stats = cascade_reconciliation(
            alice_key,
            bob_key,
            error_rate,
            num_passes=4 + attempt  # Increase passes with each retry
        )

        if stats['success']:
            stats['attempts'] = attempt + 1
            return corrected_alice, corrected_bob, stats

    # If all retries failed, return last attempt
    stats['attempts'] = max_retries
    stats['all_retries_failed'] = True
    return corrected_alice, corrected_bob, stats


# Example usage and testing
if __name__ == "__main__":
    print("=== CASCADE Reconciliation Module Test ===\n")

    # Test 1: Single error
    print("Test 1: Single Error Correction")
    alice1 = "1011010110110101"
    bob1 = "1011010010110101"  # Error at position 7
    initial_errors1 = sum(a != b for a, b in zip(alice1, bob1))
    error_rate1 = initial_errors1 / len(alice1)

    print(f"Alice:          {alice1}")
    print(f"Bob (before):   {bob1}")
    print(f"Initial errors: {initial_errors1}")
    print(f"Error rate:     {error_rate1:.2%}")

    corrected_a1, corrected_b1, stats1 = cascade_reconciliation(alice1, bob1, error_rate1)

    print(f"\nAfter CASCADE:")
    print(f"Alice:          {corrected_a1}")
    print(f"Bob (after):    {corrected_b1}")
    print(f"Final errors:   {stats1['final_errors']}")
    print(f"Total corrections: {stats1['total_corrections']}")
    print(f"Match:          {corrected_a1 == corrected_b1}")
    print(f"Success:        {stats1['success']}\n")

    # Test 2: Multiple errors
    print("Test 2: Multiple Errors Correction")
    alice2 = "10110101101101011011010110110101"  # 32 bits
    bob2 = "10110101001101010011010110010101"    # Errors at positions 8, 14, 22
    initial_errors2 = sum(a != b for a, b in zip(alice2, bob2))
    error_rate2 = initial_errors2 / len(alice2)

    print(f"Alice:          {alice2}")
    print(f"Bob (before):   {bob2}")
    print(f"Initial errors: {initial_errors2}")
    print(f"Error rate:     {error_rate2:.2%}")

    corrected_a2, corrected_b2, stats2 = cascade_reconciliation(alice2, bob2, error_rate2)

    print(f"\nAfter CASCADE:")
    print(f"Alice:          {corrected_a2}")
    print(f"Bob (after):    {corrected_b2}")
    print(f"Final errors:   {stats2['final_errors']}")
    print(f"Total corrections: {stats2['total_corrections']}")
    print(f"Match:          {corrected_a2 == corrected_b2}")
    print(f"Success:        {stats2['success']}\n")

    # Test 3: CASCADE with retry
    print("Test 3: CASCADE with Automatic Retry")
    alice3 = "1011010110110101" * 4  # 64 bits
    bob3 = "1011000110110001" * 4    # Multiple errors
    initial_errors3 = sum(a != b for a, b in zip(alice3, bob3))
    error_rate3 = initial_errors3 / len(alice3)

    print(f"Key length:     {len(alice3)} bits")
    print(f"Initial errors: {initial_errors3}")
    print(f"Error rate:     {error_rate3:.2%}")

    corrected_a3, corrected_b3, stats3 = cascade_with_retry(alice3, bob3, error_rate3)

    print(f"\nAfter CASCADE (with retry):")
    print(f"Final errors:   {stats3['final_errors']}")
    print(f"Total corrections: {stats3['total_corrections']}")
    print(f"Attempts:       {stats3.get('attempts', 1)}")
    print(f"Match:          {corrected_a3 == corrected_b3}")
    print(f"Success:        {stats3['success']}\n")

    # Display pass-by-pass statistics
    print("Pass-by-pass breakdown:")
    for pass_stat in stats3['passes']:
        print(f"  Pass {pass_stat['pass_number']}: "
              f"block_size={pass_stat['block_size']}, "
              f"corrections={pass_stat['corrections']}, "
              f"blocks_checked={pass_stat['blocks_checked']}")

    print("\n=== All Tests Completed ===")
