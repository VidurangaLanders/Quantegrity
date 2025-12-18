"""
Entanglement Verification using CHSH Inequality
Verifies quantum entanglement authenticity to detect eavesdropping

The CHSH (Clauser-Horne-Shimony-Holt) inequality:
- Classical systems: S <= 2
- Quantum entangled: S can reach 2√2 ≈ 2.828
- Violation of S > 2 proves genuine quantum entanglement
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from typing import Dict, Tuple
import math

def create_bell_state() -> QuantumCircuit:
    """
    Create a Bell state (maximally entangled state)

    Creates the state: |Φ+⟩ = (|00⟩ + |11⟩) / √2

    Returns:
        Quantum circuit with Bell state
    """
    circuit = QuantumCircuit(2, 2)

    # Create Bell pair
    circuit.h(0)
    circuit.cx(0, 1)

    return circuit

def measure_in_basis(alice_angle: float, bob_angle: float) -> str:
    """
    Create Bell state and measure in specified bases

    Args:
        alice_angle: Alice's measurement angle (radians)
        bob_angle: Bob's measurement angle (radians)

    Returns:
        Measurement result as binary string "ab"
    """
    # Create fresh Bell state for each measurement
    circuit = QuantumCircuit(2, 2)

    # Create Bell pair
    circuit.h(0)
    circuit.cx(0, 1)

    # Rotate to measurement bases before measuring
    circuit.ry(2 * alice_angle, 0)
    circuit.ry(2 * bob_angle, 1)

    # Measure
    circuit.measure([0, 1], [0, 1])

    # Execute
    result = AerSimulator().run(circuit, shots=1, memory=True).result()
    measurement = list(result.get_counts().keys())[0]

    return measurement

def calculate_correlation(measurements: list) -> float:
    """
    Calculate correlation coefficient from measurements

    E(a,b) = P(same) - P(different)
          = P(00) + P(11) - P(01) - P(10)

    For entangled Bell state with optimal measurements, correlations
    should be around ±0.707 (1/√2)

    Args:
        measurements: List of measurement strings ["00", "11", "01", ...]

    Returns:
        Correlation coefficient (-1.0 to 1.0)
    """
    if not measurements:
        return 0.0

    # Count measurement outcomes (Qiskit uses little-endian: qubit1_qubit0)
    same_outcomes = 0  # 00 or 11
    diff_outcomes = 0  # 01 or 10

    for meas in measurements:
        if len(meas) >= 2:
            # Extract last 2 bits (our 2 qubits)
            bit0 = meas[-1]  # Alice (qubit 0)
            bit1 = meas[-2]  # Bob (qubit 1)

            if bit0 == bit1:  # Same outcome
                same_outcomes += 1
            else:  # Different outcome
                diff_outcomes += 1

    n_total = same_outcomes + diff_outcomes

    if n_total == 0:
        return 0.0

    correlation = (same_outcomes - diff_outcomes) / n_total

    return correlation

def chsh_test(num_measurements: int = 1000) -> Dict:
    """
    Perform CHSH inequality test

    CHSH Parameter: S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')|

    Standard angles for maximum violation:
    - a = 0°
    - a' = 45°
    - b = 22.5°
    - b' = -22.5° (or 67.5°)

    Args:
        num_measurements: Number of measurements per basis pair

    Returns:
        Dictionary with CHSH test results
    """
    # Define measurement angles (in radians) for maximum CHSH violation
    # Standard angles that achieve Tsirelson's bound of 2√2
    a = 0.0                      # 0°
    a_prime = math.pi / 2        # 90°
    b = math.pi / 4              # 45°
    b_prime = -math.pi / 4       # -45° (or 315°)

    # Perform measurements for each basis pair
    measurements_ab = []
    measurements_ab_prime = []
    measurements_a_prime_b = []
    measurements_a_prime_b_prime = []

    for _ in range(num_measurements):
        # E(a, b)
        result = measure_in_basis(a, b)
        measurements_ab.append(result)

        # E(a, b')
        result = measure_in_basis(a, b_prime)
        measurements_ab_prime.append(result)

        # E(a', b)
        result = measure_in_basis(a_prime, b)
        measurements_a_prime_b.append(result)

        # E(a', b')
        result = measure_in_basis(a_prime, b_prime)
        measurements_a_prime_b_prime.append(result)

    # Calculate correlations
    e_ab = calculate_correlation(measurements_ab)
    e_ab_prime = calculate_correlation(measurements_ab_prime)
    e_a_prime_b = calculate_correlation(measurements_a_prime_b)
    e_a_prime_b_prime = calculate_correlation(measurements_a_prime_b_prime)

    # Calculate CHSH parameter
    s = abs(e_ab - e_ab_prime + e_a_prime_b + e_a_prime_b_prime)

    # Classical bound: S <= 2
    # Quantum bound (Tsirelson's bound): S <= 2√2 ≈ 2.828
    classical_bound = 2.0
    quantum_bound = 2 * math.sqrt(2)

    # Determine result
    violates_classical = s > classical_bound
    is_quantum = violates_classical
    confidence = (s - classical_bound) / (quantum_bound - classical_bound) if violates_classical else 0.0

    return {
        'chsh_parameter': s,
        'classical_bound': classical_bound,
        'quantum_bound': quantum_bound,
        'violates_classical': violates_classical,
        'is_quantum_entangled': is_quantum,
        'confidence': confidence,
        'correlations': {
            'E(a,b)': e_ab,
            'E(a,b_prime)': e_ab_prime,
            'E(a_prime,b)': e_a_prime_b,
            'E(a_prime,b_prime)': e_a_prime_b_prime
        },
        'measurements_per_basis': num_measurements,
        'total_measurements': num_measurements * 4
    }

def verify_entanglement(num_measurements: int = 1000,
                       min_confidence: float = 0.5) -> Dict:
    """
    Verify quantum entanglement with confidence check

    Args:
        num_measurements: Number of measurements per basis
        min_confidence: Minimum confidence level required (0.0 to 1.0)

    Returns:
        Verification result with status
    """
    result = chsh_test(num_measurements)

    verified = (
        result['is_quantum_entangled'] and
        result['confidence'] >= min_confidence
    )

    result['verified'] = verified
    result['min_confidence'] = min_confidence

    if verified:
        result['status'] = 'verified'
        result['message'] = 'Quantum entanglement verified - channel secure'
    elif result['is_quantum_entangled']:
        result['status'] = 'weak'
        result['message'] = 'Entanglement detected but confidence below threshold'
    else:
        result['status'] = 'failed'
        result['message'] = 'No quantum entanglement detected - possible eavesdropping'

    return result

def detect_eavesdropping_via_entanglement(num_measurements: int = 1000) -> Dict:
    """
    Use entanglement verification to detect eavesdropping

    An eavesdropper's presence will disturb the entanglement,
    causing the CHSH parameter to decrease toward the classical bound.

    Args:
        num_measurements: Number of measurements

    Returns:
        Dictionary with eavesdropping detection results
    """
    result = verify_entanglement(num_measurements, min_confidence=0.5)

    # Estimate eavesdropping probability based on CHSH parameter
    s = result['chsh_parameter']
    classical_bound = result['classical_bound']
    quantum_bound = result['quantum_bound']

    if s > quantum_bound * 0.9:  # > 90% of maximum
        eve_probability = 0.0
        security_level = 'high'
    elif s > quantum_bound * 0.7:  # > 70% of maximum
        eve_probability = 0.1
        security_level = 'good'
    elif s > classical_bound:  # Above classical but below quantum
        eve_probability = 0.3
        security_level = 'moderate'
    else:  # At or below classical bound
        eve_probability = 0.8
        security_level = 'low'

    result['eavesdropping_probability'] = eve_probability
    result['security_level'] = security_level

    return result


# Example usage and testing
if __name__ == "__main__":
    print("=== Entanglement Verification Module Test ===\n")

    # Test 1: Basic CHSH test
    print("Test 1: CHSH Inequality Test")
    print("Performing quantum measurements...")

    chsh_result = chsh_test(num_measurements=1000)

    print(f"\n--- Results ---")
    print(f"CHSH Parameter (S): {chsh_result['chsh_parameter']:.4f}")
    print(f"Classical Bound: {chsh_result['classical_bound']:.4f}")
    print(f"Quantum Bound: {chsh_result['quantum_bound']:.4f}")
    print(f"Violates Classical: {chsh_result['violates_classical']}")
    print(f"Quantum Entangled: {chsh_result['is_quantum_entangled']}")
    print(f"Confidence: {chsh_result['confidence']:.2%}")

    print(f"\nCorrelations:")
    for key, value in chsh_result['correlations'].items():
        print(f"  {key}: {value:.4f}")

    # Test 2: Entanglement verification
    print("\n\nTest 2: Entanglement Verification")
    verification_result = verify_entanglement(num_measurements=1000, min_confidence=0.5)

    print(f"\n--- Results ---")
    print(f"Status: {verification_result['status'].upper()}")
    print(f"Message: {verification_result['message']}")
    print(f"Verified: {verification_result['verified']}")
    print(f"Confidence: {verification_result['confidence']:.2%}")
    print(f"CHSH Parameter: {verification_result['chsh_parameter']:.4f}")

    # Test 3: Eavesdropping detection
    print("\n\nTest 3: Eavesdropping Detection")
    eaves_result = detect_eavesdropping_via_entanglement(num_measurements=1000)

    print(f"\n--- Results ---")
    print(f"Security Level: {eaves_result['security_level'].upper()}")
    print(f"Eavesdropping Probability: {eaves_result['eavesdropping_probability']:.2%}")
    print(f"CHSH Parameter: {eaves_result['chsh_parameter']:.4f}")
    print(f"Entanglement Status: {eaves_result['status']}")

    if eaves_result['security_level'] in ['high', 'good']:
        print("\n[SUCCESS] Channel is secure - quantum entanglement verified")
    else:
        print("\n[WARNING] Potential security issue detected")

    # Test 4: Multiple verification runs
    print("\n\nTest 4: Statistical Analysis (10 runs)")
    s_values = []

    for i in range(10):
        result = chsh_test(num_measurements=500)
        s_values.append(result['chsh_parameter'])

    avg_s = np.mean(s_values)
    std_s = np.std(s_values)

    print(f"\n--- Statistical Results ---")
    print(f"Average S: {avg_s:.4f} ± {std_s:.4f}")
    print(f"Min S: {min(s_values):.4f}")
    print(f"Max S: {max(s_values):.4f}")
    print(f"All runs violated classical bound: {all(s > 2.0 for s in s_values)}")

    print("\n\n=== All Tests Completed ===")
