import matplotlib.pyplot as plt
import pandas as pd


class ChartBuilder:

    @staticmethod
    def line_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
        xlabel: str = "",
        ylabel: str = ""
    ):
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(df[x], df[y], marker="o", linewidth=2)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig

    @staticmethod
    def bar_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
        xlabel: str = "",
        ylabel: str = ""
    ):
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(df[x], df[y])

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig

    @staticmethod
    def horizontal_bar_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = ""
    ):
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.barh(df[y], df[x])

        ax.set_title(title)

        plt.tight_layout()

        return fig

    @staticmethod
    def pie_chart(
        df: pd.DataFrame,
        labels: str,
        values: str,
        title: str = ""
    ):
        fig, ax = plt.subplots(figsize=(7, 7))

        ax.pie(
            df[values],
            labels=df[labels],
            autopct="%1.1f%%",
            startangle=90
        )

        ax.set_title(title)

        plt.tight_layout()

        return fig

    @staticmethod
    def scatter_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str = "",
        xlabel: str = "",
        ylabel: str = ""
    ):
        fig, ax = plt.subplots(figsize=(8, 5))

        ax.scatter(df[x], df[y])

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        plt.tight_layout()

        return fig

    @staticmethod
    def histogram(
        df: pd.DataFrame,
        column: str,
        bins: int = 15,
        title: str = ""
    ):
        fig, ax = plt.subplots(figsize=(8, 5))

        ax.hist(df[column], bins=bins)

        ax.set_title(title)

        plt.tight_layout()

        return fig