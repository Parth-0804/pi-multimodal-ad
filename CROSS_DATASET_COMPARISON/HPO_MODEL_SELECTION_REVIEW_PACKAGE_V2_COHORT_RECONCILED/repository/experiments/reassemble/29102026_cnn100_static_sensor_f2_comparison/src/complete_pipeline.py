"""Complete this CPU-only analysis once the full held-out bank is ready."""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import fcntl
import subprocess
import sys
import time
from common import ROOT, REPO, RUN, read, write, relative, utc


def main():
    lock = (RUN/'COMPLETION_PIPELINE.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    receipt = ROOT/'04_training_side_predictions/INFERENCE_RECEIPT.json'
    last = None
    while not receipt.exists():
        state = read(ROOT/'STATUS.json')
        progress = state.get('completed', 0)
        if progress != last:
            print(utc(), 'WAITING_FOR_COMPLETE_BANK', progress, '/', state.get('required', 920), flush=True)
            last = progress
        write(RUN/'PIPELINE_STATUS.json', {'utc': utc(), 'stage': 'WAITING_FOR_CPU_HELDOUT_BANK',
              'completed_actions': progress, 'future_stages': ['evaluate', 'plots', 'reports', 'validate'],
              'GPU_study_interrupted': False})
        time.sleep(10)
    assert read(receipt)['actions_per_arm'] == 920
    commands = []
    for stage in ['evaluate', 'plots', 'reports', 'validate']:
        command = [sys.executable, '-B', str(ROOT/'src'/f'{stage}.py')]
        log = RUN/'logs'/f'{stage}_{time.time_ns()}.log'
        write(RUN/'PIPELINE_STATUS.json', {'utc': utc(), 'stage': 'RUNNING_'+stage.upper(),
              'command': [relative(command[0]) if str(command[0]).startswith(str(REPO)) else command[0], '-B', relative(ROOT/'src'/f'{stage}.py')],
              'log': relative(log), 'GPU_study_interrupted': False})
        print(utc(), 'STARTING', stage, flush=True)
        with log.open('x') as output:
            process = subprocess.run(command, cwd=REPO, stdin=subprocess.DEVNULL,
                                     stdout=output, stderr=subprocess.STDOUT)
        commands.append({'stage': stage, 'log': relative(log), 'exit_code': process.returncode, 'finished_utc': utc()})
        write(RUN/'PIPELINE_COMMANDS.json', commands)
        if process.returncode != 0:
            write(RUN/'PIPELINE_STATUS.json', {'utc': utc(), 'stage': 'FAILED_'+stage.upper(),
                  'exit_code': process.returncode, 'log': relative(log), 'scientific_results_invented': False})
            print('PIPELINE_STAGE_FAILED', stage, process.returncode, relative(log), flush=True)
            raise SystemExit(process.returncode)
        print(utc(), 'FINISHED', stage, flush=True)
    write(RUN/'PIPELINE_STATUS.json', {'utc': utc(), 'stage': 'COMPLETE', 'required_reports': 8,
          'models_evaluated': 7, 'new_CNN_fits': 0, 'GPU_study_interrupted': False})
    print('COMPLETE_F2_COMPARISON_PIPELINE', flush=True)


if __name__ == '__main__':main()
