import pandas as pd


def load_excel(file_path, sheet_name=0):
    """
    Load Excel file using header row 1.
    """

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=1
    )

    return df


if __name__ == "__main__":
    print("Loader ready")