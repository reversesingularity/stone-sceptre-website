#!/usr/bin/env python3
"""
Download Nemotron 3 Super UD-IQ3_S GGUF shards to F:\models\nemotron-super\UD-IQ3_S\

Downloads directly from Xet CDN via HTTP streaming, bypassing the hf_xet
subprocess lock-contention bug on Windows (huggingface-cli hangs on shards 2+3).

Usage:
    python download_nemotron_gguf.py

Resumes automatically — skips shards already fully downloaded.
Partial shards (.incomplete) are re-downloaded.
"""

import os
import sys
import requests
from huggingface_hub import get_hf_file_metadata, hf_hub_url

REPO = "unsloth/NVIDIA-Nemotron-3-Super-120B-A12B-GGUF"
DEST_DIR = r"F:\models\nemotron-super\UD-IQ3_S"

# All 3 shards — shard 1 is the tiny GGUF metadata header (7.87 MB)
# Shards 2 and 3 contain the actual model weights (~49.78 GB + ~6.8 GB)
SHARDS = [
    "UD-IQ3_S/NVIDIA-Nemotron-3-Super-120B-A12B-UD-IQ3_S-00001-of-00003.gguf",
    "UD-IQ3_S/NVIDIA-Nemotron-3-Super-120B-A12B-UD-IQ3_S-00002-of-00003.gguf",
    "UD-IQ3_S/NVIDIA-Nemotron-3-Super-120B-A12B-UD-IQ3_S-00003-of-00003.gguf",
]

CHUNK_SIZE = 8 * 1024 * 1024   # 8 MB write chunks
PROGRESS_INTERVAL = 500 * 1024 * 1024  # print every 500 MB


def download_shard(shard_path: str, dest_dir: str) -> None:
    filename = shard_path.split("/")[-1]
    dest_file = os.path.join(dest_dir, filename)
    tmp_file = dest_file + ".incomplete"

    if os.path.exists(dest_file):
        size_gb = os.path.getsize(dest_file) / 1e9
        print(f"[SKIP] {filename} already present ({size_gb:.2f} GB)")
        return

    # Fetch the Xet CDN redirect URL
    print(f"[INFO] Resolving CDN URL for {filename}...")
    hf_url = hf_hub_url(REPO, shard_path)
    meta = get_hf_file_metadata(hf_url)
    cdn_url = str(meta.location)
    print(f"[INFO] CDN: {cdn_url[:80]}...")

    print(f"[DOWN] Downloading {filename}...")
    with requests.get(cdn_url, stream=True, timeout=7200) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        if total:
            print(f"[INFO] Size: {total / 1e9:.2f} GB")
        else:
            print("[WARN] Content-Length not reported — size unknown")

        done = 0
        last_report = 0
        with open(tmp_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                f.write(chunk)
                done += len(chunk)
                if done - last_report >= PROGRESS_INTERVAL:
                    pct = done / total * 100 if total else 0.0
                    print(
                        f"  Progress: {done / 1e9:.2f}/{total / 1e9:.2f} GB ({pct:.1f}%)",
                        flush=True,
                    )
                    last_report = done

    os.rename(tmp_file, dest_file)
    final_size = os.path.getsize(dest_file) / 1e9
    print(f"[DONE] {filename} ({final_size:.2f} GB)")


def main():
    os.makedirs(DEST_DIR, exist_ok=True)
    print(f"Destination: {DEST_DIR}")
    print(f"Repo: {REPO}")
    print(f"Shards: {len(SHARDS)}")
    print("-" * 60)

    for shard_path in SHARDS:
        try:
            download_shard(shard_path, DEST_DIR)
        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Download paused. Re-run to resume.")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Failed to download {shard_path}: {e}")
            sys.exit(1)

    print("-" * 60)
    print("[COMPLETE] All shards downloaded.")
    print(f"\nllama-server launch command:")
    print(
        f'  F:\\llama-cpp\\llama-server.exe -m "{DEST_DIR}\\NVIDIA-Nemotron-3-Super-120B-A12B-UD-IQ3_S-00001-of-00003.gguf" '
        f"--host 0.0.0.0 --port 8780 -c 131072 -ngl 25 --special"
    )


if __name__ == "__main__":
    main()
