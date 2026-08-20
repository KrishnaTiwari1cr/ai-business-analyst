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
