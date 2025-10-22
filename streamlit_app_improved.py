"""
Streamlit Financial Model Application - IMPROVED VERSION
With comprehensive assumption editing (no sliders!)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_assumptions import ModelAssumptions
from financial_model import FinancialModel
# from sensitivity_analysis import SensitivityAnalyzer  # Not used in this version

# Page config
st.set_page_config(
    page_title="Financial Model Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state
if 'model' not in st.session_state:
    st.session_state.model = None
if 'assumptions' not in st.session_state:
    st.session_state.assumptions = ModelAssumptions()

def format_currency(value):
    if pd.isna(value) or value is None:
        return "£0"
    if value < 0:
        return f"(£{abs(value):,.0f})"
    return f"£{value:,.0f}"

def format_percentage(value):
    if pd.isna(value) or value is None:
        return "0.0%"
    if value < 0:
        return f"({abs(value)*100:.1f}%)"
    return f"{value*100:.1f}%"

def format_year(value):
    """Format year without comma separator"""
    if pd.isna(value) or value is None:
        return ""
    return f"{int(value)}"

def create_bar_chart(df, x_col, y_col, title, y_label, color='#1f77b4'):
    """Generic bar chart creator"""
    if df is None or len(df) == 0:
        return None
    
    x_data = df[x_col].tolist()
    y_data = df[y_col].tolist()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_data,
        y=y_data,
        marker_color=color,
        text=[format_currency(v) if abs(v) > 1000 else f"{v:.1f}" for v in y_data],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title=y_label, rangemode='tozero'),
        height=500,
        showlegend=False
    )
    
    return fig

def create_revenue_chart(df):
    """Revenue with growth rate"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    revenue = df['Revenue'].tolist()
    growth = (df['Revenue YoY Growth %'] * 100).tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=revenue,
        name='Revenue',
        marker_color='#1f77b4',
        yaxis='y',
        text=[f"£{v/1e6:.1f}M" for v in revenue],
        textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=growth,
        name='YoY Growth %',
        marker_color='#ff7f0e',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3)
    ))
    
    fig.update_layout(
        title='Revenue and Growth Rate',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Revenue (£)', side='left', rangemode='tozero'),
        yaxis2=dict(title='Growth %', side='right', overlaying='y'),
        height=500,
        showlegend=True,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

def create_arr_chart(df):
    """ARR with growth rate"""
    if df is None or len(df) == 0:
        return None
    
    # Calculate ARR growth
    df_copy = df.copy()
    df_copy['ARR YoY Growth %'] = df_copy['ARR'].pct_change() * 100
    
    years = df_copy['Year'].tolist()
    arr = df_copy['ARR'].tolist()
    growth = df_copy['ARR YoY Growth %'].fillna(0).tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=arr,
        name='ARR',
        marker_color='#2ca02c',
        yaxis='y',
        text=[f"£{v/1e6:.1f}M" for v in arr],
        textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=growth,
        name='YoY Growth %',
        marker_color='#ff7f0e',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3)
    ))
    
    fig.update_layout(
        title='ARR and Growth Rate',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='ARR (£)', side='left', rangemode='tozero'),
        yaxis2=dict(title='Growth %', side='right', overlaying='y'),
        height=500,
        showlegend=True,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

def create_ebitda_chart(df):
    """EBITDA over time"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    ebitda = df['EBITDA'].tolist()
    colors = ['#2ca02c' if x >= 0 else '#d62728' for x in ebitda]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=ebitda,
        marker_color=colors,
        text=[f"£{v/1e6:.1f}M" if v >= 0 else f"(£{abs(v)/1e6:.1f}M)" for v in ebitda],
        textposition='outside'
    ))
    
    fig.add_hline(y=0, line_color="gray", line_width=1)
    
    fig.update_layout(
        title='EBITDA by Year',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='EBITDA (£)'),
        height=500,
        showlegend=False
    )
    
    return fig

def create_opex_total_chart(df):
    """Total Opex over time"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    opex = df['Operating Expenses'].tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=[abs(x) for x in opex],
        marker_color='#9467bd',
        text=[f"£{abs(v)/1e6:.1f}M" for v in opex],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Total Operating Expenses by Year',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Operating Expenses (£)', rangemode='tozero'),
        height=500,
        showlegend=False
    )
    
    return fig

def create_opex_by_category_chart(df):
    """Opex by category over time"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    
    # Get absolute values for display
    categories = {
        'Product Development': [abs(x) for x in df['Product Development'].tolist()],
        'Sales & Marketing': [abs(x) for x in df['Sales & Marketing'].tolist()],
        'Customer Success': [abs(x) for x in df['Customer Success'].tolist()],
        'G&A': [abs(x) for x in df['G&A'].tolist()]
    }
    
    colors = {
        'Product Development': '#1f77b4',
        'Sales & Marketing': '#ff7f0e',
        'Customer Success': '#2ca02c',
        'G&A': '#d62728'
    }
    
    fig = go.Figure()
    
    for category, values in categories.items():
        fig.add_trace(go.Bar(
            x=years,
            y=values,
            name=category,
            marker_color=colors[category]
        ))
    
    fig.update_layout(
        title='Operating Expenses by Category',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Operating Expenses (£)', rangemode='tozero'),
        barmode='stack',
        height=500,
        showlegend=True,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

def create_opex_percentage_chart(df):
    """Opex as percentage of total by category"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    
    # Calculate percentages
    total_opex = df['Operating Expenses'].abs()
    
    categories = {
        'Product Development': (df['Product Development'].abs() / total_opex * 100).tolist(),
        'Sales & Marketing': (df['Sales & Marketing'].abs() / total_opex * 100).tolist(),
        'Customer Success': (df['Customer Success'].abs() / total_opex * 100).tolist(),
        'G&A': (df['G&A'].abs() / total_opex * 100).tolist()
    }
    
    colors = {
        'Product Development': '#1f77b4',
        'Sales & Marketing': '#ff7f0e',
        'Customer Success': '#2ca02c',
        'G&A': '#d62728'
    }
    
    fig = go.Figure()
    
    for category, values in categories.items():
        fig.add_trace(go.Bar(
            x=years,
            y=values,
            name=category,
            marker_color=colors[category],
            text=[f"{v:.1f}%" for v in values],
            textposition='inside'
        ))
    
    fig.update_layout(
        title='Operating Expenses by Category (% of Total)',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Percentage of Total Opex (%)', rangemode='tozero'),
        barmode='stack',
        height=500,
        showlegend=True,
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

def create_margin_chart(df):
    """Gross and EBITDA margins"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    gross = (df['Gross Margin %'] * 100).tolist()
    ebitda = (df['EBITDA Margin %'] * 100).tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=gross,
        name='Gross Margin %',
        mode='lines+markers+text',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8),
        text=[f"{v:.1f}%" for v in gross],
        textposition='top center',
        textfont=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=ebitda,
        name='EBITDA Margin %',
        mode='lines+markers+text',
        line=dict(color='#d62728', width=3),
        marker=dict(size=8),
        text=[f"{v:.1f}%" for v in ebitda],
        textposition='bottom center',
        textfont=dict(size=10)
    ))
    
    fig.update_layout(
        title='Margin Evolution',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Margin %'),
        height=500,
        showlegend=True,
        legend=dict(x=0.01, y=0.01)
    )
    
    return fig

def create_cash_flow_chart(df):
    """Cash flow components"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=df['Operating Cash Flow'].tolist(),
        name='Operating CF',
        marker_color='#2ca02c'
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=df['Investing Cash Flow'].tolist(),
        name='Investing CF',
        marker_color='#d62728'
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=df['Financing Cash Flow'].tolist(),
        name='Financing CF',
        marker_color='#1f77b4'
    ))
    
    fig.update_layout(
        title='Cash Flow Components',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Cash Flow (£)'),
        barmode='relative',
        height=500,
        showlegend=True
    )
    
    return fig

def create_cash_balance_chart(df):
    """Cash balance over time"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    balance = df['Cash Balance c/f'].tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=balance,
        mode='lines+markers',
        fill='tozeroy',
        name='Cash Balance',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Cash Balance Over Time',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Cash Balance (£)', rangemode='tozero'),
        height=500,
        showlegend=False
    )
    
    return fig

def create_rule_of_40_chart(df):
    """Rule of 40"""
    if df is None or len(df) == 0:
        return None
    
    years = df['Year'].tolist()
    rule40 = df['Rule of 40'].tolist()
    colors = ['#2ca02c' if x >= 40 else '#d62728' for x in rule40]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=rule40,
        marker_color=colors,
        text=[f"{x:.1f}" for x in rule40],
        textposition='outside'
    ))
    
    fig.add_hline(y=40, line_dash="dash", line_color="gray", 
                  annotation_text="Target: 40")
    
    fig.update_layout(
        title='Rule of 40 Score',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Score'),
        height=500,
        showlegend=False
    )
    
    return fig

def get_excel_file_path():
    paths = [
        'Python_Financial_Model_Structure.xlsx',
        './Python_Financial_Model_Structure.xlsx',
        '/mnt/user-data/uploads/Python_Financial_Model_Structure.xlsx',
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def run_model():
    if 'excel_file_path' not in st.session_state:
        st.session_state.excel_file_path = get_excel_file_path()
    
    if st.session_state.excel_file_path is None:
        st.error("⚠️ Excel file not found")
        return
    
    with st.spinner("Running financial projections..."):
        try:
            model = FinancialModel(st.session_state.assumptions, st.session_state.excel_file_path)
            model.run_projections()
            st.session_state.model = model
            st.success("✅ Model completed successfully!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

def display_overview():
    """Overview tab"""
    st.title("📊 Financial Model Dashboard")
    
    if st.session_state.model is None:
        st.info("👈 Configure assumptions and click 'Run Model'")
        return
    
    model = st.session_state.model
    assumptions = st.session_state.assumptions
    combined_pl = model.get_combined_pl()
    
    # Key metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    profitable_years = model.pl_df[model.pl_df['EBITDA'] > 0]
    prof_year = int(profitable_years.iloc[0]['Year']) if len(profitable_years) > 0 else "Not achieved"
    
    with col1:
        st.metric("EBITDA Positive", prof_year)
    
    series_c_year = assumptions.series_c.close_date.year
    series_c_row = model.pl_df[model.pl_df['Year'] == series_c_year]
    if len(series_c_row) > 0:
        arr = series_c_row['ARR'].values[0]
        val = arr * assumptions.series_c.pre_money_arr_multiple
        with col2:
            st.metric("Series C Pre-Money", format_currency(val))
    
    exit_row = model.pl_df[model.pl_df['Year'] == assumptions.exit.exit_year]
    if len(exit_row) > 0:
        exit_ebitda = exit_row['EBITDA'].values[0]
        exit_arr = exit_row['ARR'].values[0]
        
        if assumptions.exit.valuation_basis == 'ebitda':
            exit_val = exit_ebitda * assumptions.exit.ebitda_multiple
        else:
            exit_val = exit_arr * assumptions.exit.arr_multiple
        
        with col3:
            st.metric("Exit Valuation", format_currency(exit_val))
        
        with col4:
            final_cash = model.cf_df.iloc[-1]['Cash Balance c/f']
            st.metric("Final Cash", format_currency(final_cash))
    
    # Valuation Details
    st.markdown("---")
    st.subheader("Valuation Metrics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Series C Valuation**")
        if len(series_c_row) > 0:
            st.write(f"📊 ARR at Close: **{format_currency(arr)}**")
            st.write(f"📈 ARR Multiple: **{assumptions.series_c.pre_money_arr_multiple:.1f}x**")
            st.write(f"💰 Pre-Money Valuation: **{format_currency(val)}**")
    
    with col2:
        st.markdown("**Exit Valuation**")
        if len(exit_row) > 0:
            if assumptions.exit.valuation_basis == 'ebitda':
                st.write(f"📊 EBITDA at Exit: **{format_currency(exit_ebitda)}**")
                st.write(f"📈 EBITDA Multiple: **{assumptions.exit.ebitda_multiple:.1f}x**")
            else:
                st.write(f"📊 ARR at Exit: **{format_currency(exit_arr)}**")
                st.write(f"📈 ARR Multiple: **{assumptions.exit.arr_multiple:.1f}x**")
            st.write(f"💰 Exit Valuation: **{format_currency(exit_val)}**")
    
    # Charts
    st.markdown("---")
    st.subheader("ARR Overview")
    fig = create_arr_chart(combined_pl)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='overview_arr')
    
    st.subheader("EBITDA Trajectory")
    fig = create_ebitda_chart(combined_pl)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='overview_ebitda')
    
    st.subheader("Profitability Trends")
    fig = create_margin_chart(combined_pl)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='overview_margins')

def display_pl_statement():
    """P&L tab"""
    st.title("📈 Profit & Loss Statement")
    
    if st.session_state.model is None:
        st.warning("Please run the model first")
        return
    
    model = st.session_state.model
    combined_pl = model.get_combined_pl()
    
    # Revenue chart
    st.subheader("Revenue & Growth")
    fig = create_revenue_chart(combined_pl)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='pl_revenue')
    
    # Margin chart
    st.subheader("Margin Analysis")
    fig = create_margin_chart(combined_pl)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='pl_margins')
    
    # Opex charts
    st.subheader("Operating Expenses Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        fig = create_opex_total_chart(combined_pl)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key='pl_opex_total')
    
    with col2:
        fig = create_opex_by_category_chart(combined_pl)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key='pl_opex_category')
    
    # Opex percentage chart
    fig = create_opex_percentage_chart(combined_pl)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='pl_opex_pct')
    
    # Data table
    st.subheader("Detailed P&L")
    display_df = combined_pl.copy()
    
    # Format year without commas
    display_df['Year'] = display_df['Year'].apply(format_year)
    
    currency_cols = ['Revenue', 'Cost of Sales', 'Gross Profit', 'Product Development', 
                     'Sales & Marketing', 'Customer Success', 'G&A', 'Operating Expenses',
                     'EBITDA', 'Interest Payable', 'DA', 'Exceptional Items', 
                     'Profit Before Tax', 'Tax', 'Net Income', 'ARR']
    
    for col in currency_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(format_currency)
    
    pct_cols = ['Revenue YoY Growth %', 'Gross Margin %', 'EBITDA Margin %']
    for col in pct_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(format_percentage)
    
    st.dataframe(display_df.set_index('Year'), use_container_width=True)

def display_cash_flow():
    """Cash Flow tab"""
    st.title("💰 Cash Flow Statement")
    
    if st.session_state.model is None:
        st.warning("Please run the model first")
        return
    
    model = st.session_state.model
    combined_cf = model.get_combined_cf()
    
    st.subheader("Cash Flow Components")
    fig = create_cash_flow_chart(combined_cf)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='cf_components')
    
    st.subheader("Cash Balance Trend")
    fig = create_cash_balance_chart(combined_cf)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='cf_balance')
    
    st.subheader("Detailed Cash Flow")
    display_df = combined_cf.copy()
    
    # Format year without commas
    display_df['Year'] = display_df['Year'].apply(format_year)
    
    for col in display_df.columns:
        if col != 'Year':
            display_df[col] = display_df[col].apply(format_currency)
    
    st.dataframe(display_df.set_index('Year'), use_container_width=True)

def display_balance_sheet():
    """Balance Sheet tab"""
    st.title("📋 Balance Sheet")
    
    if st.session_state.model is None:
        st.warning("Please run the model first")
        return
    
    model = st.session_state.model
    combined_bs = model.get_combined_bs()
    
    # Chart
    years = combined_bs['Year'].tolist()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=combined_bs['Total Assets'].tolist(),
        name='Total Assets',
        marker_color='#2ca02c'
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=combined_bs['Total Liabilities'].tolist(),
        name='Total Liabilities',
        marker_color='#d62728'
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=combined_bs['Net Assets'].tolist(),
        name='Net Assets',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Balance Sheet Overview',
        xaxis=dict(title='Year', dtick=1),
        yaxis=dict(title='Amount (£)'),
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True, key='bs_chart')
    
    # Table
    st.subheader("Detailed Balance Sheet")
    display_df = combined_bs.copy()
    
    # Format year without commas
    display_df['Year'] = display_df['Year'].apply(format_year)
    
    for col in display_df.columns:
        if col != 'Year':
            display_df[col] = display_df[col].apply(format_currency)
    
    st.dataframe(display_df.set_index('Year'), use_container_width=True)

def display_metrics():
    """Metrics tab"""
    st.title("📊 Operational Metrics")
    
    if st.session_state.model is None:
        st.warning("Please run the model first")
        return
    
    model = st.session_state.model
    combined_other = model.get_combined_other()
    
    # Rule of 40
    st.subheader("Rule of 40 Score")
    fig = create_rule_of_40_chart(combined_other)
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='metrics_rule40')
    
    # ARR
    st.subheader("ARR Growth")
    fig = create_bar_chart(combined_other, 'Year', 'ARR', 
                           'Annual Recurring Revenue', 'ARR (£)', '#1f77b4')
    if fig:
        st.plotly_chart(fig, use_container_width=True, key='metrics_arr')
    
    # Table
    st.subheader("Detailed Metrics")
    display_df = combined_other.copy()
    
    # Format year without commas
    display_df['Year'] = display_df['Year'].apply(format_year)
    
    display_df['Employee Numbers'] = display_df['Employee Numbers'].apply(lambda x: f"{x:,.0f}")
    display_df['ARR'] = display_df['ARR'].apply(format_currency)
    display_df['Rule of 40'] = display_df['Rule of 40'].apply(lambda x: f"{x:.1f}")
    display_df['Revenue per Employee'] = display_df['Revenue per Employee'].apply(format_currency)
    display_df['Opex per Employee'] = display_df['Opex per Employee'].apply(format_currency)
    
    st.dataframe(display_df.set_index('Year'), use_container_width=True)

def display_cap_table():
    """Cap Table tab"""
    st.title("🏢 Capitalization Table")
    
    if st.session_state.model is None:
        st.warning("Please run the model first")
        return
    
    model = st.session_state.model
    
    # Ownership
    st.subheader("Current Ownership Structure")
    ownership_df = model.cap_table.calculate_ownership_percentages()
    
    chart_df = ownership_df[ownership_df['Stakeholder'] != 'TOTAL'].copy()
    
    fig = px.pie(chart_df, values='Ownership %', names='Stakeholder',
                 title='Ownership Distribution', hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    
    st.plotly_chart(fig, use_container_width=True, key='cap_pie')
    
    # Table
    st.subheader("Ownership Details")
    display_df = ownership_df.copy()
    display_df['Shares'] = display_df['Shares'].apply(lambda x: f"{x:,.0f}")
    display_df['Ownership %'] = display_df['Ownership %'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(display_df, use_container_width=True)

def display_exit_waterfall():
    """Exit Waterfall tab"""
    st.title("🎯 Exit Waterfall Analysis")
    
    if st.session_state.model is None:
        st.warning("Please run the model first")
        return
    
    model = st.session_state.model
    waterfall_df = model.exit_waterfall_df.copy()
    
    # Metrics
    total_row = waterfall_df[waterfall_df['Stakeholder'] == 'TOTAL PROCEEDS']
    if len(total_row) > 0:
        st.metric("Total Exit Valuation", format_currency(total_row['Proceeds'].values[0]))
    
    # Chart
    st.subheader("Proceeds Distribution")
    chart_df = waterfall_df[
        ~waterfall_df['Stakeholder'].str.contains('TOTAL') & 
        (waterfall_df['Proceeds'] > 0)
    ].copy()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=chart_df['Stakeholder'].tolist(),
        y=chart_df['Proceeds'].tolist(),
        marker_color=['#d62728' if t == 'Debt' else '#2ca02c' for t in chart_df['Type']],
        text=[format_currency(x) for x in chart_df['Proceeds'].tolist()],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Exit Proceeds by Stakeholder',
        xaxis=dict(title='Stakeholder'),
        yaxis=dict(title='Proceeds (£)', rangemode='tozero'),
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, key='exit_proceeds')
    
    # Table
    st.subheader("Detailed Waterfall")
    display_df = waterfall_df.copy()
    display_df['Amount Invested'] = display_df['Amount Invested'].apply(format_currency)
    display_df['Proceeds'] = display_df['Proceeds'].apply(format_currency)
    display_df['Multiple (MoIC)'] = display_df['Multiple (MoIC)'].apply(lambda x: f"{x:.2f}x" if x > 0 else '-')
    display_df['IRR %'] = display_df['IRR %'].apply(lambda x: f"{x:.1f}%" if x > 0 else '-')
    
    st.dataframe(display_df, use_container_width=True)

def sidebar_inputs():
    """Sidebar controls with comprehensive assumption editing"""
    st.sidebar.title("📊 Model Controls")
    
    # File
    st.sidebar.markdown("### 📁 Data File")
    
    if 'excel_file_path' not in st.session_state:
        st.session_state.excel_file_path = get_excel_file_path()
    
    if st.session_state.excel_file_path and os.path.exists(st.session_state.excel_file_path):
        st.sidebar.success(f"✅ {os.path.basename(st.session_state.excel_file_path)}")
    else:
        st.sidebar.warning("⚠️ Excel file not found")
        uploaded = st.sidebar.file_uploader("Upload Excel", type=['xlsx'])
        if uploaded:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp.write(uploaded.getvalue())
                st.session_state.excel_file_path = tmp.name
            st.sidebar.success("✅ Uploaded!")
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Assumptions")
    
    assumptions = st.session_state.assumptions
    
    # Revenue Growth Rates
    with st.sidebar.expander("📈 Revenue Growth Rates", expanded=False):
        st.markdown("**Annual Revenue Growth %**")
        for year in [2025, 2026, 2027, 2028, 2029, 2030]:
            current_value = assumptions.revenue.get_growth_rate(year) * 100
            new_value = st.number_input(
                f"{year}",
                min_value=-50.0,
                max_value=200.0,
                value=float(current_value),
                step=1.0,
                format="%.1f",
                key=f"rev_growth_{year}"
            )
            setattr(assumptions.revenue, f'growth_{year}', new_value / 100)
    
    # Gross Margins
    with st.sidebar.expander("💰 Gross Margin %", expanded=False):
        st.markdown("**Gross Margin % by Year**")
        for year in [2025, 2026, 2027, 2028, 2029, 2030]:
            current_value = assumptions.gross_margin.get_margin(year) * 100
            new_value = st.number_input(
                f"{year}",
                min_value=50.0,
                max_value=100.0,
                value=float(current_value),
                step=0.5,
                format="%.1f",
                key=f"gm_{year}"
            )
            setattr(assumptions.gross_margin, f'margin_{year}', new_value / 100)
    
    # Opex Growth Rates
    with st.sidebar.expander("💼 Opex Growth Rates", expanded=False):
        st.markdown("**Operating Expense Growth %**")
        for year in [2025, 2026, 2027, 2028, 2029, 2030]:
            current_value = assumptions.opex_growth.get_growth_rate(year) * 100
            new_value = st.number_input(
                f"{year}",
                min_value=-50.0,
                max_value=100.0,
                value=float(current_value),
                step=1.0,
                format="%.1f",
                key=f"opex_growth_{year}"
            )
            setattr(assumptions.opex_growth, f'growth_{year}', new_value / 100)
    
    # Series C Financing
    with st.sidebar.expander("🏦 Series C Financing", expanded=False):
        st.markdown("**Series C Terms**")
        
        # Amount
        assumptions.series_c.amount = st.number_input(
            "Total Amount (£)",
            min_value=0.0,
            max_value=100_000_000.0,
            value=float(assumptions.series_c.amount),
            step=1_000_000.0,
            format="%.0f",
            key="series_c_amount"
        )
        
        # Close Date
        current_date = assumptions.series_c.close_date
        new_date = st.date_input(
            "Close Date",
            value=current_date,
            min_value=date(2025, 1, 1),
            max_value=date(2030, 12, 31),
            key="series_c_date"
        )
        assumptions.series_c.close_date = new_date
        
        st.markdown("**Structure Mix (must sum to 100%)**")
        
        # Equity %
        assumptions.series_c.equity_pct = st.number_input(
            "Equity %",
            min_value=0.0,
            max_value=100.0,
            value=float(assumptions.series_c.equity_pct * 100),
            step=5.0,
            format="%.1f",
            key="series_c_equity"
        ) / 100
        
        # Debt %
        assumptions.series_c.debt_pct = st.number_input(
            "Debt %",
            min_value=0.0,
            max_value=100.0,
            value=float(assumptions.series_c.debt_pct * 100),
            step=5.0,
            format="%.1f",
            key="series_c_debt"
        ) / 100
        
        # Convertible %
        assumptions.series_c.convertible_pct = st.number_input(
            "Convertible %",
            min_value=0.0,
            max_value=100.0,
            value=float(assumptions.series_c.convertible_pct * 100),
            step=5.0,
            format="%.1f",
            key="series_c_conv"
        ) / 100
        
        # Verify sum
        total_pct = (assumptions.series_c.equity_pct + 
                     assumptions.series_c.debt_pct + 
                     assumptions.series_c.convertible_pct) * 100
        if abs(total_pct - 100) > 0.1:
            st.warning(f"⚠️ Structure mix = {total_pct:.1f}% (should be 100%)")
        
        st.markdown("**Debt Terms**")
        
        # Debt Interest Rate
        assumptions.series_c.debt_interest_rate = st.number_input(
            "Debt Interest Rate %",
            min_value=0.0,
            max_value=30.0,
            value=float(assumptions.series_c.debt_interest_rate * 100),
            step=0.5,
            format="%.1f",
            key="debt_rate"
        ) / 100
        
        # Convertible Interest Rate
        assumptions.series_c.convertible_interest_rate = st.number_input(
            "Convertible Interest Rate %",
            min_value=0.0,
            max_value=30.0,
            value=float(assumptions.series_c.convertible_interest_rate * 100),
            step=0.5,
            format="%.1f",
            key="conv_rate"
        ) / 100
        
        st.markdown("**Valuation**")
        
        # ARR Multiple
        assumptions.series_c.pre_money_arr_multiple = st.number_input(
            "Pre-Money ARR Multiple",
            min_value=1.0,
            max_value=20.0,
            value=float(assumptions.series_c.pre_money_arr_multiple),
            step=0.5,
            format="%.1f",
            key="arr_multiple"
        )
    
    # Exit Assumptions
    with st.sidebar.expander("🎯 Exit Assumptions", expanded=False):
        st.markdown("**Exit/Liquidity Event**")
        
        # Exit Year
        assumptions.exit.exit_year = st.selectbox(
            "Exit Year",
            options=[2027, 2028, 2029, 2030, 2031],
            index=[2027, 2028, 2029, 2030, 2031].index(assumptions.exit.exit_year),
            key="exit_year"
        )
        
        # Valuation Basis
        valuation_options = ['higher_of_arr_or_ebitda', 'arr', 'ebitda']
        current_basis = assumptions.exit.valuation_basis
        if current_basis in valuation_options:
            default_index = valuation_options.index(current_basis)
        else:
            default_index = 0
        
        assumptions.exit.valuation_basis = st.selectbox(
            "Valuation Basis",
            options=valuation_options,
            index=default_index,
            key="exit_basis",
            help="Choose 'higher_of_arr_or_ebitda' to maximize shareholder value"
        )
        
        # EBITDA Multiple
        assumptions.exit.ebitda_multiple = st.number_input(
            "EBITDA Multiple",
            min_value=5.0,
            max_value=50.0,
            value=float(assumptions.exit.ebitda_multiple),
            step=1.0,
            format="%.1f",
            key="ebitda_mult"
        )
        
        # ARR Multiple
        assumptions.exit.arr_multiple = st.number_input(
            "ARR Multiple",
            min_value=3.0,
            max_value=20.0,
            value=float(assumptions.exit.arr_multiple),
            step=0.5,
            format="%.1f",
            key="arr_mult"
        )
    
    # Employee Growth
    with st.sidebar.expander("👥 Employee Growth", expanded=False):
        st.markdown("**Employee Headcount Growth %**")
        for year in [2025, 2026, 2027, 2028, 2029, 2030]:
            current_value = assumptions.employee_growth.get_growth_rate(year) * 100
            new_value = st.number_input(
                f"{year}",
                min_value=-50.0,
                max_value=100.0,
                value=float(current_value),
                step=1.0,
                format="%.1f",
                key=f"emp_growth_{year}"
            )
            setattr(assumptions.employee_growth, f'growth_{year}', new_value / 100)
    
    # Other Assumptions
    with st.sidebar.expander("🔧 Other Assumptions", expanded=False):
        st.markdown("**General**")
        
        # Tax Rate
        assumptions.tax_rate = st.number_input(
            "Tax Rate %",
            min_value=0.0,
            max_value=50.0,
            value=float(assumptions.tax_rate * 100),
            step=1.0,
            format="%.1f",
            key="tax_rate"
        ) / 100
        
        # DA as % of Revenue
        assumptions.da_as_pct_of_revenue = st.number_input(
            "D&A as % of Revenue",
            min_value=0.0,
            max_value=10.0,
            value=float(assumptions.da_as_pct_of_revenue * 100),
            step=0.1,
            format="%.1f",
            key="da_pct"
        ) / 100
    
    st.sidebar.markdown("---")
    
    # Action buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("▶️ Run Model", type="primary", use_container_width=True):
            run_model()
    with col2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.assumptions = ModelAssumptions()
            st.session_state.model = None
            st.rerun()

def main():
    """Main app"""
    sidebar_inputs()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "📈 P&L", "💰 Cash Flow", "📋 Balance Sheet",
        "📊 Metrics", "🏢 Cap Table", "🎯 Exit"
    ])
    
    with tab1:
        display_overview()
    with tab2:
        display_pl_statement()
    with tab3:
        display_cash_flow()
    with tab4:
        display_balance_sheet()
    with tab5:
        display_metrics()
    with tab6:
        display_cap_table()
    with tab7:
        display_exit_waterfall()

if __name__ == "__main__":
    main()
