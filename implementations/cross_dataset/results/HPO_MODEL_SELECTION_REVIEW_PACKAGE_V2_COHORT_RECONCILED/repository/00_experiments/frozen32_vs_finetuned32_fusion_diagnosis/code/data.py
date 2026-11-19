"""Read the locked cohort; unchanged pixel primitive loads existing media read-only."""
import pandas as pd
from common import STUDY,REPO,read,config

def load_cohort():return pd.DataFrame(read(STUDY/'data_manifests/cohort_and_frames.json'))
def processor_only():
    from transformers import RTDetrImageProcessor
    return RTDetrImageProcessor.from_pretrained(REPO/config()['weights_dir'],local_files_only=True)

