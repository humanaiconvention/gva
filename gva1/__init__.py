"""GVA-1 execution layer; frozen GVA-0 reference modules remain unchanged."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'reference'))
