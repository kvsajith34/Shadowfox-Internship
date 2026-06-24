#!/usr/bin/env python3
"""Smoke test: verify the API is running and all endpoints respond."""
import sys
import time
import subprocess
import requests

BASE_URL = "http://localhost:8000"


def test_endpoint(method, path, payload=None, files=None):
    """Test a single endpoint."""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        elif method == "POST":
            if files:
                r = requests.post(url, files=files, data=payload or {}, timeout=30)
            else:
                r = requests.post(url, json=payload, timeout=30)
        else:
            return False, f"Unsupported method: {method}"

        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                return True, f"✅ {method} {path} - OK"
            else:
                return False, f"⚠️  {method} {path} - Success=false: {data.get('message', '')}"
        else:
            return False, f"❌ {method} {path} - HTTP {r.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"❌ {method} {path} - Connection refused (is the server running?)"
    except Exception as e:
        return False, f"❌ {method} {path} - Error: {e}"


def main():
    """Run smoke tests."""
    print("🚀 VisualRAG Intelligence Studio - Smoke Test")
    print("=" * 50)

    tests = [
        ("GET", "/api/v1/health"),
        ("GET", "/health"),
        ("GET", "/api/v1/metrics"),
        ("GET", "/api/v1/history"),
        ("GET", "/api/v1/reports"),
        ("POST", "/api/v1/visual-chat", {"message": "Hello", "provider": "mock"}),
        ("POST", "/api/v1/pdf-rag-query", {"file_id": "test", "question": "What?", "provider": "mock"}),
        ("POST", "/api/v1/evaluate", {"question": "Test?", "answer": "Test answer", "evidence": [], "task_type": "visual_chat", "provider": "mock"}),
    ]

    passed = 0
    failed = 0

    for test in tests:
        method, path = test[0], test[1]
        payload = test[2] if len(test) > 2 else None
        ok, msg = test_endpoint(method, path, payload)
        print(msg)
        if ok:
            passed += 1
        else:
            failed += 1

    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")

    if failed > 0:
        sys.exit(1)
    print("🎉 All smoke tests passed!")


if __name__ == "__main__":
    main()
