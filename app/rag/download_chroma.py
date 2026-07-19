import os
import zipfile
import requests
from pathlib import Path

# Set CHROMA_DOWNLOAD_URL in your Railway/Render environment variables
# e.g. https://github.com/fahadkhan007/zentra-backend/releases/download/v1.0-models/chroma_db
CHROMA_DOWNLOAD_URL = os.getenv("CHROMA_DOWNLOAD_URL", "")

# Chroma DB lives at ./data/chroma_db (relative to where uvicorn is run from)
BASE_DIR = Path(__file__).parent.parent.parent  # → backend/
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
CHROMA_SQLITE = CHROMA_DIR / "chroma.sqlite3"


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

    # Always save to a temp file regardless of URL filename/extension
    tmp_path = BASE_DIR / "data" / "_chroma_tmp.zip"

    try:
        print(f"📥 Downloading ChromaDB from {CHROMA_DOWNLOAD_URL} ...")
        CHROMA_DIR.parent.mkdir(parents=True, exist_ok=True)

        # Stream download so large files don't blow memory
        with requests.get(CHROMA_DOWNLOAD_URL, stream=True, timeout=120) as r:
            r.raise_for_status()
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

    except Exception as e:
        print(f"❌ Failed to download ChromaDB: {e}")
        print("   The app will start but RAG responses may be empty.")


if __name__ == "__main__":
    download_chroma()
