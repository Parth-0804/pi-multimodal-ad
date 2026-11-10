from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from reassemble.section3_sensor import main
if __name__=='__main__':main()
