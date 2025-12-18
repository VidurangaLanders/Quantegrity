"""
Quantum Error Detection for SEDJO Protocol
Implements BER calculation, error pattern analysis, and error classification
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ErrorAnalysis:
    ber: float
    error_locations: List[int]
    error_type: str
    correction_needed: bool
    recommended_action: str

def calculate_ber(alice_bits: str, bob_bits: str) -> float:
    """
    Calculate Bit Error Rate between two bit strings

    BER = (number of differing bits) / (total bits)

    Args:
        alice_bits: Alice's measurement result
        bob_bits: Bob's measurement result

    Returns:
        Bit error rate (0.0 to 1.0)

    Example:
        >>> calculate_ber("1010", "1011")
        0.25  # 1 bit differs out of 4
    """
    if len(alice_bits) != len(bob_bits):
        raise ValueError("Bit strings must have equal length")

    errors = sum(a != b for a, b in zip(alice_bits, bob_bits))
    return errors / len(alice_bits)

def identify_error_positions(alice_bits: str, bob_bits: str) -> List[int]:
    """
    Identify positions where bits differ

    Returns:
        List of indices where errors occurred
    """
    return [i for i, (a, b) in enumerate(zip(alice_bits, bob_bits)) if a != b]

def classify_error_type(ber: float) -> str:
    """
    Classify error severity based on BER

    Quantum Error Correction Thresholds:
    - BER < 0.01: Excellent (minimal errors)
    - BER < 0.05: Good (acceptable errors)
    - BER < 0.11: Fair (near threshold, correction needed)
    - BER >= 0.11: Poor (exceeds correction capability)

    QKD Security Threshold: 11% (0.11)
    Above this, Eve's information becomes too high
    """
    if ber < 0.01:
        return "excellent"
    elif ber < 0.05:
        return "good"
    elif ber < 0.11:
        return "fair"
    else:
        return "poor"

def get_correction_strategy(ber: float) -> str:
    """
    Recommend error correction strategy based on BER
    """
    if ber < 0.01:
        return "no_correction_needed"
    elif ber < 0.05:
        return "privacy_amplification_only"
    elif ber < 0.11:
        return "cascade_and_amplification"
    else:
        return "abort_and_retry"

def detect_quantum_errors(alice_measurement: str,
                         bob_measurement: str,
                         expected_correlation: float = 0.95) -> ErrorAnalysis:
    """
    Comprehensive error detection and analysis

    Args:
        alice_measurement: Alice's quantum measurement result
        bob_measurement: Bob's quantum measurement result
        expected_correlation: Minimum acceptable correlation (default 95%)

    Returns:
        ErrorAnalysis object with detailed error information
    """
    ber = calculate_ber(alice_measurement, bob_measurement)
    error_locations = identify_error_positions(alice_measurement, bob_measurement)
    error_type = classify_error_type(ber)
    correction_needed = ber > (1 - expected_correlation)
    recommended_action = get_correction_strategy(ber)

    return ErrorAnalysis(
        ber=ber,
        error_locations=error_locations,
        error_type=error_type,
        correction_needed=correction_needed,
        recommended_action=recommended_action
    )

def analyze_error_patterns(error_locations: List[int], key_length: int) -> Dict:
    """
    Analyze error distribution patterns

    Args:
        error_locations: List of positions where errors occurred
        key_length: Total length of the key

    Returns:
        Dictionary with pattern analysis
    """
    if not error_locations:
        return {
            'pattern': 'no_errors',
            'clustering': 0.0,
            'distribution': 'uniform'
        }

    # Calculate clustering coefficient
    if len(error_locations) > 1:
        gaps = [error_locations[i+1] - error_locations[i]
                for i in range(len(error_locations)-1)]
        avg_gap = np.mean(gaps)
        std_gap = np.std(gaps)
        clustering = std_gap / avg_gap if avg_gap > 0 else 0
    else:
        clustering = 0.0

    # Determine distribution pattern
    if clustering > 1.0:
        distribution = 'clustered'
    elif clustering < 0.3:
        distribution = 'uniform'
    else:
        distribution = 'random'

    return {
        'pattern': 'errors_detected',
        'clustering': clustering,
        'distribution': distribution,
        'error_count': len(error_locations),
        'error_rate': len(error_locations) / key_length
    }

def estimate_eavesdropping_probability(ber: float) -> float:
    """
    Estimate probability of eavesdropping based on BER

    This uses a simplified model:
    - BER < 0.01: Very low probability (<1%)
    - BER < 0.05: Low probability (1-10%)
    - BER < 0.11: Moderate probability (10-50%)
    - BER >= 0.11: High probability (>50%)

    Args:
        ber: Bit error rate

    Returns:
        Estimated eavesdropping probability (0.0 to 1.0)
    """
    if ber < 0.01:
        return 0.01  # 1%
    elif ber < 0.05:
        # Linear interpolation: 1% to 10%
        return 0.01 + (ber - 0.01) / 0.04 * 0.09
    elif ber < 0.11:
        # Linear interpolation: 10% to 50%
        return 0.10 + (ber - 0.05) / 0.06 * 0.40
    else:
        # Linear interpolation: 50% to 90% (capped at 90%)
        return min(0.50 + (ber - 0.11) * 2.0, 0.90)

def generate_error_report(error_analysis: ErrorAnalysis, key_length: int) -> Dict:
    """
    Generate comprehensive error report

    Args:
        error_analysis: ErrorAnalysis object
        key_length: Length of the quantum key

    Returns:
        Detailed error report dictionary
    """
    pattern_analysis = analyze_error_patterns(error_analysis.error_locations, key_length)
    eavesdrop_prob = estimate_eavesdropping_probability(error_analysis.ber)

    return {
        'ber': error_analysis.ber,
        'error_count': len(error_analysis.error_locations),
        'key_length': key_length,
        'error_type': error_analysis.error_type,
        'correction_needed': error_analysis.correction_needed,
        'recommended_action': error_analysis.recommended_action,
        'error_locations': error_analysis.error_locations,
        'pattern_analysis': pattern_analysis,
        'eavesdropping_probability': eavesdrop_prob,
        'security_status': 'secure' if error_analysis.ber < 0.11 else 'insecure'
    }


# Example usage and testing
if __name__ == "__main__":
    print("=== Quantum Error Detection Module Test ===\n")

    # Test 1: Excellent quality (no errors)
    print("Test 1: Excellent Quality (No Errors)")
    alice1 = "1011010110110101"
    bob1 = "1011010110110101"
    analysis1 = detect_quantum_errors(alice1, bob1)
    print(f"BER: {analysis1.ber:.4f}")
    print(f"Error type: {analysis1.error_type}")
    print(f"Correction needed: {analysis1.correction_needed}")
    print(f"Recommended action: {analysis1.recommended_action}")
    report1 = generate_error_report(analysis1, len(alice1))
    print(f"Security status: {report1['security_status']}")
    print(f"Eavesdropping probability: {report1['eavesdropping_probability']:.2%}\n")

    # Test 2: Good quality (1 error out of 16)
    print("Test 2: Good Quality (1 error)")
    alice2 = "1011010110110101"
    bob2 = "1011010010110101"  # Error at position 7
    analysis2 = detect_quantum_errors(alice2, bob2)
    print(f"BER: {analysis2.ber:.4f}")
    print(f"Error positions: {analysis2.error_locations}")
    print(f"Error type: {analysis2.error_type}")
    print(f"Correction needed: {analysis2.correction_needed}")
    print(f"Recommended action: {analysis2.recommended_action}")
    report2 = generate_error_report(analysis2, len(alice2))
    print(f"Security status: {report2['security_status']}")
    print(f"Eavesdropping probability: {report2['eavesdropping_probability']:.2%}\n")

    # Test 3: Fair quality (2 errors out of 16)
    print("Test 3: Fair Quality (2 errors)")
    alice3 = "1011010110110101"
    bob3 = "1011010010110001"  # Errors at positions 7 and 14
    analysis3 = detect_quantum_errors(alice3, bob3)
    print(f"BER: {analysis3.ber:.4f}")
    print(f"Error positions: {analysis3.error_locations}")
    print(f"Error type: {analysis3.error_type}")
    print(f"Correction needed: {analysis3.correction_needed}")
    print(f"Recommended action: {analysis3.recommended_action}")
    report3 = generate_error_report(analysis3, len(alice3))
    print(f"Pattern: {report3['pattern_analysis']['distribution']}")
    print(f"Security status: {report3['security_status']}")
    print(f"Eavesdropping probability: {report3['eavesdropping_probability']:.2%}\n")

    # Test 4: Poor quality (3 errors out of 16 = 18.75%)
    print("Test 4: Poor Quality (3 errors - exceeds threshold)")
    alice4 = "1011010110110101"
    bob4 = "1011000010110001"  # Errors at positions 5, 7, 14
    analysis4 = detect_quantum_errors(alice4, bob4)
    print(f"BER: {analysis4.ber:.4f}")
    print(f"Error positions: {analysis4.error_locations}")
    print(f"Error type: {analysis4.error_type}")
    print(f"Correction needed: {analysis4.correction_needed}")
    print(f"Recommended action: {analysis4.recommended_action}")
    report4 = generate_error_report(analysis4, len(alice4))
    print(f"Security status: {report4['security_status']}")
    print(f"Eavesdropping probability: {report4['eavesdropping_probability']:.2%}\n")

    print("=== All Tests Completed ===")
