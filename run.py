"""Run the source archive without installing it into the main environment."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from mm_data_prep.cli import main
if __name__=='__main__':raise SystemExit(main())
