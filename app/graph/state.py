from typing import TypedDict, Optional, Any

import pandas as pd


class BusinessAnalystState(TypedDict, total=False):

    # =====================================================
    # USER QUESTION
    # =====================================================

    question: str

    # =====================================================
    # INTENT
    # =====================================================

    intent: Optional[str]

    target_month: Optional[Any]

    root_cause_focus: Optional[str]

    root_cause_direction: Optional[str]

    period_source: Optional[str]

    # =====================================================
    # SQL
    # =====================================================

    sql: Optional[str]

    sql_valid: bool

    sql_validation_message: Optional[str]

    # =====================================================
    # DATABASE EXECUTION
    # =====================================================

    execution_success: bool

    execution_error: Optional[str]

    data: Optional[pd.DataFrame]

    # =====================================================
    # VISUALIZATION
    # =====================================================

    visualization_data: Optional[pd.DataFrame]

    chart_path: Optional[str]

    # =====================================================
    # ANALYSIS
    # =====================================================

    analysis: Optional[Any]

    # =====================================================
    # ROOT CAUSE ANALYSIS
    # =====================================================

    category_analysis: Optional[pd.DataFrame]

    product_analysis: Optional[pd.DataFrame]

    previous_month: Optional[Any]

    current_month: Optional[Any]

    previous_total: Optional[float]

    current_total: Optional[float]

    revenue_change: Optional[float]

    revenue_change_percent: Optional[float]

    # =====================================================
    # FINAL INSIGHT
    # =====================================================

    insight: Optional[str]

    # =====================================================
    # LLM PROVIDER
    # =====================================================

    provider: Optional[str]

    # =====================================================
    # SQL REPAIR
    # =====================================================

    retry_count: int

    # =====================================================
    # GENERAL ERROR
    # =====================================================

    error: Optional[str]
