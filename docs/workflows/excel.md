---
sidebar_position: 2
title: "Excel Data Workflow"
description: "Use AI to plan and build a repeatable Excel data-cleaning workflow with Python and pandas."
keywords: [Excel, data processing, Python, pandas, AI coding]
---

# Excel Data Workflow

This workflow helps you turn a messy spreadsheet into a clean summary file. It is designed for office tasks where you receive Excel exports and need reliable repeatable steps.

## Scenario

You have an employee spreadsheet with columns such as name, department, start date, and salary. You need to remove duplicates, standardize dates, summarize by department, and export the result.

## Step 1: Describe The Data

Give the AI the column names, a few sample rows, and the desired output.

~~~text
I have an Excel file named employees.xlsx.
Columns: name, department, start_date, salary.
Please write a Python pandas script that removes duplicate names,
standardizes start_date, groups by department, and exports summary.xlsx.
~~~

## Step 2: Ask For A Small Script

Ask for readable code, not a clever one-liner. Request comments only where the logic is not obvious.

~~~python
import pandas as pd

input_file = "employees.xlsx"
output_file = "summary.xlsx"

df = pd.read_excel(input_file)
df = df.drop_duplicates(subset=["name"])
df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

summary = (
    df.groupby("department", dropna=False)
    .agg(employee_count=("name", "count"), average_salary=("salary", "mean"))
    .reset_index()
)

summary.to_excel(output_file, index=False)
~~~

## Step 3: Test With A Copy

Never test on the only copy of a work file. Save a small sample first and confirm the output columns are correct.

## Step 4: Improve The Workflow

After the first script works, ask the AI to add:

- clear error messages when required columns are missing;
- a timestamped output file name;
- a second sheet with removed duplicate rows;
- instructions for running the script.

## Prompt Template

~~~text
Act as a careful data analyst.
I need a repeatable Excel workflow for [task].
Input file: [file name]
Columns: [columns]
Rules: [cleaning and summary rules]
Output: [desired file or sheets]
Please provide Python code using pandas and explain how to run it.
~~~
