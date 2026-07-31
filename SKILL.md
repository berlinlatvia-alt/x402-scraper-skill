---
name: x402-stealth-scraper
description: Pay-per-call web scraper API for AI agents. Converts any web URL into clean Markdown text using x402 Base USDC micropayments ($0.05/req).
---

# 🌐 x402 Stealth Web Scraper Skill

## Overview
High-speed headless rendering and Markdown web scraping API for autonomous AI agents.
Agents pay $0.05 USDC per call on Base Mainnet via HTTP 402 protocol -- no API keys, no subscriptions.

## Endpoint Details
* **Scrape Endpoint**: `http://54.168.247.83/api/v1/scrape`
* **Health Check**: `http://54.168.247.83/api/v1/health`
* **Price**: 0.05 USDC / call
* **Network**: Base Mainnet (`0x29C814FA1b67c23ec614bFc96C80f2274301cEBc`)

## Integration Example (Python)
```python
import urllib.request, json

# Step 1: Send request to scrape endpoint
url = "http://54.168.247.83/api/v1/scrape?url=https://example.com"
try:
    resp = urllib.request.urlopen(url)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    if e.code == 402:
        # Step 2: Handle HTTP 402 payment challenge
        challenge = json.loads(e.read().decode())
        print("X402 Challenge Received:", challenge)
```
