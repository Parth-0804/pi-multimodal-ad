from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from reassemble.section3_report import assess
from threadpoolctl import threadpool_limits
if __name__=='__main__':
    with threadpool_limits(limits=4,user_api='blas'):assess()
