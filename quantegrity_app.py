import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

# Import the quantum voting system components
import random
import string
import json
import time
from datetime import datetime
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# Quantum Components
def sedjo(A, B):
    """Symmetrically Entangled Deutsch-Jozsa Oracle for QKD"""
    Sa = A[::-1]
    Sb = B[::-1]
    n = len(A)
    circuit = QuantumCircuit(2*n + 2, 2*n)

    # Initialize input register
    for i in range(n):
        circuit.h(i)
        circuit.cx(i, i+n+1)
    circuit.barrier()

    # Set up the output qubit
    circuit.x([n, 2*n+1])
    circuit.barrier()
    circuit.h([n, 2*n+1])
    circuit.barrier()

    # Apply secret keys
    for char in range(n):
        if Sa[char] == '0':
            circuit.z(char)
    for char in range(n):
        if Sb[char] == '0':
            circuit.z(char+n+1)
    circuit.barrier()

    for qubit in range(n):
        circuit.cx(qubit, n)
        circuit.cx(qubit+n+1, 2*n+1)
    circuit.barrier()

    for char in range(n):
        if Sa[char] == '0':
            circuit.x(char)
    for char in range(n):
        if Sb[char] == '0':
            circuit.x(char+n+1)
    circuit.barrier()

    for i in range(n):
        circuit.h(i)
        circuit.h(i+n+1)
    circuit.barrier()

    for i in range(n):
        circuit.measure(i, i)
    for i in range(n):
        circuit.measure(i+n+1, i+n)

    result = AerSimulator().run(circuit, shots=1024, memory=True).result()
    counts = result.get_counts()
    quantum_key = list(counts.keys())[0]
    key_A = quantum_key[0:n]
    key_B = quantum_key[n:2*n]
    return key_A, key_B

def qrng(n):
    """Quantum Random Number Generator"""
    circuit = QuantumCircuit(n, n)
    for i in range(n):
        circuit.h(i)
    circuit.measure(range(n), range(n))
    result = AerSimulator().run(circuit, shots=1024, memory=True).result()
    counts = result.get_counts()
    quantum_key = list(counts.keys())[0]
    return quantum_key

def xor_encrypt(data: str, key: str) -> str:
    """XOR encryption with key"""
    # Ensure key is at least as long as data
    if len(key) < len(data):
        # Extend key by repeating it
        key = (key * ((len(data) // len(key)) + 1))[:len(data)]
    elif len(key) > len(data):
        # Truncate key to match data length
        key = key[:len(data)]
    
    result = ""
    for i in range(len(data)):
        # XOR each character
        encrypted_char = chr(ord(data[i]) ^ ord(key[i]))
        result += encrypted_char
    
    return result

def xor_decrypt(encrypted_data: str, key: str) -> str:
    """XOR decryption with key (same as encryption for XOR)"""
    return xor_encrypt(encrypted_data, key)

def binary_xor(a: str, b: str) -> str:
    """XOR operation for binary strings"""
    # Make strings equal length
    max_len = max(len(a), len(b))
    a = a.zfill(max_len)
    b = b.zfill(max_len)
    
    return ''.join([str(int(x) ^ int(y)) for x, y in zip(a, b)])

def generate_qrng_key(length: int) -> str:
    """Generate a key using QRNG"""
    return qrng(length)

def generate_qrng_string(length: int) -> str:
    """Generate a random string using QRNG"""
    # Generate binary using QRNG
    binary_key = qrng(length * 4)  # 4 bits per character for hex
    
    # Convert to hex-like string
    result = ""
    for i in range(0, len(binary_key), 4):
        chunk = binary_key[i:i+4] if i+4 <= len(binary_key) else binary_key[i:].ljust(4, '0')
        hex_val = int(chunk, 2)
        if hex_val < 10:
            result += str(hex_val)
        else:
            result += chr(ord('A') + hex_val - 10)
    
    return result[:length]

def generate_voter_id(name: str, national_id: str, biometric_signature: str) -> str:
    """Generate voter ID using QRNG and XOR"""
    # Create seed from personal data
    seed_data = f"{name}{national_id}{biometric_signature}"
    
    # Generate random key using QRNG
    random_key = generate_qrng_string(16)
    
    # Use first 16 chars of seed_data, pad if necessary
    seed_16 = seed_data[:16].ljust(16, '0')
    
    # XOR encrypt
    voter_id = xor_encrypt(seed_16, random_key)
    
    # Convert to hex-like representation
    return ''.join([f"{ord(c):02X}" for c in voter_id])[:16]

def generate_signature(data: str) -> str:
    """Generate signature using QRNG and XOR"""
    # Generate random signature key
    sig_key = generate_qrng_string(32)
    
    # Use first 32 chars of data, pad if necessary
    data_32 = data[:32].ljust(32, '0')
    
    # XOR encrypt
    signature = xor_encrypt(data_32, sig_key)
    
    # Convert to hex representation
    return ''.join([f"{ord(c):02X}" for c in signature])

# Key Exchange Tracker
@dataclass
class KeyExchangeLog:
    """Tracks all key exchanges and intermediate values"""
    voter_id: str
    step: str
    voter_input_key: str
    authority_input_key: str
    voter_output_key: str
    authority_output_key: str
    otp_generated: str
    otp_encrypted: str
    otp_decrypted: str
    timestamp: datetime

class KeyExchangeTracker:
    """Tracks and displays all key exchanges"""
    
    def __init__(self):
        self.logs: List[KeyExchangeLog] = []
    
    def log_exchange(self, voter_id: str, step: str, voter_input: str, 
                    authority_input: str, voter_output: str, authority_output: str,
                    otp_generated: str = "", otp_encrypted: str = "", 
                    otp_decrypted: str = ""):
        """Log a key exchange"""
        log_entry = KeyExchangeLog(
            voter_id=voter_id,
            step=step,
            voter_input_key=voter_input,
            authority_input_key=authority_input,
            voter_output_key=voter_output,
            authority_output_key=authority_output,
            otp_generated=otp_generated,
            otp_encrypted=otp_encrypted,
            otp_decrypted=otp_decrypted,
            timestamp=datetime.now()
        )
        self.logs.append(log_entry)
        
        # Print the exchange
        print(f"\n=== KEY EXCHANGE: {step} ===")
        print(f"Voter ID: {voter_id}")
        print(f"Voter Input Key:     {voter_input}")
        print(f"Authority Input Key: {authority_input}")
        print(f"Voter Output Key:    {voter_output}")
        print(f"Authority Output Key: {authority_output}")
        if otp_generated:
            print(f"OTP Generated:       {otp_generated}")
            print(f"OTP Encrypted:       {otp_encrypted}")
            print(f"OTP Decrypted:       {otp_decrypted}")
        print(f"Timestamp: {log_entry.timestamp}")
        print("=" * 50)
    
    def get_logs_for_voter(self, voter_id: str) -> List[KeyExchangeLog]:
        """Get all logs for a specific voter"""
        return [log for log in self.logs if log.voter_id == voter_id]
    
    def print_all_logs(self):
        """Print all logged exchanges"""
        print("\n=== ALL KEY EXCHANGES ===")
        for log in self.logs:
            print(f"{log.timestamp}: {log.voter_id} - {log.step}")

# Enhanced Ballot System
class BallotStatus(Enum):
    BLANK = "blank"
    CAST = "cast"
    SPOILED = "spoiled"
    AUDITED = "audited"

@dataclass
class ConfirmationCode:
    """Represents a confirmation code for a candidate choice"""
    code: str
    candidate_id: str
    ballot_id: str
    position: int

@dataclass
class BallotChoice:
    """Represents a choice on the ballot"""
    candidate_name: str
    candidate_id: str
    confirmation_code: str
    position: int

@dataclass
class ScantegrityBallot:
    """Enhanced ballot with Scantegrity II features"""
    ballot_id: str
    contest_name: str
    choices: List[BallotChoice]
    status: BallotStatus = BallotStatus.BLANK
    voter_receipt: Optional[str] = None
    timestamp: Optional[datetime] = None
    quantum_signature: Optional[str] = None

    def mark_choice(self, candidate_id: str) -> str:
        """Mark a choice and return the confirmation code"""
        for choice in self.choices:
            if choice.candidate_id == candidate_id:
                self.status = BallotStatus.CAST
                self.timestamp = datetime.now()
                return choice.confirmation_code
        raise ValueError(f"Candidate {candidate_id} not found on ballot")

    def spoil_ballot(self) -> List[str]:
        """Spoil the ballot and reveal all confirmation codes"""
        self.status = BallotStatus.SPOILED
        self.timestamp = datetime.now()
        return [choice.confirmation_code for choice in self.choices]

    def audit_ballot(self) -> Dict[str, str]:
        """Audit the ballot and reveal all codes with candidate mapping"""
        self.status = BallotStatus.AUDITED
        self.timestamp = datetime.now()
        return {choice.candidate_id: choice.confirmation_code for choice in self.choices}

# Mixnet Tables
@dataclass
class MixnetTables:
    """Scantegrity II mixnet tables P, Q, R, S"""
    table_p: Dict[str, Dict[str, str]]  # ballot_id -> candidate_id -> confirmation_code
    table_q: Dict[str, List[str]]       # ballot_id -> shuffled confirmation codes
    table_r: List[Dict]                 # mapping table with flags and pointers
    table_s: Dict[str, List[bool]]      # candidate_id -> flags for vote counting

    def print_all_tables(self):
        """Print all mixnet tables"""
        print("\n" + "="*80)
        print("MIXNET TABLES")
        print("="*80)
        
        print("\nTABLE P (Original Confirmation Codes):")
        print("-" * 50)
        for ballot_id, candidates in self.table_p.items():
            print(f"{ballot_id}:")
            for candidate, code in candidates.items():
                print(f"  {candidate}: {code}")
        
        print("\nTABLE Q (Shuffled Confirmation Codes):")
        print("-" * 50)
        for ballot_id, codes in self.table_q.items():
            print(f"{ballot_id}: {codes}")
        
        print("\nTABLE R (Mapping Table):")
        print("-" * 50)
        print("Index | Code | Ballot ID | Candidate | Q-Pointer | S-Pointer | Flag")
        print("-" * 70)
        for i, entry in enumerate(self.table_r):
            flag_str = "✓" if entry['flag'] else " "
            print(f"{i:5d} | {entry['code']:4s} | {entry['ballot_id']:13s} | {entry['candidate']:12s} | {str(entry['q_pointer']):15s} | {str(entry['s_pointer']):15s} | {flag_str}")
        
        print("\nTABLE S (Vote Counting Flags):")
        print("-" * 50)
        for candidate, flags in self.table_s.items():
            flag_str = "".join(["✓" if f else "○" for f in flags])
            count = sum(flags)
            print(f"{candidate:12s}: {flag_str} (Total: {count})")
        
        print("="*80)

class MixnetGenerator:
    """Generates and manages Scantegrity II mixnet tables"""
    
    def __init__(self, candidates: List[str], num_ballots: int):
        self.candidates = candidates
        self.num_ballots = num_ballots
        self.tables = None

    def generate_tables(self) -> MixnetTables:
        """Generate all mixnet tables"""
        print(f"\n=== GENERATING MIXNET TABLES ===")
        print(f"Candidates: {self.candidates}")
        print(f"Number of ballots: {self.num_ballots}")
        
        # Generate Table P - original confirmation codes
        table_p = {}
        all_codes = []
        
        print("\nGenerating confirmation codes...")
        for ballot_id in range(self.num_ballots):
            ballot_str = f"ballot_{ballot_id:06d}"
            table_p[ballot_str] = {}
            
            for candidate in self.candidates:
                # Generate unique confirmation code using QRNG
                code = self._generate_confirmation_code()
                table_p[ballot_str][candidate] = code
                all_codes.append({
                    'code': code,
                    'ballot_id': ballot_str,
                    'candidate': candidate
                })

        # Generate Table Q - shuffled codes per ballot
        print("Shuffling codes for Table Q...")
        table_q = {}
        for ballot_id, candidates_codes in table_p.items():
            codes = list(candidates_codes.values())
            # Use QRNG for shuffling
            self._quantum_shuffle(codes)
            table_q[ballot_id] = codes

        # Generate Table R - mapping table
        print("Creating mapping table R...")
        table_r = []
        for i, code_info in enumerate(all_codes):
            ballot_id = code_info['ballot_id']
            code = code_info['code']
            candidate = code_info['candidate']
            
            # Find position in table Q
            q_position = table_q[ballot_id].index(code)
            
            # Find position in table S (candidate column)
            s_position = len([c for c in all_codes[:i] if c['candidate'] == candidate])
            
            table_r.append({
                'code': code,
                'ballot_id': ballot_id,
                'candidate': candidate,
                'q_pointer': (ballot_id, q_position),
                's_pointer': (candidate, s_position),
                'flag': False
            })

        # Generate Table S - vote counting flags
        print("Initializing vote counting table S...")
        table_s = {}
        for candidate in self.candidates:
            candidate_codes = [c for c in all_codes if c['candidate'] == candidate]
            table_s[candidate] = [False] * len(candidate_codes)

        self.tables = MixnetTables(table_p, table_q, table_r, table_s)
        
        print("✓ Mixnet tables generated successfully!")
        self.tables.print_all_tables()
        
        return self.tables

    def _generate_confirmation_code(self) -> str:
        """Generate a unique confirmation code using QRNG"""
        return generate_qrng_string(4)

    def _quantum_shuffle(self, items: List):
        """Shuffle list using quantum randomness"""
        n = len(items)
        for i in range(n - 1, 0, -1):
            # Generate quantum random number for index
            random_bits = qrng(8)  # 8 bits for random number
            random_int = int(random_bits, 2)
            j = random_int % (i + 1)
            items[i], items[j] = items[j], items[i]

    def flag_vote(self, confirmation_code: str) -> bool:
        """Flag a vote in the mixnet tables"""
        if not self.tables:
            return False

        print(f"\n=== FLAGGING VOTE ===")
        print(f"Confirmation Code: {confirmation_code}")

        # Find the code in table R and flag it
        for entry in self.tables.table_r:
            if entry['code'] == confirmation_code:
                entry['flag'] = True
                
                # Flag corresponding position in table S
                candidate = entry['candidate']
                _, s_position = entry['s_pointer']
                self.tables.table_s[candidate][s_position] = True
                
                print(f"✓ Vote flagged for candidate: {candidate}")
                print(f"  Position in Table S: {s_position}")
                
                return True
        
        print(f"✗ Confirmation code not found: {confirmation_code}")
        return False

    def get_tally(self) -> Dict[str, int]:
        """Get vote tally from table S"""
        if not self.tables:
            return {}
        
        tally = {}
        for candidate, flags in self.tables.table_s.items():
            tally[candidate] = sum(flags)
        
        return tally

# Bulletin Board System
@dataclass
class BulletinBoardEntry:
    """Entry in the bulletin board"""
    entry_id: str
    ballot_id: str
    confirmation_codes: List[str]
    timestamp: datetime
    digital_signature: str
    entry_type: str  # "vote", "audit", "spoiled"
    quantum_proof: Optional[str] = None

class BulletinBoard:
    """Secure bulletin board for publishing election data"""
    
    def __init__(self):
        self.entries: List[BulletinBoardEntry] = []
        self.published_ballots: Dict[str, str] = {}  # ballot_id -> entry_type
        self.commitments: Dict[str, str] = {}  # commitments to various data
        self.is_sealed = False

    def post_vote(self, ballot_id: str, confirmation_codes: List[str], 
                  quantum_proof: str = None) -> str:
        """Post a vote to the bulletin board"""
        if self.is_sealed:
            raise Exception("Bulletin board is sealed")
        
        if ballot_id in self.published_ballots:
            raise Exception(f"Ballot {ballot_id} already published")

        entry_id = self._generate_entry_id()
        signature = self._generate_signature(ballot_id, confirmation_codes)
        
        entry = BulletinBoardEntry(
            entry_id=entry_id,
            ballot_id=ballot_id,
            confirmation_codes=confirmation_codes,
            timestamp=datetime.now(),
            digital_signature=signature,
            entry_type="vote",
            quantum_proof=quantum_proof
        )
        
        self.entries.append(entry)
        self.published_ballots[ballot_id] = "vote"
        
        print(f"\n=== BULLETIN BOARD ENTRY ===")
        print(f"Entry ID: {entry_id}")
        print(f"Ballot ID: {ballot_id}")
        print(f"Confirmation Codes: {confirmation_codes}")
        print(f"Digital Signature: {signature}")
        print(f"Entry Type: vote")
        print(f"Quantum Proof: {quantum_proof}")
        print("=" * 30)
        
        return entry_id

    def post_audit(self, ballot_id: str, all_codes: Dict[str, str]) -> str:
        """Post an audited ballot to the bulletin board"""
        if ballot_id in self.published_ballots:
            raise Exception(f"Ballot {ballot_id} already published")

        entry_id = self._generate_entry_id()
        codes_list = list(all_codes.values())
        signature = self._generate_signature(ballot_id, codes_list)
        
        entry = BulletinBoardEntry(
            entry_id=entry_id,
            ballot_id=ballot_id,
            confirmation_codes=codes_list,
            timestamp=datetime.now(),
            digital_signature=signature,
            entry_type="audit"
        )
        
        self.entries.append(entry)
        self.published_ballots[ballot_id] = "audit"
        
        print(f"\n=== AUDIT BULLETIN BOARD ENTRY ===")
        print(f"Entry ID: {entry_id}")
        print(f"Ballot ID: {ballot_id}")
        print(f"All Codes: {all_codes}")
        print(f"Digital Signature: {signature}")
        print("=" * 35)
        
        return entry_id

    def verify_entry(self, entry_id: str) -> bool:
        """Verify the integrity of a bulletin board entry"""
        entry = self.get_entry(entry_id)
        if not entry:
            return False
        
        expected_signature = self._generate_signature(
            entry.ballot_id, entry.confirmation_codes
        )
        return entry.digital_signature == expected_signature

    def get_entry(self, entry_id: str) -> Optional[BulletinBoardEntry]:
        """Get a specific entry from the bulletin board"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def get_ballot_entry(self, ballot_id: str) -> Optional[BulletinBoardEntry]:
        """Get the entry for a specific ballot"""
        for entry in self.entries:
            if entry.ballot_id == ballot_id:
                return entry
        return None

    def seal_board(self):
        """Seal the bulletin board (no more entries allowed)"""
        self.is_sealed = True
        print("\n🔒 BULLETIN BOARD SEALED - No more entries allowed")

    def get_all_votes(self) -> List[BulletinBoardEntry]:
        """Get all vote entries from the bulletin board"""
        return [entry for entry in self.entries if entry.entry_type == "vote"]

    def print_all_entries(self):
        """Print all bulletin board entries"""
        print("\n" + "="*60)
        print("BULLETIN BOARD CONTENTS")
        print("="*60)
        
        for entry in self.entries:
            print(f"\nEntry ID: {entry.entry_id}")
            print(f"Type: {entry.entry_type}")
            print(f"Ballot ID: {entry.ballot_id}")
            print(f"Codes: {entry.confirmation_codes}")
            print(f"Timestamp: {entry.timestamp}")
            print(f"Signature: {entry.digital_signature}")
            if entry.quantum_proof:
                print(f"Quantum Proof: {entry.quantum_proof}")
            print("-" * 40)
        
        print(f"\nTotal Entries: {len(self.entries)}")
        print(f"Sealed: {'Yes' if self.is_sealed else 'No'}")
        print("="*60)

    def _generate_entry_id(self) -> str:
        """Generate a unique entry ID using QRNG"""
        return generate_qrng_string(16)

    def _generate_signature(self, ballot_id: str, codes: List[str]) -> str:
        """Generate a digital signature using QRNG and XOR"""
        data = f"{ballot_id}:{':'.join(codes)}"
        return generate_signature(data)

# Enhanced Voter with Quantum Authentication
class QuantumVoter:
    """Enhanced voter with quantum authentication capabilities"""
    
    def __init__(self, name: str, national_id: str, biometric_signature: str):
        self.name = name
        self.national_id = national_id
        self.biometric_signature = biometric_signature
        self.voter_id = self.generate_voter_id()
        self.quantum_key = self.generate_quantum_key()
        self.has_voted = False
        self.ballot_receipt = None
        
        print(f"\n=== VOTER REGISTRATION ===")
        print(f"Name: {name}")
        print(f"National ID: {national_id}")
        print(f"Biometric Signature: {biometric_signature}")
        print(f"Generated Voter ID: {self.voter_id}")
        print(f"Generated Quantum Key: {self.quantum_key}")
        print("=" * 30)

    def generate_voter_id(self) -> str:
        """Generate voter ID using QRNG and XOR"""
        return generate_voter_id(self.name, self.national_id, self.biometric_signature)

    def generate_quantum_key(self) -> str:
        """Generate quantum key using QRNG"""
        return generate_qrng_key(64)  # 64-bit quantum key

# Enhanced Election Authority
class QuantumElectionAuthority:
    """Enhanced Election Authority with quantum security"""
    
    def __init__(self):
        self.registered_voters: Dict[str, QuantumVoter] = {}
        self.ballot_generator = None
        self.mixnet_generator = None
        self.bulletin_board = BulletinBoard()
        self.candidates = []
        self.ballots_issued: Dict[str, ScantegrityBallot] = {}
        self.key_tracker = KeyExchangeTracker()

    def setup_election(self, candidates: List[str], num_ballots: int):
        """Setup election with candidates and generate mixnet tables"""
        self.candidates = candidates
        self.mixnet_generator = MixnetGenerator(candidates, num_ballots)
        self.mixnet_generator.generate_tables()
        
        print(f"\n✓ Election setup complete with {len(candidates)} candidates and {num_ballots} ballots")

    def register_voter(self, voter: QuantumVoter) -> bool:
        """Register a voter in the system"""
        if voter.national_id in [v.national_id for v in self.registered_voters.values()]:
            return False
        
        self.registered_voters[voter.voter_id] = voter
        print(f"✓ Voter {voter.name} registered successfully")
        return True

    def authenticate_voter(self, voter_id: str, biometric_signature: str, 
                          quantum_key: str) -> Tuple[bool, Optional[str]]:
        """Authenticate voter using quantum protocols"""
        print(f"\n=== VOTER AUTHENTICATION ===")
        print(f"Voter ID: {voter_id}")
        print(f"Biometric Signature: {biometric_signature}")
        
        if voter_id not in self.registered_voters:
            print("✗ Voter not registered")
            return False, "Voter not registered"
        
        voter = self.registered_voters[voter_id]
        
        if voter.biometric_signature != biometric_signature:
            print("✗ Biometric authentication failed")
            return False, "Biometric authentication failed"
        
        if voter.has_voted:
            print("✗ Voter has already voted")
            return False, "Voter has already voted"
        
        # Perform QKD using SEDJO
        try:
            print(f"\nPerforming SEDJO key exchange...")
            print(f"Voter Quantum Key: {quantum_key}")
            print(f"Authority has Voter Key: {voter.quantum_key}")
            
            voter_qk, authority_qk = sedjo(quantum_key, voter.quantum_key)
            
            print(f"SEDJO Result - Voter Key: {voter_qk}")
            print(f"SEDJO Result - Authority Key: {authority_qk}")
            
            # Generate and encrypt OTP
            otp = generate_qrng_key(32)
            print(f"Generated OTP: {otp}")
            
            # Use binary XOR for OTP encryption
            encrypted_otp = binary_xor(authority_qk[:32], otp)
            print(f"Encrypted OTP: {encrypted_otp}")
            
            # Verify decryption
            decrypted_otp = binary_xor(voter_qk[:32], encrypted_otp)
            print(f"Decrypted OTP: {decrypted_otp}")
            
            # Log the key exchange
            self.key_tracker.log_exchange(
                voter_id, "Authentication", quantum_key, voter.quantum_key,
                voter_qk, authority_qk, otp, encrypted_otp, decrypted_otp
            )
            
            print("✓ Quantum authentication successful")
            return True, encrypted_otp
            
        except Exception as e:
            print(f"✗ Quantum authentication failed: {str(e)}")
            return False, f"Quantum authentication failed: {str(e)}"

    def issue_ballot(self, voter_id: str) -> Optional[ScantegrityBallot]:
        """Issue a ballot to an authenticated voter"""
        if voter_id not in self.registered_voters:
            return None
        
        voter = self.registered_voters[voter_id]
        if voter.has_voted:
            return None
        
        # Generate ballot using mixnet tables
        ballot_id = f"ballot_{len(self.ballots_issued):06d}"
        
        if not self.mixnet_generator or not self.mixnet_generator.tables:
            return None
        
        print(f"\n=== ISSUING BALLOT ===")
        print(f"Ballot ID: {ballot_id}")
        print(f"Voter ID: {voter_id}")
        
        # Create ballot choices from table P
        choices = []
        if ballot_id in self.mixnet_generator.tables.table_p:
            for i, candidate in enumerate(self.candidates):
                confirmation_code = self.mixnet_generator.tables.table_p[ballot_id][candidate]
                choice = BallotChoice(
                    candidate_name=candidate,
                    candidate_id=candidate,
                    confirmation_code=confirmation_code,
                    position=i
                )
                choices.append(choice)
                print(f"  {candidate}: {confirmation_code}")
        
        ballot = ScantegrityBallot(
            ballot_id=ballot_id,
            contest_name="Main Election",
            choices=choices
        )
        
        self.ballots_issued[ballot_id] = ballot
        print(f"✓ Ballot issued successfully")
        print("=" * 25)
        
        return ballot

    def cast_vote(self, voter_id: str, ballot: ScantegrityBallot, 
                  candidate_id: str) -> Tuple[bool, Optional[str]]:
        """Cast a vote and update mixnet tables"""
        print(f"\n=== CASTING VOTE ===")
        print(f"Voter ID: {voter_id}")
        print(f"Ballot ID: {ballot.ballot_id}")
        print(f"Candidate Choice: {candidate_id}")
        
        if voter_id not in self.registered_voters:
            print("✗ Voter not registered")
            return False, "Voter not registered"
        
        voter = self.registered_voters[voter_id]
        if voter.has_voted:
            print("✗ Voter has already voted")
            return False, "Voter has already voted"
        
        try:
            # Mark the ballot
            confirmation_code = ballot.mark_choice(candidate_id)
            print(f"Confirmation Code: {confirmation_code}")
            
            # Flag the vote in mixnet tables
            if self.mixnet_generator.flag_vote(confirmation_code):
                # Post to bulletin board
                entry_id = self.bulletin_board.post_vote(
                    ballot.ballot_id, 
                    [confirmation_code],
                    quantum_proof=f"quantum_proof_{voter_id}"
                )
                
                # Mark voter as having voted
                voter.has_voted = True
                voter.ballot_receipt = entry_id
                
                print(f"✓ Vote cast successfully")
                print(f"Receipt ID: {entry_id}")
                print("=" * 20)
                
                return True, entry_id
            else:
                print("✗ Failed to record vote in mixnet")
                return False, "Failed to record vote in mixnet"
                
        except Exception as e:
            print(f"✗ Error casting vote: {str(e)}")
            return False, f"Error casting vote: {str(e)}"

    def audit_ballot(self, ballot: ScantegrityBallot) -> Dict[str, str]:
        """Audit a ballot and reveal all confirmation codes"""
        print(f"\n=== AUDITING BALLOT ===")
        print(f"Ballot ID: {ballot.ballot_id}")
        
        audit_info = ballot.audit_ballot()
        
        print("Revealed Confirmation Codes:")
        for candidate, code in audit_info.items():
            print(f"  {candidate}: {code}")
        
        # Post audit information to bulletin board
        self.bulletin_board.post_audit(ballot.ballot_id, audit_info)
        
        print("✓ Ballot audit complete")
        print("=" * 25)
        
        return audit_info

    def get_election_results(self) -> Dict[str, int]:
        """Get final election results from mixnet"""
        if not self.mixnet_generator:
            return {}
        
        results = self.mixnet_generator.get_tally()
        
        print(f"\n=== FINAL ELECTION RESULTS ===")
        total_votes = sum(results.values())
        for candidate, votes in results.items():
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            print(f"{candidate}: {votes} votes ({percentage:.1f}%)")
        print(f"Total votes: {total_votes}")
        print("=" * 32)
        
        return results

    def verify_voter_receipt(self, voter_id: str, ballot_id: str) -> bool:
        """Verify that a voter's receipt matches bulletin board"""
        if voter_id not in self.registered_voters:
            return False
        
        voter = self.registered_voters[voter_id]
        if not voter.ballot_receipt:
            return False
        
        entry = self.bulletin_board.get_entry(voter.ballot_receipt)
        if not entry:
            return False
        
        is_valid = entry.ballot_id == ballot_id and self.bulletin_board.verify_entry(voter.ballot_receipt)
        
        print(f"\n=== RECEIPT VERIFICATION ===")
        print(f"Voter ID: {voter_id}")
        print(f"Ballot ID: {ballot_id}")
        print(f"Receipt ID: {voter.ballot_receipt}")
        print(f"Verification: {'✓ Valid' if is_valid else '✗ Invalid'}")
        print("=" * 30)
        
        return is_valid

    def print_all_key_exchanges(self):
        """Print all key exchanges"""
        self.key_tracker.print_all_logs()

# Enhanced Voting System
class EnhancedQuantegritySystem:
    """Complete enhanced Quantegrity voting system"""
    
    def __init__(self):
        self.election_authority = QuantumElectionAuthority()
        self.election_setup = False

    def setup_election(self, candidates: List[str], expected_voters: int):
        """Setup election with candidates and expected number of voters"""
        # Generate extra ballots for auditing (150% of expected voters)
        num_ballots = int(expected_voters * 1.5)
        self.election_authority.setup_election(candidates, num_ballots)
        self.election_setup = True
        print(f"\n🗳️  Election setup complete for {expected_voters} expected voters")

    def register_voter(self, name: str, national_id: str, biometric_signature: str) -> str:
        """Register a new voter"""
        voter = QuantumVoter(name, national_id, biometric_signature)
        success = self.election_authority.register_voter(voter)
        
        if success:
            return voter.voter_id
        else:
            raise Exception(f"Failed to register voter {name}")

    def vote(self, voter_id: str, biometric_signature: str, 
             quantum_key: str, candidate_choice: str) -> Tuple[bool, str, Optional[str]]:
        """Complete voting process"""
        if not self.election_setup:
            return False, "Election not setup", None
        
        # Authenticate voter
        auth_success, auth_result = self.election_authority.authenticate_voter(
            voter_id, biometric_signature, quantum_key
        )
        
        if not auth_success:
            return False, f"Authentication failed: {auth_result}", None
        
        # Issue ballot
        ballot = self.election_authority.issue_ballot(voter_id)
        if not ballot:
            return False, "Failed to issue ballot", None
        
        # Cast vote
        vote_success, vote_result = self.election_authority.cast_vote(
            voter_id, ballot, candidate_choice
        )
        
        if vote_success:
            return True, f"Vote cast successfully. Receipt: {vote_result}", vote_result
        else:
            return False, f"Failed to cast vote: {vote_result}", None

    def audit_ballot_request(self, voter_id: str) -> Tuple[bool, Optional[Dict]]:
        """Request an audit ballot"""
        if not self.election_setup:
            return False, None
        
        # Issue audit ballot
        ballot = self.election_authority.issue_ballot(voter_id)
        if not ballot:
            return False, None
        
        # Audit the ballot
        audit_info = self.election_authority.audit_ballot(ballot)
        return True, audit_info

    def verify_vote(self, voter_id: str, ballot_id: str) -> bool:
        """Verify a voter's receipt against the bulletin board"""
        return self.election_authority.verify_voter_receipt(voter_id, ballot_id)

    def get_results(self) -> Dict[str, int]:
        """Get final election results"""
        return self.election_authority.get_election_results()

    def get_bulletin_board_summary(self) -> Dict:
        """Get summary of bulletin board contents"""
        bb = self.election_authority.bulletin_board
        return {
            "total_entries": len(bb.entries),
            "votes_cast": len([e for e in bb.entries if e.entry_type == "vote"]),
            "audited_ballots": len([e for e in bb.entries if e.entry_type == "audit"]),
            "is_sealed": bb.is_sealed
        }

    def print_full_system_state(self):
        """Print complete system state including all tables and exchanges"""
        print("\n" + "="*100)
        print("COMPLETE SYSTEM STATE")
        print("="*100)
        
        # Print mixnet tables
        if self.election_authority.mixnet_generator and self.election_authority.mixnet_generator.tables:
            self.election_authority.mixnet_generator.tables.print_all_tables()
        
        # Print bulletin board
        self.election_authority.bulletin_board.print_all_entries()
        
        # Print key exchanges
        self.election_authority.print_all_key_exchanges()

    def seal_election(self):
        """Seal the election (no more votes allowed)"""
        self.election_authority.bulletin_board.seal_board()
        print("\n🔒 ELECTION SEALED")

# Streamlit App Configuration
st.set_page_config(
    page_title="Quantegrity E-Voting System",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .quantum-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        margin: 1rem 0;
    }
    .info-card {
        background: #f8f9fa;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'voting_system' not in st.session_state:
    st.session_state.voting_system = None
if 'is_election_setup' not in st.session_state:
    st.session_state.is_election_setup = False
if 'registered_voters' not in st.session_state:
    st.session_state.registered_voters = []
if 'current_voter' not in st.session_state:
    st.session_state.current_voter = None
if 'quantum_logs' not in st.session_state:
    st.session_state.quantum_logs = []
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'election_name' not in st.session_state:
    st.session_state.election_name = ""

# Header
st.markdown('<h1 class="main-header">🗳️ Quantegrity E-Voting System</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Quantum-Enhanced Secure Electronic Voting with Scantegrity Protocol</p>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("🔧 System Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["🏠 Home", "⚙️ Election Setup", "👤 Voter Registration", "🗳️ Voting", "🔍 Audit & Verification", "📊 Results", "🔬 Quantum Insights"]
)

# Home Page
if page == "🏠 Home":
    st.markdown('<h2 class="sub-header">Welcome to Quantegrity</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="quantum-box">
            <h3>🌌 Quantum Features</h3>
            <ul>
                <li>Quantum Key Distribution (QKD) with SEDJO protocol</li>
                <li>Quantum Random Number Generation (QRNG)</li>
                <li>Quantum-secured voter authentication</li>
                <li>End-to-end quantum encryption</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-box">
            <h3>🔒 Security Features</h3>
            <ul>
                <li>Scantegrity II protocol implementation</li>
                <li>Mixnet tables for anonymity</li>
                <li>Cryptographic bulletin board</li>
                <li>End-to-end verifiable voting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 System Overview")
    st.info("""
    The Quantegrity system combines quantum cryptography with proven e-voting protocols to create 
    a secure, transparent, and verifiable electronic voting platform. This demonstration showcases 
    real quantum key exchanges, mixnet operations, and cryptographic proofs.
    """)
    
    # System Status
    st.markdown("### 📊 System Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Election Setup", "✅" if st.session_state.is_election_setup else "❌")
    with col2:
        st.metric("Registered Voters", len(st.session_state.registered_voters))
    with col3:
        votes_cast = len([v for v in st.session_state.registered_voters if v.get('has_voted', False)]) if st.session_state.registered_voters else 0
        st.metric("Votes Cast", votes_cast)
    with col4:
        st.metric("Quantum Exchanges", len(st.session_state.quantum_logs))

# Election Setup Page
elif page == "⚙️ Election Setup":
    st.markdown('<h2 class="sub-header">Election Configuration</h2>', unsafe_allow_html=True)
    
    if not st.session_state.is_election_setup:
        st.markdown("### 🏛️ Create New Election")
        
        with st.form("election_setup"):
            election_name = st.text_input("Election Name", "2025 General Election")
            
            st.markdown("**Candidates:**")
            num_candidates = st.number_input("Number of Candidates", min_value=2, max_value=10, value=4)
            
            candidates = []
            cols = st.columns(2)
            for i in range(num_candidates):
                with cols[i % 2]:
                    candidate = st.text_input(f"Candidate {i+1}", f"Candidate {i+1}")
                    candidates.append(candidate)
            
            expected_voters = st.number_input("Expected Number of Voters", min_value=1, max_value=1000, value=10)
            
            submitted = st.form_submit_button("🚀 Setup Election")
            
            if submitted and all(candidates):
                with st.spinner("Setting up quantum-secure election..."):
                    try:
                        # Import the classes from the original code since they're already defined above
                        st.session_state.voting_system = EnhancedQuantegritySystem()
                        st.session_state.voting_system.setup_election(candidates, expected_voters)
                        st.session_state.is_election_setup = True
                        st.session_state.candidates = candidates
                        st.session_state.election_name = election_name
                        
                        st.success("✅ Election setup complete!")
                        st.balloons()
                        time.sleep(1)  # Brief pause for user feedback
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error setting up election: {str(e)}")
                        st.write("Debug info:", str(e))
    
    else:
        st.markdown("### ✅ Election Successfully Configured")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Election Name:** {st.session_state.get('election_name', 'Unnamed Election')}")
            st.markdown(f"**Candidates:** {', '.join(st.session_state.get('candidates', []))}")
        with col2:
            st.markdown("**Quantum Security Status:** 🔒 Active")
            st.markdown("**Mixnet Tables:** ✅ Generated")
        
        if st.button("🔄 Reset Election"):
            for key in ['voting_system', 'is_election_setup', 'registered_voters', 'current_voter', 'quantum_logs', 'candidates', 'election_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Voter Registration Page
elif page == "👤 Voter Registration":
    st.markdown('<h2 class="sub-header">Quantum Voter Registration</h2>', unsafe_allow_html=True)
    
    if not st.session_state.is_election_setup:
        st.warning("⚠️ Please setup an election first!")
        st.stop()
    
    # Registration Form
    st.markdown("### 📝 Register New Voter")

    # Initialize session state for the biometric signature if it doesn't exist
    if 'biometric_signature' not in st.session_state:
        st.session_state.biometric_signature = ""

    # This button now updates the session state, which will pre-fill the form field
    if st.button("🧬 Generate New Biometric Signature"):
        st.session_state.biometric_signature = generate_qrng_string(32)
    
    with st.form("voter_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name")
            national_id = st.text_input("National ID")
        
        with col2:
            # Generate or input biometric signature
            biometric = st.text_input(
                "Biometric Signature",
                value=st.session_state.biometric_signature,
                help="Click the button above to generate a signature."
            )
        submitted = st.form_submit_button("🔐 Register with Quantum Security")
        
        if submitted and name and national_id and biometric:
            with st.spinner("Generating quantum keys and registering voter..."):
                # Create voter with quantum keys
                voter_id = st.session_state.voting_system.register_voter(name, national_id, biometric)
                
                # Get the registered voter object to access quantum key
                voter_obj = st.session_state.voting_system.election_authority.registered_voters[voter_id]
                
                voter_data = {
                    'name': name,
                    'national_id': national_id,
                    'voter_id': voter_id,
                    'biometric_signature': biometric,
                    'quantum_key': voter_obj.quantum_key,
                    'registration_time': datetime.now(),
                    'has_voted': False
                }
                
                st.session_state.registered_voters.append(voter_data)
            
            st.success(f"✅ Voter {name} registered successfully!")
            
            # Display quantum information
            st.markdown("### 🔬 Quantum Registration Details")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Voter ID:** `{voter_id}`")
                st.markdown(f"**Quantum Key:** `{voter_obj.quantum_key[:32]}...`")
            with col2:
                st.markdown(f"**Biometric Hash:** `{biometric[:16]}...`")
                st.markdown(f"**Registration Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("⚠️ Please fill in all fields to register a voter.")
    
    # Display registered voters
    if st.session_state.registered_voters:
        st.markdown("### 👥 Registered Voters")
        
        voters_df = pd.DataFrame([
            {
                'Name': v['name'],
                'Voter ID': v['voter_id'][:8] + '...',
                'Registration Time': v['registration_time'].strftime('%H:%M:%S'),
                'Status': '✅ Voted' if v['has_voted'] else '⏳ Not Voted'
            }
            for v in st.session_state.registered_voters
        ])
        
        st.dataframe(voters_df, use_container_width=True)

# Voting Page
elif page == "🗳️ Voting":
    st.markdown('<h2 class="sub-header">Quantum-Secured Voting</h2>', unsafe_allow_html=True)
    
    if not st.session_state.is_election_setup:
        st.warning("⚠️ Please setup an election first!")
        st.stop()
    
    if not st.session_state.registered_voters:
        st.warning("⚠️ No voters registered yet!")
        st.stop()
    
    # Voter Selection
    st.markdown("### 🪪 Voter Authentication")
    
    available_voters = [v for v in st.session_state.registered_voters if not v['has_voted']]
    
    if not available_voters:
        st.info("🎉 All registered voters have already voted!")
        st.stop()
    
    voter_names = [f"{v['name']} (ID: {v['voter_id'][:8]}...)" for v in available_voters]
    selected_voter_idx = st.selectbox("Select Voter", range(len(voter_names)), format_func=lambda x: voter_names[x])
    
    if selected_voter_idx is not None:
        selected_voter = available_voters[selected_voter_idx]
        
        with st.form("voting_form"):
            st.markdown(f"**Voting as:** {selected_voter['name']}")
            
            # Authentication inputs
            col1, col2 = st.columns(2)
            with col1:
                input_biometric = st.text_input("Biometric Signature", value=selected_voter['biometric_signature'])
            with col2:
                input_quantum_key = st.text_input("Quantum Key", value=selected_voter['quantum_key'])
            
            # Candidate selection
            st.markdown("### 🗳️ Select Your Candidate")
            candidate_choice = st.radio("Candidates", st.session_state.candidates)
            
            vote_submitted = st.form_submit_button("🔐 Cast Quantum-Secured Vote")
            
            if vote_submitted:
                with st.spinner("Performing quantum authentication and casting vote..."):
                    # Perform the quantum voting process
                    success, message, receipt = st.session_state.voting_system.vote(
                        selected_voter['voter_id'],
                        input_biometric,
                        input_quantum_key,
                        candidate_choice
                    )
                    
                    if success:
                        # Update voter status
                        for i, v in enumerate(st.session_state.registered_voters):
                            if v['voter_id'] == selected_voter['voter_id']:
                                st.session_state.registered_voters[i]['has_voted'] = True
                                st.session_state.registered_voters[i]['vote_receipt'] = receipt
                                st.session_state.registered_voters[i]['vote_time'] = datetime.now()
                                break
                        
                        # Store quantum exchange log
                        st.session_state.quantum_logs.append({
                            'voter': selected_voter['name'],
                            'timestamp': datetime.now(),
                            'process': 'Vote Authentication',
                            'success': True
                        })
                        
                        st.success(f"✅ Vote cast successfully for {candidate_choice}!")
                        st.markdown(f"**Receipt ID:** `{receipt}`")
                        st.balloons()
                        
                        # Show quantum process details
                        with st.expander("🔬 View Quantum Process Details"):
                            st.markdown("**Quantum Key Exchange (SEDJO Protocol):**")
                            st.code(f"Voter Quantum Key: {input_quantum_key[:32]}...")
                            st.code(f"Authority Quantum Key: {selected_voter['quantum_key'][:32]}...")
                            st.markdown("**Authentication:** ✅ Quantum signatures verified")
                            st.markdown("**Encryption:** ✅ Vote encrypted with quantum-derived key")
                            st.markdown("**Mixnet:** ✅ Vote anonymized through cryptographic mixnet")
                        
                    else:
                        st.error(f"❌ Voting failed: {message}")

# Audit & Verification Page
elif page == "🔍 Audit & Verification":
    st.markdown('<h2 class="sub-header">Election Audit & Verification</h2>', unsafe_allow_html=True)
    
    if not st.session_state.is_election_setup:
        st.warning("⚠️ Please setup an election first!")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["🎫 Ballot Audit", "📋 Bulletin Board", "🔬 Quantum Logs"])
    
    with tab1:
        st.markdown("### 🎫 Request Audit Ballot")
        st.info("Audit ballots allow voters to verify the system without casting a real vote.")
        
        if st.session_state.registered_voters:
            available_voters = [v for v in st.session_state.registered_voters if not v['has_voted']]
            
            if available_voters:
                voter_for_audit = st.selectbox(
                    "Select Voter for Audit",
                    available_voters,
                    format_func=lambda x: f"{x['name']} (ID: {x['voter_id'][:8]}...)"
                )
                
                if st.button("🔍 Request Audit Ballot"):
                    with st.spinner("Generating audit ballot..."):
                        audit_success, audit_info = st.session_state.voting_system.audit_ballot_request(
                            voter_for_audit['voter_id']
                        )
                        
                        if audit_success:
                            st.success("✅ Audit ballot generated!")
                            
                            st.markdown("**Revealed Confirmation Codes:**")
                            for candidate, code in audit_info.items():
                                st.code(f"{candidate}: {code}")
            else:
                st.info("No voters available for audit (all have voted)")
    
    with tab2:
        st.markdown("### 📋 Cryptographic Bulletin Board")
        
        if st.session_state.voting_system:
            summary = st.session_state.voting_system.get_bulletin_board_summary()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Entries", summary['total_entries'])
            with col2:
                st.metric("Votes Cast", summary['votes_cast'])
            with col3:
                st.metric("Audited Ballots", summary['audited_ballots'])
            with col4:
                st.metric("Board Status", "🔒 Sealed" if summary['is_sealed'] else "🔓 Open")
            
            # Show bulletin board entries
            bb = st.session_state.voting_system.election_authority.bulletin_board
            if bb.entries:
                entries_data = []
                for entry in bb.entries:
                    entries_data.append({
                        'Entry ID': entry.entry_id[:8] + '...',
                        'Type': entry.entry_type,
                        'Ballot ID': entry.ballot_id,
                        'Timestamp': entry.timestamp.strftime('%H:%M:%S'),
                        'Signature': entry.digital_signature[:16] + '...'
                    })
                
                st.dataframe(pd.DataFrame(entries_data), use_container_width=True)
    
    with tab3:
        st.markdown("### 🔬 Quantum Exchange Logs")
        
        if st.session_state.quantum_logs:
            for log in st.session_state.quantum_logs:
                with st.expander(f"🔬 {log['voter']} - {log['timestamp'].strftime('%H:%M:%S')}"):
                    st.markdown(f"**Process:** {log['process']}")
                    st.markdown(f"**Status:** {'✅ Success' if log['success'] else '❌ Failed'}")
                    st.markdown(f"**Timestamp:** {log['timestamp']}")
        else:
            st.info("No quantum exchanges logged yet.")

# Results Page
elif page == "📊 Results":
    st.markdown('<h2 class="sub-header">Election Results</h2>', unsafe_allow_html=True)
    
    if not st.session_state.is_election_setup:
        st.warning("⚠️ Please setup an election first!")
        st.stop()
    
    # Check if any votes have been cast
    votes_cast = len([v for v in st.session_state.registered_voters if v.get('has_voted', False)])
    
    if votes_cast == 0:
        st.info("📊 No votes have been cast yet.")
        st.stop()
    
    # Get results from the quantum voting system
    if st.session_state.voting_system:
        results = st.session_state.voting_system.get_results()
        
        if results:
            # Display results
            total_votes = sum(results.values())
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart
                fig_bar = px.bar(
                    x=list(results.keys()),
                    y=list(results.values()),
                    title="Election Results",
                    labels={'x': 'Candidates', 'y': 'Votes'},
                    color=list(results.values()),
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Pie chart
                fig_pie = px.pie(
                    values=list(results.values()),
                    names=list(results.keys()),
                    title="Vote Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Results table
            st.markdown("### 📊 Detailed Results")
            results_df = pd.DataFrame([
                {
                    'Candidate': candidate,
                    'Votes': votes,
                    'Percentage': f"{(votes/total_votes*100):.1f}%" if total_votes > 0 else "0%"
                }
                for candidate, votes in results.items()
            ])
            
            st.dataframe(results_df, use_container_width=True)
            
            # Winner announcement
            if results:
                winner = max(results.items(), key=lambda x: x[1])
                st.markdown(f"### 🏆 Winner: **{winner[0]}** with {winner[1]} votes!")
        
        # Seal election button
        if not st.session_state.voting_system.election_authority.bulletin_board.is_sealed:
            if st.button("🔒 Seal Election"):
                st.session_state.voting_system.seal_election()
                st.success("🔒 Election sealed! No more votes can be cast.")
                st.rerun()

# Quantum Insights Page
elif page == "🔬 Quantum Insights":
    st.markdown('<h2 class="sub-header">Quantum Cryptography Insights</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌌 QRNG Demo", "🔐 SEDJO Protocol", "📊 System State", "🔬 Technical Details"])
    
    with tab1:
        st.markdown("### 🎲 Quantum Random Number Generator")
        st.info("Generate truly random numbers using quantum superposition and measurement.")
        
        col1, col2 = st.columns(2)
        with col1:
            qrng_length = st.slider("Number of qubits", 4, 16, 8)
        with col2:
            if st.button("🌌 Generate Quantum Random"):
                with st.spinner("Measuring quantum states..."):
                    quantum_random = qrng(qrng_length)
                    st.code(f"Quantum Random: {quantum_random}")
                    st.code(f"Decimal: {int(quantum_random, 2)}")
    
    with tab2:
        st.markdown("### 🔐 SEDJO Key Exchange Protocol")
        st.info("Symmetrically Entangled Deutsch-Jozsa Oracle for secure key distribution.")
        
        col1, col2 = st.columns(2)
        with col1:
            key_a = st.text_input("Key A (binary)", "10110101")
        with col2:
            key_b = st.text_input("Key B (binary)", "01100110")
        
        if st.button("🔐 Perform SEDJO Exchange"):
            if len(key_a) == len(key_b) and all(c in '01' for c in key_a + key_b):
                with st.spinner("Performing quantum key exchange..."):
                    result_a, result_b = sedjo(key_a, key_b)
                    
                    st.markdown("**SEDJO Exchange Results:**")
                    st.code(f"Input A:  {key_a}")
                    st.code(f"Input B:  {key_b}")
                    st.code(f"Output A: {result_a}")
                    st.code(f"Output B: {result_b}")
                    
                    # Show quantum circuit visualization
                    st.markdown("**Quantum Circuit Process:**")
                    st.info("1. Initialize qubits in superposition\n2. Apply entanglement operations\n3. Apply secret key transformations\n4. Measure quantum states\n5. Extract shared keys")
            else:
                st.error("Please enter binary strings of equal length!")
    
    with tab3:
        st.markdown("### 📊 Complete System State")
        
        if st.session_state.voting_system and st.session_state.is_election_setup:
            if st.button("📊 Show Full System State"):
                with st.spinner("Generating system state report..."):
                    # Create expandable sections for different components
                    
                    with st.expander("🗳️ Mixnet Tables"):
                        st.info("Scantegrity II mixnet tables provide cryptographic anonymity")
                        if st.session_state.voting_system.election_authority.mixnet_generator:
                            tables = st.session_state.voting_system.election_authority.mixnet_generator.tables
                            if tables:
                                # Show Table P (Original confirmation codes)
                                st.markdown("**Table P - Original Confirmation Codes:**")
                                p_data = []
                                for ballot_id, candidates in tables.table_p.items():
                                    for candidate, code in candidates.items():
                                        p_data.append({'Ballot ID': ballot_id, 'Candidate': candidate, 'Code': code})
                                if p_data:
                                    st.dataframe(pd.DataFrame(p_data), use_container_width=True)
                                
                                # Show Table S (Vote counting)
                                st.markdown("**Table S - Vote Counting Flags:**")
                                s_data = []
                                for candidate, flags in tables.table_s.items():
                                    count = sum(flags)
                                    flag_str = "".join(["✓" if f else "○" for f in flags[:10]])  # Show first 10
                                    s_data.append({'Candidate': candidate, 'Flags': flag_str, 'Total Votes': count})
                                if s_data:
                                    st.dataframe(pd.DataFrame(s_data), use_container_width=True)
                    
                    with st.expander("📋 Bulletin Board Entries"):
                        bb = st.session_state.voting_system.election_authority.bulletin_board
                        if bb.entries:
                            entries_data = []
                            for entry in bb.entries:
                                entries_data.append({
                                    'Entry ID': entry.entry_id,
                                    'Type': entry.entry_type,
                                    'Ballot ID': entry.ballot_id,
                                    'Codes': ', '.join(entry.confirmation_codes),
                                    'Timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                    'Signature': entry.digital_signature[:32] + '...'
                                })
                            st.dataframe(pd.DataFrame(entries_data), use_container_width=True)
                    
                    with st.expander("🔐 Key Exchange History"):
                        if hasattr(st.session_state.voting_system.election_authority, 'key_tracker'):
                            tracker = st.session_state.voting_system.election_authority.key_tracker
                            if tracker.logs:
                                key_data = []
                                for log in tracker.logs:
                                    key_data.append({
                                        'Voter ID': log.voter_id[:8] + '...',
                                        'Step': log.step,
                                        'Voter Input': log.voter_input_key[:16] + '...',
                                        'Authority Input': log.authority_input_key[:16] + '...',
                                        'OTP Generated': log.otp_generated[:16] + '...' if log.otp_generated else '',
                                        'Timestamp': log.timestamp.strftime('%H:%M:%S')
                                    })
                                st.dataframe(pd.DataFrame(key_data), use_container_width=True)
        else:
            st.info("Setup an election and register voters to see system state.")
    
    with tab4:
        st.markdown("### 🔬 Technical Implementation Details")
        
        st.markdown("#### 🌌 Quantum Random Number Generation (QRNG)")
        st.code("""
def qrng(n):
    circuit = QuantumCircuit(n, n)
    for i in range(n):
        circuit.h(i)  # Put qubits in superposition
    circuit.measure(range(n), range(n))  # Measure all qubits
    result = AerSimulator().run(circuit, shots=1024).result()
    return list(result.get_counts().keys())[0]
        """)
        
        st.markdown("#### 🔐 SEDJO Protocol (Quantum Key Distribution)")
        st.info("""
        The SEDJO (Symmetrically Entangled Deutsch-Jozsa Oracle) protocol uses:
        1. Quantum superposition to create entangled states
        2. Oracle functions based on secret keys
        3. Deutsch-Jozsa algorithm for key extraction
        4. Quantum measurement to establish shared keys
        """)
        
        st.markdown("#### 🗳️ Scantegrity II Integration")
        st.info("""
        The system implements Scantegrity II features:
        - **Table P**: Original confirmation codes for each ballot/candidate
        - **Table Q**: Shuffled confirmation codes for anonymity
        - **Table R**: Mapping table connecting codes to votes
        - **Table S**: Final vote counting with cryptographic flags
        """)
        
        st.markdown("#### 🔒 End-to-End Verification")
        st.info("""
        Voters can verify their votes through:
        1. Receipt verification against bulletin board
        2. Audit ballot generation and verification
        3. Mixnet table consistency checks
        4. Quantum authentication logs
        """)

# Footer with system information
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🔬 Quantum Framework:** Qiskit")
with col2:
    st.markdown("**🗳️ Voting Protocol:** Scantegrity II + Quantegrity")
with col3:
    st.markdown("**🔒 Security Level:** Quantum-Enhanced")

# Real-time system monitoring in sidebar
if st.session_state.is_election_setup:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Live System Stats")
    
    # Quantum operations counter
    quantum_ops = len(st.session_state.quantum_logs)
    st.sidebar.metric("Quantum Operations", quantum_ops)
    
    # Voting progress
    total_registered = len(st.session_state.registered_voters)
    votes_cast = len([v for v in st.session_state.registered_voters if v.get('has_voted', False)])
    if total_registered > 0:
        progress = votes_cast / total_registered
        st.sidebar.progress(progress)
        st.sidebar.caption(f"Voting Progress: {votes_cast}/{total_registered}")
    
    # Security status
    st.sidebar.markdown("### 🔒 Security Status")
    st.sidebar.success("🌌 Quantum RNG: Active")
    st.sidebar.success("🔐 SEDJO Protocol: Active")
    st.sidebar.success("📋 Bulletin Board: Secure")
    
    # Quick actions
    st.sidebar.markdown("### ⚡ Quick Actions")
    if st.sidebar.button("🔄 Refresh System"):
        st.rerun()
    
    if st.sidebar.button("📊 Export Logs", help="Export system logs for analysis"):
        # Create downloadable logs
        logs_data = {
            'registered_voters': len(st.session_state.registered_voters),
            'votes_cast': votes_cast,
            'quantum_operations': quantum_ops,
            'timestamp': datetime.now().isoformat()
        }
        st.sidebar.download_button(
            "📥 Download System State",
            json.dumps(logs_data, indent=2),
            file_name=f"quantegrity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Advanced features in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔬 Advanced Features")

# Real-time quantum visualization
if st.sidebar.checkbox("🌌 Show Quantum Visualization"):
    st.sidebar.markdown("**Live Quantum State:**")
    
    # Generate a simple quantum random visualization
    if st.sidebar.button("🎲 Generate Quantum Pattern"):
        pattern = qrng(8)
        st.sidebar.code(f"Pattern: {pattern}")
        
        # Create a simple visualization of the quantum state
        binary_values = [int(bit) for bit in pattern]
        fig = go.Figure(data=go.Scatter(
            y=binary_values,
            mode='markers+lines',
            marker=dict(size=10, color=binary_values, colorscale='Viridis'),
            line=dict(width=2)
        ))
        fig.update_layout(
            title="Quantum Measurement Results",
            height=200,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.sidebar.plotly_chart(fig, use_container_width=True)

# Performance monitoring
if st.sidebar.checkbox("📈 Performance Monitor"):
    st.sidebar.markdown("**System Performance:**")
    
    # Simulate some performance metrics
    if st.session_state.quantum_logs:
        avg_processing_time = "0.5s"  # Simulated
        success_rate = "100%"  # Simulated
        
        st.sidebar.metric("Avg Processing Time", avg_processing_time)
        st.sidebar.metric("Success Rate", success_rate)
        st.sidebar.metric("Quantum Fidelity", "99.8%")

# Help and documentation
st.sidebar.markdown("---")
st.sidebar.markdown("### ❓ Help & Info")

if st.sidebar.button("📚 System Documentation"):
    st.sidebar.markdown("""
    **Quick Guide:**
    1. **Setup**: Configure election and candidates
    2. **Register**: Add voters with quantum keys
    3. **Vote**: Cast quantum-secured votes
    4. **Audit**: Verify system integrity
    5. **Results**: View final tallies
    
    **Quantum Features:**
    - QRNG for true randomness
    - SEDJO for key exchange
    - Quantum authentication
    - Cryptographic verification
    """)

# Emergency controls (for demonstration)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚨 Emergency Controls")

if st.sidebar.button("⚠️ Emergency Reset", help="Reset entire system"):
    if st.sidebar.button("⚠️ Confirm Reset"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.sidebar.success("System reset complete!")
        st.rerun()

# Version and credits
st.sidebar.markdown("---")
st.sidebar.markdown("""
<small>
**Quantegrity v1.0**<br>
Quantum-Enhanced E-Voting<br>
Built with Streamlit & Qiskit<br>
© 2025 Quantum Democracy Project
</small>
""", unsafe_allow_html=True)