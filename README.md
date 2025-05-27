# Quantegrity: Quantum-Enhanced E-Voting System

A comprehensive implementation of the **Quantegrity e-voting system** - a hybrid classical-quantum voting architecture that combines the end-to-end verifiability of the Scantegrity protocol with enhanced security guarantees provided by quantum cryptography.

This system is based on the research paper: *"Quantum e-voting system using QKD and enhanced quantum oracles"* by **Viduranga Shenal Landers**.

📄 **Research Paper**: [DOI: 10.1007/978-3-031-82031-1_4](https://doi.org/10.1007/978-3-031-82031-1_4)

---

## 🌌 Overview

As cyber-attacks grow in sophistication and the era of quantum computing approaches, classical cryptographic methods used in traditional e-voting systems face increasing vulnerabilities. The Quantegrity system addresses these challenges by implementing quantum-resistant security mechanisms that are resilient to both classical and quantum threats.

This application provides a **complete interactive demonstration** of the entire election lifecycle, from quantum voter registration to secure vote casting and cryptographic verification, with all key processes secured by simulated quantum protocols.

## 🏆 Recognition

A quantum network-based version of this application was recognized as an **honorable mention (Top 3 submissions)** in the Quantum Internet Application Challenge hosted by the Quantum Internet Alliance (QIA).

🔗 **QIA Quantum Network Version**: [github.com/VidurangaLanders/QIA-Quantegrity](https://github.com/VidurangaLanders/QIA-Quantegrity)

---

## ✨ Key Features

### 🔬 Quantum Security Components

- **🌌 SEDJO Protocol (Symmetrically Entangled Deutsch-Jozsa Quantum Oracle)**
  - Custom quantum key distribution protocol using entangled qubit pairs
  - Multi-stage key derivation: Q_K1 → AQ_K1 → VQ_K1
  - Real-time quantum circuit simulation with Qiskit
  - Eavesdropping detection through quantum entanglement properties

- **🎲 Quantum Random Number Generation (QRNG)**
  - True randomness from quantum superposition and measurement
  - Used for voter IDs, confirmation codes, and cryptographic keys
  - Quantum circuit-based implementation with Hadamard gates

- **🔐 Multi-Layer Quantum Authentication**
  - **Q_K1**: Primary quantum key (biometric-encrypted)
  - **Q_K2**: Device registration and verification key
  - **AQ_K1**: Authentication session keys (SEDJO-generated)
  - **VQ_K1**: Voting session keys (SEDJO-generated)
  - XOR encryption providing quantum-safe perfect secrecy

### 🗳️ E-Voting Capabilities (Scantegrity II Protocol)

- **📋 End-to-End Verifiability**
  - Cryptographic confirmation codes for vote verification
  - Public quantum bulletin board for transparency
  - Mixnet anonymization (P, Q, R, S tables)
  - Receipt-based vote verification without compromising privacy

- **🔍 Ballot Auditing**
  - Interactive ballot spoiling for system verification
  - Confirmation code revelation for transparency demonstration
  - Quantum-secured audit trail

- **📊 Real-Time Process Monitoring**
  - Live quantum operations logging
  - Cryptographic process visualization
  - Interactive demonstrations of quantum protocols

---

## 🏗️ System Architecture

The Quantegrity system consists of two main applications:

### 🏛️ Election Authority Dashboard (`election_authority.py`)
- **Election Setup**: Configure elections, candidates, and quantum ballot pools
- **Voter Management**: Register voters with quantum credentials (Q_K1, Q_K2, Biometric)
- **Device Verification**: Approve device registrations with Q_K2-encrypted OTPs
- **Security Monitoring**: Real-time quantum operations and system integrity checks
- **Results Management**: Quantum-secured vote tallying and analytics

### 🗳️ Voter Portal (`voter_portal.py`)
- **Quantum Authentication**: Multi-stage biometric and quantum key verification
- **Device Registration**: Q_K2-based device verification with encrypted OTPs
- **Secure Voting**: VQ_K1-encrypted vote casting with quantum confirmation codes
- **Receipt Verification**: Bulletin board verification of quantum-secured receipts
- **Interactive Demos**: Hands-on exploration of quantum cryptographic processes

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+**
- **pip package manager**

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install required dependencies:**
   ```bash
   pip install streamlit pandas plotly qiskit qiskit-aer
   ```

### Running the Application

Execute the main launcher:
```bash
python run_quantegrity.py
```

Or run applications individually:
```bash
# Election Authority Dashboard (Port 8501)
streamlit run election_authority.py --server.port 8501

# Voter Portal (Port 8502)
streamlit run voter_portal.py --server.port 8502
```

**Access URLs:**
- 🏛️ **Election Authority Dashboard**: http://localhost:8501
- 🗳️ **Voter Portal**: http://localhost:8502

---

## 📖 Usage Guide

### 🔧 For Election Officials

1. **Election Setup**
   - Create election with candidates
   - Generate quantum-secured ballot pool (1000+ ballots)
   - Configure quantum security parameters

2. **Voter Registration**
   - Register voters with quantum credential generation
   - Generate Q_K1, Q_K2, and Biometric signatures using QRNG
   - Encrypt Q_K1 with biometric: `Q_K1 ⊕ Biometric → Encrypted_Q_K1`

3. **Device Verification Management**
   - Review device registration requests
   - Generate encrypted OTPs: `OTP ⊕ Q_K2 → Encrypted_OTP`
   - Approve/reject device verifications

4. **Election Monitoring**
   - Real-time quantum operations tracking
   - System integrity verification
   - Vote tallying and results analysis

### 🗳️ For Voters

1. **Login Process**
   - Enter Voter ID (16-bit binary)
   - Provide Biometric Signature (16-bit binary)
   - Input Q_K2 Device Password (16-bit binary)

2. **Device Registration**
   - Request device verification from Election Authority
   - Receive encrypted OTP from EA
   - Decrypt OTP: `Encrypted_OTP ⊕ Q_K2 → OTP`
   - Submit decrypted OTP for verification

3. **Quantum Authentication**
   - Scan biometric to decrypt Q_K1: `Encrypted_Q_K1 ⊕ Biometric → Q_K1`
   - System generates AQ_K1 via SEDJO: `SEDJO(Q_K1, Q_K1) → AQ_K1`
   - Receive authentication OTP encrypted with AQ_K1
   - Decrypt and verify: `Encrypted_Auth_OTP ⊕ AQ_K1 → Auth_OTP`

4. **Voting Session**
   - System generates VQ_K1 via SEDJO: `SEDJO(AQ_K1, AQ_K1) → VQ_K1`
   - Request quantum-secured ballot from pool
   - Select candidate and encrypt vote: `Vote ⊕ VQ_K1 → Encrypted_Vote`
   - Receive quantum confirmation code

5. **Vote Verification**
   - Use receipt ID to verify vote on quantum bulletin board
   - Check cryptographic proof and quantum signatures

---

## 🔬 Quantum Cryptography Details

### 🌌 SEDJO Protocol Implementation

The **Symmetrically Entangled Deutsch-Jozsa Quantum Oracle** protocol is implemented using Qiskit quantum circuits:

```python
def sedjo(key_a: str, key_b: str) -> Tuple[str, str]:
    """
    Quantum Key Distribution using SEDJO protocol
    - Creates entangled qubit pairs
    - Applies quantum oracles based on input keys
    - Returns shared secret keys for both parties
    """
```

**Key Generation Chain:**
1. **Registration**: `QRNG → Q_K1, Q_K2, Biometric`
2. **Encryption**: `Q_K1 ⊕ Biometric → Encrypted_Q_K1`
3. **Authentication**: `SEDJO(Q_K1, Q_K1) → AQ_K1`
4. **Voting**: `SEDJO(AQ_K1, AQ_K1) → VQ_K1`
5. **Vote Encryption**: `Vote ⊕ VQ_K1 → Encrypted_Vote`

### 🎲 Quantum Random Number Generation

```python
def qrng(length: int) -> str:
    """
    Generate true random numbers using quantum superposition
    - Creates quantum circuit with Hadamard gates
    - Measures qubits in computational basis
    - Returns binary string of specified length
    """
```

### 🔐 XOR Encryption (Quantum-Safe)

All encryption uses XOR operations with quantum-generated keys, providing perfect secrecy when combined with true quantum randomness.

---

## 🧪 Interactive Demonstrations

### 🔬 Quantum Process Demos
- **Key Generation**: Interactive QRNG demonstration
- **SEDJO Protocol**: Live quantum key exchange simulation
- **Encryption/Decryption**: XOR operations with quantum keys
- **Process Monitoring**: Real-time quantum operations logging

### 🗳️ Voting System Demos
- **Ballot Auditing**: Spoil ballots to reveal confirmation codes
- **Receipt Verification**: Check votes on quantum bulletin board
- **End-to-End Flow**: Complete voter journey simulation
- **Security Analysis**: System integrity demonstrations

---

## 📁 Code Structure

```
quantegrity/
├── run_quantegrity.py          # Main launcher application
├── election_authority.py       # Election Authority dashboard
├── voter_portal.py             # Voter portal interface
├── quantum_core.py             # Core quantum cryptography functions
├── shared_state.py             # Data management and persistence
└── quantegrity_data.json       # Election data storage
```

### 🔧 Key Components

- **`quantum_core.py`**: SEDJO protocol, QRNG, quantum operations
- **`shared_state.py`**: Voter management, ballot allocation, bulletin board
- **`election_authority.py`**: EA dashboard with quantum monitoring
- **`voter_portal.py`**: Voter interface with quantum authentication

---

## 🔒 Security Features

### 🛡️ Quantum Security Guarantees
- **Unconditional Security**: Based on quantum physics, not computational complexity
- **Eavesdropping Detection**: Quantum entanglement properties detect interception
- **Future-Proof**: Resistant to both classical and quantum computer attacks
- **Perfect Secrecy**: XOR encryption with true quantum randomness

### 🔍 Verifiability Features
- **End-to-End Verification**: Voters can verify their votes without revealing choices
- **Public Bulletin Board**: All votes recorded with quantum cryptographic proofs
- **Audit Capabilities**: Interactive ballot spoiling for transparency
- **Mixnet Anonymization**: Vote privacy through cryptographic mixing

---

## 🎯 Educational Use

This application serves as an excellent educational tool for:

- **Quantum Cryptography**: Learn SEDJO, QRNG, and quantum key distribution
- **E-Voting Security**: Understand end-to-end verifiable voting systems
- **Applied Cryptography**: See real-world applications of quantum security
- **Interactive Learning**: Hands-on exploration of quantum protocols

### 📚 Learning Modules
- **Quantum Basics**: Introduction to quantum cryptographic principles
- **Protocol Simulation**: Step-by-step quantum key exchange
- **Security Analysis**: Threat models and security proofs
- **Practical Implementation**: Real quantum circuit execution

---

## 📊 System Requirements

### 🔧 Technical Specifications
- **Python**: 3.8 or higher
- **Quantum Simulator**: Qiskit Aer backend
- **Web Framework**: Streamlit for interactive interface
- **Data Processing**: Pandas for vote analysis
- **Visualization**: Plotly for quantum process charts

### 💾 Storage & Performance
- **Data Persistence**: JSON-based local storage
- **Quantum Circuits**: Real-time execution with Qiskit
- **Scalability**: Supports 1000+ voters per election
- **Response Time**: < 1 second for quantum operations

---

## 🔬 Research Applications

### 📖 Academic Research
- **Quantum Voting Protocols**: Study and extend the SEDJO protocol
- **Security Analysis**: Analyze quantum vs. classical security
- **Performance Evaluation**: Measure quantum operation efficiency
- **Protocol Comparison**: Compare with other QKD protocols

### 🏭 Industry Applications
- **Proof of Concept**: Demonstrate quantum voting feasibility
- **Security Training**: Educate on quantum cryptographic methods
- **Protocol Testing**: Validate quantum security implementations
- **Standards Development**: Contribute to quantum voting standards

---

## 🤝 Contributing

We welcome contributions to improve the Quantegrity system:

1. **Fork the repository**
2. **Create a feature branch**
3. **Implement quantum security enhancements**
4. **Add comprehensive tests**
5. **Submit a pull request**

### 🔍 Areas for Contribution
- **Quantum Protocol Optimization**: Improve SEDJO efficiency
- **Additional QKD Protocols**: Implement BB84, E91, etc.
- **Security Analysis**: Formal verification of quantum properties
- **User Interface**: Enhanced voting experience
- **Performance Optimization**: Faster quantum simulations

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

### 📚 Citation

If you use this work in your research, please cite:

```bibtex
@article{landers2024quantegrity,
  title={Quantum e-voting system using QKD and enhanced quantum oracles},
  author={Landers, Viduranga Shenal},
  journal={Springer Nature},
  year={2024},
  doi={10.1007/978-3-031-82031-1_4}
}
```

---

## 📞 Support & Contact

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Comprehensive guides available in `/docs`
- **Research Collaboration**: Contact for academic partnerships
- **Commercial Licensing**: Available for enterprise implementations

### 🌟 Acknowledgments

- **Quantum Internet Alliance**: For recognizing the QIA version
- **Qiskit Community**: For quantum computing framework
- **Scantegrity Team**: For the foundational e-voting protocol
- **Academic Reviewers**: For valuable feedback and validation

---

## 🚀 Future Roadmap

### 🔮 Planned Enhancements
- **Real Quantum Hardware**: Integration with actual quantum devices
- **Multi-Election Support**: Concurrent election management
- **Advanced Analytics**: Quantum security metrics and analysis
- **Mobile Applications**: Native mobile voting interface
- **Blockchain Integration**: Hybrid quantum-blockchain security

### 🌐 Long-term Vision
- **Global Deployment**: Scalable quantum voting infrastructure
- **Standards Compliance**: Adherence to emerging quantum voting standards
- **Hardware Integration**: Support for commercial quantum devices
- **International Collaboration**: Multi-national quantum voting networks

---

*"Securing democracy with the power of quantum mechanics"* - **Team Quler**