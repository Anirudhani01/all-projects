#!/usr/bin/env python3
import asyncio
import json
import sys
import os

import httpx

API_BASE = "http://127.0.0.1:8000/api/v1"
EMAIL = "ajio@gmail.com"
PASSWORD = "ajio123"

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Login
        resp = await client.post(f"{API_BASE}/auth/login", json={"email": EMAIL, "password": PASSWORD})
        print("Login status:", resp.status_code)
        data = resp.json()
        print("Login body:", json.dumps(data, indent=2))
        token = data.get("access_token")
        if not token:
            print("No access token; abort")
            return
        headers = {"Authorization": f"Bearer {token}"}
        # Call merchants/me
        me = await client.get(f"{API_BASE}/merchants/me", headers=headers)
        print("/merchants/me status:", me.status_code)
        print("/merchants/me body:", json.dumps(me.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
