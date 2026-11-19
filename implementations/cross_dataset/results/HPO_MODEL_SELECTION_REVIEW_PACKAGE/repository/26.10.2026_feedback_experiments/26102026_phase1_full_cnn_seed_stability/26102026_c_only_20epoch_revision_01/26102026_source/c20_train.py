"""Run the existing full-CNN fitter with the user's explicit 20-epoch cap."""
import argparse

from c20_common import ARM, REV_CONFIG, RUN, EVIDENCE, CONFIG, configuration, effective_training_configuration
from c20_common import fixed_stop, read, write, sha, utc, signature, receipt_for
import phase_training as training
from phase_common import foreign_gpu_processes
from phase_model import config as scheduler_configuration


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, required=True, choices=configuration()['seeds'])
    parser.add_argument('--job', type=int, required=True)
    args = parser.parse_args()
    jobs = read(EVIDENCE/'PHASE1_FIT_PLAN.json')
    assert not foreign_gpu_processes(), 'GPU_BUSY: do not launch competing work'
    assert sha(CONFIG) == configuration()['base_training_configuration_sha256']
    assert scheduler_configuration()['max_epochs'] == 50, 'PRESERVE_VALIDATED_COSINE50_PREFIX'
    training.config = effective_training_configuration
    training.stop_after_epoch = fixed_stop
    result = training.fit(ARM, args.seed, jobs[args.job])
    assert result['executed_epochs'] == 20
    assert [row['epoch'] for row in result['history']] == list(range(1, 21))
    write(receipt_for(args.seed, jobs[args.job]), {
        'utc': utc(), 'status': 'COMPLETE', 'arm': ARM, 'seed': args.seed, 'job_index': args.job,
        'executed_epochs': 20, 'selected_epoch': result['best']['epoch'],
        'execution_identity': signature({'base_fit_identity': result['fit_identity'], 'revision_sha256': sha(REV_CONFIG)}),
        'base_fit_identity': result['fit_identity'], 'revision_configuration_sha256': sha(REV_CONFIG),
        'training_configuration_identity': 'Original immutable checkpoint identity; changed execution horizon recorded by this separate receipt',
        'scheduler_horizon': 50, 'remaining_original_protocol_B_jobs': 0,
        'predictions_sha256': result['predictions_sha256'], 'selected_model_sha256': result['selected_model_sha256'],
        'training_seconds': result['training_seconds'],
        'inference_calibration_seconds': result['inference_calibration_seconds']})


if __name__ == '__main__':
    main()
