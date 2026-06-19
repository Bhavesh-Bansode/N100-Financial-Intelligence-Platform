import pandas as pd


def load_excel(path: str) -> pd.DataFrame:

    if any(
        file_name in path.lower()
        for file_name in [
            "sectors",
            "market_cap",
            "stock_prices",
            "peer_groups",
            "financial_ratios"
        ]
    ):

        return pd.read_excel(
            path,
            header=0
        )

    return pd.read_excel(
        path,
        header=1
    )


if __name__ == "__main__":
    print("Loader ready")