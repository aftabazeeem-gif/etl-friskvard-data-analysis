# ETL Pipeline and Data Analysis – FriskvårdsCentrum Nordic

This repository contains an ETL pipeline and data analysis project created as part of the Data Science course at TUC Yrkeshögskola.

## Project Overview
The goal of this project is to transform raw gym booking data into a structured dataset and extract business insights using KPIs and sentiment analysis.

## Files in this repository
- analysis.ipynb – Main notebook containing the full ETL pipeline, analysis, visualizations, and sentiment analysis
- friskvard_data.csv – Raw input dataset
- friskvard_data_clean.csv – Cleaned and transformed dataset
- friskvard.db – SQLite database containing the final transformed data
- clean_data.py – Script used for initial data cleaning
- analyze_insights.py – Supporting analysis script

## ETL Process
- Extract: Data loaded from CSV files
- Transform: Data cleaned, standardized, feature engineered, and sentiment analyzed
- Load: Final dataset stored in a SQLite database

## Key Insights
- Average monthly cost differs significantly between membership types
- Some gym facilities have higher booking volumes than others
- Customer feedback is predominantly positive according to sentiment analysis
