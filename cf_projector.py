"""
Cash Flow Projection Module
Projects cash flow statement based on P&L and financing activities
"""

import pandas as pd
from typing import Dict
from datetime import date
from config_assumptions import ModelAssumptions

class CashFlowProjector:
    """Project cash flow statement"""
    
    def __init__(self, assumptions: ModelAssumptions, base_year_cash: float):
        self.assumptions = assumptions
        self.base_year_cash = base_year_cash
        self.years = list(range(2025, 2031))
    
    def calculate_exceptional_item_payment(self, year: int) -> float:
        """
        Calculate exceptional item payment for the year
        £9.3M spread equally over 2025-2029 = £1.86M per year
        """
        exceptional_item_total = 9_300_000
        payment_years = [2025, 2026, 2027, 2028, 2029]
        annual_payment = exceptional_item_total / len(payment_years)
        
        if year in payment_years:
            return -annual_payment  # Negative because it's a cash outflow
        return 0
    
    def calculate_operating_cash_flow(self, pl_df: pd.DataFrame) -> Dict[int, float]:
        """
        Calculate operating cash flow from P&L
        Simplified: EBITDA - Tax + changes in working capital (assumed minimal)
        """
        ocf = {}
        
        for _, row in pl_df.iterrows():
            year = int(row['Year'])
            # Operating cash flow ≈ EBITDA + Tax paid (tax is already negative if expense)
            # Simplified model: assume working capital changes are minimal
            ocf[year] = row['EBITDA'] + row['Tax']
        
        return ocf
    
    def calculate_investing_cash_flow(self, pl_df: pd.DataFrame) -> Dict[int, float]:
        """
        Calculate investing cash flow
        Capex assumed as % of revenue (tied to DA)
        """
        icf = {}
        
        for _, row in pl_df.iterrows():
            year = int(row['Year'])
            # Capex roughly equals DA for steady state
            # Use DA as proxy (DA is negative, capex is negative cash flow)
            capex = row['DA']  # Already negative
            icf[year] = capex
        
        return icf
    
    def calculate_financing_cash_flow(self, pl_df: pd.DataFrame) -> Dict[int, float]:
        """
        Calculate financing cash flow including Series C and CLN
        """
        fcf = {}
        
        for year in self.years:
            financing = 0
            
            # CLN 2025 (drawn in 2025)
            if year == 2025:
                financing += self.assumptions.historical_funding.cln_2025
            
            # Series C funding
            if year == self.assumptions.series_c.close_date.year:
                financing += self.assumptions.series_c.amount
            
            fcf[year] = financing
        
        return fcf
    
    def project_cash_flow(self, pl_df: pd.DataFrame) -> pd.DataFrame:
        """Project complete cash flow statement"""
        ocf = self.calculate_operating_cash_flow(pl_df)
        icf = self.calculate_investing_cash_flow(pl_df)
        fcf = self.calculate_financing_cash_flow(pl_df)
        
        cf_data = []
        cash_balance = self.base_year_cash
        
        for year in self.years:
            operating = ocf[year]
            investing = icf[year]
            financing = fcf[year]
            
            # Add exceptional item payment as operating outflow
            # ✓ YES - Exceptional Item Payment IS part of Net Change in Cash
            exceptional_payment = self.calculate_exceptional_item_payment(year)
            operating += exceptional_payment
            
            net_change = operating + investing + financing
            
            cash_bf = cash_balance
            cash_cf = cash_bf + net_change
            cash_balance = cash_cf
            
            cf_data.append({
                'Year': year,
                'Operating Cash Flow': operating,
                'Investing Cash Flow': investing,
                'Financing Cash Flow': financing,
                'Exceptional Item Payment': exceptional_payment,
                'Net Change in Cash': net_change,
                'Cash Balance b/f': cash_bf,
                'Cash Balance c/f': cash_cf
            })
        
        return pd.DataFrame(cf_data)
