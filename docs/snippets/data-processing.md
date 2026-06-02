---
sidebar_position: 2
title: "Data Processing Snippets"
description: "Small Python snippets for reading, cleaning, merging, and summarizing CSV or Excel data."
keywords: [data processing, Python, pandas, CSV, Excel]
---

# Data Processing Snippets

Use these snippets as starting points for common data cleanup tasks.

## Read A CSV

~~~python
import pandas as pd

df = pd.read_csv("input.csv")
print(df.head())
print(df.columns)
~~~

## Read An Excel File

~~~python
import pandas as pd

df = pd.read_excel("input.xlsx")
print(df.head())
~~~

## Remove Duplicate Rows

~~~python
import pandas as pd

df = pd.read_csv("input.csv")
clean = df.drop_duplicates()
clean.to_csv("deduplicated.csv", index=False)
~~~

## Clean Column Names

~~~python
import pandas as pd

df = pd.read_csv("input.csv")
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)
df.to_csv("clean_columns.csv", index=False)
~~~

## Group And Summarize

~~~python
import pandas as pd

df = pd.read_csv("sales.csv")
summary = (
    df.groupby("region")
    .agg(total_sales=("amount", "sum"), order_count=("amount", "count"))
    .reset_index()
)
summary.to_csv("summary_by_region.csv", index=False)
~~~

## Merge Two CSV Files

~~~python
import pandas as pd

orders = pd.read_csv("orders.csv")
customers = pd.read_csv("customers.csv")

merged = orders.merge(customers, on="customer_id", how="left")
merged.to_csv("orders_with_customers.csv", index=False)
~~~

## Prompt To Adapt A Snippet

~~~text
Adapt this pandas snippet to my file.
Input file:
Columns:
Cleaning rules:
Output file:
Please include checks for missing columns and explain how to run it.
~~~
