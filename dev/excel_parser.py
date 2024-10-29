import pandas as pd
import yaml

df = pd.read_excel(
    "/Users/joshbaumann/sw/tools/deliverables-tracker/TACFI_Combined_Milestone_Draft_20240729.xlsx",
    header=6,
    usecols="B:G",
)

df["Expected Delivery (Award + Months)"] = df[
    "Expected Delivery (Award + Months)"
].str.replace("Award + ", "")
df["Expected Delivery (Award + Months)"] = (
    df["Expected Delivery (Award + Months)"].str.replace(" Months", "").astype(int)
)

print(df)
with open("df_to_yaml.yaml", "w") as file:
    documents = yaml.dump(
        df.to_dict(orient="records"), file, default_flow_style=False, sort_keys=False
    )
