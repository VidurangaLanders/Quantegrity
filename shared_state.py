"""
Enhanced Shared State Management for Quantegrity E-Voting System
Proper implementation following the research paper specifications
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Data file path
DATA_FILE = "quantegrity_data.json"

class VoteStatus(Enum):
    NOT_VOTED = "not_voted"
    VOTED = "voted"
    BALLOT_SPOILED = "spoiled"

class DeviceStatus(Enum):
    NOT_REQUESTED = "not_requested"
    REQUESTED = "requested"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"

class AuthenticationStatus(Enum):
    NOT_AUTHENTICATED = "not_authenticated"
    BIOMETRIC_VERIFIED = "biometric_verified"
    AQ_K1_GENERATED = "aq_k1_generated"
    AUTHENTICATED = "authenticated"

# Enhanced data classes following the paper
@dataclass
class QuantumKeys:
    """Quantum keys as defined in the paper"""
    q_k1: str = ""  # Original quantum key
    q_k2: str = ""  # Device registration key
    encrypted_q_k1: str = ""  # Q_K1 encrypted with biometric
    aq_k1_alice: str = ""  # Authentication key (Alice side)
    aq_k1_bob: str = ""  # Authentication key (Bob side)
    vq_k1_alice: str = ""  # Voting key (Alice side)
    vq_k1_bob: str = ""  # Voting key (Bob side)

@dataclass
class BiometricData:
    """Biometric signature data"""
    signature: str = ""  # 16-bit biometric signature
    is_enrolled: bool = False
    enrollment_time: str = ""

@dataclass
class DeviceInfo:
    """Device registration information"""
    device_id: str = ""
    device_fingerprint: str = ""
    registration_time: str = ""
    verification_otp: str = ""
    encrypted_otp: str = ""
    is_verified: bool = False

@dataclass
class Voter:
    voter_id: str
    name: str
    national_id: str
    quantum_keys: QuantumKeys
    biometric_data: BiometricData
    device_info: DeviceInfo
    is_registered: bool = False
    device_status: str = "not_requested"
    auth_status: str = "not_authenticated"
    vote_status: str = "not_voted"
    vote_receipt: str = ""
    registration_time: str = ""
    last_login_time: str = ""
    auth_otp: str = ""  # Authentication OTP (encrypted with AQ_K1)
    auth_encrypted_otp: str = ""  # Encrypted authentication OTP

@dataclass
class Election:
    election_id: str
    name: str
    candidates: List[str]
    is_active: bool = False
    creation_time: str = ""
    ballot_pool_size: int = 1000

@dataclass
class Ballot:
    ballot_id: str
    voter_id: str
    election_id: str
    confirmation_codes: Dict[str, str]  # candidate -> confirmation_code
    is_cast: bool = False
    is_spoiled: bool = False
    is_allocated: bool = False
    selected_candidate: str = ""
    encrypted_vote: str = ""  # Vote encrypted with VQ_K1
    cast_time: str = ""
    allocation_time: str = ""

@dataclass
class BulletinEntry:
    entry_id: str
    ballot_id: str
    confirmation_codes: List[str]
    entry_type: str  # "vote" or "spoiled"
    timestamp: str
    signature: str
    quantum_proof: str = ""  # Quantum cryptographic proof

@dataclass
class CryptographicSession:
    """Track cryptographic operations for demonstration"""
    session_id: str
    voter_id: str
    operations: List[Dict] = None
    current_step: str = ""
    session_start: str = ""
    last_activity: str = ""

    def __post_init__(self):
        if self.operations is None:
            self.operations = []

# Custom JSON encoder to handle nested dataclasses and Enums
class QuantegrityJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (VoteStatus, DeviceStatus, AuthenticationStatus)):
            return obj.value
        elif hasattr(obj, '__dict__'):
            return asdict(obj)
        return super().default(obj)

class SharedState:
    """Enhanced shared state manager following paper specifications"""
    
    def __init__(self):
        self.data = self._load_data()
        self.crypto_sessions = {}
    
    def _load_data(self) -> Dict:
        """Load data from file or initialize empty state"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert back to proper structure
                    return self._convert_loaded_data(data)
            except Exception as e:
                print(f"Error loading data: {e}")
                pass
        
        return {
            "elections": {},
            "voters": {},
            "ballots": {},
            "ballot_pools": {},
            "bulletin_board": {},
            "mixnet_tables": {},
            "crypto_sessions": {},
            "system_stats": {
                "total_voters": 0,
                "total_votes": 0,
                "last_updated": "",
                "quantum_operations": 0
            }
        }
    
    def _convert_loaded_data(self, data: Dict) -> Dict:
        """Convert loaded JSON data back to proper dataclass structure"""
        # Convert voters
        if "voters" in data:
            for voter_id, voter_data in data["voters"].items():
                if isinstance(voter_data, dict):
                    # Convert nested structures
                    if "quantum_keys" in voter_data and isinstance(voter_data["quantum_keys"], dict):
                        voter_data["quantum_keys"] = QuantumKeys(**voter_data["quantum_keys"])
                    if "biometric_data" in voter_data and isinstance(voter_data["biometric_data"], dict):
                        voter_data["biometric_data"] = BiometricData(**voter_data["biometric_data"])
                    if "device_info" in voter_data and isinstance(voter_data["device_info"], dict):
                        voter_data["device_info"] = DeviceInfo(**voter_data["device_info"])
        
        return data
    
    def _save_data(self):
        """Save data to file"""
        self.data["system_stats"]["last_updated"] = datetime.now().isoformat()
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f, indent=2, cls=QuantegrityJSONEncoder)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    # Enhanced Election Management
    def create_election(self, election: Election):
        """Create a new election with ballot pool"""
        self.data["elections"][election.election_id] = asdict(election)
        
        # Create ballot pool
        self._create_ballot_pool(election.election_id, election.candidates, election.ballot_pool_size)
        self._save_data()
    
    def _create_ballot_pool(self, election_id: str, candidates: List[str], pool_size: int):
        """Create pre-configured ballot pool as per paper"""
        from quantum_core import generate_confirmation_code, generate_ballot_id
        
        ballot_pool = []
        for i in range(pool_size):
            ballot_id = generate_ballot_id()
            confirmation_codes = {}
            
            for candidate in candidates:
                confirmation_codes[candidate] = generate_confirmation_code()
            
            ballot = Ballot(
                ballot_id=ballot_id,
                voter_id="",  # Not assigned yet
                election_id=election_id,
                confirmation_codes=confirmation_codes,
                is_allocated=False
            )
            ballot_pool.append(asdict(ballot))
        
        self.data["ballot_pools"][election_id] = ballot_pool
    
    def get_election(self, election_id: str) -> Optional[Election]:
        """Get election by ID"""
        if election_id in self.data["elections"]:
            return Election(**self.data["elections"][election_id])
        return None
    
    def get_active_election(self) -> Optional[Election]:
        """Get the currently active election"""
        for election_data in self.data["elections"].values():
            if election_data["is_active"]:
                return Election(**election_data)
        return None
    
    # Enhanced Voter Management with Proper Key Handling
    def register_voter_with_quantum_keys(self, name: str, national_id: str, 
                                       q_k1: str, q_k2: str, biometric: str) -> Voter:
        """Register voter with proper quantum key management as per paper"""
        from quantum_core import generate_voter_id, encrypt_q_k1_with_biometric
        
        voter_id = generate_voter_id()
        
        # Encrypt Q_K1 with biometric signature
        encrypted_q_k1 = encrypt_q_k1_with_biometric(q_k1, biometric)
        
        # Create quantum keys structure
        quantum_keys = QuantumKeys(
            q_k1=q_k1,
            q_k2=q_k2,
            encrypted_q_k1=encrypted_q_k1
        )
        
        # Create biometric data
        biometric_data = BiometricData(
            signature=biometric,
            is_enrolled=True,
            enrollment_time=datetime.now().isoformat()
        )
        
        # Create device info
        device_info = DeviceInfo()
        
        # Create voter
        voter = Voter(
            voter_id=voter_id,
            name=name,
            national_id=national_id,
            quantum_keys=quantum_keys,
            biometric_data=biometric_data,
            device_info=device_info,
            is_registered=True,
            registration_time=datetime.now().isoformat()
        )
        
        self.data["voters"][voter_id] = asdict(voter)
        self.data["system_stats"]["total_voters"] = len(self.data["voters"])
        self._save_data()
        
        return voter
    
    def get_voter(self, voter_id: str) -> Optional[Voter]:
        """Get voter by ID with proper dataclass conversion"""
        if voter_id in self.data["voters"]:
            voter_data = self.data["voters"][voter_id].copy()
            
            # Convert nested structures back to dataclasses
            if isinstance(voter_data.get("quantum_keys"), dict):
                voter_data["quantum_keys"] = QuantumKeys(**voter_data["quantum_keys"])
            if isinstance(voter_data.get("biometric_data"), dict):
                voter_data["biometric_data"] = BiometricData(**voter_data["biometric_data"])
            if isinstance(voter_data.get("device_info"), dict):
                voter_data["device_info"] = DeviceInfo(**voter_data["device_info"])
            
            return Voter(**voter_data)
        return None
    
    def update_voter(self, voter: Voter):
        """Update voter information"""
        self.data["voters"][voter.voter_id] = asdict(voter)
        self._save_data()
    
    # Device Verification Process
    def request_device_verification(self, voter_id: str, device_fingerprint: str) -> bool:
        """Request device verification as per paper"""
        voter = self.get_voter(voter_id)
        if voter:
            voter.device_status = "requested"
            voter.device_info.device_fingerprint = device_fingerprint
            voter.device_info.registration_time = datetime.now().isoformat()
            self.update_voter(voter)
            return True
        return False
    
    def approve_device_verification(self, voter_id: str) -> Tuple[bool, str]:
        """Approve device verification and generate encrypted OTP"""
        from quantum_core import generate_otp, perform_device_verification_crypto
        
        voter = self.get_voter(voter_id)
        if voter and voter.device_status == "requested":
            # Generate OTP and encrypt with Q_K2
            otp = generate_otp()
            encrypted_otp = perform_device_verification_crypto(voter.quantum_keys.q_k2, otp)
            
            voter.device_status = "pending_verification"
            voter.device_info.verification_otp = otp
            voter.device_info.encrypted_otp = encrypted_otp
            
            self.update_voter(voter)
            return True, encrypted_otp
        return False, ""
    
    def verify_device_with_otp(self, voter_id: str, otp_input: str) -> bool:
        """Verify device using OTP"""
        voter = self.get_voter(voter_id)
        if voter and voter.device_status == "pending_verification":
            if otp_input == voter.device_info.verification_otp:
                voter.device_status = "verified"
                voter.device_info.is_verified = True
                self.update_voter(voter)
                return True
        return False
    
    # Authentication Process
    def perform_biometric_authentication(self, voter_id: str, biometric_input: str) -> Tuple[bool, str, str, str]:
        """Fixed biometric authentication with proper key updates"""
        from quantum_core import perform_authentication_crypto
        
        voter = self.get_voter(voter_id)
        if voter and voter.device_status == "verified":
            if biometric_input == voter.biometric_data.signature:
                # Perform quantum authentication
                decrypted_q_k1, alice_aq_k1, bob_aq_k1 = perform_authentication_crypto(
                    voter.quantum_keys.encrypted_q_k1, 
                    biometric_input
                )
                
                # Update voter with authentication keys - FIXED: Ensure keys are stored
                voter.quantum_keys.aq_k1_alice = alice_aq_k1
                voter.quantum_keys.aq_k1_bob = bob_aq_k1
                voter.auth_status = "aq_k1_generated"
                voter.last_login_time = datetime.now().isoformat()

                # IMPORTANT: Clear any old device verification OTPs
                voter.device_info.verification_otp = ""
                voter.device_info.encrypted_otp = ""

                
                # IMPORTANT: Save the updated voter data
                self.update_voter(voter)
                
                return True, decrypted_q_k1, alice_aq_k1, bob_aq_k1
        
        return False, "", "", ""

    def generate_auth_otp(self, voter_id: str) -> Tuple[bool, str, str]:
        """Fixed auth OTP generation with proper key retrieval"""
        from quantum_core import generate_otp, xor_encrypt
        
        # Get fresh voter data to ensure we have latest keys
        voter = self.get_voter(voter_id)
        if voter and voter.auth_status == "aq_k1_generated" and voter.quantum_keys.aq_k1_bob:
            # Generate NEW OTP for authentication (different from device verification)
            auth_otp = generate_otp()
            
            # Encrypt with AQ_K1 (NOT Q_K2)
            encrypted_auth_otp = xor_encrypt(auth_otp, voter.quantum_keys.aq_k1_bob)
            
            # Store AUTHENTICATION OTP (separate from device verification)
            voter.auth_otp = auth_otp  # Store in separate field
            voter.auth_encrypted_otp = encrypted_auth_otp  # Store in separate field
            
            self.update_voter(voter)
            return True, auth_otp, encrypted_auth_otp
        
        return False, "", ""

    def verify_auth_otp(self, voter_id: str, otp_input: str) -> bool:
        """Fixed auth OTP verification with proper status update"""
        voter = self.get_voter(voter_id)
        if voter and voter.auth_status == "aq_k1_generated":
            # Check against AUTHENTICATION OTP, not device verification OTP
            if hasattr(voter, 'auth_otp') and otp_input == voter.auth_otp:
                voter.auth_status = "authenticated"
                # Clear authentication OTPs after successful verification
                voter.auth_otp = ""
                voter.auth_encrypted_otp = ""
                self.update_voter(voter)
                return True
        return False
    
    # Voting Process
    def initiate_voting_session(self, voter_id: str) -> Tuple[bool, str, str]:
        """Fixed voting session initiation with proper key handling"""
        from quantum_core import perform_voting_crypto
        
        voter = self.get_voter(voter_id)
        if voter and voter.auth_status == "authenticated" and voter.quantum_keys.aq_k1_alice:
            # Generate VQ_K1 using AQ_K1
            alice_vq_k1, bob_vq_k1 = perform_voting_crypto(voter.quantum_keys.aq_k1_alice)
            
            voter.quantum_keys.vq_k1_alice = alice_vq_k1
            voter.quantum_keys.vq_k1_bob = bob_vq_k1
            
            self.update_voter(voter)
            return True, alice_vq_k1, bob_vq_k1
        
        return False, "", ""
    
    def allocate_ballot_from_pool(self, voter_id: str, election_id: str) -> Optional[Ballot]:
        """Allocate ballot from pre-configured pool"""
        if election_id in self.data["ballot_pools"]:
            ballot_pool = self.data["ballot_pools"][election_id]
            
            # Find first unallocated ballot
            for i, ballot_data in enumerate(ballot_pool):
                if not ballot_data["is_allocated"]:
                    # Allocate this ballot
                    ballot_data["voter_id"] = voter_id
                    ballot_data["is_allocated"] = True
                    ballot_data["allocation_time"] = datetime.now().isoformat()
                    
                    # Convert to Ballot object
                    ballot = Ballot(**ballot_data)
                    
                    # Also store in ballots collection
                    self.data["ballots"][ballot.ballot_id] = ballot_data
                    
                    self._save_data()
                    return ballot
        
        return None
    
    def cast_encrypted_vote(self, voter_id: str, ballot_id: str, selected_candidate: str) -> Tuple[bool, str, str]:
        """Fixed vote casting with proper candidate encryption"""
        from quantum_core import encrypt_candidate_vote, xor_encrypt, log_quantum_operation
        
        voter = self.get_voter(voter_id)
        ballot = self.get_ballot(ballot_id)
        
        if voter and ballot and voter.quantum_keys.vq_k1_alice:
            # Use the specialized candidate encryption function
            encrypted_vote = encrypt_candidate_vote(selected_candidate, voter.quantum_keys.vq_k1_alice)
            
            # Get confirmation code for selected candidate
            confirmation_code = ballot.confirmation_codes.get(selected_candidate, "")
            
            # Encrypt confirmation code with VQ_K1 (this is binary-to-binary)
            encrypted_confirmation = xor_encrypt(confirmation_code, voter.quantum_keys.vq_k1_bob)
            
            # Update ballot
            ballot.is_cast = True
            ballot.encrypted_vote = encrypted_vote
            ballot.selected_candidate = ""  # Don't store plaintext for privacy
            ballot.cast_time = datetime.now().isoformat()
            
            # Update voter
            voter.vote_status = "voted"
            
            # Log quantum operation
            log_quantum_operation(
                operation="Vote_Encryption",
                inputs={"candidate": selected_candidate, "vq_k1": voter.quantum_keys.vq_k1_alice},
                outputs={"encrypted_vote": encrypted_vote, "confirmation_code": confirmation_code},
                metadata={"encryption_method": "XOR", "key_type": "VQ_K1"}
            )
            
            self.update_ballot(ballot)
            self.update_voter(voter)
            
            return True, confirmation_code, encrypted_confirmation
        
        return False, "", ""
    
    def spoil_ballot(self, voter_id: str, ballot_id: str) -> Tuple[bool, Dict[str, str]]:
        """Spoil ballot and reveal all confirmation codes"""
        voter = self.get_voter(voter_id)
        ballot = self.get_ballot(ballot_id)
        
        if voter and ballot:
            ballot.is_spoiled = True
            ballot.cast_time = datetime.now().isoformat()
            
            voter.vote_status = "spoiled"
            
            self.update_ballot(ballot)
            self.update_voter(voter)
            
            return True, ballot.confirmation_codes
        
        return False, {}
    
    # Ballot Management
    def get_ballot(self, ballot_id: str) -> Optional[Ballot]:
        """Get ballot by ID"""
        if ballot_id in self.data["ballots"]:
            return Ballot(**self.data["ballots"][ballot_id])
        return None
    
    def update_ballot(self, ballot: Ballot):
        """Update ballot information"""
        self.data["ballots"][ballot.ballot_id] = asdict(ballot)
        self._save_data()
    
    def get_voter_ballots(self, voter_id: str) -> List[Ballot]:
        """Get all ballots for a voter"""
        ballots = []
        for ballot_data in self.data["ballots"].values():
            if ballot_data["voter_id"] == voter_id:
                ballots.append(Ballot(**ballot_data))
        return ballots
    
    # Bulletin Board Management
    def add_bulletin_entry(self, entry: BulletinEntry):
        """Add entry to bulletin board"""
        self.data["bulletin_board"][entry.entry_id] = asdict(entry)
        self._save_data()
    
    def get_bulletin_entry(self, entry_id: str) -> Optional[BulletinEntry]:
        """Get bulletin board entry by ID"""
        if entry_id in self.data["bulletin_board"]:
            return BulletinEntry(**self.data["bulletin_board"][entry_id])
        return None
    
    def get_all_bulletin_entries(self) -> List[BulletinEntry]:
        """Get all bulletin board entries"""
        entries = []
        for entry_data in self.data["bulletin_board"].values():
            entries.append(BulletinEntry(**entry_data))
        return sorted(entries, key=lambda x: x.timestamp)
    
    # Cryptographic Session Management
    def create_crypto_session(self, voter_id: str) -> str:
        """Create cryptographic session for demonstration"""
        session_id = str(uuid.uuid4())[:12]
        session = CryptographicSession(
            session_id=session_id,
            voter_id=voter_id,
            session_start=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat()
        )
        
        self.crypto_sessions[session_id] = session
        return session_id
    
    def get_crypto_session(self, session_id: str) -> Optional[CryptographicSession]:
        """Get cryptographic session"""
        return self.crypto_sessions.get(session_id)
    
    def update_crypto_session(self, session_id: str, operation: Dict):
        """Update cryptographic session with new operation"""
        if session_id in self.crypto_sessions:
            self.crypto_sessions[session_id].operations.append(operation)
            self.crypto_sessions[session_id].last_activity = datetime.now().isoformat()
    
    # Results and Statistics
    def get_election_results(self, election_id: str) -> Dict[str, int]:
        """Calculate election results using bulletin board entries"""
        results = {}
        election = self.get_election(election_id)
        if not election:
            return results
        
        # Initialize candidate counts
        for candidate in election.candidates:
            results[candidate] = 0
        
        # Count votes from bulletin board entries
        bulletin_entries = self.get_all_bulletin_entries()
        
        for entry in bulletin_entries:
            if entry.entry_type == "vote":
                ballot = self.get_ballot(entry.ballot_id)
                if ballot and ballot.election_id == election_id:
                    # Match confirmation code to candidate
                    for candidate, code in ballot.confirmation_codes.items():
                        if code in entry.confirmation_codes:
                            if candidate in results:
                                results[candidate] += 1
                            break
        
        # Update system stats
        self.data["system_stats"]["total_votes"] = sum(results.values())
        self._save_data()
        
        return results
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        return self.data["system_stats"]
    
    def get_all_voters(self) -> List[Voter]:
        """Get all registered voters"""
        voters = []
        for voter_data in self.data["voters"].values():
            voter_data_copy = voter_data.copy()
            
            # Convert nested structures
            if isinstance(voter_data_copy.get("quantum_keys"), dict):
                voter_data_copy["quantum_keys"] = QuantumKeys(**voter_data_copy["quantum_keys"])
            if isinstance(voter_data_copy.get("biometric_data"), dict):
                voter_data_copy["biometric_data"] = BiometricData(**voter_data_copy["biometric_data"])
            if isinstance(voter_data_copy.get("device_info"), dict):
                voter_data_copy["device_info"] = DeviceInfo(**voter_data_copy["device_info"])
            
            voters.append(Voter(**voter_data_copy))
        return voters
    
    def get_pending_device_verifications(self) -> List[Voter]:
        """Get voters with pending device verification requests"""
        pending_voters = []
        for voter in self.get_all_voters():
            if voter.device_status == "requested":
                pending_voters.append(voter)
        return pending_voters
    
    # Utility functions
    def refresh_data(self):
        """Refresh data from file"""
        self.data = self._load_data()
    
    def clear_all_data(self):
        """Clear all data (for testing)"""
        self.data = {
            "elections": {},
            "voters": {},
            "ballots": {},
            "ballot_pools": {},
            "bulletin_board": {},
            "mixnet_tables": {},
            "crypto_sessions": {},
            "system_stats": {
                "total_voters": 0,
                "total_votes": 0,
                "last_updated": "",
                "quantum_operations": 0
            }
        }
        self.crypto_sessions = {}
        self._save_data()
    
    def voter_exists_by_national_id(self, national_id: str) -> bool:
        """Check if voter exists by national ID"""
        for voter in self.get_all_voters():
            if voter.national_id == national_id:
                return True
        return False
    
    def increment_quantum_operations(self):
        """Increment quantum operations counter"""
        self.data["system_stats"]["quantum_operations"] += 1
        self._save_data()
    
    # Demonstration and Logging
    def get_demonstration_data(self, voter_id: str) -> Dict:
        """Get comprehensive demonstration data for a voter"""
        voter = self.get_voter(voter_id)
        if not voter:
            return {}
        
        return {
            "voter_info": {
                "voter_id": voter.voter_id,
                "name": voter.name,
                "registration_status": voter.is_registered,
                "device_status": voter.device_status,
                "auth_status": voter.auth_status,
                "vote_status": voter.vote_status
            },
            "quantum_keys": {
                "q_k1": voter.quantum_keys.q_k1,
                "q_k2": voter.quantum_keys.q_k2,
                "encrypted_q_k1": voter.quantum_keys.encrypted_q_k1,
                "aq_k1_alice": voter.quantum_keys.aq_k1_alice,
                "aq_k1_bob": voter.quantum_keys.aq_k1_bob,
                "vq_k1_alice": voter.quantum_keys.vq_k1_alice,
                "vq_k1_bob": voter.quantum_keys.vq_k1_bob
            },
            "biometric_data": {
                "signature": voter.biometric_data.signature,
                "is_enrolled": voter.biometric_data.is_enrolled,
                "enrollment_time": voter.biometric_data.enrollment_time
            },
            "device_info": {
                "device_fingerprint": voter.device_info.device_fingerprint,
                "verification_otp": voter.device_info.verification_otp,
                "encrypted_otp": voter.device_info.encrypted_otp,
                "is_verified": voter.device_info.is_verified
            },
            "ballots": [asdict(ballot) for ballot in self.get_voter_ballots(voter_id)]
        }
    
    # Additional helper to show the complete flow in voter portal
    def show_authentication_flow_summary():
        """Helper function to show the complete authentication flow"""
        st.markdown("### 📋 Complete Authentication Flow")
        
        flow_steps = [
            {
                "step": "1. Device Verification (Completed)",
                "description": "OTP encrypted with Q_K2",
                "status": "✅ Done"
            },
            {
                "step": "2. Biometric Authentication", 
                "description": "Decrypt Q_K1 with biometric, generate AQ_K1",
                "status": "✅ Done"
            },
            {
                "step": "3. Authentication OTP (Current)",
                "description": "NEW OTP encrypted with AQ_K1",
                "status": "⏳ In Progress"
            },
            {
                "step": "4. Voting Session",
                "description": "Generate VQ_K1 from AQ_K1",
                "status": "⏳ Pending"
            }
        ]
        
        for step_info in flow_steps:
            st.markdown(f"""
            <div class="process-step">
                <strong>{step_info['step']}</strong> - {step_info['status']}<br>
                {step_info['description']}
            </div>
            """, unsafe_allow_html=True)

# Global shared state instance
shared_state = SharedState()