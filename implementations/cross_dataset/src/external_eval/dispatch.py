"""CLI for explicit versioned dataset roots; model code stays shared."""
import argparse
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['features','evaluate','reports'],required=True)
    p.add_argument('--root',required=True);p.add_argument('--condition',default='P');a=p.parse_args()
    root=Path(a.root)
    if not any(root.resolve().is_relative_to(Path(d).resolve()) for d in ['MSM','HANDOVER']):raise ValueError('Dataset outputs must remain under their authorized root')
    if a.stage=='features':
        if a.condition=='R':
            # A resumed R bank must keep the exact selected source checkpoint.
            import json
            from msm.transfer import validated_source
            config=json.loads((root/'04_experiment_protocol/experiment_config.json').read_text())
            _,receipt=validated_source(config['source_R']['folder'],42,4)
            identity=root/'03_processed_model_inputs/visual_features/R/identity.json'
            if identity.exists():
                transfer=json.loads(identity.read_text())['transfer']
                if transfer['source_checkpoint_sha256']!=receipt['selected_model_sha256']:raise ValueError('R resume source identity changed')
        from .features import run
        run(a.root,a.condition)
    elif a.stage=='evaluate':
        from .evaluate import run
        run(a.root,a.condition)
    else:
        from .reports import run
        run(a.root)


if __name__=='__main__':main()
