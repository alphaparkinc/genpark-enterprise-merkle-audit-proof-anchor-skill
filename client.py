"""
Cryptographic Enterprise Audit Trail Merkle Tree Anchor (Zero External Dependencies)
Constructs binary Merkle trees from agent logs and generates cryptographic inclusion proofs.
"""
import time
import math
import hashlib
import json
from typing import Dict, Any, List, Optional

def sha256_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

class EnterpriseMerkleAuditProofAnchor:
    def __init__(self):
        self.leaves: List[str] = []
        self.tree_levels: List[List[str]] = []
        self.root_hash: Optional[str] = None

    def anchor_audit_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Hashes all events into leaf nodes, builds the full Merkle tree, and computes the Merkle Root.
        """
        if not events:
            return {"error": "No events provided", "root_hash": None}

        # Step 1: Hash each event deterministically
        self.leaves = [sha256_hash(json.dumps(ev, sort_keys=True)) for ev in events]

        # Step 2: Build tree levels
        current_level = list(self.leaves)
        self.tree_levels = [current_level]

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1] if i+1 < len(current_level) else left # duplicate last if odd
                combined = sha256_hash(left + right)
                next_level.append(combined)
            current_level = next_level
            self.tree_levels.append(current_level)

        self.root_hash = self.tree_levels[-1][0] if self.tree_levels else None

        return {
            "total_leaves": len(self.leaves),
            "tree_depth": len(self.tree_levels),
            "merkle_root_hash": self.root_hash,
            "anchored_at": time.time(),
            "status": "CRYPTOGRAPHICALLY_ANCHORED"
        }

    def generate_inclusion_proof(self, leaf_index: int) -> Dict[str, Any]:
        """Generates the sibling inclusion proof path for a given leaf index."""
        if not self.leaves or leaf_index >= len(self.leaves):
            return {"error": f"Leaf index {leaf_index} out of bounds"}

        proof = []
        idx = leaf_index

        for level_idx in range(len(self.tree_levels) - 1):
            level = self.tree_levels[level_idx]
            is_right_child = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right_child else (idx + 1 if idx + 1 < len(level) else idx)

            proof.append({
                "level": level_idx,
                "position": "left" if is_right_child else "right",
                "sibling_hash": level[sibling_idx]
            })
            idx = idx // 2

        return {
            "leaf_index": leaf_index,
            "leaf_hash": self.leaves[leaf_index],
            "merkle_root": self.root_hash,
            "audit_proof_path": proof
        }

    def verify_inclusion_proof(
        self,
        leaf_hash: str,
        proof_path: List[Dict[str, Any]],
        expected_root: str
    ) -> Dict[str, Any]:
        """Verifies inclusion proof path reaches expected Merkle Root."""
        current_hash = leaf_hash
        for p in proof_path:
            pos = p.get("position")
            sibling = p.get("sibling_hash")
            if pos == "left":
                current_hash = sha256_hash(sibling + current_hash)
            else:
                current_hash = sha256_hash(current_hash + sibling)

        is_valid = (current_hash == expected_root)
        return {
            "valid": is_valid,
            "calculated_root": current_hash,
            "expected_root": expected_root,
            "tamper_detected": not is_valid
        }
