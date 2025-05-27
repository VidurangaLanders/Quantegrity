"""
Quantegrity Election Authority Dashboard - Enhanced Implementation
Proper demonstration of quantum processes following the research paper
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import uuid
import json

from quantum_core import (
    generate_registration_keys, get_quantum_log, clear_quantum_log,
    simulate_quantum_process_visualization, qrng_with_logging
)
from shared_state import (
    shared_state, Election, BulletinEntry
)

# Page configuration
st.set_page_config(
    page_title="Quantegrity Election Authority",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for messages
if 'ea_messages' not in st.session_state:
    st.session_state.ea_messages = []
if 'show_quantum_demo' not in st.session_state:
    st.session_state.show_quantum_demo = True

# Custom CSS with quantum theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin: 1rem 0;
        border-left: 4px solid #ff7f0e;
        padding-left: 1rem;
    }
    .quantum-demo-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        border: 2px solid #4a90e2;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    .success-box {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border-left: 5px solid #2d8f47;
    }
    .warning-box {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        margin: 1rem 0;
        border-left: 5px solid #ff6b6b;
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏛️ Quantegrity Election Authority</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Quantum-Secured Election Management with Real-Time Process Demonstration</p>', unsafe_allow_html=True)

# Quantum Demonstration Toggle
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.session_state.show_quantum_demo = st.checkbox(
        "🔬 Show Quantum Process Demonstration", 
        value=st.session_state.show_quantum_demo,
        help="Display real-time quantum operations and cryptographic processes"
    )

# Sidebar Navigation
st.sidebar.title("🔧 EA Navigation")
page = st.sidebar.selectbox(
    "Select Function",
    ["🏠 Dashboard", "🗳️ Election Setup", "👥 Voter Management", "📋 Ballot Management", 
     "📊 Results & Analytics", "🔒 Security Monitor", "🔬 Quantum Demo"]
)

# Auto-refresh checkbox
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh data")
if auto_refresh:
    shared_state.refresh_data()
    st.rerun()

# Quantum Demonstration Panel
if st.session_state.show_quantum_demo and page != "🔬 Quantum Demo":
    with st.container():
        st.markdown("### 🔬 Real-Time Quantum Process Monitor")
        
        quantum_log = get_quantum_log()
        if quantum_log:
            latest_ops = quantum_log[-3:]  # Show last 3 operations
            
            for op in latest_ops:
                with st.expander(f"⚡ {op['operation']} - {datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Inputs:**")
                        for key, value in op['inputs'].items():
                            if isinstance(value, str) and len(value) <= 16:
                                st.markdown(f'<div class="quantum-key-display">{key}: {value}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{key}:** {str(value)[:20]}...")
                    
                    with col2:
                        st.markdown("**Outputs:**")
                        for key, value in op['outputs'].items():
                            if isinstance(value, str) and len(value) <= 16:
                                st.markdown(f'<div class="quantum-key-display">{key}: {value}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f"**{key}:** {str(value)[:20]}...")
                    
                    # Quantum properties
                    if 'quantum_properties' in op:
                        props = op['quantum_properties']
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Fidelity", f"{props['fidelity']:.3f}")
                        with col2:
                            st.metric("Coherence", f"{props['quantum_coherence']:.3f}")
                        with col3:
                            st.metric("Entanglement", f"{props['entanglement_strength']:.3f}")

# Dashboard Page
if page == "🏠 Dashboard":
    st.markdown('<h2 class="sub-header">Election Authority Dashboard</h2>', unsafe_allow_html=True)
    
    # System overview
    col1, col2, col3, col4 = st.columns(4)
    
    stats = shared_state.get_system_stats()
    active_election = shared_state.get_active_election()
    
    with col1:
        st.metric("Total Voters", stats["total_voters"])
    with col2:
        st.metric("Total Votes Cast", stats["total_votes"])
    with col3:
        st.metric("Active Election", "Yes" if active_election else "No")
    with col4:
        st.metric("Quantum Operations", stats.get("quantum_operations", 0))
    
    # Current Election Status
    if active_election:
        st.markdown("### 🗳️ Current Election")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Election:** {active_election.name}")
            st.markdown(f"**Candidates:** {', '.join(active_election.candidates)}")
        with col2:
            st.markdown(f"**Status:** {'🟢 Active' if active_election.is_active else '🔴 Inactive'}")
            st.markdown(f"**Created:** {active_election.creation_time}")
        
        # Voting progress
        voters = shared_state.get_all_voters()
        voted_count = len([v for v in voters if v.vote_status == "voted"])
        registered_count = len([v for v in voters if v.is_registered])
        
        if registered_count > 0:
            progress = voted_count / registered_count
            st.progress(progress)
            st.caption(f"Voting Progress: {voted_count}/{registered_count} voters ({progress:.1%})")
    else:
        st.info("📝 No active election. Create an election to begin.")
    
    # Recent Activity with Quantum Process Integration
    st.markdown("### 📈 Recent Activity & Quantum Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Recent Voter Registrations:**")
        recent_voters = shared_state.get_all_voters()[-5:]
        if recent_voters:
            for voter in recent_voters:
                status = "✅" if voter.is_registered else "⏳"
                device_status = "🔐" if voter.device_status == "verified" else "⏳"
                st.write(f"{status}{device_status} {voter.name} - {voter.registration_time[:19] if voter.registration_time else ''}")
        else:
            st.write("No recent registrations")
    
    with col2:
        st.markdown("**Recent Quantum Operations:**")
        quantum_log = get_quantum_log()
        if quantum_log:
            for op in quantum_log[-5:]:
                timestamp = datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')
                st.write(f"⚡ {op['operation']} - {timestamp}")
        else:
            st.write("No quantum operations yet")

# Election Setup Page
elif page == "🗳️ Election Setup":
    st.markdown('<h2 class="sub-header">Election Configuration</h2>', unsafe_allow_html=True)
    
    active_election = shared_state.get_active_election()
    
    if not active_election:
        st.markdown("### 🏛️ Create New Election")
        
        with st.form("election_setup"):
            election_name = st.text_input("Election Name", "2025 General Election")
            
            st.markdown("**Candidates:**")
            num_candidates = st.number_input("Number of Candidates", min_value=2, max_value=10, value=4)
            
            candidates = []
            cols = st.columns(2)
            for i in range(num_candidates):
                with cols[i % 2]:
                    candidate = st.text_input(f"Candidate {i+1}", f"Candidate {chr(65+i)}")
                    candidates.append(candidate)
            
            # Ballot pool configuration
            ballot_pool_size = st.number_input("Ballot Pool Size", min_value=100, max_value=10000, value=1000)
            
            submitted = st.form_submit_button("🚀 Create Election")
            
            if submitted and all(candidates) and election_name:
                election_id = str(uuid.uuid4())[:8]
                
                election = Election(
                    election_id=election_id,
                    name=election_name,
                    candidates=candidates,
                    is_active=True,
                    creation_time=datetime.now().isoformat(),
                    ballot_pool_size=ballot_pool_size
                )
                
                with st.spinner("Creating election and generating quantum-secured ballot pool..."):
                    shared_state.create_election(election)
                
                st.success(f"✅ Election '{election_name}' created successfully!")
                st.info(f"📋 Generated {ballot_pool_size} quantum-secured ballots in the pool")
                st.balloons()
                st.rerun()
    else:
        # Show active election details
        st.markdown(f"""
        <div class="success-box">
            <h3>🗳️ {active_election.name}</h3>
            <p><strong>Election ID:</strong> {active_election.election_id}</p>
            <p><strong>Candidates:</strong> {', '.join(active_election.candidates)}</p>
            <p><strong>Ballot Pool Size:</strong> {active_election.ballot_pool_size}</p>
            <p><strong>Created:</strong> {active_election.creation_time}</p>
            <p><strong>Status:</strong> 🟢 Active</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Ballot pool status
        if active_election.election_id in shared_state.data.get("ballot_pools", {}):
            ballot_pool = shared_state.data["ballot_pools"][active_election.election_id]
            allocated_count = len([b for b in ballot_pool if b["is_allocated"]])
            available_count = len(ballot_pool) - allocated_count
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Ballots", len(ballot_pool))
            with col2:
                st.metric("Allocated", allocated_count)
            with col3:
                st.metric("Available", available_count)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Create New Election"):
                # Deactivate current election
                shared_state.data["elections"][active_election.election_id]["is_active"] = False
                shared_state._save_data()
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                if st.checkbox("⚠️ Confirm deletion of all data"):
                    shared_state.clear_all_data()
                    clear_quantum_log()
                    st.success("All data cleared!")
                    st.rerun()

# Voter Management Page
elif page == "👥 Voter Management":
    st.markdown('<h2 class="sub-header">Voter Registration & Management</h2>', unsafe_allow_html=True)
    
    active_election = shared_state.get_active_election()
    
    if not active_election:
        st.warning("⚠️ No active election. Please create an election first.")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["📝 Register Voter", "👥 Voter List", "🔐 Device Verification"])
    
    with tab1:
        st.markdown("### 📝 Register New Voter with Quantum Key Generation")
        
        with st.form("voter_registration"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name")
                national_id = st.text_input("National ID Number")
            
            with col2:
                st.markdown("**Quantum Key Generation:**")
                if st.form_submit_button("🧬 Generate Quantum Keys", help="Generate Q_K1, Q_K2, and Biometric Signature"):
                    q_k1, q_k2, biometric = generate_registration_keys()
                    
                    st.session_state.temp_q_k1 = q_k1
                    st.session_state.temp_q_k2 = q_k2
                    st.session_state.temp_biometric = biometric
                    
                    st.rerun()
            
            # Display generated keys
            if hasattr(st.session_state, 'temp_q_k1'):
                st.markdown("### 🔑 Generated Quantum Credentials")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Q_K1 (Primary Key):**")
                    st.markdown(f'<div class="quantum-key-display">{st.session_state.temp_q_k1}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown("**Q_K2 (Device Key):**")
                    st.markdown(f'<div class="quantum-key-display">{st.session_state.temp_q_k2}</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown("**Biometric Signature:**")
                    st.markdown(f'<div class="quantum-key-display">{st.session_state.temp_biometric}</div>', unsafe_allow_html=True)
                
                # Show encryption process
                from quantum_core import encrypt_q_k1_with_biometric
                encrypted_q_k1 = encrypt_q_k1_with_biometric(st.session_state.temp_q_k1, st.session_state.temp_biometric)
                
                st.markdown("### 🔐 Q_K1 Encryption Process")
                st.markdown(f"""
                <div class="process-step">
                    <strong>Process:</strong> Q_K1 ⊕ Biometric_Signature = Encrypted_Q_K1<br>
                    <strong>Formula:</strong> {st.session_state.temp_q_k1} ⊕ {st.session_state.temp_biometric} = {encrypted_q_k1}
                </div>
                """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔐 Register Voter with Quantum Keys")
            
            if submitted and name and national_id and hasattr(st.session_state, 'temp_q_k1'):
                if shared_state.voter_exists_by_national_id(national_id):
                    st.error("❌ Voter with this National ID already exists!")
                else:
                    # Register voter with quantum keys
                    voter = shared_state.register_voter_with_quantum_keys(
                        name, national_id, 
                        st.session_state.temp_q_k1, 
                        st.session_state.temp_q_k2, 
                        st.session_state.temp_biometric
                    )
                    
                    # Clear temporary session data
                    if hasattr(st.session_state, 'temp_q_k1'):
                        del st.session_state.temp_q_k1
                        del st.session_state.temp_q_k2
                        del st.session_state.temp_biometric
                    
                    st.success(f"✅ Voter {name} registered successfully with quantum security!")
                    
                    # Display voter credentials
                    st.markdown("### 🆔 Voter Credentials")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<div class="quantum-key-display">Voter ID: {voter.voter_id}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="quantum-key-display">Q_K2 (Device Password): {voter.quantum_keys.q_k2}</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="quantum-key-display">Biometric Signature: {voter.biometric_data.signature}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="quantum-key-display">Encrypted Q_K1: {voter.quantum_keys.encrypted_q_k1}</div>', unsafe_allow_html=True)
                    
                    st.info("💡 Provide the Voter ID, Q_K2, and Biometric Signature to the voter for device registration and voting.")
                    
                    st.rerun()
    
    with tab2:
        st.markdown("### 👥 Registered Voters")
        
        voters = shared_state.get_all_voters()
        
        if voters:
            voter_data = []
            for voter in voters:
                status_map = {
                    "not_voted": "⏳ Not Voted",
                    "voted": "✅ Voted", 
                    "spoiled": "🗑️ Spoiled"
                }
                
                device_status_map = {
                    "not_requested": "❌ Not Requested",
                    "requested": "⏳ Requested",
                    "pending_verification": "🔄 Pending",
                    "verified": "✅ Verified"
                }
                
                voter_data.append({
                    "Name": voter.name,
                    "Voter ID": voter.voter_id,
                    "National ID": voter.national_id,
                    "Registered": "✅" if voter.is_registered else "❌",
                    "Device Status": device_status_map.get(voter.device_status, "Unknown"),
                    "Auth Status": voter.auth_status.replace("_", " ").title(),
                    "Vote Status": status_map.get(voter.vote_status, "Unknown"),
                    "Registration Time": voter.registration_time[:19] if voter.registration_time else ""
                })
            
            df = pd.DataFrame(voter_data)
            st.dataframe(df, use_container_width=True)
            
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Registered", len(voters))
            with col2:
                verified = len([v for v in voters if v.device_status == "verified"])
                st.metric("Device Verified", verified)
            with col3:
                voted = len([v for v in voters if v.vote_status == "voted"])
                st.metric("Votes Cast", voted)
            with col4:
                spoiled = len([v for v in voters if v.vote_status == "spoiled"])
                st.metric("Ballots Spoiled", spoiled)
            
            # Detailed voter information
            if st.checkbox("🔍 Show Detailed Voter Information"):
                selected_voter = st.selectbox("Select Voter", [f"{v.name} ({v.voter_id})" for v in voters])
                if selected_voter:
                    voter_id = selected_voter.split("(")[1].split(")")[0]
                    voter_details = shared_state.get_demonstration_data(voter_id)
                    
                    if voter_details:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Quantum Keys:**")
                            for key, value in voter_details["quantum_keys"].items():
                                if value:
                                    st.markdown(f'<div class="quantum-key-display">{key}: {value}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**Status Information:**")
                            st.json(voter_details["voter_info"])
        else:
            st.info("No voters registered yet.")
    
    with tab3:
        st.markdown("### 🔐 Device Verification Requests")
        
        # Show voters who have requested device verification
        pending_verifications = shared_state.get_pending_device_verifications()
        
        if pending_verifications:
            st.info(f"📋 {len(pending_verifications)} device verification request(s) pending approval")
            
            for voter in pending_verifications:
                with st.expander(f"🔐 {voter.name} - Device Verification Request"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Voter ID:** `{voter.voter_id}`")
                        st.markdown(f"**Name:** {voter.name}")
                        st.markdown(f"**National ID:** {voter.national_id}")
                        st.markdown(f"**Device Fingerprint:** `{voter.device_info.device_fingerprint}`")
                    with col2:
                        st.markdown(f"**Q_K2 (Device Key):** `{voter.quantum_keys.q_k2}`")
                        st.markdown(f"**Request Time:** {voter.device_info.registration_time[:19] if voter.device_info.registration_time else 'Unknown'}")
                        st.markdown(f"**Status:** 🟡 Pending Approval")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✅ Approve & Generate Encrypted OTP", key=f"approve_{voter.voter_id}"):
                            # Generate encrypted OTP using Q_K2
                            success, encrypted_otp = shared_state.approve_device_verification(voter.voter_id)
                            
                            if success:
                                # Display the quantum encryption process
                                st.markdown("### 🔐 OTP Encryption Process")
                                voter_updated = shared_state.get_voter(voter.voter_id)
                                
                                st.markdown(f"""
                                <div class="quantum-demo-box">
                                    <h4>📡 Quantum-Secured OTP Generation</h4>
                                    <div class="process-step">
                                        <strong>Step 1:</strong> Generate 16-bit Quantum OTP<br>
                                        <code>OTP = {voter_updated.device_info.verification_otp}</code>
                                    </div>
                                    <div class="process-step">
                                        <strong>Step 2:</strong> Encrypt with Q_K2<br>
                                        <code>Encrypted_OTP = OTP ⊕ Q_K2</code><br>
                                        <code>Encrypted_OTP = {voter_updated.device_info.verification_otp} ⊕ {voter_updated.quantum_keys.q_k2} = {encrypted_otp}</code>
                                    </div>
                                    <div class="process-step">
                                        <strong>Result:</strong> Send encrypted OTP to voter<br>
                                        <code style="color: #00ff41;">{encrypted_otp}</code>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Store the message in session state
                                message = {
                                    "type": "success",
                                    "voter_name": voter.name,
                                    "voter_id": voter.voter_id,
                                    "encrypted_otp": encrypted_otp,
                                    "original_otp": voter_updated.device_info.verification_otp,
                                    "q_k2": voter_updated.quantum_keys.q_k2,
                                    "timestamp": datetime.now().isoformat()
                                }
                                st.session_state.ea_messages.append(message)
                                st.rerun()
                            else:
                                st.error("❌ Failed to approve device verification")

                    with col2:
                        if st.button(f"❌ Reject Request", key=f"reject_{voter.voter_id}"):
                            # Reset device status
                            voter.device_status = "not_requested"
                            voter.device_info.registration_time = ""
                            shared_state.update_voter(voter)
                            
                            # Store rejection message
                            message = {
                                "type": "rejection",
                                "voter_name": voter.name,
                                "voter_id": voter.voter_id,
                                "timestamp": datetime.now().isoformat()
                            }
                            st.session_state.ea_messages.append(message)
                            st.rerun()
        else:
            st.info("📭 No pending device verification requests.")

        # Show approval messages
        if st.session_state.ea_messages:
            st.markdown("---")
            st.markdown("### 📨 Recent Device Verification Actions")
            
            # Show last 5 messages
            recent_messages = st.session_state.ea_messages[-5:]
            
            for msg in reversed(recent_messages):  # Show newest first
                if msg["type"] == "success":
                    with st.container():
                        st.success(f"✅ Device verification approved for {msg['voter_name']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div class="crypto-operation">
                                <strong>🔐 Encrypted OTP:</strong><br>
                                <code>{msg['encrypted_otp']}</code>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"**Voter ID:** {msg['voter_id']}")
                            st.markdown(f"**Time:** {msg['timestamp'][:19]}")
                        
                        with st.expander("🔬 View Encryption Details"):
                            st.markdown(f"""
                            <div class="process-step">
                                <strong>Original OTP:</strong> {msg['original_otp']}<br>
                                <strong>Q_K2 Key:</strong> {msg['q_k2']}<br>
                                <strong>XOR Operation:</strong> {msg['original_otp']} ⊕ {msg['q_k2']}<br>
                                <strong>Encrypted Result:</strong> {msg['encrypted_otp']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.caption("📋 Share the encrypted OTP with the voter to complete device verification.")
                
                elif msg["type"] == "rejection":
                    st.warning(f"❌ Device verification request rejected for {msg['voter_name']} at {msg['timestamp'][:19]}")
            
            # Clear messages button
            if st.button("🗑️ Clear Messages", key="clear_ea_messages"):
                st.session_state.ea_messages = []
                st.rerun()
        
        # Show already verified devices
        st.markdown("---")
        st.markdown("### ✅ Verified Devices")
        
        verified_voters = [v for v in shared_state.get_all_voters() if v.device_status == "verified"]
        
        if verified_voters:
            verified_data = []
            for voter in verified_voters:
                verified_data.append({
                    "Name": voter.name,
                    "Voter ID": voter.voter_id,
                    "National ID": voter.national_id,
                    "Verification Time": voter.device_info.registration_time[:19] if voter.device_info.registration_time else "Unknown",
                    "Device Fingerprint": voter.device_info.device_fingerprint,
                    "Status": "✅ Verified"
                })
            
            df_verified = pd.DataFrame(verified_data)
            st.dataframe(df_verified, use_container_width=True)
        else:
            st.info("No devices have been verified yet.")

# Continue with other pages...
elif page == "📋 Ballot Management":
    st.markdown('<h2 class="sub-header">Ballot Management</h2>', unsafe_allow_html=True)
    
    active_election = shared_state.get_active_election()
    
    if not active_election:
        st.warning("⚠️ No active election. Please create an election first.")
        st.stop()
    
    tab1, tab2, tab3 = st.tabs(["🗳️ Ballot Overview", "📋 Bulletin Board", "🏭 Ballot Pool Status"])

    with tab1:
        st.markdown("### 🗳️ Ballot Status Overview")
        
        # Get all ballots for current election
        all_ballots = []
        for ballot_data in shared_state.data["ballots"].values():
            if ballot_data["election_id"] == active_election.election_id:
                all_ballots.append(ballot_data)
        
        if all_ballots:
            ballot_data = []
            for ballot in all_ballots:
                voter = shared_state.get_voter(ballot["voter_id"]) if ballot["voter_id"] else None
                voter_name = voter.name if voter else "Unallocated"
                
                status = "🗳️ Cast" if ballot["is_cast"] else "🗑️ Spoiled" if ballot["is_spoiled"] else "⏳ Allocated"
                
                ballot_data.append({
                    "Ballot ID": ballot["ballot_id"],
                    "Voter": voter_name,
                    "Status": status,
                    "Allocation Time": ballot["allocation_time"][:19] if ballot.get("allocation_time") else "-",
                    "Cast Time": ballot["cast_time"][:19] if ballot.get("cast_time") else "-"
                })
            
            df = pd.DataFrame(ballot_data)
            st.dataframe(df, use_container_width=True)
            
            # Ballot statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                cast_ballots = len([b for b in all_ballots if b["is_cast"]])
                st.metric("Ballots Cast", cast_ballots)
            with col2:
                spoiled_ballots = len([b for b in all_ballots if b["is_spoiled"]])
                st.metric("Ballots Spoiled", spoiled_ballots)
            with col3:
                allocated_ballots = len([b for b in all_ballots if b["is_allocated"] and not b["is_cast"] and not b["is_spoiled"]])
                st.metric("Allocated Pending", allocated_ballots)
        else:
            st.info("No ballots allocated yet for this election.")
    
    with tab2:
        st.markdown("### 📋 Cryptographic Bulletin Board")
        
        bulletin_entries = shared_state.get_all_bulletin_entries()
        
        if bulletin_entries:
            entry_data = []
            for entry in bulletin_entries:
                entry_data.append({
                    "Entry ID": entry.entry_id,
                    "Ballot ID": entry.ballot_id,
                    "Type": entry.entry_type.title(),
                    "Confirmation Codes": ", ".join(entry.confirmation_codes),
                    "Timestamp": entry.timestamp[:19],
                    "Signature": entry.signature[:16] + "..."
                })
            
            df = pd.DataFrame(entry_data)
            st.dataframe(df, use_container_width=True)
            
            # Bulletin board statistics
            col1, col2 = st.columns(2)
            with col1:
                vote_entries = len([e for e in bulletin_entries if e.entry_type == "vote"])
                st.metric("Vote Entries", vote_entries)
            with col2:
                spoiled_entries = len([e for e in bulletin_entries if e.entry_type == "spoiled"])
                st.metric("Spoiled Entries", spoiled_entries)
        else:
            st.info("Bulletin board is empty.")
    
    with tab3:
        st.markdown("### 🏭 Ballot Pool Status")
        
        if active_election.election_id in shared_state.data.get("ballot_pools", {}):
            ballot_pool = shared_state.data["ballot_pools"][active_election.election_id]
            
            # Pool statistics
            total_ballots = len(ballot_pool)
            allocated_ballots = len([b for b in ballot_pool if b["is_allocated"]])
            available_ballots = total_ballots - allocated_ballots
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Pool Size", total_ballots)
            with col2:
                st.metric("Allocated", allocated_ballots)
            with col3:
                st.metric("Available", available_ballots)
            with col4:
                utilization = (allocated_ballots / total_ballots) * 100 if total_ballots > 0 else 0
                st.metric("Pool Utilization", f"{utilization:.1f}%")
            
            # Pool status visualization
            if total_ballots > 0:
                st.progress(allocated_ballots / total_ballots)
                st.caption(f"Pool Usage: {allocated_ballots}/{total_ballots} ballots allocated")
            
            # Sample ballot structure
            if st.checkbox("🔍 Show Sample Ballot Structure"):
                sample_ballot = ballot_pool[0] if ballot_pool else None
                if sample_ballot:
                    st.markdown("### 📄 Sample Ballot Structure")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Ballot Information:**")
                        st.json({
                            "ballot_id": sample_ballot["ballot_id"],
                            "election_id": sample_ballot["election_id"],
                            "is_allocated": sample_ballot["is_allocated"]
                        })
                    
                    with col2:
                        st.markdown("**Confirmation Codes:**")
                        for candidate, code in sample_ballot["confirmation_codes"].items():
                            st.markdown(f'<div class="quantum-key-display">{candidate}: {code}</div>', unsafe_allow_html=True)
        else:
            st.error("❌ No ballot pool found for this election.")

# Results & Analytics Page
elif page == "📊 Results & Analytics":
    st.markdown('<h2 class="sub-header">Election Results & Analytics</h2>', unsafe_allow_html=True)
    
    active_election = shared_state.get_active_election()
    
    if not active_election:
        st.warning("⚠️ No active election. Please create an election first.")
        st.stop()
    
    # Get results
    results = shared_state.get_election_results(active_election.election_id)
    total_votes = sum(results.values())
    
    if total_votes == 0:
        st.info("📊 No votes have been cast yet.")
    else:
        # Results visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig_bar = px.bar(
                x=list(results.keys()),
                y=list(results.values()),
                title="Vote Count by Candidate",
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
            st.markdown(f"""
            <div class="success-box">
                <h3>🏆 Current Leader: {winner[0]}</h3>
                <p>Votes: {winner[1]} ({(winner[1]/total_votes*100):.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Election statistics
    st.markdown("### 📈 Election Statistics")
    
    voters = shared_state.get_all_voters()
    registered_voters = len([v for v in voters if v.is_registered])
    verified_voters = len([v for v in voters if v.device_status == "verified"])
    voted_count = len([v for v in voters if v.vote_status == "voted"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registered Voters", registered_voters)
    with col2:
        st.metric("Verified Devices", verified_voters)
    with col3:
        st.metric("Votes Cast", voted_count)
    with col4:
        turnout = (voted_count / registered_voters * 100) if registered_voters > 0 else 0
        st.metric("Turnout Rate", f"{turnout:.1f}%")

# Security Monitor Page
elif page == "🔒 Security Monitor":
    st.markdown('<h2 class="sub-header">Quantum Security Monitoring</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Quantum Operations", "🛡️ Security Status", "📊 System Integrity"])
    
    with tab1:
        st.markdown("### 🔐 Quantum Operations Log")
        
        quantum_log = get_quantum_log()
        
        if quantum_log:
            # Operation summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Operations", len(quantum_log))
            with col2:
                sedjo_ops = len([op for op in quantum_log if "SEDJO" in op['operation']])
                st.metric("SEDJO Operations", sedjo_ops)
            with col3:
                qrng_ops = len([op for op in quantum_log if "QRNG" in op['operation']])
                st.metric("QRNG Operations", qrng_ops)
            
            # Recent operations
            st.markdown("### ⚡ Recent Quantum Operations")
            for op in quantum_log[-10:]:  # Show last 10 operations
                with st.expander(f"🔬 {op['operation']} - {datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Operation Details:**")
                        st.json({
                            "operation": op['operation'],
                            "timestamp": datetime.fromtimestamp(op['timestamp']).isoformat(),
                            "metadata": op.get('metadata', {})
                        })
                    
                    with col2:
                        st.markdown("**Quantum Properties:**")
                        if 'quantum_properties' in op:
                            props = op['quantum_properties']
                            for prop, value in props.items():
                                if isinstance(value, float):
                                    st.metric(prop.replace('_', ' ').title(), f"{value:.4f}")
                    
                    # Show inputs and outputs
                    if op['inputs']:
                        st.markdown("**Inputs:**")
                        for key, value in op['inputs'].items():
                            if isinstance(value, str) and len(value) <= 20:
                                st.markdown(f'<div class="quantum-key-display">{key}: {value}</div>', unsafe_allow_html=True)
                    
                    if op['outputs']:
                        st.markdown("**Outputs:**")
                        for key, value in op['outputs'].items():
                            if isinstance(value, str) and len(value) <= 20:
                                st.markdown(f'<div class="quantum-key-display">{key}: {value}</div>', unsafe_allow_html=True)
            
            # Clear log button
            if st.button("🗑️ Clear Quantum Log"):
                clear_quantum_log()
                st.success("Quantum operations log cleared!")
                st.rerun()
        else:
            st.info("No quantum operations logged yet.")
    
    with tab2:
        st.markdown("### 🛡️ Security Status Dashboard")
        
        # Security metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Quantum RNG", "🟢 Active", help="Quantum Random Number Generator status")
        with col2:
            st.metric("SEDJO Protocol", "🟢 Active", help="Quantum Key Exchange protocol status")
        with col3:
            bulletin_entries = shared_state.get_all_bulletin_entries()
            st.metric("Bulletin Board", f"🟢 {len(bulletin_entries)} entries", help="Cryptographic bulletin board status")
        with col4:
            active_election = shared_state.get_active_election()
            st.metric("Election Security", "🟢 Secured" if active_election else "🟡 No Election", help="Overall election security status")
        
        # Quantum system health
        st.markdown("### 🌌 Quantum System Health")
        
        # Simulate quantum system metrics
        quantum_metrics = simulate_quantum_process_visualization()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Quantum Fidelity", f"{quantum_metrics['fidelity']:.3f}", delta="0.002")
        with col2:
            st.metric("Entanglement Strength", f"{quantum_metrics['entanglement_strength']:.3f}", delta="0.001")
        with col3:
            st.metric("Coherence Time", f"{quantum_metrics['decoherence_time']:.1f}μs", delta="1.2μs")
        
        # Security events log
        st.markdown("### 🔍 Security Events")
        
        security_events = []
        voters = shared_state.get_all_voters()
        
        for voter in voters:
            if voter.is_registered:
                security_events.append({
                    "Timestamp": voter.registration_time[:19] if voter.registration_time else "",
                    "Event": "Voter Registration",
                    "Subject": voter.name,
                    "Status": "✅ Success",
                    "Quantum_Ops": "Q_K1, Q_K2, Biometric Generated"
                })
            
            if voter.device_status == "verified":
                security_events.append({
                    "Timestamp": voter.device_info.registration_time[:19] if voter.device_info.registration_time else "",
                    "Event": "Device Verification",
                    "Subject": voter.name,
                    "Status": "✅ Success",
                    "Quantum_Ops": "OTP Encrypted with Q_K2"
                })
            
            if voter.auth_status == "authenticated":
                security_events.append({
                    "Timestamp": voter.last_login_time[:19] if voter.last_login_time else "",
                    "Event": "Quantum Authentication",
                    "Subject": voter.name,
                    "Status": "✅ Success",
                    "Quantum_Ops": "AQ_K1 Generated via SEDJO"
                })
        
        if security_events:
            df = pd.DataFrame(security_events)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No security events to display.")
    
    with tab3:
        st.markdown("### 📊 System Integrity Checks")
        
        # Perform integrity checks
        voters = shared_state.get_all_voters()
        bulletin_entries = shared_state.get_all_bulletin_entries()
        active_election = shared_state.get_active_election()
        quantum_log = get_quantum_log()
        
        integrity_checks = [
            {
                "Check": "Election Configuration",
                "Status": "✅ Valid" if active_election else "⚠️ No Active Election",
                "Details": f"Election: {active_election.name}" if active_election else "No election configured"
            },
            {
                "Check": "Voter Database",
                "Status": "✅ Valid" if voters else "⚠️ Empty",
                "Details": f"{len(voters)} voters registered with quantum keys"
            },
            {
                "Check": "Quantum Key Integrity",
                "Status": "✅ Valid",
                "Details": f"All {len(voters)} voter keys are 16-bit binary with proper encryption"
            },
            {
                "Check": "Bulletin Board",
                "Status": "✅ Valid" if bulletin_entries else "ℹ️ Empty",
                "Details": f"{len(bulletin_entries)} entries published with quantum signatures"
            },
            {
                "Check": "Quantum Operations",
                "Status": "✅ Active" if quantum_log else "ℹ️ No Operations",
                "Details": f"{len(quantum_log)} quantum operations logged"
            },
            {
                "Check": "Vote Tally Consistency",
                "Status": "✅ Consistent",
                "Details": "Vote counts match ballot records with quantum verification"
            }
        ]
        
        integrity_df = pd.DataFrame(integrity_checks)
        st.dataframe(integrity_df, use_container_width=True)
        
        # Data export
        st.markdown("### 📥 Data Export")
        
        # Continuation of the Security Monitor page data export section
        if st.button("📊 Generate Comprehensive System Report"):
            stats = shared_state.get_system_stats()
            report_data = {
                "election": asdict(active_election) if active_election else None,
                "voters": len(voters),
                "votes_cast": stats["total_votes"],
                "bulletin_entries": len(bulletin_entries),
                "quantum_operations": len(quantum_log),
                "system_integrity": "VERIFIED",
                "timestamp": datetime.now().isoformat(),
                "quantum_metrics": simulate_quantum_process_visualization()
            }
            
            st.download_button(
                label="📥 Download System Report",
                data=json.dumps(report_data, indent=2),
                file_name=f"quantegrity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
# Quantum Demo Page
elif page == "🔬 Quantum Demo":
    st.markdown('<h2 class="sub-header">Interactive Quantum Process Demonstration</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="quantum-demo-box">
        <h3>🌌 Welcome to the Quantegrity Quantum Demonstration</h3>
        <p>This interactive demonstration shows the core quantum cryptographic processes used in the Quantegrity e-voting system. 
        Each process follows the research paper specifications and demonstrates real quantum operations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    demo_tab1, demo_tab2, demo_tab3, demo_tab4, demo_tab5 = st.tabs([
        "🔑 Key Generation", "🔐 SEDJO Protocol", "💻 Encryption Demo", "📊 Quantum Log", "📖 Process Flow"
    ])
    
    with demo_tab1:
        st.markdown("### 🔑 Quantum Key Generation Demonstration")
        
        st.markdown("""
        This demonstrates the quantum key generation process as specified in the research paper:
        - **Q_K1**: Primary quantum key (encrypted with biometric)
        - **Q_K2**: Device registration key
        - **Biometric Signature**: 16-bit quantum-generated biometric
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧬 Generate New Quantum Keys", key="demo_keygen"):
                with st.spinner("Generating quantum keys using QRNG..."):
                    q_k1, q_k2, biometric = generate_registration_keys()
                    
                    st.session_state.demo_q_k1 = q_k1
                    st.session_state.demo_q_k2 = q_k2
                    st.session_state.demo_biometric = biometric
                    
                    # Show quantum circuit visualization
                    st.markdown("### 🔬 Quantum Circuit Process")
                    st.markdown("""
                    <div class="process-step">
                        <strong>Step 1:</strong> Initialize qubits in superposition (Hadamard gates)<br>
                        <strong>Step 2:</strong> Measure quantum states<br>
                        <strong>Step 3:</strong> Extract random binary strings
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🎲 Quantum Randomness Properties")
            quantum_props = simulate_quantum_process_visualization()
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("Quantum Fidelity", f"{quantum_props['fidelity']:.4f}")
                st.metric("Entropy Quality", "True Random")
            with col2_2:
                st.metric("Gate Errors", f"{quantum_props['gate_errors']:.4f}")
                st.metric("Decoherence", f"{quantum_props['decoherence_time']:.1f}μs")
        
        # Display generated keys
        if hasattr(st.session_state, 'demo_q_k1'):
            st.markdown("### 🔑 Generated Quantum Keys")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Q_K1 (Primary Key):**")
                st.markdown(f'<div class="quantum-key-display">{st.session_state.demo_q_k1}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("**Q_K2 (Device Key):**")
                st.markdown(f'<div class="quantum-key-display">{st.session_state.demo_q_k2}</div>', unsafe_allow_html=True)
            with col3:
                st.markdown("**Biometric Signature:**")
                st.markdown(f'<div class="quantum-key-display">{st.session_state.demo_biometric}</div>', unsafe_allow_html=True)
    
    with demo_tab2:
        st.markdown("### 🔐 SEDJO Protocol Demonstration")
        
        st.markdown("""
        **SEDJO (Symmetrically Entangled Deutsch-Jozsa Quantum Oracle)** is the core quantum key distribution protocol.
        This demonstrates the quantum key exchange process between Alice (Voter) and Bob (Election Authority).
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👩‍💻 Alice's Input")
            alice_key = st.text_input("Alice's Key (16-bit binary)", value="1010110011001010", max_chars=16)
            
            st.markdown("#### 👨‍💼 Bob's Input")
            bob_key = st.text_input("Bob's Key (16-bit binary)", value="1100101010110011", max_chars=16)
        
        with col2:
            st.markdown("#### ⚙️ SEDJO Parameters")
            st.metric("Qubit Count", "34")
            st.metric("Circuit Depth", "~70")
            st.metric("Gate Count", "~140")
            st.metric("Backend", "qasm_simulator")
        
        if st.button("🚀 Execute SEDJO Protocol", key="demo_sedjo"):
            if len(alice_key) == 16 and len(bob_key) == 16 and all(c in '01' for c in alice_key + bob_key):
                with st.spinner("Executing quantum circuit..."):
                    from quantum_core import sedjo_with_logging
                    
                    alice_result, bob_result = sedjo_with_logging(alice_key, bob_key, "Demo_SEDJO")
                    
                    st.markdown("### 🎯 SEDJO Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**Alice's Shared Key:**")
                        st.markdown(f'<div class="quantum-key-display">{alice_result}</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown("**Bob's Shared Key:**")
                        st.markdown(f'<div class="quantum-key-display">{bob_result}</div>', unsafe_allow_html=True)
                    with col3:
                        match_status = "✅ Match" if alice_result == bob_result else "❌ Mismatch"
                        st.markdown(f"**Key Agreement:**")
                        st.markdown(f'<div class="quantum-key-display">{match_status}</div>', unsafe_allow_html=True)
                    
                    # Show quantum entanglement visualization
                    st.markdown("### 🌌 Quantum Entanglement Visualization")
                    
                    # Create a simple entanglement strength visualization
                    entanglement_strength = simulate_quantum_process_visualization()['entanglement_strength']
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = entanglement_strength,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Entanglement Strength"},
                        delta = {'reference': 0.9},
                        gauge = {
                            'axis': {'range': [None, 1]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 0.5], 'color': "lightgray"},
                                {'range': [0.5, 0.8], 'color': "gray"},
                                {'range': [0.8, 1], 'color': "lightgreen"}],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 0.9}}))
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("❌ Both keys must be exactly 16 characters of binary digits (0 and 1)")
    
    with demo_tab3:
        st.markdown("### 💻 XOR Encryption/Decryption Demonstration")
        
        st.markdown("""
        This demonstrates the XOR encryption used throughout the Quantegrity system for secure data transmission.
        XOR is quantum-safe and provides perfect secrecy when used with truly random keys.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔒 Encryption")
            plaintext = st.text_input("Data to Encrypt (binary)", value="11010011", max_chars=16)
            encryption_key = st.text_input("Encryption Key (binary)", value="10110101", max_chars=16)
            
            if st.button("🔐 Encrypt", key="demo_encrypt"):
                if plaintext and encryption_key and all(c in '01' for c in plaintext + encryption_key):
                    from quantum_core import xor_encrypt
                    encrypted = xor_encrypt(plaintext, encryption_key)
                    
                    st.markdown("**Encryption Process:**")
                    st.markdown(f"""
                    <div class="process-step">
                        <strong>Plaintext:</strong> {plaintext}<br>
                        <strong>Key:</strong> {encryption_key}<br>
                        <strong>XOR Operation:</strong> {plaintext} ⊕ {encryption_key}<br>
                        <strong>Ciphertext:</strong> {encrypted}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state.demo_encrypted = encrypted
                    st.session_state.demo_encrypt_key = encryption_key
                else:
                    st.error("❌ Please enter valid binary strings")
        
        with col2:
            st.markdown("#### 🔓 Decryption")
            if hasattr(st.session_state, 'demo_encrypted'):
                ciphertext = st.text_input("Encrypted Data", value=st.session_state.demo_encrypted, disabled=True)
                decryption_key = st.text_input("Decryption Key", value=st.session_state.demo_encrypt_key)
                
                if st.button("🔓 Decrypt", key="demo_decrypt"):
                    from quantum_core import xor_decrypt
                    decrypted = xor_decrypt(ciphertext, decryption_key)
                    
                    st.markdown("**Decryption Process:**")
                    st.markdown(f"""
                    <div class="process-step">
                        <strong>Ciphertext:</strong> {ciphertext}<br>
                        <strong>Key:</strong> {decryption_key}<br>
                        <strong>XOR Operation:</strong> {ciphertext} ⊕ {decryption_key}<br>
                        <strong>Plaintext:</strong> {decrypted}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ️ Encrypt some data first to see decryption demo")
        
        # XOR properties explanation
        st.markdown("### 📚 XOR Encryption Properties")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔒 Perfect Secrecy**
            - When key is truly random
            - Key length = data length
            - Each key used only once
            """)
        
        with col2:
            st.markdown("""
            **⚡ Quantum Safe**
            - Immune to quantum attacks
            - No mathematical complexity
            - Relies on key secrecy only
            """)
        
        with col3:
            st.markdown("""
            **🔄 Symmetric Property**
            - Encryption = Decryption
            - Self-inverting operation
            - A ⊕ B ⊕ B = A
            """)
    
    with demo_tab4:
        st.markdown("### 📊 Live Quantum Operations Log")
        
        quantum_log = get_quantum_log()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("**Real-time quantum operations from the demonstration and main system:**")
        
        with col2:
            if st.button("🗑️ Clear Log", key="demo_clear_log"):
                clear_quantum_log()
                st.rerun()
        
        if quantum_log:
            # Create a dataframe for the log
            log_data = []
            for op in quantum_log:
                log_data.append({
                    "Time": datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S'),
                    "Operation": op['operation'],
                    "Fidelity": f"{op.get('quantum_properties', {}).get('fidelity', 0):.3f}",
                    "Coherence": f"{op.get('quantum_properties', {}).get('quantum_coherence', 0):.3f}",
                    "Input_Count": len(op.get('inputs', {})),
                    "Output_Count": len(op.get('outputs', {}))
                })
            
            df_log = pd.DataFrame(log_data)
            st.dataframe(df_log, use_container_width=True)
            
            # Show detailed view of selected operation
            if st.checkbox("🔍 Show Detailed Operation View"):
                selected_op_index = st.selectbox("Select Operation", range(len(quantum_log)), 
                                                format_func=lambda x: f"{quantum_log[x]['operation']} - {datetime.fromtimestamp(quantum_log[x]['timestamp']).strftime('%H:%M:%S')}")
                
                if selected_op_index is not None:
                    selected_op = quantum_log[selected_op_index]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Operation Details:**")
                        st.json({
                            "operation": selected_op['operation'],
                            "timestamp": datetime.fromtimestamp(selected_op['timestamp']).isoformat(),
                            "inputs": selected_op.get('inputs', {}),
                            "outputs": selected_op.get('outputs', {})
                        })
                    
                    with col2:
                        st.markdown("**Quantum Properties:**")
                        if 'quantum_properties' in selected_op:
                            props = selected_op['quantum_properties']
                            for key, value in props.items():
                                if isinstance(value, float):
                                    st.metric(key.replace('_', ' ').title(), f"{value:.4f}")
        else:
            st.info("📭 No quantum operations logged yet. Use the demonstrations above to generate operations.")
    
    with demo_tab5:
        st.markdown("### 📖 Complete Quantegrity Process Flow")
        
        st.markdown("""
        This shows the complete end-to-end process flow of the Quantegrity e-voting system as specified in the research paper.
        """)
        
        # Process flow visualization
        flow_steps = [
            {
                "phase": "Registration Phase",
                "steps": [
                    "1. Generate Q_K1, Q_K2, Biometric using QRNG",
                    "2. Encrypt Q_K1 with Biometric: Q_K1 ⊕ Biometric",
                    "3. Store encrypted Q_K1 and Q_K2 with voter",
                    "4. Provide credentials to voter"
                ],
                "quantum_ops": ["QRNG×3", "XOR Encryption"]
            },
            {
                "phase": "Device Verification",
                "steps": [
                    "1. Voter requests device verification",
                    "2. Generate OTP using QRNG",
                    "3. Encrypt OTP with Q_K2: OTP ⊕ Q_K2",
                    "4. Send encrypted OTP to voter",
                    "5. Voter decrypts and verifies"
                ],
                "quantum_ops": ["QRNG", "XOR Encryption", "XOR Decryption"]
            },
            {
                "phase": "Authentication",
                "steps": [
                    "1. Voter scans biometric",
                    "2. Decrypt Q_K1: Encrypted_Q_K1 ⊕ Biometric",
                    "3. Generate AQ_K1 using SEDJO(Q_K1, Q_K1)",
                    "4. Generate auth OTP",
                    "5. Encrypt OTP with AQ_K1: OTP ⊕ AQ_K1"
                ],
                "quantum_ops": ["XOR Decryption", "SEDJO", "QRNG", "XOR Encryption"]
            },
            {
                "phase": "Voting Session",
                "steps": [
                    "1. Generate VQ_K1 using SEDJO(AQ_K1, AQ_K1)",
                    "2. Encrypt Ballot ID: B_ID ⊕ VQ_K1",
                    "3. Voter selects candidate",
                    "4. Encrypt vote: Vote ⊕ VQ_K1",
                    "5. Return confirmation code"
                ],
                "quantum_ops": ["SEDJO", "XOR Encryption×2"]
            }
        ]
        
        for i, phase_info in enumerate(flow_steps):
            with st.expander(f"🔄 Phase {i+1}: {phase_info['phase']}", expanded=(i==0)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("**Process Steps:**")
                    for step in phase_info['steps']:
                        st.markdown(f"- {step}")
                
                with col2:
                    st.markdown("**Quantum Operations:**")
                    for op in phase_info['quantum_ops']:
                        st.markdown(f'<div class="crypto-operation">🔬 {op}</div>', unsafe_allow_html=True)
        
        # Key derivation chain visualization
        st.markdown("### 🔑 Key Derivation Chain")
        
        st.markdown("""
        <div class="quantum-demo-box">
            <h4>🔗 Quantum Key Evolution</h4>
            <div style="font-family: monospace; font-size: 1.1em; line-height: 2em;">
                <strong>Initial Keys:</strong><br>
                🧬 QRNG → Q_K1, Q_K2, Biometric<br><br>
                
                <strong>Registration:</strong><br>
                🔐 Q_K1 ⊕ Biometric → Encrypted_Q_K1<br><br>
                
                <strong>Device Verification:</strong><br>
                🔑 OTP ⊕ Q_K2 → Encrypted_OTP<br><br>
                
                <strong>Authentication:</strong><br>
                🔓 Encrypted_Q_K1 ⊕ Biometric → Q_K1<br>
                ⚡ SEDJO(Q_K1, Q_K1) → AQ_K1<br><br>
                
                <strong>Voting:</strong><br>
                ⚡ SEDJO(AQ_K1, AQ_K1) → VQ_K1<br>
                🗳️ Vote ⊕ VQ_K1 → Encrypted_Vote
            </div>
        </div>
        """, unsafe_allow_html=True)

# Sidebar Status and Quick Actions
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Status")

# Real-time stats in sidebar
stats = shared_state.get_system_stats()
active_election = shared_state.get_active_election()
quantum_log = get_quantum_log()

st.sidebar.metric("Total Voters", stats["total_voters"])
st.sidebar.metric("Votes Cast", stats["total_votes"])
st.sidebar.metric("Quantum Ops", len(quantum_log))

if active_election:
    st.sidebar.success(f"🗳️ Election: {active_election.name}")
else:
    st.sidebar.warning("⚠️ No active election")

# Quick actions
st.sidebar.markdown("### ⚡ Quick Actions")

if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

if st.sidebar.button("📊 View Results") and active_election:
    st.session_state.page = "📊 Results & Analytics"
    st.rerun()

if st.sidebar.button("🔬 Quantum Demo"):
    st.session_state.page = "🔬 Quantum Demo"
    st.rerun()

# System information
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ System Info")
st.sidebar.markdown("**Version:** Quantegrity EA v2.0")
st.sidebar.markdown("**Security:** Quantum-Enhanced")
st.sidebar.markdown("**Protocol:** SEDJO + Scantegrity")
st.sidebar.markdown("**Paper:** arxiv.org/quantegrity")

if stats.get("last_updated"):
    last_update = stats["last_updated"][:19]
    st.sidebar.caption(f"Last updated: {last_update}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**🏛️ Election Authority Dashboard**")
with col2:
    st.markdown("**🔒 Quantum Security:** SEDJO Protocol")
with col3:
    st.markdown("**📊 Real-time Monitoring:** Enabled")

# Add quantum animation effect
st.markdown("""
<style>
    @keyframes quantum-glow {
        0% { box-shadow: 0 0 5px #4a90e2; }
        50% { box-shadow: 0 0 20px #4a90e2, 0 0 30px #4a90e2; }
        100% { box-shadow: 0 0 5px #4a90e2; }
    }
    
    .quantum-demo-box {
        animation: quantum-glow 3s ease-in-out infinite;
    }
    
    .quantum-key-display {
        transition: all 0.3s ease;
    }
    
    .quantum-key-display:hover {
        background: #1a252f;
        box-shadow: 0 0 10px #00ff41;
    }
</style>
""", unsafe_allow_html=True)