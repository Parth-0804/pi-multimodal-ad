#!/usr/bin/env python3
"""One resumable stage. The controller owns ordering and resource interlocks."""
from pathlib import Path
import argparse,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from vifailback.common import config


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',required=True,choices=['labels','cohort','sensors','features','baselines','train','fusion','augmentation','robustness','qc_gallery','gallery','verify','reports'])
    parser.add_argument('--condition',choices=['V1','V1_high_only','V2','V3'],default='V1');parser.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    args=parser.parse_args();c=config()
    if args.device=='cuda':
        from vifailback.resources import wait_for_gpu
        wait_for_gpu(c)
    if args.stage=='labels':
        from vifailback.verification import native_labels
        native_labels(c)
    elif args.stage=='cohort':
        from vifailback.cohort import finalize
        from vifailback.splits import prepare
        finalize(c);prepare(c)
    elif args.stage=='sensors':
        from vifailback.sensors import prepare
        prepare(c)
    elif args.stage=='features':
        from vifailback.feature_bank import build
        build(c,args.condition,args.device)
    elif args.stage=='baselines':
        from vifailback.baselines import run
        run(c)
    elif args.stage=='train':
        from vifailback.training import run
        run(c,(args.condition,),args.device)
    elif args.stage=='fusion':
        from vifailback.fusion import run
        run(c,(args.condition,))
    elif args.stage=='augmentation':
        from vifailback.augmentation import run
        run(c,args.condition,args.device)
    elif args.stage=='robustness':
        from vifailback.robustness import run
        run(c,(args.condition,),args.device)
    elif args.stage=='qc_gallery':
        from vifailback.gallery import blinded
        blinded(c)
    elif args.stage=='gallery':
        from vifailback.gallery import blinded,prediction_gallery
        blinded(c);prediction_gallery(c,(args.condition,))
    elif args.stage=='verify':
        from vifailback.verification import saved_results
        saved_results(c)
    elif args.stage=='reports':
        from vifailback.reporting import publish
        publish(c)


if __name__=='__main__':main()
