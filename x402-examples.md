# x402 Paid Web Scraper API — Examples

Scrape any webpage for **0.05 USDC per request** on Base or Polygon (USDC).
No API key. Pay per request. Get clean HTML/Markdown back.

- **Endpoint:** `http://54.168.247.83:8402/api/v1/scrape?url=<TARGET_URL>`
- **Health:** `http://54.168.247.83:8402/api/v1/health`
- **Recipient wallet:** `0x29C814FA1b67c23ec614bFc96C80f2274301cEBc`
- **Networks:** Base Mainnet (8453) or Polygon POS (137), native USDC

## How it works

1. Send a request without proof → server returns `402 Payment Required` + x402 challenge.
2. Send any amount of USDC (≥0.05) to the recipient wallet on Base or Polygon.
3. Retry the request with header `X-402-Payment-Proof: <your_tx_hash>`.
4. Get `200 OK` + scraped content. Unused credits persist per tx hash (max 200).

## curl

```bash
# Step 1: get the challenge
curl "http://54.168.247.83:8402/api/v1/scrape?url=https://example.com"

# Step 2: after paying 0.05+ USDC to 0x29C814FA1b67c23ec614bFc96C80f2274301cEBc
curl -H "X-402-Payment-Proof: 0xYOUR_TX_HASH" \
  "http://54.168.247.83:8402/api/v1/scrape?url=https://example.com"
```

## Python

```python
import urllib.request, urllib.parse

TARGET = "https://example.com"
TX_HASH = "0xYOUR_TX_HASH"

url = "http://54.168.247.83:8402/api/v1/scrape?" + urllib.parse.urlencode({"url": TARGET})
req = urllib.request.Request(url, headers={"X-402-Payment-Proof": TX_HASH})
with urllib.request.urlopen(req, timeout=60) as resp:
    print(resp.status)          # 200
    print(resp.read().decode()) # scraped markdown/html
```

## JavaScript (fetch)

```js
const txHash = "0xYOUR_TX_HASH";
const res = await fetch(
  "http://54.168.247.83:8402/api/v1/scrape?url=" + encodeURIComponent("https://example.com"),
  { headers: { "X-402-Payment-Proof": txHash } }
);
console.log(res.status);            // 200
console.log(await res.text());      // scraped content
```

## Paying

Send USDC (0.05 or more) on **Base** or **Polygon** to:
`0x29C814FA1b67c23ec614bFc96C80f2274301cEBc`

One payment = up to 200 scrape credits. Credits are tracked per transaction hash.
