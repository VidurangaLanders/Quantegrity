"""
Intrusion Detection System for Quantegrity
Monitors quantum channel security and detects potential attacks
"""

import time
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: float
    event_type: str
    threat_level: ThreatLevel
    description: str
    source: str
    metrics: Dict


class QuantumIntrusionDetector:
    """
    Intrusion Detection System for Quantum Channels

    Monitors:
    1. Bit Error Rate (BER) anomalies
    2. Authentication failures
    3. Entanglement quality degradation
    4. Unusual access patterns
    5. Timing attacks
    """

    def __init__(self,
                 ber_threshold: float = 0.11,
                 auth_failure_threshold: int = 3,
                 time_window: float = 300.0):
        """
        Initialize IDS

        Args:
            ber_threshold: Maximum acceptable BER (default 11%)
            auth_failure_threshold: Max auth failures before alert
            time_window: Time window for pattern analysis (seconds)
        """
        self.ber_threshold = ber_threshold
        self.auth_failure_threshold = auth_failure_threshold
        self.time_window = time_window

        # Event tracking
        self.security_events: List[SecurityEvent] = []
        self.auth_failures: Dict[str, List[float]] = {}  # user_id -> timestamps
        self.ber_history: List[Tuple[float, float]] = []  # (timestamp, ber)

        # Threat counters
        self.threat_counts = {
            ThreatLevel.NONE: 0,
            ThreatLevel.LOW: 0,
            ThreatLevel.MEDIUM: 0,
            ThreatLevel.HIGH: 0,
            ThreatLevel.CRITICAL: 0
        }

    def analyze_ber(self, ber: float, user_id: str = "unknown") -> SecurityEvent:
        """
        Analyze Bit Error Rate for anomalies

        Args:
            ber: Current bit error rate
            user_id: User identifier

        Returns:
            SecurityEvent if threat detected, None otherwise
        """
        current_time = time.time()
        self.ber_history.append((current_time, ber))

        # Clean old history
        self.ber_history = [
            (t, b) for t, b in self.ber_history
            if current_time - t < self.time_window
        ]

        # Determine threat level based on BER
        if ber >= 0.20:  # 20% - Severe
            threat_level = ThreatLevel.CRITICAL
            description = f"CRITICAL: BER {ber:.2%} indicates severe channel compromise"
        elif ber >= self.ber_threshold:  # 11%+ - High
            threat_level = ThreatLevel.HIGH
            description = f"HIGH: BER {ber:.2%} exceeds security threshold"
        elif ber >= 0.08:  # 8%+ - Medium
            threat_level = ThreatLevel.MEDIUM
            description = f"MEDIUM: Elevated BER {ber:.2%} detected"
        elif ber >= 0.05:  # 5%+ - Low
            threat_level = ThreatLevel.LOW
            description = f"LOW: Slightly elevated BER {ber:.2%}"
        else:
            return None  # No threat

        event = SecurityEvent(
            timestamp=current_time,
            event_type="BER_ANOMALY",
            threat_level=threat_level,
            description=description,
            source=user_id,
            metrics={"ber": ber, "threshold": self.ber_threshold}
        )

        self._log_event(event)
        return event

    def analyze_authentication(self, user_id: str, success: bool) -> SecurityEvent:
        """
        Analyze authentication attempts for suspicious patterns

        Args:
            user_id: User identifier
            success: Whether authentication succeeded

        Returns:
            SecurityEvent if threat detected
        """
        current_time = time.time()

        if not success:
            # Track failed authentication
            if user_id not in self.auth_failures:
                self.auth_failures[user_id] = []

            self.auth_failures[user_id].append(current_time)

            # Clean old failures
            self.auth_failures[user_id] = [
                t for t in self.auth_failures[user_id]
                if current_time - t < self.time_window
            ]

            failure_count = len(self.auth_failures[user_id])

            # Determine threat level
            if failure_count >= 10:
                threat_level = ThreatLevel.CRITICAL
                description = f"CRITICAL: {failure_count} authentication failures for {user_id}"
            elif failure_count >= self.auth_failure_threshold:
                threat_level = ThreatLevel.HIGH
                description = f"HIGH: {failure_count} authentication failures for {user_id}"
            elif failure_count >= 2:
                threat_level = ThreatLevel.MEDIUM
                description = f"MEDIUM: Multiple authentication failures for {user_id}"
            else:
                threat_level = ThreatLevel.LOW
                description = f"LOW: Authentication failure for {user_id}"

            event = SecurityEvent(
                timestamp=current_time,
                event_type="AUTH_FAILURE",
                threat_level=threat_level,
                description=description,
                source=user_id,
                metrics={"failure_count": failure_count}
            )

            self._log_event(event)
            return event

        return None

    def analyze_entanglement_quality(self,
                                    correlation: float,
                                    expected_correlation: float = 0.95) -> SecurityEvent:
        """
        Analyze entanglement quality for degradation

        Args:
            correlation: Measured entanglement correlation
            expected_correlation: Expected correlation (default 95%)

        Returns:
            SecurityEvent if threat detected
        """
        current_time = time.time()
        deviation = abs(correlation - expected_correlation)

        if deviation >= 0.20:  # 20%+ deviation
            threat_level = ThreatLevel.CRITICAL
            description = f"CRITICAL: Entanglement quality severely degraded ({correlation:.2%})"
        elif deviation >= 0.10:  # 10%+ deviation
            threat_level = ThreatLevel.HIGH
            description = f"HIGH: Significant entanglement degradation ({correlation:.2%})"
        elif deviation >= 0.05:  # 5%+ deviation
            threat_level = ThreatLevel.MEDIUM
            description = f"MEDIUM: Entanglement quality reduced ({correlation:.2%})"
        else:
            return None  # Quality acceptable

        event = SecurityEvent(
            timestamp=current_time,
            event_type="ENTANGLEMENT_DEGRADATION",
            threat_level=threat_level,
            description=description,
            source="quantum_channel",
            metrics={
                "correlation": correlation,
                "expected": expected_correlation,
                "deviation": deviation
            }
        )

        self._log_event(event)
        return event

    def analyze_timing_pattern(self,
                              operation_times: List[float],
                              operation_type: str) -> SecurityEvent:
        """
        Analyze timing patterns for timing attacks

        Args:
            operation_times: List of operation durations
            operation_type: Type of operation

        Returns:
            SecurityEvent if threat detected
        """
        if len(operation_times) < 5:
            return None  # Need more samples

        import statistics

        current_time = time.time()
        mean_time = statistics.mean(operation_times)
        std_time = statistics.stdev(operation_times)

        # Check for timing anomalies
        if std_time > mean_time * 0.5:  # High variance
            threat_level = ThreatLevel.MEDIUM
            description = f"MEDIUM: Unusual timing variance in {operation_type}"

            event = SecurityEvent(
                timestamp=current_time,
                event_type="TIMING_ANOMALY",
                threat_level=threat_level,
                description=description,
                source=operation_type,
                metrics={
                    "mean_time": mean_time,
                    "std_time": std_time,
                    "samples": len(operation_times)
                }
            )

            self._log_event(event)
            return event

        return None

    def _log_event(self, event: SecurityEvent):
        """Log security event"""
        self.security_events.append(event)
        self.threat_counts[event.threat_level] += 1

        # Log to logger
        if event.threat_level == ThreatLevel.CRITICAL:
            logger.critical(event.description)
        elif event.threat_level == ThreatLevel.HIGH:
            logger.error(event.description)
        elif event.threat_level == ThreatLevel.MEDIUM:
            logger.warning(event.description)
        else:
            logger.info(event.description)

    def get_security_status(self) -> Dict:
        """
        Get current security status summary

        Returns:
            Dictionary with security metrics
        """
        current_time = time.time()

        # Recent events (last hour)
        recent_events = [
            e for e in self.security_events
            if current_time - e.timestamp < 3600
        ]

        # Calculate threat score (0-100)
        threat_score = (
            self.threat_counts[ThreatLevel.LOW] * 5 +
            self.threat_counts[ThreatLevel.MEDIUM] * 15 +
            self.threat_counts[ThreatLevel.HIGH] * 40 +
            self.threat_counts[ThreatLevel.CRITICAL] * 100
        )

        # Overall security level
        if threat_score >= 100 or self.threat_counts[ThreatLevel.CRITICAL] > 0:
            overall_level = "CRITICAL"
        elif threat_score >= 40 or self.threat_counts[ThreatLevel.HIGH] > 0:
            overall_level = "HIGH"
        elif threat_score >= 15 or self.threat_counts[ThreatLevel.MEDIUM] > 0:
            overall_level = "MEDIUM"
        elif threat_score > 0:
            overall_level = "LOW"
        else:
            overall_level = "SECURE"

        return {
            "overall_level": overall_level,
            "threat_score": min(threat_score, 100),
            "total_events": len(self.security_events),
            "recent_events": len(recent_events),
            "threat_counts": dict(self.threat_counts),
            "active_threats": [
                {
                    "type": e.event_type,
                    "level": e.threat_level.name,
                    "description": e.description,
                    "source": e.source,
                    "timestamp": e.timestamp
                }
                for e in recent_events[-10:]  # Last 10 events
            ]
        }

    def clear_history(self):
        """Clear event history"""
        self.security_events.clear()
        self.auth_failures.clear()
        self.ber_history.clear()
        self.threat_counts = {level: 0 for level in ThreatLevel}
        logger.info("Security event history cleared")


# Example usage and testing
if __name__ == "__main__":
    print("=== Intrusion Detection System Test ===\n")

    ids = QuantumIntrusionDetector()

    # Test 1: BER Analysis
    print("Test 1: BER Anomaly Detection")
    test_bers = [0.01, 0.03, 0.08, 0.12, 0.15]

    for ber in test_bers:
        event = ids.analyze_ber(ber, "test_user")
        if event:
            print(f"  BER {ber:.2%}: {event.threat_level.name} - {event.description}")
        else:
            print(f"  BER {ber:.2%}: No threat")

    # Test 2: Authentication Failures
    print("\n\nTest 2: Authentication Failure Detection")
    for i in range(5):
        event = ids.analyze_authentication("attacker_001", success=False)
        if event:
            print(f"  Attempt {i+1}: {event.threat_level.name} - {event.description}")

    # Test 3: Entanglement Quality
    print("\n\nTest 3: Entanglement Quality Analysis")
    test_correlations = [0.95, 0.90, 0.80, 0.70]

    for corr in test_correlations:
        event = ids.analyze_entanglement_quality(corr)
        if event:
            print(f"  Correlation {corr:.2%}: {event.threat_level.name}")
        else:
            print(f"  Correlation {corr:.2%}: Quality acceptable")

    # Test 4: Security Status
    print("\n\nTest 4: Overall Security Status")
    status = ids.get_security_status()

    print(f"Overall Level: {status['overall_level']}")
    print(f"Threat Score: {status['threat_score']}/100")
    print(f"Total Events: {status['total_events']}")
    print(f"\nThreat Breakdown:")
    for level, count in status['threat_counts'].items():
        if count > 0:
            print(f"  {level.name}: {count}")

    print("\n\n=== All Tests Completed ===")
