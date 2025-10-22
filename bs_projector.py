"""
Balance Sheet Projection Module
Projects balance sheet based on cash flow and debt
"""

import pandas as pd
from typing import Dict
from config_assumptions import ModelAssumptions

class BalanceSheetProjector:
    """Project balance sheet"""
    
    def __init__(self, assumptions: ModelAssumptions, 
                 base_year_assets: float, 
                 base_year_liabilities: float,
                 base_year_net_assets: float):
        self.assumptions = assumptions
        self.base_year_assets = base_year_assets
        self.base_year_liabilities = base_year_liabilities
        self.base_year_net_assets = base_year_net_assets
        self.years = list(range(2025, 2031))
    
    def calculate_exceptional_item_liability(self, year: int) -> float:
        """
        Calculate outstanding exceptional item liability
        £9.3M total, paid in equal installments 2025-2029
        """
        exceptional_item_total = 9_300_000
        annual_payment = exceptional_item_total / 5  # 5 years: 2025-2029
        
        if year < 2025:
            return exceptional_item_total  # Full liability before payments start
        elif year <= 2029:
            years_paid = year - 2024  # How many years of payments made
            return exceptional_item_total - (annual_payment * years_paid)
        else:
            return 0  # Fully paid off after 2029
    
    def calculate_total_debt(self, year: int) -> float:
        """Calculate total debt outstanding for a year"""
        total_debt = 0
        
        # Check if Series C has closed - CLNs convert to equity at Series C
        series_c_closed = year >= self.assumptions.series_c.close_date.year
        
        # CLN 2024 - rolled up with interest (only if Series C hasn't closed yet)
        if not series_c_closed and year >= 2024 and year <= self.assumptions.historical_funding.cln_2024_maturity:
            years_outstanding = year - 2024
            cln_2024_balance = (self.assumptions.historical_funding.cln_2024 * 
                               (1 + self.assumptions.historical_funding.cln_2024_interest) ** years_outstanding)
            total_debt += cln_2024_balance
        
        # CLN 2025 - rolled up with interest (only if Series C hasn't closed yet)
        if not series_c_closed and year >= 2025 and year <= self.assumptions.historical_funding.cln_2025_maturity:
            years_outstanding = year - 2025
            cln_2025_balance = (self.assumptions.historical_funding.cln_2025 * 
                               (1 + self.assumptions.historical_funding.cln_2025_interest) ** years_outstanding)
            total_debt += cln_2025_balance
        
        # Series C debt component
        if year >= self.assumptions.series_c.close_date.year:
            debt_component = self.assumptions.series_c.amount * self.assumptions.series_c.debt_pct
            if self.assumptions.series_c.debt_repayment_profile == "rolled_up":
                years_outstanding = year - self.assumptions.series_c.close_date.year
                debt_balance = debt_component * (1 + self.assumptions.series_c.debt_interest_rate) ** years_outstanding
                total_debt += debt_balance
            else:
                # Simplified: outstanding principal (not modeling amortization in detail)
                total_debt += debt_component
        
        # Series C convertible component
        if year >= self.assumptions.series_c.close_date.year:
            conv_component = self.assumptions.series_c.amount * self.assumptions.series_c.convertible_pct
            if self.assumptions.series_c.convertible_repayment_profile == "rolled_up":
                years_outstanding = year - self.assumptions.series_c.close_date.year
                conv_balance = conv_component * (1 + self.assumptions.series_c.convertible_interest_rate) ** years_outstanding
                total_debt += conv_balance
            else:
                total_debt += conv_component
        
        return total_debt
    
    def project_balance_sheet(self, cf_df: pd.DataFrame, pl_df: pd.DataFrame) -> pd.DataFrame:
        """Project complete balance sheet"""
        bs_data = []
        
        for year in self.years:
            # Get cash from cash flow projection
            cash_row = cf_df[cf_df['Year'] == year]
            cash = cash_row['Cash Balance c/f'].values[0] if len(cash_row) > 0 else 0
            
            # Calculate total debt
            total_debt = self.calculate_total_debt(year)
            
            # Calculate exceptional item liability
            exceptional_liability = self.calculate_exceptional_item_liability(year)
            
            # Get cumulative net income for retained earnings
            pl_subset = pl_df[pl_df['Year'] <= year]
            cumulative_net_income = pl_subset['Net Income'].sum()
            
            # Get Series C equity raised
            if year >= self.assumptions.series_c.close_date.year:
                equity_raised = self.assumptions.series_c.amount * self.assumptions.series_c.equity_pct
            else:
                equity_raised = 0
            
            # Historical equity (simplified)
            historical_equity = (self.assumptions.historical_funding.founder_2018 +
                               self.assumptions.historical_funding.seed_2019 +
                               self.assumptions.historical_funding.series_a_2020 +
                               self.assumptions.historical_funding.series_b1_2021 +
                               self.assumptions.historical_funding.series_b2_2022)
            
            # Total equity = historical + Series C equity + retained earnings from 2025 onwards
            total_equity = historical_equity + equity_raised + cumulative_net_income
            
            # Total liabilities (debt + exceptional items + other liabilities from base)
            # ✓ YES - Exceptional Item Liability IS part of Total Liabilities
            # Assume other liabilities stay constant at historical base
            other_liabilities_base = self.base_year_liabilities - 6000000 - 9300000  # Subtract CLN 2024 and exceptional item
            total_liabilities = total_debt + exceptional_liability + abs(other_liabilities_base)
            
            # Total assets = cash + other assets (assumed to grow with revenue)
            pl_row = pl_df[pl_df['Year'] == year]
            revenue = pl_row['Revenue'].values[0] if len(pl_row) > 0 else 0
            
            # Other assets scale with revenue growth
            revenue_growth_from_base = revenue / pl_df.iloc[0]['Revenue'] if len(pl_df) > 0 else 1
            other_assets_base = self.base_year_assets - self.base_year_liabilities  # Net assets approx
            other_assets = max(0, abs(other_assets_base) * revenue_growth_from_base)
            
            total_assets = cash + other_assets
            
            # Net assets
            net_assets = total_assets - total_liabilities
            
            bs_data.append({
                'Year': year,
                'Total Assets': total_assets,
                'Total Liabilities': -total_liabilities,  # Negative per convention
                'Net Assets': net_assets,
                'Cash': cash,
                'Total Debt': total_debt,
                'Exceptional Item Liability': exceptional_liability
            })
        
        return pd.DataFrame(bs_data)
