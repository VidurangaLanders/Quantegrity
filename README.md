# Quantegrity: A Quantum-Enhanced E-Voting System Simulation

This project is a Streamlit web application that simulates the **Quantegrity e-voting system**. It provides an interactive demonstration of a hybrid classical-quantum voting architecture that combines the end-to-end verifiability of the Scantegrity protocol with the enhanced security guarantees of quantum cryptography.

The system is based on the concepts outlined in the research paper: *Quantum e-voting system using QKD and enhanced quantum oracles* by *Viduranga Landers*. It utilizes the `qiskit` library to simulate quantum behaviors for key distribution and random number generation.

Link to paper: https://doi.org/10.1007/978-3-031-82031-1_4

---

## 🌌 Overview

As cyber-attacks grow in sophistication and the era of quantum computing approaches, classical cryptographic methods used in traditional e-voting systems face increasing vulnerabilities. The Quantegrity system is designed to be resilient to both classical and quantum threats, ensuring the security and integrity of modern democratic processes.

This application simulates the entire election lifecycle, from setup and voter registration to casting votes, auditing, and tallying results, with key processes secured by simulated quantum protocols.

## 🏆 Achievements

A quantum network based version of this application (using `QNE-ADK` and `squidasm` libraries) was recognized as an honorable mention (Top 3 submissions) in the Quantum Internet Application Challenge hosted by the Quantum Internet Alliance (QIA).
Link to repo: https://github.com/VidurangaLanders/QIA-Quantegrity

## ✨ Features

### Quantum Security Features
* **Quantum Key Distribution (QKD):** Implements the **Symmetrically Entangled Deutsch-Jozsa Oracle (SEDJO)** protocol to securely generate and distribute cryptographic keys between voters and the election authority. Any eavesdropping attempt on the key exchange would introduce detectable errors, thanks to fundamental principles of quantum mechanics like the no-cloning theorem.
* **Quantum Random Number Generation (QRNG):** Utilizes quantum superposition and measurement to generate true random numbers. This is crucial for creating unpredictable voter IDs, ballot confirmation codes, and for shuffling ballots to prevent bias.
* **Quantum-Secured Authentication:** Voter identity is verified through a challenge-response mechanism using keys established via the SEDJO protocol, ensuring that only the legitimate voter can proceed.

### Verifiability & Integrity (Scantegrity II Protocol)
* **End-to-End (E2E) Verifiability:** Based on the Scantegrity voting system, which allows voters to confirm their votes were correctly recorded without compromising anonymity.
* **Invisible Ink Confirmation Codes:** Simulates the use of ballots with hidden confirmation codes that are "revealed" when a voter makes a selection. Voters receive a receipt with this code.
* **Cryptographic Mixnets:** Employs a series of publicly verifiable tables (P, Q, R, S) to anonymize votes before tallying, ensuring voter privacy.
* **Public Bulletin Board:** All cast votes (represented by their confirmation codes) and audit data are posted to a public, immutable bulletin board, allowing anyone to verify the election tally.
* **Ballot Auditing:** Voters can choose to "spoil" a ballot to audit it. The system will reveal all confirmation codes for that ballot, allowing the voter to verify its integrity.

---

## ⚙️ System Workflow

The application is divided into several pages, each representing a stage of the election process:

1.  **🏠 Home:** An overview of the system, its features, and live status metrics.
2.  **⚙️ Election Setup:** The election authority configures the election by defining the candidates and the number of expected voters. The system pre-generates the cryptographic mixnet tables (P, Q, R, S).
3.  **👤 Voter Registration:** Voters are registered with their personal information. The system generates a unique Voter ID and a secret quantum key for each voter using QRNG.
4.  **🗳️ Voting:**
    * A registered voter selects their name from a list.
    * They authenticate using their simulated biometric data and the secret quantum key. This triggers a **SEDJO QKD exchange** to secure the session.
    * Upon successful authentication, the voter is issued a ballot. They select a candidate, and the corresponding confirmation code is revealed and stored as their receipt.
    * The vote is cryptographically "flagged" in the mixnet tables and posted anonymously to the bulletin board.
5.  **🔍 Audit & Verification:**
    * **Ballot Audit:** Users can request an audit ballot, which reveals all its confirmation codes for inspection.
    * **Bulletin Board:** Displays all entries (cast votes, audited ballots) with their cryptographic signatures, ensuring transparency.
    * **Quantum Logs:** Shows a log of all quantum key exchanges that have occurred.
6.  **📊 Results:** Displays the final election tally, calculated from the mixnet's "S" table. The results are visualized with bar and pie charts. The election can be cryptographically "sealed" here.
7.  **🔬 Quantum Insights:** A technical deep-dive into the quantum primitives, allowing users to:
    * Generate random numbers with the QRNG.
    * Perform a standalone SEDJO key exchange.
    * View the complete state of the system's cryptographic tables.

---

## 🚀 Installation and Usage

### Prerequisites
* Python 3.8+
* pip package manager

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install the required libraries:**
    ```bash
    pip install streamlit pandas plotly qiskit qiskit-aer numpy
    ```

### Running the Application

1.  Navigate to the directory containing the `quantegrity_app.py` script.
2.  Run the following command in your terminal:
    ```bash
    streamlit run quantegrity_app.py
    ```
3.  The application will open in a new tab in your default web browser.

---

## 📂 Code Structure

The application is contained within a single Python script and is organized into several key components:

* **Quantum Components:**
    * `sedjo(A, B)`: A function that simulates the SEDJO QKD protocol using a `qiskit` quantum circuit.
    * `qrng(n)`: A function that simulates a Quantum Random Number Generator.

* **Cryptographic & Utility Functions:**
    * `xor_encrypt()`, `xor_decrypt()`, `binary_xor()`: Helper functions for simple cryptographic operations.
    * `generate_qrng_key()`, `generate_qrng_string()`, `generate_voter_id()`: Functions that use QRNG to create secure, random data.

* **Core Data Structures (Classes):**
    * `ScantegrityBallot`: Represents a single ballot with choices and confirmation codes.
    * `MixnetTables`: Holds the P, Q, R, and S tables for vote anonymization.
    * `MixnetGenerator`: Manages the creation and state of the mixnet tables.
    * `BulletinBoard`: Manages the public, verifiable log of election events.
    * `QuantumVoter`: Represents a voter, holding their ID and quantum key.
    * `QuantumElectionAuthority`: The central authority that manages voter registration, ballot issuance, and vote tallying.
    * `EnhancedQuantegritySystem`: The main class that encapsulates the entire voting system logic.

* **Streamlit UI:**
    * The final part of the script uses the `streamlit` library to create the interactive multi-page web interface, with separate sections for each stage of the election process.

---

## 📜 License

This project is intended for demonstration and educational purposes. It is licensed under the MIT License.