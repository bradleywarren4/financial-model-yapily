"""
P&L Projection Module
Projects income statement based on assumptions
"""

import pandas as pd
import numpy as np
from typing import Dict
from config_assumptions import ModelAssumptions

class PLProjector:
    """Project P&L statement"""
    
    def __init__(self, assumptions: ModelAssumptions, base_year_revenue: float, 
                 base_year_opex: float, base_year_arr: float):
        self.assumptions = assumptions
        self.base_year_revenue = base_year_revenue
        self.base_year_opex = base_year_opex
        self.base_year_arr = base_year_arr
        self.years = list(range(2025, 2031))
        self.projections = {}
        
    def project_revenue(self) -> Dict[int, float]:
        """Project revenue based on growth assumptions"""
        revenue = {}
        prev_revenue = self.base_year_revenue
        
        for year in self.years:
            growth = self.assumptions.revenue.get_growth_rate(year)
            revenue[year] = prev_revenue * (1 + growth)
            prev_revenue = revenue[year]
        
        return revenue
    
    def calculate_arr(self, revenue: Dict[int, float]) -> Dict[int, float]:
        """
        Calculate ARR based on revenue growth
        
        METHODOLOGY:
        ARR (Annual Recurring Revenue) is projected to grow at the same rate as total revenue.
        
        The approach:
        1. Start with 2024 historical ARR (£8.1M from your data)
        2. For each forecast year, apply the same growth rate that revenue experiences
        3. Formula: ARR(year) = ARR(year-1) * (1 + Revenue Growth Rate)
        
        Example:
        - 2024 ARR: £8.1M
        - 2025 Revenue growth: 35%
        - 2025 ARR: £8.1M * 1.35 = £10.9M
        
        This assumes ARR maintains roughly the same proportion of revenue as it grows,
        which is reasonable for SaaS companies with consistent recurring revenue models.
        
        Historical context from your data:
        - 2023 ARR: £5.36M, Revenue: £5.05M (ARR/Revenue = 106%)
        - 2024 ARR: £8.10M, Revenue: £6.59M (ARR/Revenue = 123%)
        
        The ratio varies because ARR can include committed contracts not yet recognized
        as revenue. The model projects ARR growing with revenue momentum.
        """
        arr = {}
        prev_arr = self.base_year_arr
        prev_revenue = self.base_year_revenue
        
        for year in self.years:
            # ARR grows in line with revenue growth rate
            if prev_arr > 0 and prev_revenue > 0:
                revenue_growth = (revenue[year] / prev_revenue) - 1
                arr[year] = prev_arr * (1 + revenue_growth)
            else:
                # Fallback: If no historical ARR, estimate at 80% of revenue
                # (conservative assumption for SaaS companies)
                arr[year] = revenue[year] * 0.80
            prev_arr = arr[year]
            prev_revenue = revenue[year]
        
        return arr
    
    def project_gross_profit(self, revenue: Dict[int, float]) -> Dict[int, Dict[str, float]]:
        """Project gross profit and margins"""
        gross_profit_data = {}
        
        for year in self.years:
            margin = self.assumptions.gross_margin.get_margin(year)
            gross_profit = revenue[year] * margin
            cost_of_sales = revenue[year] - gross_profit
            
            gross_profit_data[year] = {
                'revenue': revenue[year],
                'cost_of_sales': -cost_of_sales,
                'gross_profit': gross_profit,
                'gross_margin': margin
            }
        
        return gross_profit_data
    
    def project_opex(self) -> Dict[int, Dict[str, float]]:
        """Project operating expenses"""
        opex_data = {}
        prev_total_opex = self.base_year_opex
        
        for year in self.years:
            growth = self.assumptions.opex_growth.get_growth_rate(year)
            total_opex = prev_total_opex * (1 + growth)
            
            # Get mix for the year
            mix = self.assumptions.opex_mix.get_mix(year)
            
            opex_data[year] = {
                'total_opex': total_opex,
                'product_dev': total_opex * mix['product_dev'],
                'sales_marketing': total_opex * mix['sales_marketing'],
                'customer_success': total_opex * mix['customer_success'],
                'ga': total_opex * mix['ga']
            }
            
            prev_total_opex = total_opex
        
        return opex_data
    
    def calculate_ebitda(self, gross_profit_data: Dict[int, Dict[str, float]], 
                         opex_data: Dict[int, Dict[str, float]]) -> Dict[int, Dict[str, float]]:
        """Calculate EBITDA and margin"""
        ebitda_data = {}
        
        for year in self.years:
            gross_profit = gross_profit_data[year]['gross_profit']
            total_opex = opex_data[year]['total_opex']
            revenue = gross_profit_data[year]['revenue']
            
            ebitda = gross_profit - total_opex
            ebitda_margin = ebitda / revenue if revenue > 0 else 0
            
            ebitda_data[year] = {
                'ebitda': ebitda,
                'ebitda_margin': ebitda_margin
            }
        
        return ebitda_data
    
    def calculate_interest(self, year: int) -> float:
        """
        Calculate interest expense for a year
        
        For rolled-up debt, interest is calculated on the beginning-of-year balance.
        This means the interest compounds year over year.
        """
        total_interest = 0
        
        # Check if Series C has closed - CLNs convert to equity at Series C
        series_c_closed = year >= self.assumptions.series_c.close_date.year
        
        # CLN 2024 interest (only if Series C hasn't closed yet)
        if not series_c_closed and year >= 2024 and year <= self.assumptions.historical_funding.cln_2024_maturity:
            # For CLNs, interest is rolled up, so calculate on beginning balance
            years_outstanding = year - 2024
            beginning_balance = (self.assumptions.historical_funding.cln_2024 * 
                               (1 + self.assumptions.historical_funding.cln_2024_interest) ** years_outstanding)
            interest = beginning_balance * self.assumptions.historical_funding.cln_2024_interest
            total_interest += interest
        
        # CLN 2025 interest (only if Series C hasn't closed yet)
        if not series_c_closed and year >= 2025 and year <= self.assumptions.historical_funding.cln_2025_maturity:
            years_outstanding = year - 2025
            beginning_balance = (self.assumptions.historical_funding.cln_2025 * 
                               (1 + self.assumptions.historical_funding.cln_2025_interest) ** years_outstanding)
            interest = beginning_balance * self.assumptions.historical_funding.cln_2025_interest
            total_interest += interest
        
        # Series C debt interest (if applicable)
        if year >= self.assumptions.series_c.close_date.year:
            debt_component = self.assumptions.series_c.amount * self.assumptions.series_c.debt_pct
            if debt_component > 0:
                if self.assumptions.series_c.debt_repayment_profile == "rolled_up":
                    # For rolled-up debt, calculate interest on beginning-of-year balance
                    years_outstanding = year - self.assumptions.series_c.close_date.year
                    beginning_balance = debt_component * (1 + self.assumptions.series_c.debt_interest_rate) ** years_outstanding
                    interest = beginning_balance * self.assumptions.series_c.debt_interest_rate
                    total_interest += interest
                else:
                    # For interest-only or amortizing: simple interest on principal
                    total_interest += debt_component * self.assumptions.series_c.debt_interest_rate
        
        # Series C convertible interest (if applicable)
        if year >= self.assumptions.series_c.close_date.year:
            conv_component = self.assumptions.series_c.amount * self.assumptions.series_c.convertible_pct
            if conv_component > 0:
                if self.assumptions.series_c.convertible_repayment_profile == "rolled_up":
                    # For rolled-up convertible, calculate interest on beginning-of-year balance
                    years_outstanding = year - self.assumptions.series_c.close_date.year
                    beginning_balance = conv_component * (1 + self.assumptions.series_c.convertible_interest_rate) ** years_outstanding
                    interest = beginning_balance * self.assumptions.series_c.convertible_interest_rate
                    total_interest += interest
                else:
                    # For interest-only or amortizing: simple interest on principal
                    total_interest += conv_component * self.assumptions.series_c.convertible_interest_rate
        
        return -total_interest  # Negative because it's an expense
    
    def project_da(self, revenue: Dict[int, float]) -> Dict[int, float]:
        """Project depreciation and amortization"""
        da = {}
        for year in self.years:
            da[year] = -revenue[year] * self.assumptions.da_as_pct_of_revenue
        return da
    
    def project_full_pl(self) -> pd.DataFrame:
        """Project complete P&L statement"""
        
        # Project each component
        revenue = self.project_revenue()
        arr = self.calculate_arr(revenue)
        gross_profit_data = self.project_gross_profit(revenue)
        opex_data = self.project_opex()
        ebitda_data = self.calculate_ebitda(gross_profit_data, opex_data)
        da = self.project_da(revenue)
        
        # Build P&L DataFrame
        pl_data = []
        
        for year in self.years:
            # Calculate interest
            interest = self.calculate_interest(year)
            
            # Calculate PBT
            ebitda = ebitda_data[year]['ebitda']
            pbt = ebitda + interest + da[year]  # DA is already negative
            
            # Calculate tax (only on positive profits)
            tax = -pbt * self.assumptions.tax_rate if pbt > 0 else 0
            
            # Net income
            net_income = pbt + tax
            
            # Revenue growth
            if year == 2025:
                rev_growth = (revenue[year] / self.base_year_revenue) - 1
            else:
                rev_growth = (revenue[year] / revenue[year-1]) - 1
            
            pl_data.append({
                'Year': year,
                'Revenue': revenue[year],
                'Revenue YoY Growth %': rev_growth,
                'Cost of Sales': gross_profit_data[year]['cost_of_sales'],
                'Gross Profit': gross_profit_data[year]['gross_profit'],
                'Gross Margin %': gross_profit_data[year]['gross_margin'],
                'Product Development': -opex_data[year]['product_dev'],
                'Sales & Marketing': -opex_data[year]['sales_marketing'],
                'Customer Success': -opex_data[year]['customer_success'],
                'G&A': -opex_data[year]['ga'],
                'Operating Expenses': -opex_data[year]['total_opex'],
                'EBITDA': ebitda,
                'EBITDA Margin %': ebitda_data[year]['ebitda_margin'],
                'Interest Payable': interest,
                'DA': da[year],
                'Exceptional Items': 0,  # Assume no exceptional items in forecast
                'Profit Before Tax': pbt,
                'Tax': tax,
                'Net Income': net_income,
                'ARR': arr[year]
            })
        
        return pd.DataFrame(pl_data)
