import pandas as pd


def load_excel(path: str) -> pd.DataFrame:
    """
    Load Excel file using header row 1.
    """

    df = pd.read_excel(
        path,
        header=1
    )

    return df


if __name__ == "__main__":
    print("Loader ready")