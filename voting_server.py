import streamlit as st
import time
import random
import hashlib
import json
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Quantegrity E-Voting System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for Quantegrity system
def init_session_state():
    defaults = {
        'current_phase': 'registration',
        'voters_db': {},
        'ea_data': {},
        'ballots_pool': [],
        'cast_votes': [],
        'bulletin_board': [],
        'qkd_sessions': {},
        'current_voter': None,
        'system_status': 'Pre-Election Setup',
        'election_config': {
            'candidates': ['Candidate A', 'Candidate B', 'Candidate C'],
            'positions': ['President'],
            'election_id': f"ELEC_{random.randint(10000, 99999)}"
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Quantum cryptographic functions
def generate_quantum_key(length=8):
    """Generate quantum random key using QRNG simulation"""
    return ''.join([str(random.randint(0, 1)) for _ in range(length)])

def generate_qrng_number(length=6):
    """Generate true random number using QRNG"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def sedjo_qkd_protocol(alice_key, bob_key):
    """Simulate SEDJO QKD protocol for key distribution"""
    # Simulate quantum entanglement and measurement
    entangled_state = generate_quantum_key(16)
    
    # Both parties measure their qubits
    alice_measurement = hashlib.sha256(f"{alice_key}{entangled_state}".encode()).hexdigest()[:8]
    bob_measurement = hashlib.sha256(f"{bob_key}{entangled_state}".encode()).hexdigest()[:8]
    
    # If keys match, they derive the same measurement
    if alice_key == bob_key:
        return alice_measurement
    else:
        return None

def encrypt_with_biometric(data, biometric_signature):
    """Encrypt data using biometric signature"""
    return hashlib.sha256(f"{data}{biometric_signature}".encode()).hexdigest()

def create_ballot_with_confirmation_codes():
    """Create Scantegrity-style ballot with hidden confirmation codes"""
    ballot_id = f"B_{generate_qrng_number(6)}"
    confirmation_codes = {}
    
    for position in st.session_state.election_config['positions']:
        confirmation_codes[position] = {}
        for candidate in st.session_state.election_config['candidates']:
            confirmation_codes[position][candidate] = f"CC_{generate_qrng_number(4)}"
    
    return {
        'ballot_id': ballot_id,
        'confirmation_codes': confirmation_codes,
        'used': False,
        'spoiled': False
    }

# Custom CSS for Quantegrity styling
st.markdown("""
<style>
.phase-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 20px;
}
.quantum-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
.security-indicator {
    background-color: #000000;
    border-left: 4px solid #28a745;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}
.voter-card {
    background-color: #000000;
    border: 2px solid #dee2e6;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
}
.bulletin-board {
    background-color: #000000;
    border: 1px solid #ffeaa7;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    max-height: 300px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
init_session_state()

# Sidebar for system control
with st.sidebar:
    st.markdown("## 🔬 Quantegrity Control Panel")
    
    # Phase selection
    phases = ['registration', 'device_verification', 'election_day', 'voting', 'results']
    current_phase = st.selectbox(
        "Election Phase:",
        phases,
        index=phases.index(st.session_state.current_phase)
    )
    st.session_state.current_phase = current_phase
    
    st.markdown("---")
    
    # System status
    st.markdown(f"**System Status:** {st.session_state.system_status}")
    st.markdown(f"**Election ID:** {st.session_state.election_config['election_id']}")
    st.markdown(f"**Registered Voters:** {len(st.session_state.voters_db)}")
    st.markdown(f"**Votes Cast:** {len(st.session_state.cast_votes)}")
    
    st.markdown("---")
    
    if st.button("🔄 Reset System", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ['current_phase']:
                del st.session_state[key]
        init_session_state()
        st.rerun()

# Main interface
st.markdown('<div class="phase-header">🔬 Quantegrity E-Voting System</div>', unsafe_allow_html=True)

# Phase 1: Voter Registration
if st.session_state.current_phase == 'registration':
    st.markdown("## Phase 1: Voter Registration & Biometric Enrollment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Voter Registration Process")
        
        with st.form("voter_registration"):
            st.markdown("#### Personal Information")
            voter_name = st.text_input("Full Name:", value="Alice Johnson")
            national_id = st.text_input("National ID:", value="NID12345")
            email = st.text_input("Email:", value="alice@example.com")
            phone = st.text_input("Phone:", value="+1-555-0101")
            
            st.markdown("#### Biometric Data")
            st.info("👆 Simulate fingerprint scan by checking the box below")
            biometric_scanned = st.checkbox("✅ Fingerprint Scanned")

            submitted = st.form_submit_button("Register Voter", use_container_width=True)
            if submitted:
                if voter_name and national_id and biometric_scanned:
                    # Generate quantum keys
                    q_k1 = generate_quantum_key()
                    q_k2 = generate_quantum_key()
                    v_id = f"V_{generate_qrng_number(6)}"
                    
                    # Simulate biometric signature
                    bs_k = hashlib.sha256(f"biometric_{national_id}_{voter_name}".encode()).hexdigest()[:16]
                    
                    # Encrypt Q_K1 with biometric signature for voter ID card
                    encrypted_qk1 = encrypt_with_biometric(q_k1, bs_k)
                    
                    # Store in database
                    st.session_state.voters_db[v_id] = {
                        'name': voter_name,
                        'national_id': national_id,
                        'email': email,
                        'phone': phone,
                        'biometric_signature': bs_k,
                        'q_k1': q_k1,
                        'q_k2': q_k2,
                        'voter_id': v_id,
                        'encrypted_qk1_card': encrypted_qk1,
                        'device_registered': False,
                        'voted': False,
                        'registration_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.success(f"✅ Voter registered successfully! Voter ID: {v_id}")
                    st.session_state.current_voter = v_id
                else:
                    st.error("Please complete all fields and simulate the fingerprint scan")

    
    with col2:
        st.markdown("### EA (Bob) Dashboard")
        
        if st.session_state.voters_db:
            st.markdown("#### Registered Voters")
            for v_id, voter in st.session_state.voters_db.items():
                st.markdown(f"""
                <div class="voter-card">
                    <strong>{voter['name']}</strong><br>
                    Voter ID: {v_id}<br>
                    Status: {'✅ Device Registered' if voter['device_registered'] else '⏳ Pending Device Registration'}
                </div>
                """, unsafe_allow_html=True)
        
        # Pre-election setup
        st.markdown("#### Pre-Election Setup")
        if st.button("🗳️ Generate Ballot Pool", use_container_width=True):
            # Generate pool of ballots with confirmation codes
            ballot_count = 100  # Generate 100 ballots in pool
            st.session_state.ballots_pool = []
            
            for _ in range(ballot_count):
                ballot = create_ballot_with_confirmation_codes()
                st.session_state.ballots_pool.append(ballot)
            
            st.success(f"Generated {ballot_count} ballots in pool")
            st.session_state.system_status = 'Ballots Generated'

# Phase 2: Device Verification
elif st.session_state.current_phase == 'device_verification':
    st.markdown("## Phase 2: Device Registration & Verification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Voter Device Registration")
        
        voter_id = st.selectbox(
            "Select Voter ID:",
            [""] + list(st.session_state.voters_db.keys())
        )
        
        if voter_id and voter_id in st.session_state.voters_db:
            voter = st.session_state.voters_db[voter_id]
            
            st.markdown(f"**Voter:** {voter['name']}")
            st.markdown(f"**Email:** {voter['email']}")
            
            if not voter['device_registered']:
                if st.button("🔐 Initiate Device Registration", type="primary"):
                    # EA (Bob) generates OTP encrypted with Q_K2
                    device_otp = generate_qrng_number(6)
                    encrypted_otp = hashlib.sha256(f"{device_otp}{voter['q_k2']}".encode()).hexdigest()[:8]
                    
                    st.session_state.voters_db[voter_id]['device_otp'] = device_otp
                    st.session_state.voters_db[voter_id]['encrypted_otp'] = encrypted_otp
                    
                    st.success("📱 OTP sent to voter's device")
                    st.code(f"Encrypted OTP: {encrypted_otp}")
                    st.code(f"Raw OTP (for testing): {device_otp}")  # 👈 Add this line

                
                # OTP verification
                if 'device_otp' in voter:
                    st.markdown("#### Verify Device")
                    entered_otp = st.text_input("Enter OTP from your device:")
                    
                    if st.button("Verify Device"):
                        if entered_otp == voter['device_otp']:
                            st.session_state.voters_db[voter_id]['device_registered'] = True
                            st.success("✅ Device registered successfully!")
                        else:
                            st.error("❌ Invalid OTP")
            else:
                st.success("✅ Device already registered")
    
    with col2:
        st.markdown("### QKD Security Status")
        
        st.markdown("""
        <div class="quantum-box">
            <h4>🔐 Quantum Key Distribution Status</h4>
            <p>• Biometric signatures secured with quantum encryption</p>
            <p>• Device OTPs encrypted with quantum keys (Q_K2)</p>
            <p>• SEDJO protocol ready for election day authentication</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Device registration status
        registered_devices = sum(1 for v in st.session_state.voters_db.values() if v['device_registered'])
        total_voters = len(st.session_state.voters_db)
        
        st.metric("Device Registration Progress", f"{registered_devices}/{total_voters}")
        
        if registered_devices == total_voters and total_voters > 0:
            st.session_state.system_status = 'Ready for Election'
            st.success("🎉 All devices registered! System ready for election day.")

# Phase 3: Election Day Authentication
elif st.session_state.current_phase == 'election_day':
    st.markdown("## Phase 3: Election Day Login & Authentication")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Voter Authentication")
        
        voter_id = st.selectbox(
            "Voter ID:",
            [""] + [v_id for v_id, v in st.session_state.voters_db.items() if v['device_registered']]
        )
        
        if voter_id:
            voter = st.session_state.voters_db[voter_id]
            
            st.markdown(f"**Welcome:** {voter['name']}")
            
            # Biometric authentication
            if st.button("👆 Biometric Authentication", type="primary"):
                # Simulate biometric verification
                st.success("✅ Biometric authentication successful")
                
                # Decrypt Q_K1 from voter ID card using biometric signature
                decrypted_qk1 = voter['q_k1']  # In real system, this would be decrypted from card
                
                # Initiate SEDJO QKD protocol
                st.info("🔐 Initiating SEDJO QKD protocol...")
                
                # Both Alice and Bob input Q_K1 into their oracles
                aq_k1 = sedjo_qkd_protocol(decrypted_qk1, voter['q_k1'])
                
                if aq_k1:
                    # Store session key
                    st.session_state.qkd_sessions[voter_id] = {
                        'aq_k1': aq_k1,
                        'authenticated': True,
                        'session_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # EA sends OTP encrypted with AQ_K1
                    election_otp = generate_qrng_number(6)
                    encrypted_election_otp = hashlib.sha256(f"{election_otp}{aq_k1}".encode()).hexdigest()[:8]
                    
                    st.session_state.voters_db[voter_id]['election_otp'] = election_otp
                    st.session_state.voters_db[voter_id]['encrypted_election_otp'] = encrypted_election_otp
                    
                    st.success("🔑 Quantum keys established successfully!")
                    st.code(f"Encrypted Election OTP: {encrypted_election_otp}")
                    st.code(f"Election OTP: {election_otp}")

            
            # OTP verification for election access
            if voter_id in st.session_state.qkd_sessions and 'election_otp' in voter:
                st.markdown("#### Enter Election OTP")
                election_otp_input = st.text_input("Election OTP:")
                
                if st.button("Access Voting System"):
                    if election_otp_input == voter['election_otp']:
                        st.session_state.current_voter = voter_id
                        st.success("✅ Election access granted! Proceed to voting.")
                    else:
                        st.error("❌ Invalid election OTP")
    
    with col2:
        st.markdown("### Security Dashboard")
        
        st.markdown("""
        <div class="security-indicator">
            <h4>🛡️ Quantum Security Active</h4>
            <p>• Biometric authentication verified</p>
            <p>• SEDJO QKD protocol executed</p>
            <p>• Quantum-secured communication established</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show active QKD sessions
        if st.session_state.qkd_sessions:
            st.markdown("#### Active QKD Sessions")
            for v_id, session in st.session_state.qkd_sessions.items():
                voter_name = st.session_state.voters_db[v_id]['name']
                st.markdown(f"- {voter_name} ({v_id}) - {session['session_time']}")

# Phase 4: Voting Process
elif st.session_state.current_phase == 'voting':
    st.markdown("## Phase 4: Secure Vote Casting")
    
    if st.session_state.current_voter and st.session_state.current_voter in st.session_state.qkd_sessions:
        voter_id = st.session_state.current_voter
        voter = st.session_state.voters_db[voter_id]
        session = st.session_state.qkd_sessions[voter_id]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### Welcome, {voter['name']}")
            
            if not voter['voted']:
                # Initiate another QKD for voting key
                if st.button("🔐 Initialize Secure Voting Session"):
                    # Generate VQ_K1 for voting encryption
                    vq_k1 = sedjo_qkd_protocol(session['aq_k1'], session['aq_k1'])
                    st.session_state.qkd_sessions[voter_id]['vq_k1'] = vq_k1
                    
                    # Get ballot from pool
                    available_ballots = [b for b in st.session_state.ballots_pool if not b['used'] and not b['spoiled']]
                    if available_ballots:
                        ballot = available_ballots[0]
                        ballot['used'] = True
                        
                        # Encrypt ballot ID with VQ_K1
                        encrypted_ballot_id = hashlib.sha256(f"{ballot['ballot_id']}{vq_k1}".encode()).hexdigest()[:8]
                        
                        st.session_state.qkd_sessions[voter_id]['current_ballot'] = ballot
                        st.session_state.qkd_sessions[voter_id]['encrypted_ballot_id'] = encrypted_ballot_id
                        
                        st.success("🗳️ Secure voting session initialized!")
                        st.code(f"Encrypted Ballot ID: {encrypted_ballot_id}")
                
                # Voting interface
                if 'vq_k1' in st.session_state.qkd_sessions[voter_id]:
                    ballot = st.session_state.qkd_sessions[voter_id]['current_ballot']
                    vq_k1 = st.session_state.qkd_sessions[voter_id]['vq_k1']
                    
                    st.markdown("#### Cast Your Vote")
                    
                    # Option to spoil ballot
                    if st.button("📋 Spoil Ballot (Show Confirmation Codes)"):
                        ballot['spoiled'] = True
                        st.warning("Ballot spoiled. Here are the confirmation codes:")
                        st.json(ballot['confirmation_codes'])
                    
                    else:
                        # Regular voting
                        st.markdown("**Election Questions:**")
                        
                        votes = {}
                        for position in st.session_state.election_config['positions']:
                            st.markdown(f"**{position}:**")
                            selected_candidate = st.radio(
                                f"Select candidate for {position}:",
                                st.session_state.election_config['candidates'],
                                key=f"vote_{position}"
                            )
                            votes[position] = selected_candidate
                        
                        if st.button("🗳️ Cast Vote", type="primary"):
                            # Encrypt vote with VQ_K1
                            vote_data = json.dumps(votes)
                            encrypted_vote = hashlib.sha256(f"{vote_data}{vq_k1}".encode()).hexdigest()
                            
                            # Generate confirmation code
                            confirmation_code = ballot['confirmation_codes'][list(votes.keys())[0]][list(votes.values())[0]]
                            encrypted_confirmation = hashlib.sha256(f"{confirmation_code}{vq_k1}".encode()).hexdigest()[:8]
                            
                            # Record vote
                            vote_record = {
                                'voter_id': voter_id,
                                'ballot_id': ballot['ballot_id'],
                                'encrypted_vote': encrypted_vote,
                                'confirmation_code': confirmation_code,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'votes': votes
                            }
                            
                            st.session_state.cast_votes.append(vote_record)
                            st.session_state.voters_db[voter_id]['voted'] = True
                            
                            # Add to bulletin board
                            st.session_state.bulletin_board.append({
                                'ballot_id': ballot['ballot_id'],
                                'encrypted_vote': encrypted_vote,
                                'timestamp': vote_record['timestamp']
                            })
                            
                            st.success(f"✅ Vote cast successfully!")
                            st.success(f"🎫 Your confirmation code: {confirmation_code}")
                            st.info("Please save your confirmation code for verification.")
            else:
                st.success("✅ You have already voted in this election.")
                # Show voter's confirmation code
                voter_vote = next((v for v in st.session_state.cast_votes if v['voter_id'] == voter_id), None)
                if voter_vote:
                    st.info(f"Your confirmation code: {voter_vote['confirmation_code']}")
        
        with col2:
            st.markdown("### Quantum Voting Security")
            
            st.markdown("""
            <div class="quantum-box">
                <h4>🔐 Active Security Measures</h4>
                <p>• Vote encrypted with VQ_K1 quantum key</p>
                <p>• Scantegrity confirmation codes</p>
                <p>• Ballot pool randomization</p>
                <p>• Quantum-secured transmission</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Bulletin Board
            st.markdown("#### Public Bulletin Board")
            st.markdown("""
            <div class="bulletin-board">
                <h5>📋 Published Vote Records</h5>
            """, unsafe_allow_html=True)
            
            for record in st.session_state.bulletin_board[-5:]:  # Show last 5 records
                st.markdown(f"**Ballot:** {record['ballot_id']}<br>**Encrypted:** {record['encrypted_vote'][:16]}...<br>**Time:** {record['timestamp']}<br>---")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        st.warning("Please complete election day authentication first.")

# Phase 5: Results & Verification
elif st.session_state.current_phase == 'results':
    st.markdown("## Phase 5: Election Results & Verification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Election Results")
        
        if st.session_state.cast_votes:
            # Tally votes
            vote_counts = {}
            for vote_record in st.session_state.cast_votes:
                for position, candidate in vote_record['votes'].items():
                    if position not in vote_counts:
                        vote_counts[position] = {}
                    if candidate not in vote_counts[position]:
                        vote_counts[position][candidate] = 0
                    vote_counts[position][candidate] += 1
            
            # Display results
            for position, candidates in vote_counts.items():
                st.markdown(f"#### {position}")
                total_votes = sum(candidates.values())
                
                for candidate, count in candidates.items():
                    percentage = (count / total_votes) * 100 if total_votes > 0 else 0
                    st.markdown(f"**{candidate}:** {count} votes ({percentage:.1f}%)")
                    st.progress(percentage / 100)
                
                # Winner
                if candidates:
                    winner = max(candidates.items(), key=lambda x: x[1])
                    st.success(f"🏆 Winner: {winner[0]} with {winner[1]} votes")
            
            st.markdown(f"**Total Votes Cast:** {len(st.session_state.cast_votes)}")
        else:
            st.info("No votes have been cast yet.")
    
    with col2:
        st.markdown("### Verification Tools")
        
        # Confirmation code verification
        st.markdown("#### Verify Your Vote")
        confirmation_input = st.text_input("Enter your confirmation code:")
        
        if st.button("Verify Confirmation Code"):
            if confirmation_input:
                # Check if confirmation code exists
                matching_vote = None
                for vote_record in st.session_state.cast_votes:
                    if vote_record['confirmation_code'] == confirmation_input:
                        matching_vote = vote_record
                        break
                
                if matching_vote:
                    st.success("✅ Confirmation code verified!")
                    st.info(f"Vote cast at: {matching_vote['timestamp']}")
                    st.info(f"Ballot ID: {matching_vote['ballot_id']}")
                else:
                    st.error("❌ Confirmation code not found")
            else:
                st.warning("Please enter a confirmation code")
        
        # Bulletin board verification
        st.markdown("#### Public Bulletin Board")
        st.markdown("""
        <div class="bulletin-board">
            <h5>📋 All Published Records</h5>
        """, unsafe_allow_html=True)
        
        for i, record in enumerate(st.session_state.bulletin_board):
            st.markdown(f"**Record {i+1}:**")
            st.markdown(f"Ballot: {record['ballot_id']}")
            st.markdown(f"Encrypted: {record['encrypted_vote']}")
            st.markdown(f"Time: {record['timestamp']}")
            st.markdown("---")
        
        st.markdown("</div>", unsafe_allow_html=True)

# System footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Registered Voters", len(st.session_state.voters_db))

with col2:
    device_registered = sum(1 for v in st.session_state.voters_db.values() if v['device_registered'])
    st.metric("Devices Registered", device_registered)

with col3:
    st.metric("Votes Cast", len(st.session_state.cast_votes))

with col4:
    ballots_used = sum(1 for b in st.session_state.ballots_pool if b['used'] or b['spoiled'])
    st.metric("Ballots Used", ballots_used)

st.markdown("---")
st.markdown("**🔬 Quantegrity E-Voting System** - Quantum-Enhanced Secure Electronic Voting")
st.markdown("*Powered by SEDJO QKD Protocol, Scantegrity Confirmation Codes, and Quantum Random Number Generation*")
