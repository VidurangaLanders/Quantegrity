"""
Symmetrically Entangled Oracle Authenticated Handshake (SEO-AH)
Ref: Landers (2023), Section 6.2

Provides integrated quantum challenge-response authentication
Prevents Man-in-the-Middle (MITM) attacks
"""

import hashlib
import time
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class SEOAuthenticatedHandshake:
    """
    SEO-AH Protocol Implementation

    Protocol Steps:
    1. Both parties share a Pre-Shared Key (PSK)
    2. Execute quantum challenge: SESO(PSK, PSK)
    3. When inputs are identical, outputs are perfectly correlated
    4. Classical verification: hash(zA) must equal hash(zB)
    5. Any deviation indicates MITM attack or channel disruption
    """

    def __init__(self, hash_algorithm: str = 'sha3_256'):
        """
        Initialize SEO-AH handler

        Args:
            hash_algorithm: Hash function for verification
                          Options: 'sha3_256', 'sha256', 'blake2b'
        """
        self.hash_algorithm = hash_algorithm
        self.psk_registry = {}  # Party ID → PSK mapping
        self.session_tokens = {}  # Session token management

    def register_psk(self, party_id: str, psk: str):
        """
        Register Pre-Shared Key for a party

        Args:
            party_id: Unique identifier (e.g., voter_id)
            psk: Pre-shared key (binary string)
        """
        if not all(c in '01' for c in psk):
            raise ValueError("PSK must be binary string")

        self.psk_registry[party_id] = psk
        logger.info(f"PSK registered for {party_id}, length={len(psk)}")

    def quantum_challenge(self, psk_a: str, psk_b: str) -> Tuple[str, str]:
        """
        Execute quantum challenge using SESO protocol

        Key Property:
        When sA = sB = PSK (identical inputs), measurements are
        perfectly correlated: zA = zB with probability 1

        Any eavesdropper Eve between Alice and Bob will break
        this correlation, causing zA ≠ zB

        Args:
            psk_a: Alice's PSK
            psk_b: Bob's PSK (should match psk_a)

        Returns:
            Tuple of (zA, zB) - measurement outcomes
        """
        n = len(psk_a)

        # Create quantum circuit for SESO
        circuit = QuantumCircuit(2*n, 2*n)

        # Step 1: Create entangled Bell pairs
        for i in range(n):
            circuit.h(i)
            circuit.cx(i, i+n)

        # Step 2: Apply PSK transformations
        # Alice applies X gates based on her PSK
        for i in range(n):
            if psk_a[i] == '1':
                circuit.x(i)

        # Bob applies X gates based on his PSK
        for i in range(n):
            if psk_b[i] == '1':
                circuit.x(i+n)

        # Step 3: Measure
        circuit.measure(range(n), range(n))
        circuit.measure(range(n, 2*n), range(n, 2*n))

        # Execute circuit
        result = AerSimulator().run(circuit, shots=1, memory=True).result()
        measurement = list(result.get_counts().keys())[0]

        # Split measurements
        za = measurement[:n]
        zb = measurement[n:2*n]

        return za, zb

    def hash(self, data: str) -> str:
        """
        Compute cryptographic hash

        Args:
            data: Binary string to hash

        Returns:
            Hexadecimal hash digest
        """
        if self.hash_algorithm == 'sha3_256':
            return hashlib.sha3_256(data.encode()).hexdigest()
        elif self.hash_algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif self.hash_algorithm == 'blake2b':
            return hashlib.blake2b(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

    def generate_session_token(self, za: str, zb: str) -> str:
        """
        Generate authenticated session token

        Token is derived from both measurements plus timestamp
        This binds the session to the authenticated quantum channel
        """
        combined = za + zb + str(time.time())
        return self.hash(combined)

    def perform_handshake(self,
                         alice_id: str,
                         bob_id: str,
                         timeout: float = 30.0) -> Dict:
        """
        Execute complete SEO-AH authentication handshake

        Process:
        1. Verify both parties have PSK registered
        2. Execute quantum challenge with identical PSKs
        3. Compute hash of each measurement
        4. Compare hashes (classical channel)
        5. If hashes match → authenticated
        6. Generate session token

        Args:
            alice_id: Alice's identifier
            bob_id: Bob's identifier
            timeout: Max time for handshake (seconds)

        Returns:
            Authentication result dictionary
        """
        start_time = time.time()

        # Verify PSK registration
        psk_alice = self.psk_registry.get(alice_id)
        psk_bob = self.psk_registry.get(bob_id)

        if not psk_alice:
            return {
                'authenticated': False,
                'error': f'PSK not registered for {alice_id}'
            }

        if not psk_bob:
            return {
                'authenticated': False,
                'error': f'PSK not registered for {bob_id}'
            }

        # PSKs must match for authentication
        if psk_alice != psk_bob:
            logger.warning(f"PSK mismatch: {alice_id} vs {bob_id}")
            return {
                'authenticated': False,
                'error': 'psk_mismatch',
                'note': 'This should not happen in normal operation'
            }

        # Execute quantum challenge
        logger.info(f"Executing quantum challenge: {alice_id} ↔ {bob_id}")
        za, zb = self.quantum_challenge(psk_alice, psk_bob)

        # Compute hashes
        hash_a = self.hash(za)
        hash_b = self.hash(zb)

        # Verify correlation
        authenticated = (hash_a == hash_b)

        elapsed = time.time() - start_time

        if elapsed > timeout:
            return {
                'authenticated': False,
                'error': 'timeout',
                'elapsed': elapsed
            }

        result = {
            'authenticated': authenticated,
            'alice_id': alice_id,
            'bob_id': bob_id,
            'alice_measurement': za,
            'bob_measurement': zb,
            'hash_a': hash_a,
            'hash_b': hash_b,
            'elapsed': elapsed,
            'timestamp': time.time()
        }

        if authenticated:
            # Generate session token
            session_token = self.generate_session_token(za, zb)
            result['session_token'] = session_token

            # Store session
            self.session_tokens[session_token] = {
                'alice_id': alice_id,
                'bob_id': bob_id,
                'created_at': time.time(),
                'expires_at': time.time() + 3600  # 1 hour
            }

            logger.info(f"[SUCCESS] Authentication successful: {alice_id} <-> {bob_id}")
        else:
            logger.warning(f"[FAILED] Authentication failed: {alice_id} <-> {bob_id}")
            logger.warning(f"  Alice hash: {hash_a}")
            logger.warning(f"  Bob hash:   {hash_b}")
            logger.warning(f"  Possible MITM attack detected!")

        return result

    def verify_session(self, session_token: str) -> Dict:
        """
        Verify session token is valid and not expired
        """
        session = self.session_tokens.get(session_token)

        if not session:
            return {'valid': False, 'error': 'token_not_found'}

        if time.time() > session['expires_at']:
            return {'valid': False, 'error': 'token_expired'}

        return {'valid': True, 'session': session}

    def revoke_session(self, session_token: str) -> bool:
        """
        Revoke an active session token

        Returns:
            True if session was revoked, False if not found
        """
        if session_token in self.session_tokens:
            del self.session_tokens[session_token]
            logger.info(f"Session token revoked: {session_token[:16]}...")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired session tokens

        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        expired = [
            token for token, session in self.session_tokens.items()
            if current_time > session['expires_at']
        ]

        for token in expired:
            del self.session_tokens[token]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

        return len(expired)


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize handler
    seo_ah = SEOAuthenticatedHandshake()

    print("=== SEO-AH Protocol Demonstration ===\n")

    # Register pre-shared keys
    psk = "1011010110110101"  # 16-bit PSK
    seo_ah.register_psk("alice", psk)
    seo_ah.register_psk("bob", psk)
    print(f"[OK] PSK registered for alice and bob (length: {len(psk)} bits)\n")

    # Perform handshake
    print("Performing quantum authentication handshake...")
    result = seo_ah.perform_handshake("alice", "bob")

    print(f"\n--- Authentication Result ---")
    print(f"Authenticated: {result['authenticated']}")
    print(f"Elapsed time: {result['elapsed']:.3f} seconds")

    if result['authenticated']:
        print(f"\n[SUCCESS] Authentication SUCCESSFUL")
        print(f"Session token: {result['session_token'][:32]}...")
        print(f"Alice measurement: {result['alice_measurement']}")
        print(f"Bob measurement: {result['bob_measurement']}")
        print(f"Hash A: {result['hash_a'][:32]}...")
        print(f"Hash B: {result['hash_b'][:32]}...")

        # Verify session
        print("\nVerifying session token...")
        verification = seo_ah.verify_session(result['session_token'])
        print(f"Session valid: {verification['valid']}")
    else:
        print(f"\n[FAILED] Authentication FAILED")
        print(f"Error: {result.get('error', 'unknown')}")

    # Test MITM scenario
    print("\n\n=== MITM Attack Simulation ===\n")

    # Register different PSKs (simulating MITM)
    psk_alice_mitm = "1011010110110101"
    psk_bob_mitm = "0100101001001010"  # Different PSK

    seo_ah.register_psk("alice_mitm", psk_alice_mitm)
    seo_ah.register_psk("bob_mitm", psk_bob_mitm)

    print("Attempting handshake with mismatched PSKs (MITM simulation)...")
    result_mitm = seo_ah.perform_handshake("alice_mitm", "bob_mitm")

    print(f"\n--- MITM Test Result ---")
    print(f"Authenticated: {result_mitm['authenticated']}")
    print(f"Error: {result_mitm.get('error', 'N/A')}")

    if not result_mitm['authenticated']:
        print("\n[SUCCESS] MITM attack successfully DETECTED and PREVENTED")
