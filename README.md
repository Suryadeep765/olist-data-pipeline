# Olist E-Commerce Data Pipeline & Analytics

An end-to-end data engineering and analytics project built using Python, Pandas, PostgreSQL, SQLAlchemy, Pytest, Jupyter Notebook, and Power BI using the Brazilian Olist e-commerce dataset.

## Project Overview

This project implements a complete data pipeline for ingesting, validating, transforming, storing, and analyzing multi-source e-commerce data.

The pipeline processes multiple CSV sources, converts product data to JSON as part of the ingestion workflow, performs automated data-quality checks, transforms the data into analysis-ready datasets, and loads the resulting relational data into PostgreSQL.

The project also includes SQL-based business analytics and exploratory data analysis using Python.

## Architecture

```text
Olist CSV / JSON Sources
          |
          v
     Data Ingestion
          |
          v
   Data Quality Checks
          |
          v
   Data Transformation
          |
          v
      PostgreSQL
          |
          +----------------+
          |                |
          v                v
     SQL Analytics     Python EDA
                           |
                           v
                    Power BI Dashboard
