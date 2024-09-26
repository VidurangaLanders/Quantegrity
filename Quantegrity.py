import hashlib
import random
import string
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
import numpy as np

# Quantum Key Distribution functions
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
    for char in range(n):
        if Sa[char] == '0':
            circuit.z(char)
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
    for char in range(n):
        if Sa[char] == '0':
            circuit.x(char)
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
    result = AerSimulator().run(circuit, shots=1024, memory=True).result()
    counts = result.get_counts()
    quantum_key = list(counts.keys())[0]
    key_A = quantum_key[0:n]
    key_B = quantum_key[n:2*n]
    return key_A, key_B

def qrng(n):
    circuit = QuantumCircuit(n, n)
    for i in range(n):
        circuit.h(i)
    circuit.measure(range(n), range(n))
    result = AerSimulator().run(circuit, shots=1024, memory=True).result()
    counts = result.get_counts()
    quantum_key = list(counts.keys())[0]
    return quantum_key

def xor(a, b):
    return ''.join([str(int(x) ^ int(y)) for x, y in zip(a, b)])

def hex_to_binary(hex_string):
    return bin(int(hex_string, 16))[2:].zfill(len(hex_string) * 4)

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
        return quantum_key

class Ballot:
    def __init__(self, ballot_id, questions):
        self.ballot_id = ballot_id
        self.questions = questions
        self.codes = {q: {o: self.generate_code() for o in options} for q, options in questions.items()}
        self.marked_options = {}
        self.status = "Not Cast"  # Can be "Not Cast", "Cast", "Audited", or "Spoiled"

    def generate_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

    def mark(self, question, option):
        self.marked_options[question] = option

    def get_code(self, question):
        return self.codes[question][self.marked_options[question]] if question in self.marked_options else None

class ElectionAuthority:
    def __init__(self, questions):
        self.registered_voters = {}
        self.voter_records = {}
        self.questions = questions
        self.ballots = {}
        self.table_q = {}
        self.table_s = self.create_table_s()
        self.tables_r = [self.create_table_r() for _ in range(10)]
        self.cast_votes = []
        self.audited_ballots = []
        self.spoiled_ballots = []

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
        self.create_ballots(voter.voter_id)

    def create_ballots(self, voter_id):
        ballot1 = Ballot(f"{voter_id}-1", self.questions)
        ballot2 = Ballot(f"{voter_id}-2", self.questions)
        self.ballots[voter_id] = [ballot1, ballot2]
        self.update_table_q(voter_id, ballot1, ballot2)

    def update_table_q(self, voter_id, ballot1, ballot2):
        self.table_q[voter_id] = {}
        for question in self.questions:
            codes1 = list(ballot1.codes[question].values())
            codes2 = list(ballot2.codes[question].values())
            random.shuffle(codes1)
            random.shuffle(codes2)
            self.table_q[voter_id][question] = [codes1, codes2]

    def create_table_s(self):
        return {q: {o: set() for o in options} for q, options in self.questions.items()}

    def create_table_r(self):
        table_r = []
        for voter_id in self.voter_records:
            for ballot_index in range(2):
                for question in self.questions:
                    for i, code in enumerate(self.table_q[voter_id][question][ballot_index]):
                        q_pointer = (voter_id, ballot_index, question, i)
                        s_pointer = (question, list(self.questions[question])[i % len(self.questions[question])])
                        table_r.append({"flag": False, "q_pointer": q_pointer, "s_pointer": s_pointer})
        random.shuffle(table_r)
        return table_r

    def authorize_voter(self, voter_id, biometric_signature):
        if voter_id not in self.voter_records:
            return False
        voter = self.voter_records[voter_id]
        if voter["biometric_signature"] != biometric_signature:
            return False
        if voter["has_voted"]:
            return False
        return True

    def generate_otp(self, voter_id):
        voter_key = self.voter_records[voter_id]["quantum_key"]
        authority_key = qrng(128)
        voter_qk, authority_qk = sedjo(voter_key, authority_key)
        otp = qrng(32)
        encrypted_otp = xor(authority_qk[:32], otp)
        return encrypted_otp, voter_qk, authority_qk, otp

    def validate_otp(self, voter_id, received_otp, voter_qk, authority_qk, original_otp):
        decrypted_otp = xor(voter_qk[:32], received_otp)
        return decrypted_otp == original_otp

    def get_ballot(self, voter_id):
        if voter_id not in self.ballots:
            raise ValueError("Invalid voter ID")
        ballot_to_cast, ballot_to_spoil = random.sample(self.ballots[voter_id], 2)
        self.spoil_ballot(ballot_to_spoil)
        return ballot_to_cast

    def cast_vote(self, ballot, choices):
        if ballot.status == "Not Cast":
            for question, option in choices.items():
                ballot.mark(question, option)
            ballot.status = "Cast"
            for question, option in choices.items():
                code = ballot.get_code(question)
                self.cast_votes.append((ballot.ballot_id, question, code))

                # Update Tables R and S
                for table_r in self.tables_r:
                    for entry in table_r:
                        if (entry["q_pointer"][0] == ballot.ballot_id.split('-')[0] and
                            entry["q_pointer"][2] == question and
                            self.table_q[ballot.ballot_id.split('-')[0]][question][int(ballot.ballot_id.split('-')[1]) - 1][entry["q_pointer"][3]] == code):
                            entry["flag"] = True
                            self.table_s[question][option].add(code)
                            break
            self.voter_records[ballot.ballot_id.split('-')[0]]["has_voted"] = True
        else:
            raise ValueError("Ballot has already been cast, audited, or spoiled")

    def spoil_ballot(self, ballot):
        if ballot.status == "Not Cast":
            ballot.status = "Spoiled"
            self.spoiled_ballots.append(ballot)
            # Reveal all information for this ballot in all R tables
            for table_r in self.tables_r:
                for entry in table_r:
                    if entry["q_pointer"][0] == ballot.ballot_id.split('-')[0] and entry["q_pointer"][1] == int(ballot.ballot_id.split('-')[1]) - 1:
                        entry["flag"] = True
        else:
            raise ValueError("Ballot has already been cast, audited, or spoiled")

    def get_results(self):
        return {q: {o: len(codes) for o, codes in options.items()} for q, options in self.table_s.items()}

class QuantegrityVotingSystem:
    def __init__(self, questions):
        self.election_authority = ElectionAuthority(questions)

    def register_voter(self, name, national_id, biometric_signature):
        voter = Voter(name, national_id, biometric_signature)
        self.election_authority.register_voter(voter)
        return voter.voter_id

    def authorize_voter(self, voter_id, biometric_signature):
        if not self.election_authority.authorize_voter(voter_id, biometric_signature):
            return False
        encrypted_otp, voter_qk, authority_qk, original_otp = self.election_authority.generate_otp(voter_id)
        return encrypted_otp, voter_qk, authority_qk, original_otp

    def validate_otp(self, voter_id, received_otp, voter_qk, authority_qk, original_otp):
        return self.election_authority.validate_otp(voter_id, received_otp, voter_qk, authority_qk, original_otp)

    def get_ballot(self, voter_id):
        return self.election_authority.get_ballot(voter_id)

    def cast_vote(self, ballot, choices):
        return self.election_authority.cast_vote(ballot, choices)

    def get_results(self):
        return self.election_authority.get_results()

    def print_tables(self):
        print("Table Q:")
        for voter_id, questions in self.election_authority.table_q.items():
            print(f"{voter_id}:")
            for question, ballots in questions.items():
                print(f"  {question}:")
                for i, codes in enumerate(ballots):
                    print(f"    Ballot {i+1}: {codes}")
        print()

        print("Table S:")
        for question, options in self.election_authority.table_s.items():
            print(f"{question}:")
            for option, codes in options.items():
                print(f"  {option}: {codes}")
        print()

        print("Tables R (showing only the first table):")
        for entry in self.election_authority.tables_r[0]:
            print(f"Flag: {entry['flag']}, Q-Pointer: {entry['q_pointer']}, S-Pointer: {entry['s_pointer']}")
        print()

    def print_results(self):
        results = self.get_results()
        print("Election Results:")
        for question, options in results.items():
            print(f"{question}:")
            for option, votes in options.items():
                print(f"  {option}: {votes} votes")

        print("\nCast Votes (Ballot ID, Question, Code):")
        for vote in self.election_authority.cast_votes:
            print(f"{vote[0]}, {vote[1]}: {vote[2]}")

        print("\nSpoiled Ballots:")
        for ballot in self.election_authority.spoiled_ballots:
            print(ballot.ballot_id)

def run_election_simulation():
    questions = {
        "Mayor": ["Alice", "Bob", "Carol"],
        "City Council": ["Dan", "Eve", "Frank", "Grace"]
    }
    voting_system = QuantegrityVotingSystem(questions)

    # Register voters
    num_voters = 5
    voter_ids = []
    for i in range(num_voters):
        name = f"Voter{i+1}"
        national_id = f"ID{i+1:05d}"
        biometric_signature = hashlib.sha256(f"bio{i+1}".encode()).hexdigest()[:32]
        voter_id = voting_system.register_voter(name, national_id, biometric_signature)
        voter_ids.append(voter_id)
        print(f"Voter {i+1} registered with ID: {voter_id}")

    print("\nInitial state of tables:")
    voting_system.print_tables()

    # Simulate voting process
    for voter_id in voter_ids:
        print(f"\nProcessing voter: {voter_id}")
        
        # Authorization
        biometric_signature = voting_system.election_authority.voter_records[voter_id]["biometric_signature"]
        auth_result = voting_system.authorize_voter(voter_id, biometric_signature)
        if not auth_result:
            print(f"Voter {voter_id} failed authorization")
            continue
        
        encrypted_otp, voter_qk, authority_qk, original_otp = auth_result
        print(f"Voter {voter_id} authorized. OTP sent.")

        # OTP validation (simulating voter input)
        received_otp = encrypted_otp  # In a real scenario, this would be decrypted by the voter
        if not voting_system.validate_otp(voter_id, received_otp, voter_qk, authority_qk, original_otp):
            print(f"Voter {voter_id} failed OTP validation")
            continue
        print(f"Voter {voter_id} passed OTP validation")

        # Get ballot and cast vote
        try:
            ballot = voting_system.get_ballot(voter_id)
            print(f"Ballot {ballot.ballot_id} issued to voter {voter_id}")
            
            # Simulate voter choices
            choices = {}
            for question in questions:
                choice = random.choice(questions[question])
                choices[question] = choice
            
            voting_system.cast_vote(ballot, choices)
            print(f"Voter {voter_id} successfully voted")
            
            # Print the voter's choices and corresponding codes
            for question, choice in choices.items():
                code = ballot.get_code(question)
                print(f"  {question}: {choice} (Code: {code})")
        except ValueError as e:
            print(f"Error for voter {voter_id}: {e}")

    print("\nFinal state of tables:")
    voting_system.print_tables()
    voting_system.print_results()

if __name__ == "__main__":
    run_election_simulation()