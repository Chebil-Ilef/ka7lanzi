import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List

class Visualizer:
    def __init__(self):
        sns.set_style("whitegrid")

    def heatmap(self, df: pd.DataFrame, columns: List[str]):
        corr = df[columns].corr()
        fig, ax = plt.subplots(figsize=(6,5))
        sns.heatmap(corr, annot=True, ax=ax)
        ax.set_title("Correlation heatmap")
        return fig

    def boxplot(self, df: pd.DataFrame, column: str, by: str = None):
        fig, ax = plt.subplots(figsize=(6,4))
        if by is None:
            sns.boxplot(y=df[column], ax=ax)
        else:
            sns.boxplot(x=by, y=column, data=df, ax=ax)
        ax.set_title(f"Boxplot {column}")
        return fig

    def scatter(self, df: pd.DataFrame, x: str, y: str):
        fig, ax = plt.subplots(figsize=(6,4))
        sns.scatterplot(x=df[x], y=df[y], ax=ax)
        ax.set_xlabel(x); ax.set_ylabel(y)
        return fig

    def histogram(self, df: pd.DataFrame, column: str, bins: int = 30):
        fig, ax = plt.subplots(figsize=(6,4))
        ax.hist(df[column].dropna(), bins=bins)
        ax.set_title(f"Histogram {column}")
        return fig