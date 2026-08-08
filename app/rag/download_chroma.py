import os
import zipfile
import requests
from pathlib import Path

# Set CHROMA_DOWNLOAD_URL in your Render environment variables.
# Must be a DIRECT download URL to a .zip file, e.g.:
#   https://github.com/fahadkhan007/zentra-backend/releases/download/v1.0/chroma_db.zip
CHROMA_DOWNLOAD_URL = os.getenv("CHROMA_DOWNLOAD_URL", "")

# Chroma DB lives at ./data/chroma_db (relative to where uvicorn is run from)
BASE_DIR = Path(__file__).parent.parent.parent  # → backend/
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
CHROMA_SQLITE = CHROMA_DIR / "chroma.sqlite3"

# GitHub requires a User-Agent header; without it you get a 403 client error.
HEADERS = {
    "User-Agent": "zentra-backend/1.0 (github-release-downloader)",
    "Accept": "application/octet-stream",
}


def download_chroma():
    """
    Download and extract the ChromaDB vector store from a GitHub Release zip.
    Skipped if chroma.sqlite3 already exists (avoids re-downloading on every restart).
    Works whether the URL ends in .zip or not — reads file bytes directly.
    """
    if CHROMA_SQLITE.exists():
        print(f"✅ ChromaDB already present at {CHROMA_DIR} — skipping download.")
        return

    if not CHROMA_DOWNLOAD_URL:
        print("⚠️  CHROMA_DOWNLOAD_URL not set. Skipping ChromaDB download.")
        print("   The RAG system will start with an empty vector store.")
        return

    print(f"📥 Downloading ChromaDB from: {CHROMA_DOWNLOAD_URL}")
    CHROMA_DIR.parent.mkdir(parents=True, exist_ok=True)

    # Always save to a temp file regardless of URL filename/extension
    tmp_path = BASE_DIR / "data" / "_chroma_tmp.zip"

    try:
        # Stream download so large files don't blow memory.
        # allow_redirects=True (default) handles GitHub's CDN redirects.
        with requests.get(
            CHROMA_DOWNLOAD_URL,
            stream=True,
            timeout=120,
            headers=HEADERS,
            allow_redirects=True,
        ) as r:
            # Log the final URL after redirects so we can debug mismatches
            if r.url != CHROMA_DOWNLOAD_URL:
                print(f"   ↳ Redirected to: {r.url}")

            if not r.ok:
                # Print full details so it's easy to debug in Render logs
                print(f"❌ HTTP {r.status_code} error fetching ChromaDB.")
                print(f"   URL: {CHROMA_DOWNLOAD_URL}")
                print(f"   Response headers: {dict(r.headers)}")
                # Print first 500 chars of body (often contains error message)
                body = r.text[:500] if r.text else "(empty body)"
                print(f"   Response body (first 500 chars): {body}")
                print()
                print("   Common causes:")
                print("   • 403 Forbidden → GitHub blocked the request (User-Agent issue) or repo is private")
                print("   • 404 Not Found → CHROMA_DOWNLOAD_URL is wrong; check the release asset URL carefully")
                print("   • 302 redirect to HTML → you set the release *page* URL instead of the direct asset URL")
                print("   The app will start but RAG responses may be empty.")
                return

            # Sanity-check: if Content-Type is HTML we got a browser page, not a zip
            content_type = r.headers.get("Content-Type", "")
            if "text/html" in content_type:
                print("❌ Download returned HTML instead of a zip file.")
                print(f"   Content-Type: {content_type}")
                print("   You likely set the GitHub release *page* URL instead of the direct asset download URL.")
                print("   Correct format: https://github.com/<user>/<repo>/releases/download/<tag>/<file>.zip")
                return

            downloaded = 0
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)

        mb = downloaded / 1_048_576
        print(f"✅ Downloaded {mb:.1f} MB")

        # Validate it's actually a zip before extracting
        if not zipfile.is_zipfile(tmp_path):
            print("❌ Downloaded file is not a valid zip archive!")
            print("   Make sure you zipped the chroma_db folder before uploading to GitHub Releases.")
            tmp_path.unlink()
            return

        print("📦 Extracting ChromaDB ...")
        with zipfile.ZipFile(tmp_path, "r") as zf:
            zf.extractall(BASE_DIR / "data")

        tmp_path.unlink()  # clean up temp file
        print(f"✅ ChromaDB extracted to {CHROMA_DIR}")

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error downloading ChromaDB: {e}")
        print("   Check that CHROMA_DOWNLOAD_URL is reachable from Render's servers.")
    except requests.exceptions.Timeout:
        print("❌ Timed out downloading ChromaDB (120s limit exceeded).")
        print("   The zip file may be too large, or the server is slow.")
    except Exception as e:
        print(f"❌ Unexpected error downloading ChromaDB: {type(e).__name__}: {e}")
        print("   The app will start but RAG responses may be empty.")
    finally:
        # Clean up temp file if it exists and something went wrong
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    download_chroma()
