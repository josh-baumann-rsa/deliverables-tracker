import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import yaml


def _load_yaml(filepath: Path) -> dict:
    with open(filepath) as f:
        data = yaml.safe_load(f)
    return data


def _date_offset_months(x_months):
    return pd.DateOffset(months=x_months)


def _date_offset_months_alt(x_months):
    return pd.DateOffset(days=30 * x_months)


def make_plotly_table_from_summary(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=[
                        "Project",
                        "Milestone ID",
                        "Description",
                        "Deliverable",
                        "Value",
                        "Due Date",
                    ],
                    align="left",
                ),
                cells=dict(
                    values=[
                        df.name,
                        df.milestone,
                        df.description,
                        df.deliverable,
                        df.value,
                        df.due_date,
                    ],
                    align="left",
                ),
            )
        ],
    )

    fig.update_layout(
        title_text=f"RSA Master Deliverables List ({datetime.date.today()})",
        updatemenus=[
            {
                "buttons": [
                    {
                        "label": c,
                        "method": "update",
                        "args": [
                            {
                                "cells": {
                                    "values": df.T.values
                                    if c == "All"
                                    else df.loc[df["name"].eq(c)].T.values,
                                    "align": "left",
                                }
                            }
                        ],
                    }
                    for c in ["All"] + df["name"].unique().tolist()
                ]
            }
        ],
    )

    return fig


class Project:
    def __init__(self, filepath) -> None:
        yaml_data = _load_yaml(filepath)
        self.name = yaml_data["name"]
        self.initiated = yaml_data["initiated"]
        self.milestones = pd.DataFrame.from_dict(yaml_data["milestones"])

        try:
            self.milestones["due_date"] = self.initiated + self.milestones[
                "due_date_months"
            ].apply(_date_offset_months)
        except ValueError:
            self.milestones["due_date"] = self.initiated + self.milestones[
                "due_date_months"
            ].apply(_date_offset_months_alt)

        self.milestones["due_date_datetime"] = pd.to_datetime(
            self.milestones["due_date"]
        )
        self.milestones["due_date"] = self.milestones["due_date_datetime"].dt.strftime(
            "%Y-%m-%d"
        )

        self.milestones["value"] = self.milestones["value"].apply(
            lambda x: "${:,.2f}".format(x)
        )

    def summary_df(self) -> pd.DataFrame:
        df = self.milestones
        df.insert(loc=0, column="name", value=self.name)
        df = df.drop(columns=["due_date_months"])
        df = df.drop(columns=["due_date_datetime"])
        return df


def main():
    save_name = f"output/master_deliverables_{datetime.date.today()}".replace("-", "_")

    df_master = pd.DataFrame()
    projects_path = Path(__file__).parent / "projects"
    all_project_filepaths = list(projects_path.glob("*.yaml"))
    for this_project_filepath in all_project_filepaths:
        this_project = Project(this_project_filepath)
        df_master = pd.concat([df_master, this_project.summary_df()])

    df_master = df_master.sort_values(by="due_date")

    df_master.to_html(f"{save_name}_ugly.html", index=False)

    fig = make_plotly_table_from_summary(df=df_master)
    fig.show()
    fig.write_html(f"{save_name}.html")


if __name__ == "__main__":
    main()
