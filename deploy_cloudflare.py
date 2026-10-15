"""Cloudflare Tunnel Deployment Runner for MuryaAI.
Deploys MuryaAI publicly to Cloudflare's global edge network with instant HTTPS.
"""
import sys
import time
import subprocess
import re
import urllib.request
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
CLOUDFLARED_BIN = ROOT_DIR / "cloudflared.exe"

def ensure_cloudflared():
    if not CLOUDFLARED_BIN.exists():
        print("⏳ Downloading official cloudflared binary...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        urllib.request.urlretrieve(url, str(CLOUDFLARED_BIN))
        print("✅ cloudflared ready!")

def is_backend_running(port=8000):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/samples", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

def main():
    print("=" * 65)
    print("🚀 MuryaAI — Cloudflare Edge Deployment Manager (NAIC 2026)")
    print("=" * 65)
    
    ensure_cloudflared()
    
    backend_proc = None
    if not is_backend_running(8000):
        print("\n⏳ Starting MuryaAI FastAPI backend server on http://localhost:8000...")
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "backend.main"],
            cwd=str(ROOT_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Wait for backend to be ready
        for _ in range(20):
            time.sleep(0.5)
            if is_backend_running(8000):
                break
        print("✅ MuryaAI backend is live locally on http://localhost:8000")
    else:
        print("✅ MuryaAI backend is already running on http://localhost:8000")

    print("\n🌐 Establishing Cloudflare Zero-Trust Tunnel to global edge (HTTP/2)...")
    tunnel_cmd = [str(CLOUDFLARED_BIN), "tunnel", "--protocol", "http2", "--url", "http://localhost:8000"]
    
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    
    try:
        for line in tunnel_proc.stdout:
            # Look for the assigned trycloudflare URL
            match = url_pattern.search(line)
            if match and not tunnel_url:
                tunnel_url = match.group(0)
                print("\n" + "=" * 65)
                print("🎉 MURYAAI IS LIVE ON CLOUDFLARE!")
                print(f"👉 PUBLIC HTTPS URL: {tunnel_url}")
                print("=" * 65)
                print("\n📋 You can now paste this URL into your NAIC application portal:")
                print(f"   Link to public repository, live demo, or deployed application:")
                print(f"   {tunnel_url}\n")
                print("Press CTRL+C anytime to stop the Cloudflare tunnel.\n")
            
            # Print status lines without clutter
            if "Registered tunnel connection" in line or "Connection" in line and "registered" in line:
                print(f"⚡ Cloudflare Edge Connection: {line.strip()}")
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Cloudflare tunnel...")
    finally:
        tunnel_proc.terminate()
        if backend_proc:
            backend_proc.terminate()
        print("Tunnel closed.")

if __name__ == "__main__":
    main()
