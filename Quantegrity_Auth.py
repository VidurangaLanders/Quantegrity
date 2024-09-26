import hashlib
import random
import string
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np

# Symmetrically Entangled Duetsch-Jozsa Oracle
def sedjo(A, B):
    Sa = A[::-1]
    Sb = B[::-1]
    n = len(A)
    circuit = QuantumCircuit(2*n + 2, 2*n)

    # Initialize input register
    for i in range(n):
        circuit.h(i)
        circuit.cx(i, i+n+1)
    circuit.barrier()

    # Set up the output qubit:
    circuit.x([n,2*n+1])
    circuit.barrier()

    circuit.h([n,2*n+1])
    circuit.barrier()

    # Apply secret keys (simulating Alice and Bob's inputs)

    # Layer 01

    # for Sa
    for char in range(n):
        if Sa[char] == '0':
            circuit.z(char)
    # for Sb
    for char in range(n):
        if Sb[char] == '0':
            circuit.z(char+n+1)
    circuit.barrier()

    # Layer 02
    for qubit in range(n):
        circuit.cx(qubit, n)
        circuit.cx(qubit+n+1,2*n+1)
    circuit.barrier()

    # Layer 03

    #for Sa
    for char in range(n):
        if Sa[char] == '0':
            circuit.x(char)
    #for Sb
    for char in range(n):
        if Sb[char] == '0':
            circuit.x(char+n+1)
    circuit.barrier()

    # Set output
    for i in range(n):
        circuit.h(i)
        circuit.h(i+n+1)
    circuit.barrier()

    # Measure qubits
    for i in range(n):
        circuit.measure(i, i)
    for i in range(n):
        circuit.measure(i+n+1 ,i+n)

    # Execute the circuit
    #display(circuit.draw("mpl"))
    result = AerSimulator().run(circuit, shots=1024, memory=True).result()
    counts = result.get_counts()
    # return counts
    quantum_key = list(counts.keys())[0]
    key_A = quantum_key[0:n]
    key_B = quantum_key[n:2*n]
    return key_A, key_B

# Quantum Random Number Generator
def qrng(n):
    circuit = QuantumCircuit(n, n)
    for i in range(n):
        circuit.h(i)
    circuit.measure(range(n), range(n))
    result = AerSimulator().run(circuit, shots=1024, memory=True).result()
    counts = result.get_counts()
    quantum_key = list(counts.keys())[0]
    return quantum_key

# xor definition
def xor(a, b):
    return ''.join([str(int(x) ^ int(y)) for x, y in zip(a, b)])

def hex_to_binary(hex_string):
  return bin(int(hex_string, 16))[2:]

class Voter:
    def __init__(self, name, national_id, biometric_signature):
        self.name = name
        self.national_id = national_id
        self.biometric_signature = biometric_signature
        self.voter_id = self.generate_voter_id()
        self.quantum_key = self.generate_quantum_key()

    def generate_voter_id(self):
        return hashlib.sha256(f"{self.name}{self.national_id}{self.biometric_signature}".encode()).hexdigest()[:16]

    def generate_quantum_key(self):
        temp_key = qrng(128)
        bin_biometric_signature = hex_to_binary(self.biometric_signature)
        quantum_key = xor(temp_key, bin_biometric_signature)
        return quantum_key  # Generate a 128-bit quantum key

class ElectionAuthority:
    def __init__(self):
        self.registered_voters = {}
        self.voter_records = {}
        self.candidates = []
        self.ballots = {}

    def register_voter(self, voter):
        if voter.national_id in self.registered_voters:
            raise ValueError("Voter already registered")
        self.registered_voters[voter.national_id] = voter
        self.voter_records[voter.voter_id] = {
            "name": voter.name,
            "national_id": voter.national_id,
            "biometric_signature": voter.biometric_signature,
            "quantum_key": voter.quantum_key,
            "has_voted": False
        }

    def authorize_voter(self, voter_id, biometric_signature):
        if voter_id not in self.voter_records:
            return False
        voter = self.voter_records[voter_id]
        if voter["biometric_signature"] != biometric_signature:
            return False
        if voter["has_voted"]:
            return False
        return True

    def set_candidates(self, candidates):
        self.candidates = candidates

    def generate_ballot(self, voter_id):
        if voter_id not in self.voter_records:
            raise ValueError("Invalid voter ID")

        ballot = Ballot(voter_id, self.candidates)
        self.ballots[voter_id] = ballot
        return ballot

    def cast_vote(self, voter_id, candidate, code):
        if voter_id not in self.voter_records or voter_id not in self.ballots:
            raise ValueError("Invalid voter ID")
        if self.voter_records[voter_id]["has_voted"]:
            raise ValueError("Voter has already cast a vote")

        ballot = self.ballots[voter_id]
        if ballot.cast_vote(candidate, code):
            self.voter_records[voter_id]["has_voted"] = True
            return True
        return False

    def get_results(self):
        results = {candidate: 0 for candidate in self.candidates}
        for ballot in self.ballots.values():
            if ballot.status == "Cast" and ballot.marked_candidate:
                results[ballot.marked_candidate] += 1
        return results

class Ballot:
    def __init__(self, voter_id, candidates):
        self.voter_id = voter_id
        self.candidates = candidates
        self.codes = {candidate: self.generate_code() for candidate in candidates}
        self.marked_candidate = None
        self.status = "Not Cast"  # Can be "Not Cast", "Cast", "Audited", or "Spoiled"

    def generate_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def cast_vote(self, candidate, code):
        if self.status != "Not Cast":
            return False
        if candidate not in self.candidates or self.codes[candidate] != code:
            return False
        self.marked_candidate = candidate
        self.status = "Cast"
        return True

    def spoil(self):
        if self.status != "Not Cast":
            return False
        self.status = "Spoiled"
        return True

    def audit(self):
        if self.status != "Not Cast":
            return False
        self.status = "Audited"
        return True

class QuantegrityVotingSystem:
    def __init__(self):
        self.election_authority = ElectionAuthority()

    def register_voter(self, name, national_id, biometric_signature):
        voter = Voter(name, national_id, biometric_signature)
        self.election_authority.register_voter(voter)
        return voter.voter_id

    def set_candidates(self, candidates):
        self.election_authority.set_candidates(candidates)

    def authorize_voter(self, voter_id, biometric_signature, quantum_key):
        print(f"Authorizing voter: {voter_id}")
        if not self.election_authority.authorize_voter(voter_id, biometric_signature):
            print(f"Voter {voter_id} failed biometric authorization")
            return False
        print(f"Voter {voter_id} passed biometric authorization")

        # Perform QKD for OTP generation
        voter_key = quantum_key
        authority_key = self.election_authority.voter_records[voter_id]["quantum_key"]

        # print(f"Voter key: {voter_key}")
        # print(f"Authority key: {authority_key}")
        voter_qk, authority_qk = sedjo(voter_key, authority_key)
        print(f"Voter QK: {voter_qk}")
        print(f"Authority QK: {authority_qk}")

        # Generate and encrypt OTP
        otp = qrng(32)  # 32-bit OTP
        print(f"Original OTP: {otp}")
        encrypted_otp = xor(authority_qk[:32], otp)
        # print(f"Encrypted OTP: {encrypted_otp}")

        # Decrypt and transmit OTP
        decrypted_otp = xor(voter_qk[:32], encrypted_otp)
        # print(f"Decrypted OTP: {decrypted_otp}")
        transmitted_otp = decrypted_otp
        # print(f"Transmitted OTP: {transmitted_otp}")

        return encrypted_otp, voter_qk, authority_qk

    def validate_otp(self, voter_id, encrypted_otp, voter_qk, authority_qk):
        expected_otp = xor(authority_qk[:32], encrypted_otp)
        transmitted_otp = xor(voter_qk[:32], encrypted_otp)
        # print(f"Expected OTP: {expected_otp}")
        # print(f"Transmitted OTP: {transmitted_otp}")
        if expected_otp != transmitted_otp:
            print("OTP validation failed")
            return False
        print("OTP validation passed")
        return True


    def get_ballot(self, voter_id):
        return self.election_authority.generate_ballot(voter_id)

    def cast_vote(self, voter_id, candidate, code):
        return self.election_authority.cast_vote(voter_id, candidate, code)

    def get_results(self):
        return self.election_authority.get_results()


# Test functions
def run_election_simulation(num_voters, candidates):
    voting_system = QuantegrityVotingSystem()
    voting_system.set_candidates(candidates)

    # Register voters
    voter_ids = []
    for i in range(num_voters):
        name = f"Voter{i+1}"
        national_id = f"ID{i+1:05d}"
        biometric_signature = hashlib.sha256(f"bio{i+1}".encode()).hexdigest()[:32]
        voter_id = voting_system.register_voter(name, national_id, biometric_signature)
        voter_ids.append(voter_id)
        print(f"Voter {i+1} registered with ID: {voter_id}")

    print("\nVoter Information:")
    print_voter_info(voting_system)

    # Simulate voting process
    for voter_id in voter_ids:
        # Authorization
        biometric_signature = voting_system.election_authority.voter_records[voter_id]["biometric_signature"]
        quantum_key = voting_system.election_authority.voter_records[voter_id]["quantum_key"]
        encrypted_otp, voter_qk, ea_qk = voting_system.authorize_voter(voter_id, biometric_signature, quantum_key)
        if not encrypted_otp:
            print(f"Voter {voter_id} failed authorization")
            continue

        # OTP validation
        if not voting_system.validate_otp(voter_id, encrypted_otp, voter_qk, ea_qk):
            print(f"Voter {voter_id} failed OTP validation")
            continue

        # Get ballot and cast vote
        ballot = voting_system.get_ballot(voter_id)
        candidate = random.choice(candidates)
        code = ballot.codes[candidate]
        if voting_system.cast_vote(voter_id, candidate, code):
            print(f"Voter {voter_id} successfully voted for {candidate}\n")
        else:
            print(f"Voter {voter_id} failed to cast vote\n")

    # Get and print results
    results = voting_system.get_results()
    print("\nElection Results:")
    for candidate, votes in results.items():
        print(f"{candidate}: {votes} votes")

    return voting_system

def run_invalid_voter_tests(voting_system):
    print("\nRunning Invalid Voter Tests:")

    # Test 1: Unregistered voter
    unregistered_voter_id = "unregistered123"
    result = voting_system.authorize_voter(unregistered_voter_id, "fake_biometric", "fake_quantum_key")
    print(f"Unregistered voter authorization: {'Failed' if not result else 'Passed'}")

    # Test 2: Wrong biometric signature
    registered_voter_id = list(voting_system.election_authority.voter_records.keys())[0]
    wrong_biometric = "wrong_biometric_signature"
    registered_quantum_key = voting_system.election_authority.voter_records[registered_voter_id]["quantum_key"]
    result = voting_system.authorize_voter(registered_voter_id, wrong_biometric, registered_quantum_key)
    print(f"Wrong biometric signature: {'Failed' if not result else 'Passed'}")

    # Test 3: Double voting
    biometric_signature = voting_system.election_authority.voter_records[registered_voter_id]["biometric_signature"]
    quantum_key = voting_system.election_authority.voter_records[registered_voter_id]["quantum_key"]
    voting_system.authorize_voter(registered_voter_id, biometric_signature, quantum_key)
    ballot = voting_system.get_ballot(registered_voter_id)
    candidate = voting_system.election_authority.candidates[0]
    code = ballot.codes[candidate]
    voting_system.cast_vote(registered_voter_id, candidate, code)

    result = voting_system.authorize_voter(registered_voter_id, biometric_signature)
    print(f"Double voting prevention: {'Passed' if not result else 'Failed'}")

# Print voter information
def print_voter_info(voting_system):
    for voter_id, voter_info in voting_system.election_authority.voter_records.items():
        print(f"Voter ID: {voter_id}")
        print(f"Name: {voter_info['name']}")
        print(f"National ID: {voter_info['national_id']}")
        print(f"Biometric Signature: {voter_info['biometric_signature']}")
        print(f"Has Voted: {voter_info['has_voted']}")
        print("\n")


# Run the simulation and tests
if __name__ == "__main__":
    num_voters = 5
    candidates = ["Alice", "Bob", "Carol"]

    print("Running Quantegrity Voting System Simulation")
    voting_system = run_election_simulation(num_voters, candidates)

    run_invalid_voter_tests(voting_system)