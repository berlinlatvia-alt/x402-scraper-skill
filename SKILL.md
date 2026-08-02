---
name: x402-stealth-scraper
description: Pay-per-call web scraper API for AI agents. Converts any web URL into clean Markdown text using x402 Base USDC micropayments ($0.05/req). Use when an agent needs to extract readable content from a URL for summarization, analysis, or data extraction.
---

# x402 Stealth Web Scraper Skill

## Overview
High-speed headless rendering and Markdown web scraping API for autonomous AI agents.
Agents pay $0.05 USDC per call on Base Mainnet via HTTP 402 protocol -- no API keys, no subscriptions.

## Endpoint Details
* **Scrape Endpoint**: `http://54.168.247.83:8402/api/v1/scrape?url=<TARGET>`
* **Discovery Manifest**: `http://54.168.247.83:8402/.well-known/x402.json`
* **Health Check**: `http://54.168.247.83:8402/api/v1/health`
* **Price**: 0.05 USDC / call
* **Network**: Base Mainnet (eip155:8453)
* **Recipient Wallet**: `0x29C814FA1b67c23ec614bFc96C80f2274301cEBc`
* **Payment Proof**: attach confirmed tx hash in the `X-402-Payment-Proof` header

## Integration Example (Python)
```python
import urllib.request, json

# Step 1: Send request to scrape endpoint (unpaid -> HTTP 402 challenge)
url = "http://54.168.247.83:8402/api/v1/scrape?url=https://example.com"
try:
    resp = urllib.request.urlopen(url)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    if e.code == 402:
        # Step 2: Handle HTTP 402 payment challenge
        challenge = json.loads(e.read().decode())
        print("X402 Challenge Received:", challenge)
        # Pay 0.05 USDC on Base to 0x29C814FA1b67c23ec614bFc96C80f2274301cEBc
        # then retry with the confirmed tx hash:
        req = urllib.request.Request(url, headers={"X-402-Payment-Proof": "0xYOUR_TX_HASH"})
        print(urllib.request.urlopen(req).read().decode())
```

## Agent Framework Wrappers
LangChain and CrewAI tool wrappers are in `x402_scraper_wrappers.py` in this repo:
```python
from x402_scraper_wrappers import langchain_scrape_tool, crewai_scrape_tool
# tools = [langchain_scrape_tool()]   # LangChain
# tools = [crewai_scrape_tool()]      # CrewAI
```

## Links
* Landing page: https://berlinlatvia-alt.github.io/x402-scraper-skill/
* Examples (curl / Python / JS): https://gist.github.com/berlinlatvia-alt/f00456ac570a5827b44b63d9a7dc37b0
