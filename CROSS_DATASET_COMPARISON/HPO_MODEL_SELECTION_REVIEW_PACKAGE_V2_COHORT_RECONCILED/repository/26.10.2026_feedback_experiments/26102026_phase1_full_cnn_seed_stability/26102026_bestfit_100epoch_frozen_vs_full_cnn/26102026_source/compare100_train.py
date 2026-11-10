"""Reuse the verified fitter with isolated outputs and a matched cosine100 budget."""
import argparse

from compare100_common import DETOUR,RUN,CONFIG,JOB,configuration,effective_configuration
from compare100_common import folder_for,fit_identity,scheduler100,fixed_stop,read,write,sha,utc
import phase_training as training
from phase_common import foreign_gpu_processes


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--arm',required=True,choices=configuration()['arms'])
    args=parser.parse_args()
    assert not foreign_gpu_processes(),'GPU_BUSY: wait for other GPU jobs'
    c=configuration()
    original=training.config()
    for name in ['head_lr','backbone_lr','weight_decay','gradient_clip']:
        assert original[name]==c[name],'UNREVIEWED_OPTIMIZER_CHANGE'
    # Runtime adapters are confined to this new child process. Original source,
    # current75-fit checkpoints and its cosine50 schedule are untouched.
    training.config=effective_configuration
    training.make_scheduler=scheduler100
    training.stop_after_epoch=fixed_stop
    training.folder_for=folder_for
    training.run_identity=fit_identity
    training.EXEC=RUN
    training.ROOT=DETOUR
    job=read(JOB)
    result=training.fit(args.arm,c['seed'],job)
    assert result['executed_epochs']==100
    assert [r['epoch'] for r in result['history']]==list(range(1,101))
    write(folder_for(args.arm,c['seed'],job)/'PHASE1_COMPARISON_ARM_COMPLETE.json',{
        'utc':utc(),'status':'COMPLETE','arm':args.arm,'seed':c['seed'],'epochs':100,
        'selected_epoch':result['best']['epoch'],'configuration_sha256':sha(CONFIG),
        'fit_identity':result['fit_identity'],'predictions_sha256':result['predictions_sha256'],
        'selected_model_sha256':result['selected_model_sha256'],
        'fresh_original_pretrained_initialization':True,'training_seconds':result['training_seconds'],
        'inference_calibration_seconds':result['inference_calibration_seconds']})


if __name__=='__main__':
    main()
