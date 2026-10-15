import os
from pathlib import Path
from dotenv import dotenv_values
from huggingface_hub import HfApi

# 1. Load Token
env_path = Path(__file__).resolve().parent.parent / "agrivoice" / ".env"
env = dotenv_values(env_path) if env_path.exists() else {}
token = env.get("HF_TOKEN") or env.get("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")

if not token:
    raise ValueError("HF_TOKEN not found in environment or ../agrivoice/.env")

repo_id = "theAlpha419/murya-ai"
api = HfApi(token=token)

print(f"Connecting to Hugging Face as {api.whoami().get('name')}...")

# 2. Prepare Space README
readme_content = """---
title: MuryaAI Voice-First Citizen Resolution Agent
emoji: 🎙️
colorFrom: green
colorTo: green
sdk: static
pinned: false
---

# MuryaAI (N-VoiceCare) 🎙️🇳🇬
**Voice-First Citizen Customer Resolution Agent Powered by Nigeria's Foundational N-ATLAS Model**

Submission for the **National AI Innovation Challenge (NAIC 2026)**
Organized by **FMCIDE / NITDA / NCAIR**  
Problem Statement: **PS2 — Voice-First Access**

### Key Capabilities:
- **Zero Smartphone Barrier:** Designed for 2G feature phones (SIP/IVR) and WhatsApp voice notes.
- **Multilingual N-ATLAS Engine:** Native reasoning in Hausa, Yoruba, Igbo, and Nigerian English / Pidgin.
- **Core National Integrations:** NIBSS instant dispute auto-reversal & DisCo STS 20-digit token recovery.
- **Ultra-low latency:** ~128ms end-to-end processing pipeline.
"""

static_dir = Path(__file__).resolve().parent / "static"

# 3. Upload files
print("Uploading README.md...")
api.upload_file(
    path_or_fileobj=readme_content.encode("utf-8"),
    path_in_repo="README.md",
    repo_id=repo_id,
    repo_type="space"
)

files_to_upload = ["index.html", "style.css", "app.js"]
for fname in files_to_upload:
    local_path = static_dir / fname
    print(f"Uploading {fname} ({local_path.stat().st_size} bytes)...")
    api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=fname,
        repo_id=repo_id,
        repo_type="space"
    )

print(" All files successfully uploaded to Hugging Face Space!")
print(f"Space URL: https://huggingface.co/spaces/{repo_id}")
print(f"Direct Web URL: https://thealpha419-murya-ai.hf.space")
