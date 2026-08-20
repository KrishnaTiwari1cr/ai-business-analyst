# 🤖 AI Business Analyst

> An LLM-powered business analytics agent that converts natural-language business questions into SQL, validates and executes queries, automatically repairs SQL execution errors, analyzes results, generates visualizations, and produces business-friendly insights.

---

## 📌 Overview

**AI Business Analyst** is an intelligent business analytics application built using **LangGraph, Python, PostgreSQL, Gemini, Groq, Streamlit, Pandas, and Plotly**.

The system allows business users to interact with structured business data using natural language instead of manually writing SQL queries.

For example, a user can ask:

> **"Which product category generated the most revenue?"**

The system automatically:

```text
Natural Language Question
          ↓
Intent Detection
          ↓
SQL Generation
          ↓
SQL Validation
          ↓
PostgreSQL Execution
          ↓
Execution Error?
     ↙          ↘
   Yes           No
    ↓             ↓
 SQL Repair    Data Analysis
    ↓             ↓
 Re-execute   Visualization
     ↘          ↙
      Business Insight
---

## 🎯 Problem Statement

Traditional business analysis often requires users to manually write SQL queries, validate database results, analyze data, create visualizations, and interpret the findings.

AI Business Analyst automates this workflow by allowing users to ask business questions in natural language.

For example:

> "Which product category generated the most revenue?"

The system automatically converts the question into SQL, validates and executes the query, analyzes the result, generates a visualization, and produces a business-friendly insight.
