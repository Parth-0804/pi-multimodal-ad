import pandas as pd
from pathlib import Path


def load_csv(path: str, **kwargs) -> pd.DataFrame:
    """Load a CSV file into a DataFrame.

    Args:
        path: Path to the CSV file.
        **kwargs: Passed to `pd.read_csv`.

    Returns:
        pd.DataFrame
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {p}")
    return pd.read_csv(p, **kwargs)
