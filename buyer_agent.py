import urllib.request
import urllib.parse
import json
import uuid
import time
from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account import Account
import sys

def execute_bounty_hunt():
    """
    Simulates a Buyer Agent finding a bounty, completing the work, 
    and paying the APG using EIP-712 off-chain state channels.
    This executes the x402-payment-verification meta-skill.
    """
    # 1. Generate a temporary off-chain wallet for the buyer agent
    Account.enable_unaudited_hdwallet_features()
    acct = Account.create()
    agent_uuid = str(uuid.uuid4())
    
    # 2. Cryptographic EIP-712 Signature (The x402 Header)
    # The message EXACTLY matches what the APG expects in Phase 3
    msg_text = f"Phylosophy AGI Agent Payment: {agent_uuid}"
    message = encode_defunct(text=msg_text)
    signed_message = acct.sign_message(message)
    signature_hex = signed_message.signature.hex()
    
    # 3. Hit the APG
    url = "http://127.0.0.1:8402/api/v1/pay"
    headers = {
        "x402-agent-uuid": agent_uuid,
        "x402-signature": signature_hex,
        "Content-Type": "application/json"
    }
    
    # Empty payload, payment is strictly in the headers
    data = json.dumps({}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(json.dumps({
                "agent_status": "x402_payment_accepted",
                "wallet": acct.address,
                "server_response": res
            }))
            return True
    except urllib.error.HTTPError as e:
        print(json.dumps({
            "agent_status": "x402_payment_rejected",
            "error_code": e.code,
            "reason": e.read().decode("utf-8")
        }))
        return False
    except Exception as e:
        print(json.dumps({
            "agent_status": "x402_network_failure",
            "error": str(e)
        }))
        return False

if __name__ == "__main__":
    execute_bounty_hunt()
