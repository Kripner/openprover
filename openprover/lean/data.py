"""Lean Explore data management - fetch and check local search data."""

import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger("openprover.lean")

# Minimum declaration count for a valid database.  A proper Mathlib index
# has ~400k declarations; anything below this threshold is likely a corrupt
# or incomplete fetch (e.g. only FormalConjectures/PhysLean packages).
_MIN_DECLARATIONS = 100_000


def _has_lean_explore() -> bool:
    try:
        import lean_explore  # noqa: F401
        return True
    except ImportError:
        return False


def _has_torch() -> bool:
    try:
        import torch  # noqa: F401
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def _validate_db(db_path: Path) -> bool:
    """Check the DB has enough declarations and includes Mathlib."""
    import sqlite3
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM declarations")
        total = cur.fetchone()[0]
        if total < _MIN_DECLARATIONS:
            logger.warning(
                "lean_explore DB has only %d declarations (need >=%d): %s",
                total, _MIN_DECLARATIONS, db_path,
            )
            conn.close()
            return False
        cur.execute(
            "SELECT COUNT(*) FROM declarations WHERE module LIKE 'Mathlib.%'"
        )
        mathlib_count = cur.fetchone()[0]
        conn.close()
        if mathlib_count == 0:
            logger.warning(
                "lean_explore DB has 0 Mathlib declarations: %s", db_path,
            )
            return False
        return True
    except Exception as e:
        logger.warning("lean_explore DB validation failed: %s", e)
        return False


def is_lean_data_available() -> bool:
    """Check if Lean Explore search data has been fetched and deps installed."""
    if not _has_lean_explore() or not _has_torch():
        return False
    try:
        from lean_explore.config import Config
        cfg = Config()
        cache = cfg.CACHE_DIRECTORY
        if not cache.exists():
            return False
        # Data lives in versioned subdirs: cache/<version>/lean_explore.db
        for version_dir in cache.iterdir():
            if version_dir.is_dir():
                db = version_dir / "lean_explore.db"
                if db.exists() and _validate_db(db):
                    return True
        return False
    except Exception:
        return False


def fetch_lean_data() -> bool:
    """Fetch Lean Explore data and deps. Returns True if ready after call."""
    bin_dir = Path(sys.executable).parent
    pip_bin = str(bin_dir / "pip") if (bin_dir / "pip").exists() else "pip"

    # Install lean-explore if missing
    if not _has_lean_explore():
        print("Installing lean-explore...")
        try:
            subprocess.run(
                [pip_bin, "install", "lean-explore"],
                check=True, capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing lean-explore: {e}")
            return False

    # Install torch (CPU) and sentence-transformers if missing
    if not _has_torch():
        print("Installing torch (CPU) and sentence-transformers...")
        try:
            subprocess.run(
                [pip_bin, "install", "torch",
                 "--index-url", "https://download.pytorch.org/whl/cpu"],
                check=True, capture_output=True,
            )
            subprocess.run(
                [pip_bin, "install", "sentence-transformers"],
                check=True, capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return False

    # Check if data already fetched
    if is_lean_data_available():
        print("Lean Explore data already available.")
        return True

    # Fetch data
    print("Fetching Lean Explore data (declarations, embeddings, index)...")
    lean_explore_bin = bin_dir / "lean-explore"
    if not lean_explore_bin.exists():
        lean_explore_bin = "lean-explore"
    try:
        subprocess.run(
            [str(lean_explore_bin), "data", "fetch"],
            check=True,
        )
        if not is_lean_data_available():
            print("Warning: fetch completed but data validation failed "
                  "(too few declarations or missing Mathlib). "
                  "Check logs or try an older lean-explore data version.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error fetching Lean Explore data: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

    # Pre-download models so first search doesn't hit the network
    print("Pre-downloading embedding model (Qwen3-Embedding-0.6B)...")
    try:
        from sentence_transformers import SentenceTransformer
        SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
    except Exception as e:
        print(f"Warning: failed to pre-download embedding model: {e}")

    try:
        import torch
        if torch.cuda.is_available():
            print("GPU detected - pre-downloading reranker model (Qwen3-Reranker-0.6B)...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            AutoTokenizer.from_pretrained("Qwen/Qwen3-Reranker-0.6B")
            AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-Reranker-0.6B")
    except Exception as e:
        print(f"Warning: failed to pre-download reranker model: {e}")

    print("Lean Explore data ready.")
    return True
