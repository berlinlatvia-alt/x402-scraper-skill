---
tags: [x402, integration, spec, agent-native]
---

# x402 Integration Spec — One Page for the Human Operator

## What This Is

An HTTP 402 "Payment Required" endpoint that agents call, pay $0.05 USDC, and get a rendered webpage back. **The endpoint is agent-native. This page is for the human wiring it in.**

## Architecture

```
Agent → agentskill.sh discovery → x402 endpoint → $0.05 USDC → response
```

## Endpoint

| Property | Value |
|----------|-------|
| URL | `http://54.168.247.83:8402/api/v1/scrape` |
| Health | `http://54.168.247.83:8402/api/v1/health` |
| Protocol | HTTP 402 (x402) |
| Payment | 0.05 USDC on Base Mainnet |
| Wallet | `0x29C814FA1b67c23ec614bFc96C80f2274301cEBc` |

## How an Agent Calls It

1. Send 0.05 USDC to wallet on Base Mainnet
2. Call `POST /api/v1/scrape` with header `X-402-Payment-Proof: <tx_hash>`
3. Body: `{"url": "https://target.com/page"}`
4. Receive: rendered HTML/Markdown of the target page

## How to Integrate

```python
# Agent pseudocode
tx_hash = send_usdc("0x29C814FA...", 0.05, "base-mainnet")
response = requests.post(
    "http://54.168.247.83:8402/api/v1/scrape",
    headers={"X-402-Payment-Proof": tx_hash},
    json={"url": target_url}
)
content = response.json()["markdown"]
```

## Status

- ✅ VPS online (Tokyo)
- ✅ Endpoint responding
- ✅ Wallet configured
- ⏳ First payment not yet received
- ⏳ Not yet listed on agentskill.sh (needs Git repo claimed)

## Where to List

| Registry | Status | Action |
|----------|--------|--------|
| agentskill.sh | ❌ Not claimed | Claim repo, submit manifest |
| x402 Bazaar | ❌ Not listed | Submit via form |
| GitHub agent-skills | ⏳ Listed but unclaimed | Claim ownership |

## Rules

1. One endpoint. No new endpoints until first payment clears. (C3)
2. Only 0.05 USDC. No price changes until first sale. (C5)
3. No new infra. VPS is all we get until revenue. (C1/C6)
