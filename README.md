# 🤖 AI Business Analyst

> An LLM-powered business analytics agent that converts natural-language business questions into SQL, validates and executes queries, automatically repairs SQL execution errors, analyzes results, generates visualizations, and produces business-friendly insights.

---

## 📌 Overview

**AI Business Analyst** is an intelligent business analytics application built using **LangGraph, Python, PostgreSQL, Gemini, Groq, Streamlit, Pandas, and Plotly**.

The system allows business users to interact with structured business data using natural language instead of manually writing SQL queries.

For example, a user can ask:

> **"Which product category generated the most revenue?"**

The system automatically performs the analytical workflow:

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
```

---

## 🎯 Problem Statement

Traditional business analysis often requires users to manually:

- Understand the database structure
- Write SQL queries
- Validate and debug SQL
- Execute queries against the database
- Analyze returned data
- Create visualizations
- Interpret the results into business insights

This creates a gap between business questions and data-driven decisions, especially for users without strong SQL or technical skills.

AI Business Analyst automates this workflow by allowing users to ask business questions in natural language.

---

## 🚀 Key Features

- 🧠 Natural-language business analytics
- 🔄 LangGraph-based agent orchestration
- 🤖 Gemini → Groq LLM fallback
- 🔐 SQL validation before execution
- 🔧 Automatic SQL self-correction
- 🗄️ PostgreSQL database integration
- 📊 Automatic KPI and chart generation
- 🔍 Root-cause analysis
- 💡 AI-generated business insights
- 🖥️ Streamlit analytics interface
- 💰 Business-friendly ₹K / ₹M / ₹B formatting
- 🧪 End-to-end SQL repair testing

---

## 🏗️ Architecture

The application uses a stateful LangGraph workflow to coordinate the different stages of the business analysis process.

```text
                         ┌──────────────────────┐
                         │    Business User     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     Streamlit UI      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      LangGraph        │
                         │    Agent Workflow     │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       Intent Detection       SQL Generation       Data Analysis
              │                     │                     │
              │                     ▼                     │
              │              SQL Validation               │
              │                     │                     │
              │                     ▼                     │
              │             PostgreSQL Execution          │
              │                     │                     │
              │              Execution Error?             │
              │                 /       \                 │
              │               Yes        No                │
              │                │          │                │
              │                ▼          │                │
              │            SQL Repair     │                │
              │                │          │                │
              │                └──────────┘                │
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ▼
                            Visualization
                                    │
                                    ▼
                           Business Insight
```

---

## ⚙️ How It Works

```text
User Question
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
SQL Repair   Data Analysis
  ↓             ↓
Re-execute  Visualization
   ↘          ↙
    Business Insight
```

The workflow allows the system to recover from certain SQL execution errors and continue the analysis automatically.

---

## 🔧 SQL Self-Correction

One of the core features of the application is execution-aware SQL self-correction.

The system does not assume that every LLM-generated SQL query will execute successfully.

For example, an LLM may generate:

```sql
SELECT
    p.category,
    SUM(oi.revenue) AS total_revenue
FROM order_items oi
JOIN productss p
    ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC
LIMIT 1;
```

PostgreSQL returns:

```text
relation "productss" does not exist
```

Instead of stopping the application, the database error is routed back through the LangGraph workflow.

The SQL repair node can generate the corrected query:

```sql
SELECT
    p.category,
    SUM(oi.revenue) AS total_revenue
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC
LIMIT 1;
```

The repaired SQL is then validated and executed again.

```text
Generated SQL
      ↓
SQL Validation
      ↓
Database Execution
      ↓
Execution Error
      ↓
SQL Repair
      ↓
SQL Validation
      ↓
Re-execution
      ↓
Successful Result
```

Repair attempts are limited to prevent infinite correction loops.

---

## 🤖 LLM Provider Fallback

The application uses a multi-provider fallback strategy.

```text
              Gemini
                 ↓
             Available?
            ↙         ↘
          Yes          No
           ↓            ↓
        Response       Groq
                         ↓
                     Response
```

Gemini is used as the primary LLM provider.

If Gemini becomes unavailable because of quota limits, rate limits, or another provider error, the system automatically switches to Groq.

Example:

```text
🤖 Trying Gemini...
⚠️ Gemini unavailable.
🟢 Switching to Groq...
✅ Groq response received.
```

This prevents a temporary failure of one LLM provider from stopping the analytical workflow.

---

## 🔐 SQL Validation

Generated SQL is validated before database execution.

The workflow follows:

```text
LLM-generated SQL
       ↓
SQL Validation
       ↓
PostgreSQL
```

This provides an additional reliability layer between the LLM and the database.

---

## 🗄️ PostgreSQL Integration

PostgreSQL acts as the application's business data store.

The database layer handles:

- Database connection
- Schema management
- Query execution
- Structured result retrieval
- Database execution errors

Database operations are separated from the user interface and agent orchestration layers.

---

## 📊 Automatic Visualization

The application automatically selects an appropriate visualization based on the returned data.

**KPI Analysis**

For questions such as *"What is the total revenue?"*, the application displays a formatted KPI.

Example: `₹43.50M`

**Category Analysis**

For questions such as *"Which product category generated the most revenue?"*, the application generates a category comparison visualization.

**Time-Series Analysis**

For questions such as *"How did revenue change over the last 6 months?"*, the application generates a time-series visualization.

---

## 💰 Business KPI Formatting

Large monetary values are formatted into business-friendly units.

| Raw Value | Formatted |
|---|---|
| ₹43,501,095 | ₹43.50M |
| ₹11,183,572 | ₹11.18M |
| ₹463,900 | ₹463.9K |

Supported formats include:

- ₹K — Thousands
- ₹M — Millions
- ₹B — Billions

---

## 🔍 Root-Cause Analysis

The application supports analytical questions beyond simple aggregations.

Examples:

- "Why did revenue drop?"
- "Which categories contributed most to the decline?"
- "Which products caused the largest revenue loss?"

The root-cause workflow can analyze changes across:

- Time periods
- Product categories
- Individual products

Example:

| Metric | Value |
|---|---|
| August 2025 | ₹2.08M |
| September 2025 | ₹1.62M |
| Revenue Change | -₹463.9K |
| Change % | -22.25% |

The system can then identify major category and product contributors to the change.

---

## 💡 AI Business Insights

After analyzing the query results, the system generates a concise business-friendly interpretation.

Example:

> **Key Insight:** The Furniture category generated the highest revenue, totaling ₹11.18M.
>
> **Evidence:**
> - Category: Furniture
> - Total revenue: ₹11,183,572.77
>
> **Business Takeaway:** Furniture is the leading revenue driver among product categories.

The insight generator is designed to:

- Use only the provided data
- Avoid fabricated facts
- Support findings with numerical evidence
- Distinguish observations from assumptions
- Present results in business-friendly language

---

## 🖥️ Application Screenshots

**Main Dashboard**

**Analytics & Visualization**

**Root-Cause Analysis**

---

## 💬 Example Questions

**Revenue Analysis**
- What is the total revenue?

**Category Performance**
- Which product category generated the most revenue?

**Product Performance**
- What are the top 5 products by revenue?

**Trend Analysis**
- How did revenue change over the last 6 months?

**Root-Cause Analysis**
- Why did revenue drop?

**Category Drivers**
- Which categories contributed most to the decline?

**Product Drivers**
- Which products caused the largest revenue loss?

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| LangGraph | Stateful agent orchestration |
| PostgreSQL | Business database |
| SQLAlchemy | Database interaction |
| Gemini | Primary LLM provider |
| Groq | Fallback LLM provider |
| Pandas | Data processing and analysis |
| Plotly | Data visualization |
| Streamlit | User interface |
| python-dotenv | Environment configuration |

---

## 📂 Project Structure

```text
ai-business-analyst/
│
├── app/
│   ├── agents/
│   │   ├── business_agent.py
│   │   ├── deep_root_cause_agent.py
│   │   ├── insight_generator.py
│   │   ├── query_executor.py
│   │   ├── root_cause_agent.py
│   │   ├── sql_generator.py
│   │   └── sql_validator.py
│   │
│   ├── analytics/
│   │   ├── analysis.py
│   │   ├── monthly_analysis.py
│   │   ├── product_root_cause.py
│   │   ├── question_parser.py
│   │   ├── root_cause.py
│   │   └── visualization.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── schema.py
│   │   └── seed.py
│   │
│   ├── graph/
│   │   ├── business_graph.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   ├── test_end_to_end_repair.py
│   │   ├── test_sql_repair.py
│   │   └── visualize_graph.py
│   │
│   ├── llm/
│   │   └── llm_client.py
│   │
│   └── ui/
│       └── streamlit_app.py
│
├── screenshots/
│   ├── main_dashboard.png
│   ├── analytics_visualization.png
│   └── root_cause_analysis.png
│
├── business_analyst_graph.png
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/KrishnaTiwari1cr/ai-business-analyst.git
cd ai-business-analyst
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install Dependencies

Install the dependencies required by the project:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_postgresql_database_url
```

⚠️ Never commit `.env` to GitHub.

### 6. Run the Application

```bash
streamlit run app/ui/streamlit_app.py
```

---

## 🧪 Testing

**LangGraph Workflow**

```bash
python -m app.graph.business_graph
```

**SQL Self-Correction**

```bash
python -m app.graph.test_end_to_end_repair
```

This test intentionally introduces an invalid database reference and verifies the SQL repair workflow.

**SQL Repair**

```bash
python -m app.graph.test_sql_repair
```

**Visualization**

```bash
python -m app.analytics.visualization
```

---

## 🔄 End-to-End Execution Flow

1. User asks a business question
2. Intent is detected
3. SQL is generated
4. SQL is validated
5. SQL is executed against PostgreSQL
6. If execution fails, SQL repair is triggered
7. Repaired SQL is validated
8. Query is executed again
9. Results are analyzed
10. Visualization data is prepared
11. Chart / KPI is generated
12. Business insight is generated
13. Final result is displayed

---

## 🛡️ Reliability Features

The system includes several reliability mechanisms:

- **LLM Fallback** — Gemini → Groq
- **SQL Validation** — Generated SQL is validated before database execution
- **SQL Execution Recovery** — Database errors can trigger automatic SQL repair
- **Retry Limiting** — SQL repair attempts are bounded to prevent infinite loops
- **Empty Response Handling** — The application checks for empty responses from LLM providers
- **Visualization Fallback** — The visualization layer can use suitable query results when dedicated visualization data is unavailable

---

## 🧪 SQL Self-Correction Test

The project includes an end-to-end test that intentionally introduces an invalid table reference.

Example: `productss` instead of `products`.

The test verifies:

```text
Invalid SQL
    ↓
Database Error
    ↓
LangGraph Error Routing
    ↓
SQL Repair
    ↓
SQL Validation
    ↓
Database Execution
    ↓
Successful Result
```

---

## 🚀 Future Improvements

Potential future enhancements include:

- Multi-turn conversational analytics
- Query history
- User authentication
- Role-based database access
- Semantic database schema retrieval
- Advanced anomaly detection
- Revenue forecasting
- Automated KPI monitoring
- Scheduled business reports
- Email and Slack alerts
- Query caching
- LLM evaluation framework
- Production observability
- Docker deployment
- Cloud deployment
- Fine-grained SQL permissions

---

## 🎯 Project Objective

The project demonstrates how LLMs and agentic workflows can automate traditional business intelligence tasks.

**Traditional Workflow**

```text
Business Question
       ↓
Manual SQL
       ↓
Database Query
       ↓
Manual Analysis
       ↓
Manual Visualization
       ↓
Manual Business Summary
```

**AI Business Analyst**

```text
Business Question
       ↓
AI Business Analyst
       ↓
SQL Generation
       ↓
Validation
       ↓
Execution
       ↓
Analysis
       ↓
Visualization
       ↓
Business Insight
```

---

## 🔐 Security Considerations

This project is primarily intended for educational and portfolio purposes.

A production deployment should additionally implement:

- Authentication
- Authorization
- Read-only database users
- Database role restrictions
- SQL sandboxing
- Query allowlists / denylists
- Rate limiting
- API key protection
- Audit logging
- Monitoring and observability
- Input validation

---

## 👨‍💻 Author

**Krishna Tiwari**

B.Tech Computer Science

**Interests**
- Data Analytics
- AI Engineering
- Generative AI
- Agentic AI
- Machine Learning

---

## ⭐ Project Highlights

```text
Natural Language
       ↓
SQL Generation
       ↓
LangGraph Agent
       ↓
SQL Validation
       ↓
SQL Self-Correction
       ↓
PostgreSQL
       ↓
Data Analysis
       ↓
Automatic Visualization
       ↓
Business Insight
```

Built with Python · LangGraph · PostgreSQL · Gemini · Groq · Pandas · Plotly · Streamlit
