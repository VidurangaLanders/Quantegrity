"""
Integrated Error Correction for SEDJO Protocol
Combines error detection, CASCADE, and privacy amplification
"""

from quantum_error_detection import detect_quantum_errors, generate_error_report
from cascade_reconciliation import cascade_with_retry
from privacy_amplification import privacy_amplification, adaptive_privacy_amplification
from typing import Dict
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QECProtocol:
    """
    Quantum Error Correction Protocol Manager

    Integrates:
    1. Error detection
    2. CASCADE reconciliation
    3. Privacy amplification
    4. Retry logic
    """

    def __init__(self,
                 max_retries: int = 3,
                 error_threshold: float = 0.11,
                 security_parameter: int = 128,
                 adaptive_amplification: bool = True):
        """
        Initialize QEC Protocol

        Args:
            max_retries: Maximum retry attempts for CASCADE
            error_threshold: Maximum acceptable BER (default 11%)
            security_parameter: Security level for amplification (default 128 bits)
            adaptive_amplification: Use adaptive amplification for short keys
        """
        self.max_retries = max_retries
        self.error_threshold = error_threshold
        self.security_parameter = security_parameter
        self.adaptive_amplification = adaptive_amplification

    def correct_errors(self,
                      alice_key: str,
                      bob_key: str) -> Dict:
        """
        Apply complete error correction pipeline

        Pipeline:
        1. Detect errors
        2. If BER > threshold, abort
        3. Apply CASCADE reconciliation
        4. Apply privacy amplification
        5. Return secure key

        Args:
            alice_key: Alice's raw key from SEDJO
            bob_key: Bob's raw key from SEDJO

        Returns:
            Dict with status and corrected key
        """
        start_time = time.time()

        logger.info(f"Starting error correction pipeline for {len(alice_key)}-bit key")

        # Step 1: Error detection
        logger.info("Step 1: Error detection")
        error_analysis = detect_quantum_errors(alice_key, bob_key)

        logger.info(f"  BER: {error_analysis.ber:.4f} ({error_analysis.error_type})")
        logger.info(f"  Errors: {len(error_analysis.error_locations)}")
        logger.info(f"  Recommended action: {error_analysis.recommended_action}")

        # Generate detailed error report
        error_report = generate_error_report(error_analysis, len(alice_key))

        # Step 2: Check if errors are correctable
        if error_analysis.ber >= self.error_threshold:
            logger.error(f"BER {error_analysis.ber:.4f} exceeds threshold {self.error_threshold}")
            return {
                'success': False,
                'error': 'ber_too_high',
                'ber': error_analysis.ber,
                'threshold': self.error_threshold,
                'error_report': error_report,
                'elapsed': time.time() - start_time
            }

        # Step 3: Apply CASCADE if needed
        if error_analysis.correction_needed:
            logger.info("Step 2: Applying CASCADE reconciliation")

            corrected_alice, corrected_bob, cascade_stats = cascade_with_retry(
                alice_key,
                bob_key,
                error_analysis.ber,
                self.max_retries
            )

            # Verify correction
            if not cascade_stats['success']:
                logger.error("CASCADE failed to correct all errors")
                return {
                    'success': False,
                    'error': 'cascade_failed',
                    'cascade_stats': cascade_stats,
                    'error_report': error_report,
                    'elapsed': time.time() - start_time
                }

            logger.info(f"  CASCADE successful: {cascade_stats['total_corrections']} corrections")
            logger.info(f"  Attempts: {cascade_stats.get('attempts', 1)}")
            final_key = corrected_alice
        else:
            logger.info("Step 2: No correction needed (excellent quality)")
            cascade_stats = None
            final_key = alice_key

        # Step 4: Privacy amplification
        if error_analysis.ber > 0:
            logger.info("Step 3: Applying privacy amplification")

            if self.adaptive_amplification:
                secure_key, amplification_stats = adaptive_privacy_amplification(
                    final_key,
                    error_analysis.ber
                )
            else:
                secure_key, amplification_stats = privacy_amplification(
                    final_key,
                    error_analysis.ber,
                    self.security_parameter
                )

            if not amplification_stats['success']:
                logger.warning(f"Privacy amplification warning: {amplification_stats.get('error', 'unknown')}")
                logger.warning("Returning reconciled key without amplification")

                return {
                    'success': True,
                    'secure_key': final_key,
                    'warning': 'amplification_skipped',
                    'amplification_error': amplification_stats.get('error'),
                    'original_ber': error_analysis.ber,
                    'original_length': len(alice_key),
                    'final_length': len(final_key),
                    'correction_applied': error_analysis.correction_needed,
                    'cascade_stats': cascade_stats,
                    'error_report': error_report,
                    'elapsed': time.time() - start_time
                }

            logger.info(f"  Amplification successful: {len(final_key)} → {amplification_stats['final_length']} bits")
            logger.info(f"  Compression ratio: {amplification_stats['compression_ratio']:.2%}")
        else:
            logger.info("Step 3: No amplification needed (zero BER)")
            secure_key = final_key
            amplification_stats = {
                'success': True,
                'original_length': len(final_key),
                'final_length': len(final_key),
                'info_leaked': 0,
                'security_parameter': 0,
                'compression_ratio': 1.0,
                'ber': 0.0
            }

        elapsed = time.time() - start_time
        logger.info(f"Error correction pipeline completed in {elapsed:.3f}s")

        return {
            'success': True,
            'secure_key': secure_key,
            'original_ber': error_analysis.ber,
            'original_length': len(alice_key),
            'final_length': len(secure_key),
            'correction_applied': error_analysis.correction_needed,
            'cascade_stats': cascade_stats,
            'amplification_stats': amplification_stats,
            'error_report': error_report,
            'elapsed': elapsed
        }

    def verify_key_quality(self, key: str) -> Dict:
        """
        Verify the quality of a quantum key

        Args:
            key: Quantum key to verify

        Returns:
            Dictionary with quality metrics
        """
        # Calculate entropy (should be close to 1.0 for random keys)
        ones = key.count('1')
        zeros = key.count('0')
        total = len(key)

        p_one = ones / total if total > 0 else 0
        p_zero = zeros / total if total > 0 else 0

        if p_one > 0 and p_zero > 0:
            import math
            entropy = -(p_one * math.log2(p_one) + p_zero * math.log2(p_zero))
        else:
            entropy = 0.0

        return {
            'length': total,
            'ones': ones,
            'zeros': zeros,
            'balance': min(p_one, p_zero) / max(p_one, p_zero) if max(p_one, p_zero) > 0 else 0,
            'entropy': entropy,
            'quality': 'excellent' if entropy > 0.99 else 'good' if entropy > 0.95 else 'fair' if entropy > 0.90 else 'poor'
        }


# Example usage and testing
if __name__ == "__main__":
    print("=== Integrated Quantum Error Correction Test ===\n")

    # Initialize QEC protocol
    qec = QECProtocol(
        max_retries=3,
        error_threshold=0.11,
        security_parameter=64,  # Use 64-bit for testing
        adaptive_amplification=True
    )

    # Test 1: Good quality with minimal errors
    print("Test 1: Good Quality Key (Minimal Errors)")
    alice1 = "10110101" * 16  # 128 bits
    bob1 = "10110101" * 15 + "10110100"  # 1 error in last byte

    result1 = qec.correct_errors(alice1, bob1)

    print(f"\n--- Results ---")
    print(f"Success: {result1['success']}")
    if result1['success']:
        print(f"Original length: {result1['original_length']} bits")
        print(f"Final length: {result1['final_length']} bits")
        print(f"BER: {result1['original_ber']:.4f}")
        print(f"Correction applied: {result1['correction_applied']}")
        print(f"Elapsed time: {result1['elapsed']:.3f}s")

        # Verify key quality
        quality = qec.verify_key_quality(result1['secure_key'])
        print(f"\nKey quality: {quality['quality']}")
        print(f"Entropy: {quality['entropy']:.4f}")
    else:
        print(f"Error: {result1['error']}")

    # Test 2: Multiple errors requiring CASCADE
    print("\n\nTest 2: Moderate Quality (Multiple Errors)")
    alice2 = "10110101" * 32  # 256 bits
    bob2_list = list(alice2)
    # Introduce 5 errors (about 2% BER)
    for pos in [10, 45, 89, 134, 200]:
        bob2_list[pos] = '1' if bob2_list[pos] == '0' else '0'
    bob2 = ''.join(bob2_list)

    result2 = qec.correct_errors(alice2, bob2)

    print(f"\n--- Results ---")
    print(f"Success: {result2['success']}")
    if result2['success']:
        print(f"Original length: {result2['original_length']} bits")
        print(f"Final length: {result2['final_length']} bits")
        print(f"BER: {result2['original_ber']:.4f}")
        if result2['cascade_stats']:
            print(f"CASCADE corrections: {result2['cascade_stats']['total_corrections']}")
        if result2['amplification_stats']:
            print(f"Compression ratio: {result2['amplification_stats']['compression_ratio']:.2%}")
        print(f"Elapsed time: {result2['elapsed']:.3f}s")
    else:
        print(f"Error: {result2['error']}")

    # Test 3: Too many errors (should fail)
    print("\n\nTest 3: Poor Quality (Exceeds Threshold)")
    alice3 = "10110101" * 16  # 128 bits
    bob3_list = list(alice3)
    # Introduce 20 errors (15.6% BER - exceeds 11% threshold)
    import random
    random.seed(42)
    error_positions = random.sample(range(len(alice3)), 20)
    for pos in error_positions:
        bob3_list[pos] = '1' if bob3_list[pos] == '0' else '0'
    bob3 = ''.join(bob3_list)

    result3 = qec.correct_errors(alice3, bob3)

    print(f"\n--- Results ---")
    print(f"Success: {result3['success']}")
    if not result3['success']:
        print(f"Error: {result3['error']}")
        print(f"BER: {result3['ber']:.4f}")
        print(f"Threshold: {result3['threshold']:.4f}")
        print(f"Security status: {result3['error_report']['security_status']}")

    print("\n\n=== All Tests Completed ===")
