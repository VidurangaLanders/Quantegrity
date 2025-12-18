"""
Quantegrity Security Manager
Unified interface for all security modules
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
import uuid
import time

# Import security modules
from seo_ah_protocol import SEOAuthenticatedHandshake
from quantum_error_correction import QECProtocol
from intrusion_detection import QuantumIntrusionDetector
from shared_state import shared_state, SecurityEvent, ErrorCorrectionStats


class QuantegritySecurityManager:
    """
    Unified security manager for Quantegrity system

    Integrates:
    - SEO-AH authentication
    - Quantum error correction
    - Intrusion detection system
    """

    def __init__(self):
        # Initialize security modules
        self.seo_ah = SEOAuthenticatedHandshake(hash_algorithm='sha3_256')
        self.qec = QECProtocol(
            max_retries=3,
            error_threshold=0.11,
            security_parameter=64,  # Reduced for demo
            adaptive_amplification=True
        )
        self.ids = QuantumIntrusionDetector(
            ber_threshold=0.11,
            auth_failure_threshold=3,
            time_window=300.0
        )

    # ========================================================================
    # SEO-AH Authentication Methods
    # ========================================================================

    def register_voter_psk(self, voter_id: str, psk: str):
        """Register Pre-Shared Key for voter"""
        self.seo_ah.register_psk(voter_id, psk)
        self.seo_ah.register_psk("election_authority", psk)

    def perform_seo_ah_authentication(self, voter_id: str) -> Dict:
        """
        Perform SEO-AH quantum authentication

        Returns:
            Dict with authentication result
        """
        result = self.seo_ah.perform_handshake(voter_id, "election_authority")

        # Log security event
        if result['authenticated']:
            event = SecurityEvent(
                event_id=str(uuid.uuid4())[:12],
                timestamp=datetime.now().isoformat(),
                event_type="SEO_AH_SUCCESS",
                threat_level="NONE",
                source=voter_id,
                description=f"SEO-AH authentication successful",
                metrics={"elapsed": result['elapsed']}
            )
            shared_state.log_security_event(event)

            # Store session token
            if 'session_token' in result:
                shared_state.store_session_token(
                    result['session_token'],
                    {
                        'voter_id': voter_id,
                        'created_at': time.time(),
                        'expires_at': time.time() + 3600
                    }
                )
        else:
            # Log failure as security event
            event = SecurityEvent(
                event_id=str(uuid.uuid4())[:12],
                timestamp=datetime.now().isoformat(),
                event_type="SEO_AH_FAILURE",
                threat_level="HIGH",
                source=voter_id,
                description=f"SEO-AH authentication failed: {result.get('error', 'unknown')}",
                metrics=result
            )
            shared_state.log_security_event(event)

            # Log with IDS
            self.ids.analyze_authentication(voter_id, success=False)

        return result

    def verify_session_token(self, token: str) -> bool:
        """Verify SEO-AH session token"""
        verification = self.seo_ah.verify_session(token)
        return verification.get('valid', False)

    # ========================================================================
    # Error Correction Methods
    # ========================================================================

    def apply_error_correction(self, voter_id: str, alice_key: str, bob_key: str) -> Dict:
        """
        Apply quantum error correction to keys

        Returns:
            Dict with correction result and secure key
        """
        result = self.qec.correct_errors(alice_key, bob_key)

        # Log error correction statistics
        if result['success']:
            stats = ErrorCorrectionStats(
                timestamp=datetime.now().isoformat(),
                voter_id=voter_id,
                original_ber=result['original_ber'],
                final_ber=0.0,  # After correction
                key_length_before=result['original_length'],
                key_length_after=result['final_length'],
                corrections_applied=result.get('cascade_stats', {}).get('total_corrections', 0) if result.get('cascade_stats') else 0,
                success=True
            )
            shared_state.log_error_correction(stats)

            # Analyze BER with IDS
            ber_event = self.ids.analyze_ber(result['original_ber'], voter_id)
            if ber_event:
                event = SecurityEvent(
                    event_id=str(uuid.uuid4())[:12],
                    timestamp=datetime.now().isoformat(),
                    event_type="BER_ANOMALY",
                    threat_level=ber_event.threat_level.name,
                    source=voter_id,
                    description=ber_event.description,
                    metrics=ber_event.metrics
                )
                shared_state.log_security_event(event)
        else:
            # Log failure
            stats = ErrorCorrectionStats(
                timestamp=datetime.now().isoformat(),
                voter_id=voter_id,
                original_ber=result.get('ber', 0.0),
                final_ber=result.get('ber', 0.0),
                key_length_before=len(alice_key),
                key_length_after=0,
                corrections_applied=0,
                success=False
            )
            shared_state.log_error_correction(stats)

            # Log security event for high BER
            if result.get('ber', 0) > 0.11:
                event = SecurityEvent(
                    event_id=str(uuid.uuid4())[:12],
                    timestamp=datetime.now().isoformat(),
                    event_type="HIGH_BER_REJECTED",
                    threat_level="CRITICAL",
                    source=voter_id,
                    description=f"BER {result.get('ber', 0):.2%} exceeds security threshold",
                    metrics=result
                )
                shared_state.log_security_event(event)

        return result

    # ========================================================================
    # Intrusion Detection Methods
    # ========================================================================

    def monitor_authentication_attempt(self, voter_id: str, success: bool) -> Optional[SecurityEvent]:
        """Monitor authentication attempt"""
        event = self.ids.analyze_authentication(voter_id, success)

        if event:
            security_event = SecurityEvent(
                event_id=str(uuid.uuid4())[:12],
                timestamp=datetime.now().isoformat(),
                event_type="AUTH_FAILURE",
                threat_level=event.threat_level.name,
                source=voter_id,
                description=event.description,
                metrics=event.metrics
            )
            shared_state.log_security_event(security_event)
            return security_event

        return None

    def get_security_status(self) -> Dict:
        """Get overall security status from IDS"""
        ids_status = self.ids.get_security_status()
        dashboard_stats = shared_state.get_security_dashboard_stats()

        return {
            **ids_status,
            **dashboard_stats,
            'seo_ah_sessions': len(self.seo_ah.session_tokens),
            'timestamp': datetime.now().isoformat()
        }

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        self.seo_ah.cleanup_expired_sessions()

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def reset_ids_history(self):
        """Reset IDS history (for testing)"""
        self.ids.clear_history()

    def get_voter_security_summary(self, voter_id: str) -> Dict:
        """Get security summary for specific voter"""
        # Get voter's security events
        all_events = shared_state.get_security_events(1000)
        voter_events = [e for e in all_events if e.source == voter_id]

        # Get error correction stats
        ec_stats = shared_state.get_error_correction_stats(voter_id)

        # Calculate threat level
        threat_counts = {"NONE": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for event in voter_events:
            threat_counts[event.threat_level] = threat_counts.get(event.threat_level, 0) + 1

        # Determine overall security level
        if threat_counts["CRITICAL"] > 0:
            overall_level = "CRITICAL"
        elif threat_counts["HIGH"] > 0:
            overall_level = "HIGH"
        elif threat_counts["MEDIUM"] > 0:
            overall_level="MEDIUM"
        elif threat_counts["LOW"] > 0:
            overall_level = "LOW"
        else:
            overall_level = "SECURE"

        return {
            "voter_id": voter_id,
            "overall_security_level": overall_level,
            "total_events": len(voter_events),
            "threat_counts": threat_counts,
            "recent_events": [
                {
                    "type": e.event_type,
                    "level": e.threat_level,
                    "description": e.description,
                    "timestamp": e.timestamp
                }
                for e in voter_events[:5]
            ],
            "error_corrections": len(ec_stats),
            "avg_ber": sum(s.original_ber for s in ec_stats) / len(ec_stats) if ec_stats else 0.0
        }


# Global security manager instance
security_manager = QuantegritySecurityManager()
