"""
Quantegrity Voter Portal - Enhanced Implementation
Proper demonstration of quantum processes following the research paper
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
import json

from quantum_core import (
    xor_decrypt, xor_encrypt, perform_authentication_crypto, 
    perform_voting_crypto, get_quantum_log, clear_quantum_log,
    simulate_quantum_process_visualization, log_quantum_operation
)
from shared_state import (
    shared_state, BulletinEntry
)

# Page configuration
st.set_page_config(
    page_title="Quantegrity Voter Portal",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_voter' not in st.session_state:
    st.session_state.current_voter = None
if 'voting_step' not in st.session_state:
    st.session_state.voting_step = 'login'
if 'crypto_session' not in st.session_state:
    st.session_state.crypto_session = None
if 'show_crypto_demo' not in st.session_state:
    st.session_state.show_crypto_demo = True
if 'current_ballot' not in st.session_state:
    st.session_state.current_ballot = None

# Custom CSS with quantum theme
st.markdown("""
<style>
    .voter-header {
        font-size: 3rem;
        text-align: center;
        color: #2E8B57;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FF6347;
        margin: 1rem 0;
        border-left: 4px solid #FF6347;
        padding-left: 1rem;
    }
    .crypto-demo-box {
        background: linear-gradient(135deg, #4169E1 0%, #8A2BE2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        border: 2px solid #6a5acd;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    .success-box {
        background: linear-gradient(135deg, #32CD32 0%, #98FB98 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border-left: 5px solid #228b22;
    }
    .warning-box {
        background: linear-gradient(135deg, #FF4500 0%, #FFB6C1 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        margin: 1rem 0;
        border-left: 5px solid #ff6347;
    }
    .ballot-card {
        background: #F0F8FF;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #4169E1;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .quantum-key-display {
        font-family: 'Courier New', monospace;
        background: #2c3e50;
        color: #00ff41;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #00ff41;
        font-size: 0.9rem;
    }
    .process-step {
        background: #f8f9fa;
        padding: 1rem;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .crypto-operation {
        background: #e8f4f8;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 0.3rem 0;
        border: 1px solid #17a2b8;
    }
    .confirmation-code {
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        font-weight: bold;
        color: #8B0000;
        background: #FFFACD;
        padding: 0.8rem;
        border-radius: 8px;
        border: 2px solid #DAA520;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-indicator {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    .status-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .status-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .status-pending { background: #cce7ff; color: #004085; border: 1px solid #99d6ff; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="voter-header">🗳️ Quantegrity Voter Portal</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Secure Quantum-Enhanced Electronic Voting with Real-Time Process Demonstration</p>', unsafe_allow_html=True)

# Check if election is active
shared_state.refresh_data()
active_election = shared_state.get_active_election()
if not active_election:
    st.error("❌ No active election found. Please contact the Election Authority.")
    st.stop()

# Cryptographic Process Toggle
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.session_state.show_crypto_demo = st.checkbox(
        "🔬 Show Cryptographic Process Demonstration", 
        value=st.session_state.show_crypto_demo,
        help="Display real-time quantum operations and encryption/decryption processes"
    )

# Sidebar Navigation
st.sidebar.title("🔧 Voter Navigation")
page = st.sidebar.selectbox(
    "Select Action",
    ["🏠 Home", "🔐 Login", "📝 Device Registration", "🗳️ Voting", "🎫 Ballot Audit", "📋 Receipt Verification", "🔬 Crypto Demo", "ℹ️ Help"]
)

# Real-time Cryptographic Process Monitor
if st.session_state.show_crypto_demo and page not in ["🔬 Crypto Demo", "ℹ️ Help"]:
    with st.container():
        st.markdown("### 🔬 Real-Time Cryptographic Process Monitor")
        
        quantum_log = get_quantum_log()
        if quantum_log:
            latest_ops = quantum_log[-2:]  # Show last 2 operations
            
            for op in latest_ops:
                with st.expander(f"⚡ {op['operation']} - {datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Process:**")
                        if 'SEDJO' in op['operation']:
                            st.markdown("🌌 Quantum Key Exchange using entangled qubits")
                        elif 'QRNG' in op['operation']:
                            st.markdown("🎲 True random generation via quantum superposition")
                        elif 'Encryption' in op['operation']:
                            st.markdown("🔐 XOR encryption with quantum keys")
                        elif 'Decryption' in op['operation']:
                            st.markdown("🔓 XOR decryption with quantum keys")
                    
                    with col2:
                        st.markdown("**Quantum Properties:**")
                        if 'quantum_properties' in op:
                            props = op['quantum_properties']
                            st.write(f"Fidelity: {props['fidelity']:.3f}")
                            st.write(f"Coherence: {props['quantum_coherence']:.3f}")

# Home Page
if page == "🏠 Home":
    st.markdown('<h2 class="sub-header">Welcome to Quantegrity Voter Portal</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="crypto-demo-box">
            <h3>🌟 Your Quantum Voting Journey</h3>
            <ol>
                <li><strong>Login:</strong> Enter Voter ID, Biometric, and Q_K2</li>
                <li><strong>Device Registration:</strong> Verify device with encrypted OTP</li>
                <li><strong>Quantum Authentication:</strong> Decrypt Q_K1 and generate AQ_K1</li>
                <li><strong>Voting Session:</strong> Generate VQ_K1 and cast encrypted vote</li>
                <li><strong>Verification:</strong> Receive quantum-secured confirmation</li>
                <li><strong>Audit:</strong> Verify receipt on bulletin board</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-box">
            <h3>🔒 Quantum Security Features</h3>
            <ul>
                <li><strong>SEDJO Protocol:</strong> Quantum key distribution</li>
                <li><strong>Q_K1 Encryption:</strong> Biometric-secured primary key</li>
                <li><strong>Q_K2 Verification:</strong> Device authentication</li>
                <li><strong>AQ_K1 Generation:</strong> Authentication keys via SEDJO</li>
                <li><strong>VQ_K1 Session:</strong> Voting encryption keys</li>
                <li><strong>XOR Encryption:</strong> Quantum-safe vote protection</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Current Election Info
    st.markdown("### 🗳️ Current Election")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Election:** {active_election.name}")
        st.markdown(f"**Candidates:** {', '.join(active_election.candidates)}")
    with col2:
        st.markdown(f"**Status:** 🟢 Active")
        st.markdown(f"**Ballot Pool:** {active_election.ballot_pool_size} ballots")
    
    # Voter Status Overview
    st.markdown("### 📊 Your Current Status")
    
    current_voter = st.session_state.current_voter
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "✅ Logged In" if current_voter else "❌ Not Logged In"
        st.markdown(f'<div class="status-indicator status-{"success" if current_voter else "warning"}">{status}</div>', unsafe_allow_html=True)
    
    with col2:
        if current_voter:
            device_status = current_voter.device_status
            if device_status == "verified":
                status_class = "success"
                status_text = "✅ Device Verified"
            elif device_status in ["requested", "pending_verification"]:
                status_class = "pending"
                status_text = "⏳ Verification Pending"
            else:
                status_class = "warning"
                status_text = "❌ Not Verified"
        else:
            status_class = "warning"
            status_text = "❌ Not Verified"
        
        st.markdown(f'<div class="status-indicator status-{status_class}">{status_text}</div>', unsafe_allow_html=True)
    
    with col3:
        if current_voter:
            auth_status = current_voter.auth_status
            if auth_status == "authenticated":
                status_class = "success"
                status_text = "✅ Authenticated"
            elif auth_status in ["biometric_verified", "aq_k1_generated"]:
                status_class = "pending"
                status_text = "⏳ In Progress"
            else:
                status_class = "warning"
                status_text = "❌ Not Authenticated"
        else:
            status_class = "warning"
            status_text = "❌ Not Authenticated"
        
        st.markdown(f'<div class="status-indicator status-{status_class}">{status_text}</div>', unsafe_allow_html=True)
    
    with col4:
        if current_voter:
            vote_status = current_voter.vote_status
            if vote_status == "voted":
                status_class = "success"
                status_text = "✅ Vote Cast"
            elif vote_status == "spoiled":
                status_class = "warning"
                status_text = "🗑️ Ballot Spoiled"
            else:
                status_class = "pending"
                status_text = "⏳ Ready to Vote"
        else:
            status_class = "warning"
            status_text = "❌ Not Ready"
        
        st.markdown(f'<div class="status-indicator status-{status_class}">{status_text}</div>', unsafe_allow_html=True)
    
    # Quick actions based on status
    if current_voter:
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if current_voter.device_status != "verified":
                if st.button("📝 Register Device", use_container_width=True):
                    st.session_state.page = "📝 Device Registration"
                    st.rerun()
        
        with col2:
            if current_voter.device_status == "verified" and current_voter.auth_status != "authenticated":
                if st.button("🔐 Authenticate", use_container_width=True):
                    st.session_state.page = "🗳️ Voting"
                    st.rerun()
        
        with col3:
            if current_voter.auth_status == "authenticated" and current_voter.vote_status == "not_voted":
                if st.button("🗳️ Cast Vote", use_container_width=True):
                    st.session_state.page = "🗳️ Voting"
                    st.rerun()

# Login Page
elif page == "🔐 Login":
    st.markdown('<h2 class="sub-header">Voter Login with Quantum Credentials</h2>', unsafe_allow_html=True)
    
    if not st.session_state.current_voter:
        st.markdown("### 🆔 Enter Your Quantum Credentials")
        st.info("Please enter the credentials provided during registration. All fields must be 16-bit binary strings.")
        
        with st.form("voter_login"):
            col1, col2 = st.columns(2)
            
            with col1:
                voter_id = st.text_input(
                    "Voter ID (16-bit binary)", 
                    max_chars=16, 
                    help="16-character binary voter ID generated during registration"
                )
                biometric = st.text_input(
                    "Biometric Signature (16-bit binary)", 
                    max_chars=16, 
                    help="16-character binary biometric signature from registration"
                )
            
            with col2:
                q_k2 = st.text_input(
                    "Q_K2 Device Password (16-bit binary)", 
                    max_chars=16, 
                    help="16-character binary Q_K2 key for device registration"
                )
                
                # Show login demonstration
                if st.checkbox("🔬 Show Login Process"):
                    st.markdown("""
                    <div class="process-step">
                        <strong>Login Process:</strong><br>
                        1. Verify Voter ID exists in database<br>
                        2. Validate Biometric Signature<br>
                        3. Confirm Q_K2 matches stored value<br>
                        4. Grant access to voting system
                    </div>
                    """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔐 Login to Quantegrity")
            
            if submitted and voter_id and biometric and q_k2:
                # Validate input format
                if not all(c in '01' for c in voter_id + biometric + q_k2):
                    st.error("❌ All fields must be 16-bit binary strings (only 0s and 1s)")
                elif len(voter_id) != 16 or len(biometric) != 16 or len(q_k2) != 16:
                    st.error("❌ All fields must be exactly 16 characters long")
                else:
                    # Check voter credentials
                    voter = shared_state.get_voter(voter_id)
                    
                    if not voter:
                        st.error("❌ Voter ID not found. Please contact the Election Authority.")
                    elif voter.biometric_data.signature != biometric:
                        st.error("❌ Invalid biometric signature.")
                    elif voter.quantum_keys.q_k2 != q_k2:
                        st.error("❌ Invalid Q_K2 device password.")
                    else:
                        st.session_state.current_voter = voter
                        st.session_state.voting_step = 'logged_in'
                        
                        # Create cryptographic session
                        session_id = shared_state.create_crypto_session(voter_id)
                        st.session_state.crypto_session = session_id
                        
                        st.success(f"✅ Welcome, {voter.name}!")
                        
                        # Show credential verification process
                        if st.session_state.show_crypto_demo:
                            st.markdown("### 🔐 Credential Verification Process")
                            st.markdown(f"""
                            <div class="crypto-demo-box">
                                <h4>✅ Successful Authentication</h4>
                                <div class="process-step">
                                    <strong>Step 1:</strong> Voter ID Lookup<br>
                                    <code>Database[{voter_id}] → Found: {voter.name}</code>
                                </div>
                                <div class="process-step">
                                    <strong>Step 2:</strong> Biometric Verification<br>
                                    <code>Input: {biometric} ≟ Stored: {voter.biometric_data.signature} → ✅ Match</code>
                                </div>
                                <div class="process-step">
                                    <strong>Step 3:</strong> Q_K2 Validation<br>
                                    <code>Input: {q_k2} ≟ Stored: {voter.quantum_keys.q_k2} → ✅ Match</code>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.rerun()
    else:
        voter = st.session_state.current_voter
        st.markdown(f"""
        <div class="success-box">
            <h3>✅ Successfully Logged In</h3>
            <p><strong>Name:</strong> {voter.name}</p>
            <p><strong>Voter ID:</strong> {voter.voter_id}</p>
            <p><strong>Device Status:</strong> {voter.device_status.replace('_', ' ').title()}</p>
            <p><strong>Auth Status:</strong> {voter.auth_status.replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show quantum credentials
        if st.session_state.show_crypto_demo:
            with st.expander("🔑 View Quantum Credentials", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Your Quantum Keys:**")
                    st.markdown(f'<div class="quantum-key-display">Q_K1: {voter.quantum_keys.q_k1}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="quantum-key-display">Q_K2: {voter.quantum_keys.q_k2}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="quantum-key-display">Encrypted Q_K1: {voter.quantum_keys.encrypted_q_k1}</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Generated Keys (if available):**")
                    if voter.quantum_keys.aq_k1_alice:
                        st.markdown(f'<div class="quantum-key-display">AQ_K1: {voter.quantum_keys.aq_k1_alice}</div>', unsafe_allow_html=True)
                    if voter.quantum_keys.vq_k1_alice:
                        st.markdown(f'<div class="quantum-key-display">VQ_K1: {voter.quantum_keys.vq_k1_alice}</div>', unsafe_allow_html=True)
        
        if st.button("🔓 Logout", key="main_logout"):
            st.session_state.current_voter = None
            st.session_state.voting_step = 'login'
            st.session_state.crypto_session = None
            st.session_state.current_ballot = None
            st.rerun()

# Device Registration Page
elif page == "📝 Device Registration":
    st.markdown('<h2 class="sub-header">Device Registration with Q_K2 Encryption</h2>', unsafe_allow_html=True)
    
    if not st.session_state.current_voter:
        st.warning("⚠️ Please login first!")
        st.stop()
    
    voter = st.session_state.current_voter
    
    # Check current device status
    if voter.device_status == "not_requested":
        st.markdown("### 🔐 Register Your Device")
        st.info("Your device needs to be registered and verified with the Election Authority before you can vote.")
        
        # Simulate device fingerprinting
        device_fingerprint = f"DEV_{hash(str(datetime.now()))}"[-12:]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Voter Information:**")
            st.markdown(f"**Name:** {voter.name}")
            st.markdown(f"**Voter ID:** {voter.voter_id}")
            st.markdown(f"**Device Fingerprint:** `{device_fingerprint}`")
        
        with col2:
            st.markdown("**Registration Process:**")
            st.markdown("""
            1. Generate device fingerprint
            2. Send registration request to EA
            3. Wait for EA approval
            4. Receive encrypted OTP via Q_K2
            5. Decrypt and verify OTP
            """)
        
        if st.button("📝 Request Device Registration"):
            with st.spinner("Sending device registration request to Election Authority..."):
                # Send device registration request
                success = shared_state.request_device_verification(voter.voter_id, device_fingerprint)
                
                if success:
                    # Update session state with fresh voter data
                    updated_voter = shared_state.get_voter(voter.voter_id)
                    st.session_state.current_voter = updated_voter
                    
                    st.success("✅ Device registration request sent!")
                    st.info("📋 Your request has been submitted to the Election Authority. Please wait for approval.")
                    st.rerun()
                else:
                    st.error("❌ Failed to send device registration request. Please try again.")
    
    elif voter.device_status == "requested":
        st.markdown("### ⏳ Waiting for Election Authority Approval")
        st.info("""
        📋 Your device registration request has been submitted to the Election Authority.
        
        **Status:** Pending Approval
        
        **Next Steps:**
        1. Wait for the Election Authority to review your request
        2. Once approved, you will receive an encrypted OTP
        3. Decrypt the OTP using your Q_K2 key
        4. Enter the decrypted OTP to complete verification
        """)
        
        st.markdown(f"**Request Time:** {voter.device_info.registration_time[:19] if voter.device_info.registration_time else 'Unknown'}")
        st.markdown(f"**Device Fingerprint:** `{voter.device_info.device_fingerprint}`")
        
        # Check if approval has been processed (encrypted OTP available)
        if st.button("🔄 Check Approval Status", key="check_approval"):
            with st.spinner("Checking approval status..."):
                # Refresh voter data to check for updates
                updated_voter = shared_state.get_voter(voter.voter_id)
                if updated_voter:
                    st.session_state.current_voter = updated_voter
                    
                    if updated_voter.device_status == "pending_verification" and updated_voter.device_info.encrypted_otp:
                        st.success("✅ Your device registration has been approved!")
                        st.info("🔐 You have received an encrypted OTP. Use your Q_K2 to decrypt it.")
                        st.rerun()
                    else:
                        st.info("⏳ Still waiting for Election Authority approval.")
    
    elif voter.device_status == "pending_verification":
        st.markdown("### 🔐 Device Verification with Q_K2 Decryption")
        st.success("✅ Your request has been approved! Decrypt the OTP using your Q_K2 key.")
        
        # Show encrypted OTP and decryption process
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Received from Election Authority:**")
            encrypted_otp = voter.device_info.encrypted_otp
            st.markdown(f'<div class="quantum-key-display">Encrypted OTP: {encrypted_otp}</div>', unsafe_allow_html=True)
            
            st.markdown("**Your Q_K2 Key:**")
            st.markdown(f'<div class="quantum-key-display">Q_K2: {voter.quantum_keys.q_k2}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Decryption Process:**")
            if encrypted_otp and voter.quantum_keys.q_k2:
                decrypted_otp = xor_decrypt(encrypted_otp, voter.quantum_keys.q_k2)
                
                st.markdown(f"""
                <div class="crypto-demo-box">
                    <h4>🔓 XOR Decryption Process</h4>
                    <div class="process-step">
                        <strong>Formula:</strong> Encrypted_OTP ⊕ Q_K2 = OTP<br>
                        <strong>Calculation:</strong> {encrypted_otp} ⊕ {voter.quantum_keys.q_k2}<br>
                        <strong>Result:</strong> {decrypted_otp}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption("Use the decrypted OTP above for device verification")
        
        with st.form("otp_verification"):
            otp_input = st.text_input(
                "Enter Decrypted OTP (16-bit binary)", 
                max_chars=16,
                help="16-character binary OTP after decryption with Q_K2"
            )
            
            submitted = st.form_submit_button("🔓 Verify Device")
            
            if submitted and otp_input:
                if not all(c in '01' for c in otp_input) or len(otp_input) != 16:
                    st.error("❌ OTP must be exactly 16 binary digits (0s and 1s)")
                else:
                    # Verify OTP
                    success = shared_state.verify_device_with_otp(voter.voter_id, otp_input)
                    
                    if success:
                        updated_voter = shared_state.get_voter(voter.voter_id)
                        st.session_state.current_voter = updated_voter
                        
                        st.success("✅ Device verified successfully!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid OTP. Please check your decryption process.")
    
    elif voter.device_status == "verified":
        st.markdown("""
        <div class="success-box">
            <h3>✅ Device Successfully Verified</h3>
            <p>Your device is registered and verified for quantum-secured voting. You can now proceed to authenticate and cast your vote.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Verification Time:** {voter.device_info.registration_time[:19] if voter.device_info.registration_time else 'Unknown'}")
            st.markdown(f"**Device Status:** ✅ Verified")
        with col2:
            st.markdown(f"**Device Fingerprint:** `{voter.device_info.device_fingerprint}`")
            st.markdown(f"**OTP Used:** `{voter.device_info.verification_otp if voter.device_info.verification_otp else 'N/A'}`")
        
        if st.button("🗳️ Proceed to Voting", key="proceed_voting"):
            st.session_state.page = "🗳️ Voting"
            st.rerun()
    
    else:
        # Handle any unexpected states
        st.warning("⚠️ Unexpected device status. Please contact technical support.")
        st.markdown(f"**Current Status:** {voter.device_status}")
        
        if st.button("🔄 Reset Device Registration", key="reset_device"):
            voter.device_status = "not_requested"
            voter.device_info.registration_time = ""
            voter.device_info.encrypted_otp = ""
            voter.device_info.verification_otp = ""
            shared_state.update_voter(voter)
            st.session_state.current_voter = voter
            st.rerun()

# Voting Page
elif page == "🗳️ Voting":
    st.markdown('<h2 class="sub-header">Quantum-Secured Voting Process</h2>', unsafe_allow_html=True)
    
    if not st.session_state.current_voter:
        st.warning("⚠️ Please login first!")
        st.stop()
    
    voter = st.session_state.current_voter
    
    if voter.device_status != "verified":
        st.warning("⚠️ Please register and verify your device first!")
        if st.button("📝 Go to Device Registration"):
            st.session_state.page = "📝 Device Registration"
            st.rerun()
        st.stop()
    
    if voter.vote_status == "voted":
        st.info("✅ You have already cast your vote!")
        
        # Show receipt if available
        if voter.vote_receipt:
            st.markdown("### 🧾 Your Vote Receipt")
            receipt_entry = shared_state.get_bulletin_entry(voter.vote_receipt)
            if receipt_entry:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Receipt ID:** `{receipt_entry.entry_id}`")
                    st.markdown(f"**Ballot ID:** `{receipt_entry.ballot_id}`")
                with col2:
                    st.markdown(f"**Timestamp:** {receipt_entry.timestamp[:19]}")
                    st.markdown(f"**Confirmation Codes:** `{', '.join(receipt_entry.confirmation_codes)}`")
        st.stop()
    
    # Voting workflow with proper quantum processes
    if voter.auth_status == "not_authenticated":
        st.markdown("### 🔐 Quantum Authentication Process")
        st.info("Perform biometric verification and quantum key exchange for secure voting session.")
        
        # Step 1: Biometric authentication
        with st.form("biometric_auth"):
            st.markdown("**Step 1: Biometric Authentication**")
            biometric_input = st.text_input(
                "Scan Biometric Signature (16-bit binary)", 
                max_chars=16,
                help="Enter your 16-bit biometric signature to decrypt Q_K1"
            )
            
            if st.session_state.show_crypto_demo:
                st.markdown("""
                <div class="process-step">
                    <strong>Authentication Process:</strong><br>
                    1. Verify biometric signature<br>
                    2. Decrypt Q_K1 using biometric: Encrypted_Q_K1 ⊕ Biometric<br>
                    3. Generate AQ_K1 using SEDJO(Q_K1, Q_K1)<br>
                    4. Encrypt authentication OTP with AQ_K1
                </div>
                """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔓 Authenticate with Biometric")
            
            if submitted and biometric_input:
                if not all(c in '01' for c in biometric_input) or len(biometric_input) != 16:
                    st.error("❌ Biometric signature must be exactly 16 binary digits")
                else:
                    # Perform biometric authentication
                    success, decrypted_q_k1, alice_aq_k1, bob_aq_k1 = shared_state.perform_biometric_authentication(
                        voter.voter_id, biometric_input
                    )
                    
                    if success:
                        # Update session voter
                        updated_voter = shared_state.get_voter(voter.voter_id)
                        st.session_state.current_voter = updated_voter
                        
                        st.success("✅ Biometric authentication successful!")
                        
                        # Show cryptographic process
                        if st.session_state.show_crypto_demo:
                            st.markdown("### 🔐 Quantum Authentication Process")
                            st.markdown(f"""
                            <div class="crypto-demo-box">
                                <h4>🌌 Quantum Key Operations</h4>
                                <div class="process-step">
                                    <strong>Step 1:</strong> Q_K1 Decryption<br>
                                    <code>Encrypted_Q_K1 ⊕ Biometric = Q_K1</code><br>
                                    <code>{voter.quantum_keys.encrypted_q_k1} ⊕ {biometric_input} = {decrypted_q_k1}</code>
                                </div>
                                <div class="process-step">
                                    <strong>Step 2:</strong> AQ_K1 Generation via SEDJO<br>
                                    <code>SEDJO(Q_K1, Q_K1) → AQ_K1</code><br>
                                    <code>Alice AQ_K1: {alice_aq_k1}</code><br>
                                    <code>Bob AQ_K1: {bob_aq_k1}</code>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.rerun()
                    else:
                        st.error("❌ Invalid biometric signature. Authentication failed.")
    
    elif voter.auth_status == "aq_k1_generated":
        st.markdown("### 🔑 Authentication OTP Verification")
        st.info("Generate and verify authentication OTP encrypted with AQ_K1 (different from device verification).")
        
        # Generate NEW authentication OTP (separate from device verification)
        if not hasattr(voter, 'auth_encrypted_otp') or not voter.auth_encrypted_otp:
            if st.button("🔐 Generate Authentication OTP"):
                success, otp, encrypted_otp = shared_state.generate_auth_otp(voter.voter_id)
                
                if success:
                    updated_voter = shared_state.get_voter(voter.voter_id)
                    st.session_state.current_voter = updated_voter
                    st.rerun()
                else:
                    st.error("❌ Failed to generate authentication OTP. Please try again.")
        else:
            # Show AUTHENTICATION OTP decryption process (NOT device verification OTP)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Received Encrypted Authentication OTP:**")
                encrypted_otp = voter.auth_encrypted_otp  # Use AUTH OTP, not device OTP
                st.markdown(f'<div class="quantum-key-display">Encrypted Auth OTP: {encrypted_otp}</div>', unsafe_allow_html=True)
                
                st.markdown("**Your AQ_K1 Key:**")
                st.markdown(f'<div class="quantum-key-display">AQ_K1: {voter.quantum_keys.aq_k1_alice}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Decryption Process:**")
                if encrypted_otp and voter.quantum_keys.aq_k1_alice:
                    decrypted_otp = xor_decrypt(encrypted_otp, voter.quantum_keys.aq_k1_alice)
                    
                    st.markdown(f"""
                    <div class="crypto-demo-box">
                        <h4>🔓 AQ_K1 Authentication Decryption</h4>
                        <div class="process-step">
                            <strong>Formula:</strong> Encrypted_Auth_OTP ⊕ AQ_K1 = Auth_OTP<br>
                            <strong>Calculation:</strong> {encrypted_otp} ⊕ {voter.quantum_keys.aq_k1_alice}<br>
                            <strong>Result:</strong> {decrypted_otp}
                        </div>
                        <div class="process-step">
                            <strong>Note:</strong> This is a NEW OTP for authentication,<br>
                            different from the device verification OTP that used Q_K2.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🔄 Process Summary")
            st.markdown("""
            **Two Different OTP Processes:**
            1. **Device Verification OTP**: Uses Q_K2 (already completed)
            2. **Authentication OTP**: Uses AQ_K1 (current step)
            
            These are separate security steps with different keys and different OTPs.
            """)
            
            with st.form("auth_otp_verification"):
                auth_otp_input = st.text_input(
                    "Enter Decrypted Authentication OTP (16-bit binary)", 
                    max_chars=16,
                    help="Enter the AUTHENTICATION OTP after decrypting with AQ_K1"
                )
                
                submitted = st.form_submit_button("🔓 Verify Authentication")
                
                if submitted and auth_otp_input:
                    if not all(c in '01' for c in auth_otp_input) or len(auth_otp_input) != 16:
                        st.error("❌ Authentication OTP must be exactly 16 binary digits")
                    else:
                        success = shared_state.verify_auth_otp(voter.voter_id, auth_otp_input)
                        
                        if success:
                            updated_voter = shared_state.get_voter(voter.voter_id)
                            st.session_state.current_voter = updated_voter
                            
                            st.success("✅ Authentication complete! You can now cast your vote.")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid authentication OTP.")

    elif voter.auth_status == "authenticated":
        st.markdown("### 🗳️ Quantum-Secured Voting Session")
        
        # Initialize voting session and generate VQ_K1
        if not voter.quantum_keys.vq_k1_alice:
            if st.button("🚀 Start Voting Session"):
                with st.spinner("Generating voting session keys using SEDJO..."):
                    success, alice_vq_k1, bob_vq_k1 = shared_state.initiate_voting_session(voter.voter_id)
                    
                    if success:
                        updated_voter = shared_state.get_voter(voter.voter_id)
                        st.session_state.current_voter = updated_voter
                        
                        # Show VQ_K1 generation process
                        if st.session_state.show_crypto_demo:
                            st.markdown("### 🌌 VQ_K1 Generation via SEDJO")
                            st.markdown(f"""
                            <div class="crypto-demo-box">
                                <h4>⚡ Voting Key Generation</h4>
                                <div class="process-step">
                                    <strong>Process:</strong> SEDJO(AQ_K1, AQ_K1) → VQ_K1<br>
                                    <strong>Input:</strong> AQ_K1 = {voter.quantum_keys.aq_k1_alice}<br>
                                    <strong>Output:</strong> VQ_K1 = {alice_vq_k1}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.rerun()
        
        else:
            # Request ballot if not already allocated
            if not st.session_state.current_ballot:
                if st.button("📄 Request Quantum-Secured Ballot"):
                    with st.spinner("Allocating ballot from quantum-secured pool..."):
                        ballot = shared_state.allocate_ballot_from_pool(voter.voter_id, active_election.election_id)
                        
                        if ballot:
                            st.session_state.current_ballot = ballot
                            st.success("✅ Ballot allocated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ No ballots available. Please contact Election Authority.")
            
            else:
                # Display ballot and voting interface
                ballot = st.session_state.current_ballot
                
                st.markdown(f"""
                <div class="ballot-card">
                    <h3>🗳️ Official Quantum-Secured Ballot</h3>
                    <p><strong>Ballot ID:</strong> {ballot.ballot_id}</p>
                    <p><strong>Election:</strong> {active_election.name}</p>
                    <p><strong>VQ_K1 Session Key:</strong> <code>{voter.quantum_keys.vq_k1_alice}</code></p>
                    <p><em>Select one candidate below:</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show confirmation codes if crypto demo is enabled
                if st.session_state.show_crypto_demo:
                    with st.expander("🔍 View Ballot Confirmation Codes (Demo)", expanded=False):
                        st.markdown("**Confirmation Codes for this Ballot:**")
                        for candidate, code in ballot.confirmation_codes.items():
                            st.markdown(f'<div class="quantum-key-display">{candidate}: {code}</div>', unsafe_allow_html=True)
                        st.caption("⚠️ In a real election, these codes would only be revealed upon voting or spoiling")
                
                # FIXED: Voting Form with buttons outside
                with st.form("voting_form"):
                    st.markdown("### 👥 Select Your Candidate")
                    
                    selected_candidate = st.radio(
                        "Candidates:",
                        active_election.candidates,
                        format_func=lambda x: f"🗳️ {x}"
                    )
                    
                    # Form submission buttons
                    vote_submitted = st.form_submit_button("✅ Cast Vote", type="primary")
                    spoil_submitted = st.form_submit_button("🗑️ Spoil Ballot")
                
                # Handle form submissions OUTSIDE the form
                if vote_submitted and selected_candidate:
                    with st.spinner("Casting your quantum-secured vote..."):
                        # Cast the vote with proper encryption
                        success, confirmation_code, encrypted_confirmation = shared_state.cast_encrypted_vote(
                            voter.voter_id, ballot.ballot_id, selected_candidate
                        )
                        
                        if success:
                            # Update session voter
                            updated_voter = shared_state.get_voter(voter.voter_id)
                            st.session_state.current_voter = updated_voter
                            
                            # Create bulletin board entry
                            entry_id = str(uuid.uuid4())[:8]
                            bulletin_entry = BulletinEntry(
                                entry_id=entry_id,
                                ballot_id=ballot.ballot_id,
                                confirmation_codes=[confirmation_code],
                                entry_type="vote",
                                timestamp=datetime.now().isoformat(),
                                signature=f"quantum_sig_{entry_id}",
                                quantum_proof=f"SEDJO_proof_{entry_id}"
                            )
                            
                            shared_state.add_bulletin_entry(bulletin_entry)
                            
                            # Update voter with receipt
                            updated_voter.vote_receipt = entry_id
                            shared_state.update_voter(updated_voter)
                            st.session_state.current_voter = updated_voter
                            
                            st.success(f"✅ Vote cast successfully for {selected_candidate}!")
                            st.balloons()
                            
                            # Show vote encryption process
                            if st.session_state.show_crypto_demo:
                                st.markdown("### 🔐 Vote Encryption Process")
                                st.markdown(f"""
                                <div class="crypto-demo-box">
                                    <h4>🗳️ Quantum Vote Encryption</h4>
                                    <div class="process-step">
                                        <strong>Step 1:</strong> Convert Candidate to Binary<br>
                                        <code>Candidate: {selected_candidate} → Binary Format</code>
                                    </div>
                                    <div class="process-step">
                                        <strong>Step 2:</strong> Encrypt with VQ_K1<br>
                                        <code>Vote_Binary ⊕ VQ_K1 = Encrypted_Vote</code>
                                    </div>
                                    <div class="process-step">
                                        <strong>Step 3:</strong> Generate Confirmation<br>
                                        <code>Confirmation Code: {confirmation_code}</code>
                                    </div>
                                    <div class="process-step">
                                        <strong>Step 4:</strong> Publish to Bulletin Board<br>
                                        <code>Entry ID: {entry_id}</code>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Show receipt details
                            st.markdown("### 🧾 Your Quantum Vote Receipt")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Receipt ID:** `{entry_id}`")
                                st.markdown(f"**Ballot ID:** `{ballot.ballot_id}`")
                            with col2:
                                st.markdown(f"**Timestamp:** {bulletin_entry.timestamp[:19]}")
                                st.markdown(f"""
                                <div class="confirmation-code">
                                    Confirmation Code: {confirmation_code}
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.info("💡 Save your confirmation code! You can use it to verify your vote on the bulletin board.")
                            
                            # Reset ballot
                            st.session_state.current_ballot = None

                elif spoil_submitted:
                    with st.spinner("Spoiling ballot and revealing all codes..."):
                        # Spoil the ballot
                        success, all_codes = shared_state.spoil_ballot(voter.voter_id, ballot.ballot_id)
                        
                        if success:
                            # Update session voter
                            updated_voter = shared_state.get_voter(voter.voter_id)
                            st.session_state.current_voter = updated_voter
                            
                            # Create bulletin board entry for spoiled ballot
                            entry_id = str(uuid.uuid4())[:8]
                            all_codes_list = list(all_codes.values())
                            
                            bulletin_entry = BulletinEntry(
                                entry_id=entry_id,
                                ballot_id=ballot.ballot_id,
                                confirmation_codes=all_codes_list,
                                entry_type="spoiled",
                                timestamp=datetime.now().isoformat(),
                                signature=f"spoiled_sig_{entry_id}",
                                quantum_proof=f"SPOIL_proof_{entry_id}"
                            )
                            
                            shared_state.add_bulletin_entry(bulletin_entry)
                            
                            # Update voter with receipt
                            updated_voter.vote_receipt = entry_id
                            shared_state.update_voter(updated_voter)
                            st.session_state.current_voter = updated_voter
                            
                            st.warning("🗑️ Ballot Spoiled - All confirmation codes revealed:")
                            
                            # Show ballot information in a clear format
                            st.markdown("### 📋 Spoiled Ballot Information")
                            for candidate, code in all_codes.items():
                                st.markdown(f"""
                                <div style="display: flex; justify-content: space-between; padding: 0.5rem; 
                                    margin: 0.2rem 0; background: #FFE4E1; border-radius: 5px; border-left: 4px solid #FF6347;">
                                    <strong>🗳️ {candidate}</strong>
                                    <code style="background: #FFFACD; padding: 0.2rem 0.5rem; border-radius: 3px;">{code}</code>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("""
                            ### ✅ Ballot Spoiled Successfully
                            - All confirmation codes have been revealed for transparency
                            - This ballot cannot be used for voting
                            - The spoiled ballot is recorded on the quantum bulletin board
                            - You may request a new ballot to continue voting
                            """)
                            
                            st.session_state.current_ballot = None
                            
                            # FIXED: Button outside form - using session state to trigger action
                            st.session_state.show_new_ballot_button = True

                # FIXED: New ballot request button outside form
                if hasattr(st.session_state, 'show_new_ballot_button') and st.session_state.show_new_ballot_button:
                    if st.button("📋 Request New Ballot", key="request_new_after_spoil"):
                        st.session_state.current_ballot = None
                        st.session_state.show_new_ballot_button = False
                        st.info("✅ Ready to request a new ballot!")
                        st.rerun()

# Ballot Audit Page
elif page == "🎫 Ballot Audit":
    st.markdown('<h2 class="sub-header">Quantum Ballot Audit</h2>', unsafe_allow_html=True)
    
    if not st.session_state.current_voter:
        st.warning("⚠️ Please login first!")
        st.stop()
    
    voter = st.session_state.current_voter
    
    if voter.device_status != "verified":
        st.warning("⚠️ Please register and verify your device first!")
        st.stop()
    
    st.markdown("### 🔍 Audit Your Ballot")
    st.info("""
    Ballot auditing allows you to verify the integrity of the quantum voting system without casting an actual vote. 
    When you audit a ballot, all confirmation codes are revealed, demonstrating the quantum security mechanisms.
    """)
    
    if st.button("🔍 Request Quantum Audit Ballot"):
        with st.spinner("Generating quantum audit ballot..."):
            # Allocate audit ballot from pool
            audit_ballot = shared_state.allocate_ballot_from_pool(voter.voter_id, active_election.election_id)
            
            if audit_ballot:
                # Immediately spoil for audit purposes
                success, all_codes = shared_state.spoil_ballot(voter.voter_id, audit_ballot.ballot_id)
                
                if success:
                    st.success("✅ Quantum audit ballot generated!")
                    
                    st.markdown(f"""
                    <div class="ballot-card">
                        <h3>🔍 Quantum Audit Ballot Results</h3>
                        <p><strong>Ballot ID:</strong> {audit_ballot.ballot_id}</p>
                        <p><strong>Status:</strong> Audited (Not counted in election)</p>
                        <p><strong>Quantum Security:</strong> Full transparency mode</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 📋 Revealed Quantum Confirmation Codes")
                    
                    for candidate, code in all_codes.items():
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; padding: 0.5rem; 
                             margin: 0.2rem 0; background: #F0F8FF; border-radius: 5px; border-left: 4px solid #4169E1;">
                            <strong>{candidate}</strong>
                            <code style="background: #FFFACD; padding: 0.2rem 0.5rem; border-radius: 3px;">{code}</code>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    ### ✅ Quantum Audit Complete
                    This audit confirms that:
                    - Each candidate has a unique quantum-generated confirmation code
                    - The codes are generated using true quantum randomness (QRNG)
                    - The system correctly associates codes with candidates
                    - Your vote would be properly encrypted with VQ_K1 keys
                    - The quantum bulletin board maintains cryptographic integrity
                    """)
                    
                    # Show quantum verification process
                    if st.session_state.show_crypto_demo:
                        st.markdown("### 🌌 Quantum Verification Process")
                        quantum_props = simulate_quantum_process_visualization()
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Quantum Fidelity", f"{quantum_props['fidelity']:.4f}")
                        with col2:
                            st.metric("Entanglement", f"{quantum_props['entanglement_strength']:.4f}")
                        with col3:
                            st.metric("Coherence", f"{quantum_props['quantum_coherence']:.4f}")
            else:
                st.error("❌ No audit ballots available. Please contact Election Authority.")

# Receipt Verification Page
elif page == "📋 Receipt Verification":
    st.markdown('<h2 class="sub-header">Quantum Receipt Verification</h2>', unsafe_allow_html=True)
    
    st.markdown("### 🔍 Verify Your Vote Receipt on Quantum Bulletin Board")
    st.info("Enter your receipt ID to verify that your vote was properly recorded on the quantum-secured bulletin board.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        receipt_id = st.text_input("Receipt ID", placeholder="Enter your receipt ID")
        
        if st.button("🔍 Verify Receipt"):
            if receipt_id:
                with st.spinner("Verifying receipt on quantum bulletin board..."):
                    receipt_entry = shared_state.get_bulletin_entry(receipt_id)
                    
                    if receipt_entry:
                        st.success("✅ Receipt verified successfully on quantum bulletin board!")
                        
                        st.markdown("### 📋 Verified Receipt Details")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Receipt ID:** `{receipt_entry.entry_id}`")
                            st.markdown(f"**Ballot ID:** `{receipt_entry.ballot_id}`")
                            st.markdown(f"**Type:** {receipt_entry.entry_type.title()}")
                        with col2:
                            st.markdown(f"**Confirmation Codes:** `{', '.join(receipt_entry.confirmation_codes)}`")
                            st.markdown(f"**Timestamp:** {receipt_entry.timestamp[:19]}")
                            st.markdown(f"**Quantum Proof:** `{receipt_entry.quantum_proof}`")
                        
                        st.markdown("""
                        <div class="success-box">
                            <h4>🔒 Your Vote is Quantum-Secured</h4>
                            <p>Your vote has been successfully verified on the quantum-secured bulletin board. 
                            The confirmation code and quantum cryptographic proof ensure your vote was recorded 
                            correctly while maintaining your privacy through quantum anonymization.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show quantum verification details
                        if st.session_state.show_crypto_demo:
                            st.markdown("### 🌌 Quantum Verification Details")
                            st.markdown(f"""
                            <div class="crypto-demo-box">
                                <h4>🔬 Cryptographic Verification</h4>
                                <div class="process-step">
                                    <strong>Bulletin Board Entry:</strong> Found and verified<br>
                                    <strong>Quantum Signature:</strong> {receipt_entry.signature}<br>
                                    <strong>Cryptographic Proof:</strong> {receipt_entry.quantum_proof}<br>
                                    <strong>Integrity Status:</strong> ✅ Verified
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Receipt not found or verification failed.")
            else:
                st.warning("Please enter a receipt ID.")
    
    with col2:
        st.markdown("### 📊 Bulletin Board Statistics")
        bulletin_entries = shared_state.get_all_bulletin_entries()
        
        if bulletin_entries:
            vote_entries = len([e for e in bulletin_entries if e.entry_type == "vote"])
            spoiled_entries = len([e for e in bulletin_entries if e.entry_type == "spoiled"])
            
            st.metric("Total Entries", len(bulletin_entries))
            st.metric("Vote Entries", vote_entries)
            st.metric("Spoiled Entries", spoiled_entries)
            
            # Show recent entries
            st.markdown("**Recent Bulletin Entries:**")
            for entry in bulletin_entries[-3:]:
                entry_type_icon = "🗳️" if entry.entry_type == "vote" else "🗑️"
                st.write(f"{entry_type_icon} {entry.entry_id} - {entry.timestamp[:16]}")
        else:
            st.info("No entries on bulletin board yet.")
    
    # Show current receipt if available
    if st.session_state.current_voter and st.session_state.current_voter.vote_receipt:
        st.markdown("---")
        st.markdown("### 🧾 Your Current Receipt")
        
        voter = st.session_state.current_voter
        receipt_entry = shared_state.get_bulletin_entry(voter.vote_receipt)
        
        if receipt_entry:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Receipt ID", receipt_entry.entry_id)
            with col2:
                st.metric("Confirmation Codes", len(receipt_entry.confirmation_codes))
            with col3:
                st.metric("Vote Time", receipt_entry.timestamp[:10])
            
            if st.button("🔍 Verify My Receipt"):
                # Auto-fill and verify current receipt
                st.session_state.auto_verify_receipt = receipt_entry.entry_id
                st.rerun()

# Crypto Demo Page
elif page == "🔬 Crypto Demo":
    st.markdown('<h2 class="sub-header">Interactive Quantum Cryptography Demonstration</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="crypto-demo-box">
        <h3>🌌 Welcome to the Quantegrity Cryptographic Demonstration</h3>
        <p>This interactive demonstration shows the quantum cryptographic processes used in the Quantegrity 
        e-voting system from the voter's perspective. Experience the power of quantum security!</p>
    </div>
    """, unsafe_allow_html=True)
    
    demo_tab1, demo_tab2, demo_tab3, demo_tab4 = st.tabs([
        "🔐 XOR Encryption", "🌌 Key Decryption", "📊 Your Quantum Log", "🔑 Key Chain Demo"
    ])
    
    with demo_tab1:
        st.markdown("### 🔐 XOR Encryption/Decryption Demo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔒 Encrypt Data")
            plaintext = st.text_input("Data (16-bit binary)", value="1101001111010011", max_chars=16)
            key = st.text_input("Key (16-bit binary)", value="1011101110111011", max_chars=16)
            
            if st.button("🔐 Encrypt"):
                if plaintext and key and all(c in '01' for c in plaintext + key):
                    encrypted = xor_encrypt(plaintext, key)
                    st.session_state.demo_encrypted = encrypted
                    st.session_state.demo_key = key
                    
                    st.markdown(f"""
                    <div class="process-step">
                        <strong>Encryption:</strong> {plaintext} ⊕ {key} = {encrypted}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🔓 Decrypt Data")
            if hasattr(st.session_state, 'demo_encrypted'):
                ciphertext = st.text_input("Encrypted Data", value=st.session_state.demo_encrypted, disabled=True)
                decrypt_key = st.text_input("Decryption Key", value=st.session_state.demo_key)
                
                if st.button("🔓 Decrypt"):
                    decrypted = xor_decrypt(ciphertext, decrypt_key)
                    st.markdown(f"""
                    <div class="process-step">
                        <strong>Decryption:</strong> {ciphertext} ⊕ {decrypt_key} = {decrypted}
                    </div>
                    """, unsafe_allow_html=True)
    
    with demo_tab2:
        st.markdown("### 🌌 Quantum Key Decryption Demo")
        
        if st.session_state.current_voter:
            voter = st.session_state.current_voter
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔐 Q_K1 Decryption")
                st.markdown(f'<div class="quantum-key-display">Encrypted Q_K1: {voter.quantum_keys.encrypted_q_k1}</div>', unsafe_allow_html=True)
                
                bio_input = st.text_input("Biometric Signature", value=voter.biometric_data.signature)
                
                if st.button("🔓 Decrypt Q_K1"):
                    decrypted_q_k1 = xor_decrypt(voter.quantum_keys.encrypted_q_k1, bio_input)
                    st.markdown(f'<div class="quantum-key-display">Decrypted Q_K1: {decrypted_q_k1}</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🔑 OTP Decryption")
                if voter.device_info.encrypted_otp:
                    st.markdown(f'<div class="quantum-key-display">Encrypted OTP: {voter.device_info.encrypted_otp}</div>', unsafe_allow_html=True)
                    
                    key_choice = st.selectbox("Decryption Key", ["Q_K2", "AQ_K1"])
                    
                    if st.button("🔓 Decrypt OTP"):
                        if key_choice == "Q_K2":
                            decrypt_key = voter.quantum_keys.q_k2
                        else:
                            decrypt_key = voter.quantum_keys.aq_k1_alice
                        
                        if decrypt_key:
                            decrypted_otp = xor_decrypt(voter.device_info.encrypted_otp, decrypt_key)
                            st.markdown(f'<div class="quantum-key-display">Decrypted OTP: {decrypted_otp}</div>', unsafe_allow_html=True)
        else:
            st.info("Please login to see your quantum keys for demonstration.")
    
    with demo_tab3:
        st.markdown("### 📊 Your Quantum Operations Log")
        
        quantum_log = get_quantum_log()
        
        if quantum_log:
            # Filter operations that might be related to current voter
            voter_ops = quantum_log[-10:]  # Show last 10 operations
            
            for op in voter_ops:
                with st.expander(f"⚡ {op['operation']} - {datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Operation:**")
                        st.write(f"Type: {op['operation']}")
                        st.write(f"Time: {datetime.fromtimestamp(op['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    with col2:
                        st.markdown("**Quantum Properties:**")
                        if 'quantum_properties' in op:
                            props = op['quantum_properties']
                            for key, value in props.items():
                                if isinstance(value, float):
                                    st.write(f"{key.replace('_', ' ').title()}: {value:.4f}")
        else:
            st.info("No quantum operations logged yet.")
    
    with demo_tab4:
        st.markdown("### 🔑 Complete Key Chain Demonstration")
        
        if st.session_state.current_voter:
            voter = st.session_state.current_voter
            
            st.markdown("#### 🔗 Your Quantum Key Evolution Chain")
            
            # Show complete key chain
            key_chain_steps = [
                ("Initial Registration", [
                    f"Q_K1: {voter.quantum_keys.q_k1}",
                    f"Q_K2: {voter.quantum_keys.q_k2}", 
                    f"Biometric: {voter.biometric_data.signature}"
                ]),
                ("Q_K1 Encryption", [
                    f"Encrypted_Q_K1 = Q_K1 ⊕ Biometric",
                    f"Result: {voter.quantum_keys.encrypted_q_k1}"
                ]),
                ("Authentication Keys", [
                    f"AQ_K1 (Alice): {voter.quantum_keys.aq_k1_alice}" if voter.quantum_keys.aq_k1_alice else "Not generated yet",
                    f"AQ_K1 (Bob): {voter.quantum_keys.aq_k1_bob}" if voter.quantum_keys.aq_k1_bob else "Not generated yet"
                ]),
                ("Voting Keys", [
                    f"VQ_K1 (Alice): {voter.quantum_keys.vq_k1_alice}" if voter.quantum_keys.vq_k1_alice else "Not generated yet",
                    f"VQ_K1 (Bob): {voter.quantum_keys.vq_k1_bob}" if voter.quantum_keys.vq_k1_bob else "Not generated yet"
                ])
            ]
            
            for step_name, step_info in key_chain_steps:
                with st.expander(f"🔗 {step_name}", expanded=True):
                    for info in step_info:
                        if ":" in info and len(info.split(":")[1].strip()) <= 20:
                            key_name = info.split(":")[0]
                            key_value = info.split(":")[1].strip()
                            st.markdown(f'<div class="quantum-key-display">{key_name}: {key_value}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f"- {info}")
        else:
            st.info("Please login to see your complete quantum key chain.")

# Help Page
elif page == "ℹ️ Help":
    st.markdown('<h2 class="sub-header">Help & Information</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Voting Guide", "🔬 Quantum Security", "❓ FAQ", "📞 Support"])
    
    with tab1:
        st.markdown("### 📖 Complete Quantegrity Voting Guide")
        
        voting_steps = [
            {
                "title": "1. 🔐 Login with Quantum Credentials",
                "description": "Enter your 16-bit binary credentials provided during registration",
                "details": [
                    "Voter ID: Your unique quantum-generated identifier",
                    "Biometric Signature: Your 16-bit quantum biometric",
                    "Q_K2: Your device registration password"
                ]
            },
            {
                "title": "2. 📝 Device Registration & Verification",
                "description": "Secure your device using Q_K2 encryption",
                "details": [
                    "Request device registration with Election Authority",
                    "Receive encrypted OTP: OTP ⊕ Q_K2",
                    "Decrypt OTP using your Q_K2 key",
                    "Submit decrypted OTP for verification"
                ]
            },
            {
                "title": "3. 🔓 Quantum Authentication Process",
                "description": "Authenticate using biometric and quantum key exchange",
                "details": [
                    "Scan biometric signature to decrypt Q_K1",
                    "System generates AQ_K1 using SEDJO(Q_K1, Q_K1)",
                    "Receive encrypted authentication OTP",
                    "Decrypt OTP with AQ_K1 and verify"
                ]
            },
            {
                "title": "4. 🗳️ Quantum-Secured Voting",
                "description": "Cast your vote with quantum encryption",
                "details": [
                    "System generates VQ_K1 using SEDJO(AQ_K1, AQ_K1)",
                    "Request ballot from quantum-secured pool",
                    "Select candidate and encrypt vote with VQ_K1",
                    "Receive quantum confirmation code"
                ]
            },
            {
                "title": "5. 📋 Receipt Verification",
                "description": "Verify your vote on the quantum bulletin board",
                "details": [
                    "Use your receipt ID to verify vote recording",
                    "Check quantum cryptographic proof",
                    "Confirm vote integrity while maintaining privacy"
                ]
            }
        ]
        
        for step in voting_steps:
            with st.expander(step["title"], expanded=False):
                st.markdown(f"**{step['description']}**")
                for detail in step["details"]:
                    st.markdown(f"- {detail}")
    
    with tab2:
        st.markdown("### 🔬 Quantum Security Features")
        
        st.markdown("""
        #### 🌌 SEDJO Protocol (Symmetrically Entangled Deutsch-Jozsa Quantum Oracle)
        The core quantum key distribution protocol providing:
        - **Quantum Entanglement**: Uses entangled qubit pairs for secure communication
        - **Unconditional Security**: Based on quantum physics laws, not computational complexity
        - **Key Agreement**: Generates shared keys between voter and election authority
        - **Eavesdropping Detection**: Any interception attempt is immediately detected
        
        #### 🎲 Quantum Random Number Generation (QRNG)
        - **True Randomness**: Uses quantum superposition for unpredictable numbers
        - **Confirmation Codes**: Generated using pure quantum entropy
        - **Key Generation**: Q_K1, Q_K2, and biometric signatures use quantum randomness
        - **Ballot Pool**: All confirmation codes generated via quantum processes
        
        #### 🔐 Multi-Layer Quantum Encryption
        - **Q_K1 Encryption**: Primary key encrypted with biometric signature
        - **Q_K2 Verification**: Device authentication using quantum keys
        - **AQ_K1 Authentication**: Generated via quantum key exchange for session auth
        - **VQ_K1 Voting**: Session-specific keys for vote encryption
        - **XOR Security**: Quantum-safe encryption providing perfect secrecy
        
        #### 🔗 Quantum Key Evolution
        The system uses a sophisticated key derivation chain:
        1. **Initial Keys**: Q_K1, Q_K2, Biometric (via QRNG)
        2. **Registration**: Q_K1 ⊕ Biometric → Encrypted_Q_K1
        3. **Authentication**: SEDJO(Q_K1, Q_K1) → AQ_K1
        4. **Voting**: SEDJO(AQ_K1, AQ_K1) → VQ_K1
        5. **Encryption**: Vote ⊕ VQ_K1 → Encrypted_Vote
        """)
    
    with tab3:
        st.markdown("### ❓ Frequently Asked Questions")
        
        faqs = [
            {
                "question": "🤔 How does quantum security make voting more secure?",
                "answer": """Quantum security provides several advantages:
                - **Unconditional Security**: Based on physics laws, not computational assumptions
                - **Eavesdropping Detection**: Any attempt to intercept quantum keys is automatically detected
                - **True Randomness**: Quantum processes generate truly unpredictable numbers
                - **Future-Proof**: Secure against both classical and quantum computer attacks"""
            },
            {
                "question": "🔒 How is my privacy protected?",
                "answer": """Your privacy is protected through multiple quantum mechanisms:
                - **Identity Separation**: Your identity is verified but not linked to vote choice
                - **Quantum Encryption**: All communications use quantum-secured channels
                - **Anonymous Confirmation**: Only you know your confirmation code
                - **Vote Mixing**: Quantum bulletin board anonymizes all votes before counting"""
            },
            {
                "question": "🧾 What is a quantum confirmation code?",
                "answer": """A quantum confirmation code is your cryptographic proof:
                - **Quantum Generated**: Created using true quantum randomness (QRNG)
                - **Unique**: Each vote gets a different quantum-generated code
                - **Verifiable**: You can check it appears on the quantum bulletin board
                - **Anonymous**: The code doesn't reveal your vote choice or identity"""
            },
            {
                "question": "🔍 What does ballot auditing prove?",
                "answer": """Quantum ballot auditing demonstrates:
                - **Transparency**: Shows how quantum confirmation codes work
                - **Integrity**: Proves the quantum voting system operates correctly
                - **Trust**: Demonstrates the quantum cryptographic processes
                - **Verification**: Confirms quantum security without affecting election"""
            },
            {
                "question": "⚡ What is the SEDJO protocol?",
                "answer": """SEDJO (Symmetrically Entangled Deutsch-Jozsa Quantum Oracle):
                - **Quantum Algorithm**: Based on the Deutsch-Jozsa quantum algorithm
                - **Entanglement**: Uses quantum entanglement for secure key exchange
                - **Key Generation**: Creates shared secret keys between voter and authority
                - **Security**: Provides unconditional security based on quantum mechanics"""
            },
            {
                "question": "🔑 Why are there so many different keys?",
                "answer": """Multiple keys provide layered security:
                - **Q_K1**: Primary key for voter authentication (encrypted with biometric)
                - **Q_K2**: Device registration and verification
                - **AQ_K1**: Authentication session keys (generated via SEDJO)
                - **VQ_K1**: Voting session keys (generated via SEDJO)
                - Each key serves a specific purpose in the quantum security protocol"""
            }
        ]
        
        for faq in faqs:
            with st.expander(faq["question"]):
                st.markdown(faq["answer"])
    
    with tab4:
        st.markdown("### 📞 Support & Contact Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🆘 Technical Support
            For quantum voting system issues:
            - **Email**: quantum-support@quantegrity-voting.gov
            - **Phone**: 1-800-QUANTUM (1-800-782-6886)
            - **Hours**: Available 24/7 during election period
            - **Live Chat**: Available on election days
            
            #### 🏛️ Election Authority
            For voter registration and election questions:
            - **Email**: voter-info@elections.gov
            - **Phone**: 1-800-ELECTIONS
            - **Website**: www.quantegrity-elections.gov
            - **Office Hours**: 9 AM - 6 PM, Monday-Friday
            """)
        
        with col2:
            st.markdown("""
            #### 🔬 Quantum Technology Information
            Learn more about quantum security:
            - **Research Paper**: "Quantum e-voting system using QKD"
            - **Technical Docs**: docs.quantegrity.gov
            - **SEDJO Protocol**: arxiv.org/quantegrity-sedjo
            - **Security Proofs**: Available in technical documentation
            
            #### 🛡️ Security Concerns
            Report security issues immediately:
            - **Security Email**: security@quantegrity-voting.gov
            - **Emergency Hotline**: 1-800-VOTE-SEC
            - **Incident Reporting**: Available 24/7
            - **Response Time**: Within 1 hour during elections
            """)
        
        st.markdown("---")
        st.markdown("### 🚨 Emergency Procedures")
        
        emergency_procedures = [
            "🔒 **Lost Credentials**: Contact Election Authority immediately with National ID",
            "🚫 **Voting Issues**: Use technical support hotline for immediate assistance",
            "⚠️ **Security Concerns**: Report to security hotline within 15 minutes",
            "🔧 **System Errors**: Document error and contact technical support",
            "📱 **Device Problems**: Try different device or contact support"
        ]
        
        for procedure in emergency_procedures:
            st.markdown(procedure)

# Sidebar Status and Quick Actions
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Your Status")

# Status indicators
current_voter = st.session_state.current_voter

if current_voter:
    st.sidebar.success(f"✅ Logged in as {current_voter.name}")
    
    # Device status
    if current_voter.device_status == "verified":
        st.sidebar.success("✅ Device Verified")
    elif current_voter.device_status in ["requested", "pending_verification"]:
        st.sidebar.warning("⏳ Device Verification Pending")
    else:
        st.sidebar.error("❌ Device Not Registered")
    
    # Authentication status
    if current_voter.auth_status == "authenticated":
        st.sidebar.success("✅ Authenticated")
    elif current_voter.auth_status in ["biometric_verified", "aq_k1_generated"]:
        st.sidebar.warning("⏳ Authentication In Progress")
    else:
        st.sidebar.warning("⏳ Authentication Required")
    
    # Vote status
    if current_voter.vote_status == "voted":
        st.sidebar.success("✅ Vote Cast")
        if current_voter.vote_receipt:
            st.sidebar.markdown(f"**Receipt:** `{current_voter.vote_receipt}`")
    elif current_voter.vote_status == "spoiled":
        st.sidebar.info("🗑️ Ballot Spoiled")
    else:
        st.sidebar.info("⏳ Ready to Vote")
else:
    st.sidebar.error("❌ Not Logged In")

# Quick Actions
st.sidebar.markdown("### ⚡ Quick Actions")

if st.sidebar.button("🔄 Refresh Status"):
    shared_state.refresh_data()
    # Refresh current voter data if logged in
    if st.session_state.current_voter:
        updated_voter = shared_state.get_voter(st.session_state.current_voter.voter_id)
        if updated_voter:
            st.session_state.current_voter = updated_voter
    st.rerun()

if current_voter and st.sidebar.button("🔓 Logout", key="sidebar_logout"):
    st.session_state.current_voter = None
    st.session_state.voting_step = 'login'
    st.session_state.crypto_session = None
    st.session_state.current_ballot = None
    st.rerun()

if st.sidebar.button("🔬 Crypto Demo"):
    st.session_state.page = "🔬 Crypto Demo"
    st.rerun()

# System Information
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ System Info")
st.sidebar.markdown("**Version:** Quantegrity Voter v2.0")
st.sidebar.markdown("**Security:** Quantum-Enhanced")
st.sidebar.markdown("**Protocol:** SEDJO + Scantegrity")
st.sidebar.markdown("**Paper:** arxiv.org/quantegrity")

# Current election info
if active_election:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗳️ Current Election")
    st.sidebar.markdown(f"**Name:** {active_election.name}")
    st.sidebar.markdown(f"**Candidates:** {len(active_election.candidates)}")

# Emergency contact
st.sidebar.markdown("---")
st.sidebar.markdown("### 🆘 Need Help?")
st.sidebar.markdown("**Voter Hotline:**")
st.sidebar.markdown("📞 1-800-QUANTUM")
st.sidebar.markdown("**Technical Support:**")
st.sidebar.markdown("💬 Available 24/7")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🔬 Quantum Security:** SEDJO Protocol")
with col2:
    st.markdown("**🗳️ Voting System:** Quantegrity + Scantegrity")
with col3:
    st.markdown("**🔒 Privacy Level:** Quantum Anonymous")

# Real-time notifications
if current_voter:
    # Show contextual notifications based on status
    if current_voter.device_status == "not_requested":
        st.info("📝 Next Step: Register your device for quantum-secured voting")
    elif current_voter.device_status == "requested":
        st.info("⏳ Waiting for Election Authority to approve device registration")
    elif current_voter.device_status == "pending_verification":
        st.info("🔐 Device approved! Decrypt the OTP with Q_K2 to complete verification")
    elif current_voter.device_status == "verified" and current_voter.auth_status == "not_authenticated":
        st.info("🔓 Device verified! Proceed to quantum authentication")
    elif current_voter.auth_status == "authenticated" and current_voter.vote_status == "not_voted":
        st.info("🗳️ You are authenticated and ready to cast your quantum-secured vote!")
    elif current_voter.vote_status == "voted":
        st.success(f"✅ Your vote has been quantum-secured! Receipt: {current_voter.vote_receipt}")

# Debug information (for development/demonstration)
if st.sidebar.checkbox("🔧 Debug Mode"):
    st.sidebar.markdown("### 🔧 Debug Information")
    debug_info = {
        "current_voter": current_voter.voter_id if current_voter else None,
        "voting_step": st.session_state.voting_step,
        "device_status": current_voter.device_status if current_voter else None,
        "auth_status": current_voter.auth_status if current_voter else None,
        "vote_status": current_voter.vote_status if current_voter else None,
        "has_ballot": st.session_state.current_ballot is not None,
        "crypto_session": st.session_state.crypto_session
    }
    st.sidebar.json(debug_info)

# Add quantum animation effects
st.markdown("""
<style>
    @keyframes quantum-pulse {
        0% { box-shadow: 0 0 5px #4169E1; }
        50% { box-shadow: 0 0 20px #4169E1, 0 0 30px #8A2BE2; }
        100% { box-shadow: 0 0 5px #4169E1; }
    }
    
    .crypto-demo-box {
        animation: quantum-pulse 4s ease-in-out infinite;
    }
    
    .quantum-key-display {
        transition: all 0.3s ease;
    }
    
    .quantum-key-display:hover {
        background: #1a252f;
        box-shadow: 0 0 10px #00ff41;
        transform: scale(1.02);
    }
    
    .confirmation-code {
        animation: quantum-pulse 2s ease-in-out infinite;
    }
    
    .status-indicator {
        transition: all 0.3s ease;
    }
    
    .status-indicator:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)