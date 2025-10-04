import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
from typing import List
from core.interfaces.ivisualizer import IVisualizer


class Visualizer(IVisualizer):
    def __init__(self):
        sns.set_style("whitegrid")

    def heatmap(self, df: pd.DataFrame, columns: List[str])-> Figure:
        corr = df[columns].corr()
        fig, ax = plt.subplots(figsize=(6,5))
        sns.heatmap(corr, annot=True, ax=ax)
        ax.set_title("Correlation heatmap")
        return fig

    def boxplot(self, df: pd.DataFrame, column: str, by: str = None)-> Figure:
        fig, ax = plt.subplots(figsize=(6,4))
        if by is None:
            sns.boxplot(y=df[column], ax=ax)
        else:
            sns.boxplot(x=by, y=column, data=df, ax=ax)
        ax.set_title(f"Boxplot {column}")
        return fig

    def scatter(self, df: pd.DataFrame, x: str, y: str)-> Figure:
        fig, ax = plt.subplots(figsize=(6,4))
        sns.scatterplot(x=df[x], y=df[y], ax=ax)
        ax.set_xlabel(x); ax.set_ylabel(y)
        return fig

    def histogram(self, df: pd.DataFrame, column: str, bins: int = 30)-> Figure:
        fig, ax = plt.subplots(figsize=(6,4))
        ax.hist(df[column].dropna(), bins=bins)
        ax.set_title(f"Histogram {column}")
        return fig
    
    def barplot(self, df: pd.DataFrame, x: str, y: str = None) -> Figure:
        fig, ax = plt.subplots(figsize=(6,4))
        if y:
            sns.barplot(x=x, y=y, data=df, ax=ax)
        else:
            df[x].value_counts().plot(kind='bar', ax=ax)
        ax.set_title(f"Barplot {x}" if not y else f"Barplot {x} vs {y}")
        return fig

    def lineplot(self, df: pd.DataFrame, x: str, y: str) -> Figure:
        fig, ax = plt.subplots(figsize=(6,4))
        sns.lineplot(x=x, y=y, data=df, ax=ax)
        ax.set_title(f"Lineplot {y} over {x}")
        return fig
    
    def piechart(self, df: pd.DataFrame, column: str) -> Figure:
        fig, ax = plt.subplots(figsize=(5,5))
        df[column].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
        ax.set_ylabel('')
        ax.set_title(f"Pie chart of {column}")
        return fig

    def dispatch(self, df: pd.DataFrame, step: dict) -> Figure | None:
        name = step.get("name")
        params = step.get("params", {})

        if name == "heatmap":
            cols = params.get("columns", df.columns)
            numeric_cols = [c for c in cols if c in df.select_dtypes(include="number").columns]
            return self.heatmap(df, numeric_cols)
        elif name == "boxplot":
            return self.boxplot(df, params.get("column"), params.get("by"))
        elif name == "scatter":
            return self.scatter(df, params.get("x"), params.get("y"))
        elif name == "histogram":
            return self.histogram(df, params.get("column"))
        elif name == "barplot":
            return self.barplot(df, params.get("x"), params.get("y"))
        elif name == "lineplot":
            return self.lineplot(df, params.get("x"), params.get("y"))
        elif name == "piechart":
            return self.piechart(df, params.get("column"))
        print("[DEBUG]: Visualization action not considered yet!")
        return None