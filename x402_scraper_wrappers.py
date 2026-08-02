"""x402 Stealth Web Scraper — LangChain & CrewAI tool wrappers.

Makes the pay-per-call x402 scraping endpoint callable from the two most
popular agent frameworks. Payment is a 0.05 USDC transfer on Base Mainnet
to the recipient wallet; the tx hash is passed as the X-402-Payment-Proof
header.

Endpoint:  http://54.168.247.83:8402/api/v1/scrape?url=<TARGET>
Manifest:  http://54.168.247.83:8402/.well-known/x402.json
Recipient: 0x29C814FA1b67c23ec614bFc96C80f2274301cEBc
"""

import json
from typing import Optional

import httpx

ENDPOINT = "http://54.168.247.83:8402/api/v1/scrape"
RECIPIENT_WALLET = "0x29C814FA1b67c23ec614bFc96C80f2274301cEBc"
PRICE_USDC = "0.05"


def send_payment(tx_hash: str, target_url: str) -> dict:
    """Call the x402 scraper with an on-chain payment proof."""
    resp = httpx.get(
        ENDPOINT,
        params={"url": target_url},
        headers={"X-402-Payment-Proof": tx_hash},
        timeout=30,
    )
    return {
        "status_code": resp.status_code,
        "body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
    }


# --------------------------------------------------------------------------
# LangChain tool
# --------------------------------------------------------------------------
def langchain_scrape_tool():
    """Returns a LangChain @tool for the x402 scraper.

    Usage:
        from langchain_core.tools import tool
        tools = [langchain_scrape_tool()]
        # agent.llm.bind_tools(tools) ... agent.invoke(...)
    """
    from langchain_core.tools import tool

    @tool
    def x402_scrape(target_url: str, payment_tx_hash: str = "") -> str:
        """Scrape any public webpage and return clean Markdown/HTML.

        Requires a 0.05 USDC payment on Base Mainnet to
        0x29C814FA1b67c23ec614bFc96C80f2274301cEBc. Pass the confirmed
        transaction hash as payment_tx_hash. Without payment, the endpoint
        returns HTTP 402 with payment instructions in the body.

        Args:
            target_url: The webpage URL to scrape.
            payment_tx_hash: On-chain 0.05 USDC transfer tx hash (0x-prefixed).
        """
        result = send_payment(payment_tx_hash, target_url)
        return json.dumps(result, indent=2)

    return x402_scrape


# --------------------------------------------------------------------------
# CrewAI tool
# --------------------------------------------------------------------------
def crewai_scrape_tool():
    """Returns a CrewAI Tool for the x402 scraper.

    Usage:
        from crewai import Agent, Task, Crew
        agent = Agent(role="researcher", goal="gather data",
                      tools=[crewai_scrape_tool()], llm=...)
    """
    from crewai import Tool

    return Tool(
        name="x402_scrape",
        description=(
            "Scrape any public webpage and return clean Markdown/HTML. "
            "Pay 0.05 USDC on Base Mainnet to 0x29C814FA1b67c23ec614bFc96C80f2274301cEBc "
            "and pass the tx hash as the second argument. Returns HTTP 402 with "
            "instructions if unpaid."
        ),
        func=lambda target_url, payment_tx_hash="": send_payment(payment_tx_hash, target_url),
    )


if __name__ == "__main__":
    print("x402 Stealth Web Scraper wrappers")
    print(f"  Endpoint:  {ENDPOINT}")
    print(f"  Recipient: {RECIPIENT_WALLET}")
    print(f"  Price:     {PRICE_USDC} USDC on Base Mainnet")
    print("Unpaid probe:", json.dumps(send_payment("", "https://example.com"), indent=2)[:400])
