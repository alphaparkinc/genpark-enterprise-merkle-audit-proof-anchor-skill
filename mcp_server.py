"""MCP Server for Enterprise Merkle Audit Proof Anchor."""
import sys
import json
import time
from client import EnterpriseMerkleAuditProofAnchor

anchor = EnterpriseMerkleAuditProofAnchor()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "anchor_merkle_audit_proof":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "get_tree_root")
    if action == "anchor_audit_events":
        return anchor.anchor_audit_events(args.get("events", []))
    elif action == "generate_inclusion_proof":
        return anchor.generate_inclusion_proof(int(args.get("event_index", 0)))
    elif action == "verify_inclusion_proof":
        payload = args.get("proof_audit_payload", {})
        return anchor.verify_inclusion_proof(
            leaf_hash=payload.get("leaf_hash", ""),
            proof_path=payload.get("audit_proof_path", []),
            expected_root=payload.get("merkle_root", "")
        )
    elif action == "get_tree_root":
        return {"root_hash": anchor.root_hash, "leaves_count": len(anchor.leaves)}
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        evs = [
            {"action": "USER_LOGIN", "id": 1},
            {"action": "TOOL_INVOKE", "tool": "sql_query"},
            {"action": "PAYMENT_AUTHORIZED", "amt": 250}
        ]
        res = anchor.anchor_audit_events(evs)
        assert res["merkle_root_hash"] is not None
        proof = anchor.generate_inclusion_proof(1)
        verify = anchor.verify_inclusion_proof(proof["leaf_hash"], proof["audit_proof_path"], res["merkle_root_hash"])
        assert verify["valid"] is True
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "EnterpriseMerkleAuditProofAnchor", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "anchor_merkle_audit_proof",
                            "description": "Cryptographic Merkle tree audit anchoring: hash agent actions into Merkle trees, compute inclusion proofs, and verify audit log immutability.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["anchor_audit_events", "generate_inclusion_proof", "verify_inclusion_proof", "get_tree_root"]},
                                    "events": {"type": "array"},
                                    "event_index": {"type": "integer"},
                                    "proof_audit_payload": {"type": "object"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
