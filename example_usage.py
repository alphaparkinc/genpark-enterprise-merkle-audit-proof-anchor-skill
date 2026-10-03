"""Example usage for EnterpriseMerkleAuditProofAnchor."""
import sys
import json
from client import EnterpriseMerkleAuditProofAnchor

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=== Cryptographic Enterprise Merkle Audit Proof Anchor Demo ===")
    anchor = EnterpriseMerkleAuditProofAnchor()

    audit_events = [
        {"seq": 1, "actor": "workbuddy_finance_agent", "action": "INGEST_BALANCE_SHEET", "doc_id": "DOC-9912"},
        {"seq": 2, "actor": "workbuddy_finance_agent", "action": "GENERATE_PPT_SLIDES", "deck_id": "DECK-4412"},
        {"seq": 3, "actor": "compliance_auditor", "action": "SIGNOFF_CLEARANCE", "status": "APPROVED"},
        {"seq": 4, "actor": "workbuddy_finance_agent", "action": "DELEGATED_PAYMENT", "amount_usd": 15000}
    ]

    print("\n--- 1. Building Merkle Audit Tree ---")
    tree = anchor.anchor_audit_events(audit_events)
    print(f"Total Log Events Anchored: {tree['total_leaves']}")
    print(f"Cryptographic Merkle Root: {tree['merkle_root_hash']}")

    print("\n--- 2. Generating Tamper-Proof Inclusion Proof for Event #3 ---")
    proof = anchor.generate_inclusion_proof(leaf_index=2)
    print(json.dumps(proof, indent=2))

    print("\n--- 3. Verifying Inclusion Proof Validity ---")
    verification = anchor.verify_inclusion_proof(
        leaf_hash=proof["leaf_hash"],
        proof_path=proof["audit_proof_path"],
        expected_root=tree["merkle_root_hash"]
    )
    print(f"Proof Cryptographically Valid: {verification['valid']} (Tamper Detected: {verification['tamper_detected']})")

if __name__ == "__main__":
    main()
