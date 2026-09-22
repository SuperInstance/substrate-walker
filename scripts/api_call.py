"""Robust API call wrapper with retries, DNS resilience, model fallbacks.

Supports: ZAI, DeepSeek, DeepInfra, Kimi, Typesafe.ai (Jev)
"""
import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List


class APIError(Exception):
    pass


def call_with_retry(url: str, headers: Dict, payload: Dict, max_retries: int = 8, timeout: int = 60) -> Dict:
    """Call an API with retry logic for DNS failures."""
    data = json.dumps(payload).encode("utf-8")
    
    last_err = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=data,
                headers={**headers, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            if e.code == 429:
                time.sleep(2 ** attempt)
                continue
            if e.code in (500, 502, 503):
                time.sleep(1 + attempt)
                continue
            raise APIError(f"HTTP {e.code}: {body[:200]}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = str(e)
            time.sleep(1 + attempt * 0.5)
        except Exception as e:
            last_err = str(e)
            time.sleep(1 + attempt * 0.5)
    
    raise APIError(f"Failed after {max_retries} retries: {last_err}")


# ZAI
def call_zai(messages: List[Dict], model: str = "glm-5.3-flash", max_tokens: int = 4000, **kwargs) -> Dict:
    return call_with_retry(
        "https://api.z.ai/api/coding/paas/v4/chat/completions",
        {"Authorization": f"Bearer {os.environ['ZAI_TOKEN']}"},
        {"model": model, "messages": messages, "max_tokens": max_tokens, **kwargs},
    )


# DeepSeek
def call_deepseek(messages: List[Dict], model: str = "deepseek-chat", max_tokens: int = 4000, **kwargs) -> Dict:
    return call_with_retry(
        "https://api.deepseek.com/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['DEEPSEEK_TOKEN']}"},
        {"model": model, "messages": messages, "max_tokens": max_tokens, **kwargs},
    )


# DeepSeek Reasoner
def call_deepseek_reasoner(messages: List[Dict], max_tokens: int = 8000, **kwargs) -> Dict:
    return call_deepseek(messages, model="deepseek-reasoner", max_tokens=max_tokens, **kwargs)


# Kimi
def call_kimi(messages: List[Dict], model: str = "moonshot-v1-8k", max_tokens: int = 4000, **kwargs) -> Dict:
    return call_with_retry(
        "https://api.moonshot.cn/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['KIMI_TOKEN']}"},
        {"model": model, "messages": messages, "max_tokens": max_tokens, **kwargs},
    )


# DeepInfra (multiple models)
def call_deepinfra(messages: List[Dict], model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct", max_tokens: int = 4000, **kwargs) -> Dict:
    return call_with_retry(
        "https://api.deepinfra.com/v1/openai/chat/completions",
        {"Authorization": f"Bearer {os.environ['DEEPINFRA_TOKEN']}"},
        {"model": model, "messages": messages, "max_tokens": max_tokens, **kwargs},
    )


# Jev (Typesafe.ai) — special endpoint
def call_jev(state: str, questions: Dict, model: str = "jev-latest", max_retries: int = 8, timeout: int = 30) -> Dict:
    return call_with_retry(
        "https://api.typesafe.ai/v1/systemone",
        {"Authorization": f"Bearer {os.environ['TYPESAFEAI_KEY']}"},
        {"model": model, "state": state, "questions": questions},
        max_retries=max_retries,
        timeout=timeout,
    )


# Convenience: extract content from chat response
def extract_content(resp: Dict) -> str:
    try:
        return resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return ""


def extract_reasoning(resp: Dict) -> str:
    try:
        return resp["choices"][0]["message"].get("reasoning_content", "") or ""
    except (KeyError, IndexError):
        return ""


if __name__ == "__main__":
    # Quick smoke test
    print("=== API SMOKE TEST ===")
    
    print("\nJEV (Typesafe.ai):")
    r = call_jev(
        "The city breathes in concrete, exhales in neon.",
        {
            "is_noir": {"type": "noul", "instructions": "Is this cyberpunk noir?"},
            "voice": {"type": "choice", "instructions": "Which voice?", "criteria": {
                "structuralist": "architecture focus",
                "narrativist": "first-person",
                "futurist": "prophecy"
            }}
        }
    )
    print(json.dumps(r, indent=2))
    
    print("\nZAI (glM-5.3-flash):")
    try:
        r = call_zai([{"role": "user", "content": "say hi in 3 words"}], max_tokens=200)
        print(extract_content(r))
    except Exception as e:
        print(f"FAILED: {e}")
    
    print("\nDeepInfra (Llama-3.1-8b):")
    try:
        r = call_deepinfra([{"role": "user", "content": "say hi in 3 words"}], max_tokens=100)
        print(extract_content(r))
    except Exception as e:
        print(f"FAILED: {e}")
