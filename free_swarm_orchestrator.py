#!/usr/bin/env python3
"""
Free Swarm Orchestrator
=======================
Delegates ALL background AGI swarm logic to OpenRouter FREE endpoints
(see OpenRouter-Free-Models-Hierarchy.md). Every call is guarded by
assert_free(): if a model id is not a :free endpoint, the dispatcher
refuses to send it. Background agent swarms therefore cost $0.

Usage:
  python free_swarm_orchestrator.py dispatch <role> "<task>" [--context "<context>"]
  python free_swarm_orchestrator.py --test            # real $0 smoke call
  python free_swarm_orchestrator.py --models          # verify registry vs live API
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import socket
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
socket.setdefaulttimeout(120)

API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_URL = "https://openrouter.ai/api/v1/models"

# Full free-model registry parsed from OpenRouter-Free-Models-Hierarchy.md (July 25, 2026).
# The two Lyria music previews are PAID ($0.04-$0.08/song) and deliberately excluded.
FREE_MODELS = {
    "orchestrator": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "orchestrator_backup": "nvidia/nemotron-3-super-120b-a12b:free",
    "code_builder": "poolside/laguna-s-2.1:free",
    "code_builder_backup": "cohere/north-mini-code:free",
    "research": "google/gemma-4-31b-it:free",
    "research_backup": "google/gemma-4-26b-a4b-it:free",
    "quick": "inclusionai/ling-3.0-flash:free",
    "tool_calling": "nvidia/nemotron-3-nano-30b-a3b:free",
    "reasoning": "openai/gpt-oss-20b:free",
    "reasoning_flex": "nvidia/nemotron-nano-9b-v2:free",
    "safety": "nvidia/nemotron-3.5-content-safety:free",
    "vision": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "video": "nvidia/nemotron-nano-12b-v2-vl:free",
    "code_light": "poolside/laguna-xs-2.1:free",
    "code_micro": "cohere/north-mini-code:free",
    "router": "openrouter/free",
}

ROLE_ASSIGNMENT = {
    "orchestrator": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "code_builder": "poolside/laguna-s-2.1:free",
    "research": "google/gemma-4-31b-it:free",
    "quick": "inclusionai/ling-3.0-flash:free",
    "safety": "nvidia/nemotron-3.5-content-safety:free",
}

ROLE_SYSTEM_PROMPTS = {
    "orchestrator": (
        "You are the AGI swarm ORCHESTRATOR. You receive a task and must return a decisive, "
        "machine-readable plan. Output valid JSON only: "
        '{"decision": "...", "actions": ["..."], "risk": "LOW|MEDIUM|HIGH"}. No prose.'
    ),
    "code_builder": (
        "You are the swarm CODE BUILDER. You receive an engineering task. Output valid JSON only: "
        '{"approach": "...", "code_pseudocode": "...", "files_affected": ["..."]}. No prose.'
    ),
    "research": (
        "You are the swarm RESEARCH analyst. You receive a question. Output valid JSON only: "
        '{"findings": ["..."], "confidence": 0.0-1.0, "sources": ["..."]}. No prose.'
    ),
    "quick": (
        "You are the swarm QUICK task handler. You receive a small task. Output the answer "
        "directly as concise JSON, e.g. {\"answer\": \"...\"}. No prose, no disclaimers."
    ),
    "safety": (
        "You are the swarm SAFETY CHECK. Review the content. Output valid JSON only: "
        '{"approved": true|false, "issues": ["..."]}. No prose.'
    ),
}

MAX_RETRIES = 3
TIMEOUT_S = 120
MICRO_BATCH_CHARS = 800


class FreeSwarmError(Exception):
    pass


def assert_free(model_id):
    """Hard $0 guard: refuse to dispatch to any non-free endpoint."""
    if model_id == "openrouter/free":
        return
    if not model_id.endswith(":free"):
        raise FreeSwarmError(
            f"PAYMENT GUARD: {model_id} is not a free endpoint. Refusing dispatch to keep swarm at $0."
        )


def _micro_batch(content, limit=MICRO_BATCH_CHARS):
    """Truncate oversized prompts when a call times out (micro-batch retry)."""
    return content if len(content) <= limit else content[:limit]


def _post(model_id, system, user, temperature, max_tokens):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def call_free_model(model_id, system, user, temperature=0.3, max_tokens=1024):
    """
    Call a free OpenRouter endpoint with retry.
    On timeout -> cancel hanging process, retry with a micro-batch prompt.
    Returns (content, cost_cent), cost_cent is always 0.0 for free endpoints.
    """
    assert_free(model_id)
    last_err = None
    for attempt in range(MAX_RETRIES):
        prompt = _micro_batch(user) if attempt > 0 else user
        try:
            content = _post(model_id, system, prompt, temperature, max_tokens)
            return content, 0.0
        except (urllib.error.URLError, socket.timeout, TimeoutError, Exception) as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise FreeSwarmError(f"All {MAX_RETRIES} attempts to {model_id} failed: {last_err}")


def parse_json_content(raw):
    """Strip code fences and extract the first JSON object/array."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start = text.find("{")
    if start == -1:
        start = text.find("[")
    if start != -1:
        try:
            return json.loads(text[start:])
        except json.JSONDecodeError:
            pass
    return None


class FreeSwarmDispatcher:
    """Routes logic tasks to the free-model roster. Every dispatch costs $0."""

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.total_calls = 0
        self.total_cost_cent = 0.0
        self.failures = 0

    def log(self, msg):
        if self.verbose:
            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] [FREE_SWARM] {msg}", flush=True)

    def dispatch(self, role, task, context="", temperature=0.3, max_tokens=1024):
        if role not in ROLE_ASSIGNMENT:
            raise FreeSwarmError(f"Unknown role '{role}'. Valid roles: {list(ROLE_ASSIGNMENT)}")
        model_id = ROLE_ASSIGNMENT[role]
        system = ROLE_SYSTEM_PROMPTS[role]
        user = task if not context else f"CONTEXT:\n{context}\n\nTASK:\n{task}"
        self.log(f"dispatch role={role} model={model_id} task={task[:80]}")
        self.total_calls += 1
        try:
            content, cost = call_free_model(model_id, system, user, temperature, max_tokens)
        except FreeSwarmError as e:
            self.failures += 1
            self.log(f"FAILED role={role}: {e}")
            raise
        parsed = parse_json_content(content)
        self.total_cost_cent += cost
        return {"model": model_id, "role": role, "cost_cent": cost, "content": content, "parsed": parsed}

    def cost_report(self):
        return {
            "total_calls": self.total_calls,
            "total_cost": f"${self.total_cost_cent / 100:.4f}",
            "total_cost_cent": self.total_cost_cent,
            "failures": self.failures,
        }


def verify_models_live():
    """Hit the live models endpoint and confirm every registry id exists and is free."""
    req = urllib.request.Request(
        MODELS_URL, headers={"Authorization": f"Bearer {API_KEY}"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    by_id = {}
    for m in data.get("data", []):
        m_id = m["id"]
        pricing = m.get("pricing", {})
        prompt_cost = float(pricing.get("prompt") or 0)
        completion_cost = float(pricing.get("completion") or 0)
        by_id[m_id] = {"exists": True, "prompt": prompt_cost, "completion": completion_cost}
    report = {}
    problems = []
    for key, model_id in FREE_MODELS.items():
        info = by_id.get(model_id)
        if not info:
            problems.append(f"{model_id} NOT FOUND on live registry")
            report[key] = {"id": model_id, "found": False}
            continue
        is_free = info["prompt"] == 0 and info["completion"] == 0
        report[key] = {"id": model_id, "found": True, "free": is_free}
        if not is_free:
            problems.append(f"{model_id} IS NOT FREE (prompt={info['prompt']} completion={info['completion']})")
    return report, problems


def smoke_test():
    """One real $0 call through the quick role + a safety check."""
    d = FreeSwarmDispatcher()
    r1 = d.dispatch("quick", "Reply with the single word: OK")
    r2 = d.dispatch("safety", "Approve this benign test message.")
    print(json.dumps({"smoke_1": r1["content"], "smoke_2": r2["content"], "cost_report": d.cost_report()}, indent=2))
    return 0


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 0
    if args[0] == "--test":
        return smoke_test()
    if args[0] == "--models":
        report, problems = verify_models_live()
        print(json.dumps(report, indent=2))
        if problems:
            print("PROBLEMS:")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("[OK] All registry models found and free ($0).")
        return 0
    if args[0] == "dispatch":
        role = args[1]
        task = args[2]
        context = ""
        if "--context" in args:
            context = args[args.index("--context") + 1]
        d = FreeSwarmDispatcher()
        result = d.dispatch(role, task, context)
        print(json.dumps(result, indent=2, default=str))
        return 0
    print(f"Unknown command: {args[0]}")
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
