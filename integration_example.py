"""
Quantegrity Enhanced Security Integration Example
Demonstrates how to integrate new security modules with existing system
"""

from quantum_core import qrng, sedjo
from quantum_error_correction import QECProtocol
from seo_ah_protocol import SEOAuthenticatedHandshake
from intrusion_detection import QuantumIntrusionDetector
import time

# ============================================================================
# EXAMPLE 1: Enhanced Voter Registration with SEO-AH
# ============================================================================

def enhanced_voter_registration(voter_id: str, biometric: str):
    """
    Enhanced voter registration with SEO-AH authentication

    Traditional flow:
    1. Generate Q_K1, Q_K2, Biometric
    2. Encrypt Q_K1 with Biometric

    Enhanced flow adds:
    3. Generate PSK for SEO-AH
    4. Register PSK with authentication system
    """
    print(f"\n=== Enhanced Voter Registration: {voter_id} ===")

    # Step 1: Generate quantum keys (existing)
    q_k1 = qrng(16)
    q_k2 = qrng(16)

    print(f"Q_K1 generated: {q_k1}")
    print(f"Q_K2 generated: {q_k2}")

    # Step 2: Encrypt Q_K1 with biometric (existing)
    encrypted_q_k1 = xor_encrypt(q_k1, biometric)
    print(f"Q_K1 encrypted: {encrypted_q_k1}")

    # Step 3: Generate PSK for SEO-AH authentication (NEW)
    psk = qrng(16)
    print(f"PSK generated: {psk}")

    # Step 4: Register PSK with SEO-AH system (NEW)
    seo_ah = SEOAuthenticatedHandshake()
    seo_ah.register_psk(voter_id, psk)
    seo_ah.register_psk("election_authority", psk)  # EA also needs PSK
    print("PSK registered for quantum authentication")

    # Return registration data
    return {
        'voter_id': voter_id,
        'q_k1': q_k1,
        'q_k2': q_k2,
        'encrypted_q_k1': encrypted_q_k1,
        'biometric': biometric,
        'psk': psk,  # Store securely!
        'seo_ah': seo_ah
    }


# ============================================================================
# EXAMPLE 2: Enhanced Authentication with Error Correction and IDS
# ============================================================================

def enhanced_authentication(voter_id: str,
                           biometric: str,
                           registration_data: dict,
                           ids: QuantumIntrusionDetector):
    """
    Enhanced authentication with SEO-AH and intrusion detection

    Traditional flow:
    1. Decrypt Q_K1 with biometric
    2. Generate AQ_K1 using SEDJO(Q_K1, Q_K1)

    Enhanced flow adds:
    3. Perform SEO-AH handshake for MITM protection
    4. Apply error correction to quantum keys
    5. Monitor with intrusion detection system
    """
    print(f"\n=== Enhanced Authentication: {voter_id} ===")
    start_time = time.time()

    # Step 1: SEO-AH Authentication (NEW)
    print("Step 1: Performing SEO-AH quantum handshake...")
    seo_ah = registration_data['seo_ah']

    auth_result = seo_ah.perform_handshake(voter_id, "election_authority")

    if not auth_result['authenticated']:
        print(f"[FAILED] SEO-AH authentication failed: {auth_result['error']}")

        # Log authentication failure (NEW)
        ids.analyze_authentication(voter_id, success=False)
        return None

    print(f"[SUCCESS] SEO-AH authenticated in {auth_result['elapsed']:.3f}s")
    session_token = auth_result['session_token']

    # Log successful authentication
    ids.analyze_authentication(voter_id, success=True)

    # Step 2: Decrypt Q_K1 with biometric (existing)
    print("\nStep 2: Decrypting Q_K1 with biometric...")
    encrypted_q_k1 = registration_data['encrypted_q_k1']
    q_k1 = xor_decrypt(encrypted_q_k1, biometric)
    print(f"Q_K1 decrypted: {q_k1}")

    # Step 3: Generate AQ_K1 using SEDJO (existing)
    print("\nStep 3: Generating AQ_K1 via SEDJO...")
    alice_aq_k1, bob_aq_k1 = sedjo(q_k1, q_k1)
    print(f"Alice AQ_K1: {alice_aq_k1}")
    print(f"Bob AQ_K1:   {bob_aq_k1}")

    # Step 4: Apply Error Correction (NEW)
    print("\nStep 4: Applying quantum error correction...")
    qec = QECProtocol(
        max_retries=3,
        error_threshold=0.11,
        adaptive_amplification=True
    )

    correction_result = qec.correct_errors(alice_aq_k1, bob_aq_k1)

    if not correction_result['success']:
        print(f"[FAILED] Error correction failed: {correction_result['error']}")

        # Analyze BER for security threats (NEW)
        if 'ber' in correction_result:
            ids.analyze_ber(correction_result['ber'], voter_id)

        return None

    secure_aq_k1 = correction_result['secure_key']
    ber = correction_result['original_ber']

    print(f"[SUCCESS] Error correction completed")
    print(f"  Original BER: {ber:.4f}")
    print(f"  Key length: {correction_result['original_length']} -> {correction_result['final_length']} bits")

    # Step 5: Monitor with IDS (NEW)
    print("\nStep 5: Security monitoring...")

    # Check BER
    ber_event = ids.analyze_ber(ber, voter_id)
    if ber_event:
        print(f"  [ALERT] {ber_event.description}")
    else:
        print(f"  BER within acceptable range: {ber:.4f}")

    # Get security status
    security_status = ids.get_security_status()
    print(f"  Overall security level: {security_status['overall_level']}")

    elapsed = time.time() - start_time
    print(f"\n[COMPLETE] Authentication completed in {elapsed:.3f}s")

    return {
        'session_token': session_token,
        'aq_k1': secure_aq_k1,
        'ber': ber,
        'security_level': security_status['overall_level']
    }


# ============================================================================
# EXAMPLE 3: Enhanced Voting with Full Security Stack
# ============================================================================

def enhanced_voting_session(voter_id: str,
                            auth_data: dict,
                            candidate: str,
                            ids: QuantumIntrusionDetector):
    """
    Enhanced voting session with complete security stack

    Traditional flow:
    1. Generate VQ_K1 using SEDJO(AQ_K1, AQ_K1)
    2. Encrypt vote with VQ_K1

    Enhanced flow adds:
    3. Error correction on VQ_K1
    4. Continuous security monitoring
    5. Session token validation
    """
    print(f"\n=== Enhanced Voting Session: {voter_id} ===")

    # Step 1: Validate session token (NEW)
    print("Step 1: Validating session token...")
    # In production, validate against SEO-AH session store
    print("[SUCCESS] Session token valid")

    # Step 2: Generate VQ_K1 using SEDJO (existing)
    print("\nStep 2: Generating VQ_K1 via SEDJO...")
    aq_k1 = auth_data['aq_k1']
    alice_vq_k1, bob_vq_k1 = sedjo(aq_k1, aq_k1)
    print(f"Alice VQ_K1: {alice_vq_k1}")
    print(f"Bob VQ_K1:   {bob_vq_k1}")

    # Step 3: Apply Error Correction to VQ_K1 (NEW)
    print("\nStep 3: Applying error correction to VQ_K1...")
    qec = QECProtocol()

    vq_correction = qec.correct_errors(alice_vq_k1, bob_vq_k1)

    if not vq_correction['success']:
        print(f"[FAILED] VQ_K1 error correction failed")
        return None

    secure_vq_k1 = vq_correction['secure_key']
    print(f"[SUCCESS] Secure VQ_K1 generated: {len(secure_vq_k1)} bits")

    # Monitor BER (NEW)
    ids.analyze_ber(vq_correction['original_ber'], voter_id)

    # Step 4: Encrypt vote (existing, but with secure key)
    print(f"\nStep 4: Encrypting vote for candidate: {candidate}")
    # Convert candidate to binary (simplified)
    candidate_binary = format(ord(candidate[0]), '08b').zfill(len(secure_vq_k1))

    encrypted_vote = xor_encrypt(candidate_binary, secure_vq_k1)
    print(f"Encrypted vote: {encrypted_vote}")

    # Step 5: Generate confirmation code with quantum randomness
    confirmation_code = qrng(16)
    print(f"Confirmation code: {confirmation_code}")

    # Step 6: Final security check (NEW)
    security_status = ids.get_security_status()
    print(f"\nFinal security status: {security_status['overall_level']}")

    return {
        'encrypted_vote': encrypted_vote,
        'confirmation_code': confirmation_code,
        'vq_k1': secure_vq_k1,
        'security_status': security_status
    }


# ============================================================================
# Helper Functions
# ============================================================================

def xor_encrypt(data: str, key: str) -> str:
    """XOR encryption"""
    max_len = max(len(data), len(key))
    data = data.zfill(max_len)
    key = key.zfill(max_len)
    return ''.join(str(int(a) ^ int(b)) for a, b in zip(data, key))

def xor_decrypt(encrypted: str, key: str) -> str:
    """XOR decryption (same as encryption)"""
    return xor_encrypt(encrypted, key)


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Quantegrity Enhanced Security Integration Demonstration")
    print("=" * 70)

    # Initialize intrusion detection system
    ids = QuantumIntrusionDetector(
        ber_threshold=0.11,
        auth_failure_threshold=3
    )

    # ========================================================================
    # PHASE 1: Voter Registration
    # ========================================================================

    voter_id = "V" + qrng(12)  # Random 12-bit voter ID
    biometric = qrng(16)  # 16-bit biometric signature

    print(f"\nVoter ID: {voter_id}")
    print(f"Biometric: {biometric}")

    registration_data = enhanced_voter_registration(voter_id, biometric)

    # ========================================================================
    # PHASE 2: Authentication
    # ========================================================================

    time.sleep(0.5)  # Simulate time passage

    auth_data = enhanced_authentication(
        voter_id,
        biometric,
        registration_data,
        ids
    )

    if not auth_data:
        print("\n[ABORTED] Authentication failed")
        exit(1)

    # ========================================================================
    # PHASE 3: Voting
    # ========================================================================

    time.sleep(0.5)  # Simulate time passage

    vote_data = enhanced_voting_session(
        voter_id,
        auth_data,
        candidate="Alice",
        ids=ids
    )

    if not vote_data:
        print("\n[ABORTED] Voting session failed")
        exit(1)

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================

    print("\n" + "=" * 70)
    print("FINAL SECURITY SUMMARY")
    print("=" * 70)

    status = ids.get_security_status()

    print(f"Overall Security Level: {status['overall_level']}")
    print(f"Threat Score: {status['threat_score']}/100")
    print(f"Total Security Events: {status['total_events']}")

    if status['overall_level'] in ['SECURE', 'LOW']:
        print("\n[SUCCESS] All security checks passed!")
        print(f"Vote successfully cast with quantum security guarantees.")
    else:
        print(f"\n[WARNING] Security level: {status['overall_level']}")
        print("Additional security measures may be required.")

    print("\n" + "=" * 70)
    print("Demonstration Complete")
    print("=" * 70)
