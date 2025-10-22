"""
Exit Waterfall Module
Calculates distribution of exit proceeds to stakeholders
"""

import pandas as pd
from typing import Dict, List
from config_assumptions import ModelAssumptions
from cap_table import CapTableManager

class ExitWaterfallCalculator:
    """Calculate exit waterfall and returns by stakeholder"""
    
    def __init__(self, assumptions: ModelAssumptions, cap_table: CapTableManager):
        self.assumptions = assumptions
        self.cap_table = cap_table
    
    def calculate_exit_valuation(self, exit_year_arr: float, exit_year_ebitda: float) -> Dict[str, float]:
        """
        Calculate exit valuation based on assumptions
        
        Returns a dictionary with:
        - 'arr_valuation': Valuation based on ARR multiple
        - 'ebitda_valuation': Valuation based on EBITDA multiple
        - 'final_valuation': The valuation used (highest or specified basis)
        - 'valuation_method': Which method was used ('ARR', 'EBITDA', or 'Higher of ARR/EBITDA')
        """
        arr_valuation = exit_year_arr * self.assumptions.exit.arr_multiple
        ebitda_valuation = exit_year_ebitda * self.assumptions.exit.ebitda_multiple
        
        # Determine which valuation to use
        if self.assumptions.exit.valuation_basis == "arr":
            final_valuation = arr_valuation
            valuation_method = "ARR"
        elif self.assumptions.exit.valuation_basis == "ebitda":
            final_valuation = ebitda_valuation
            valuation_method = "EBITDA"
        else:  # "higher_of_arr_or_ebitda" or any other value
            # ALWAYS choose the higher valuation to maximize shareholder value
            if arr_valuation >= ebitda_valuation:
                final_valuation = arr_valuation
                valuation_method = "Higher of ARR/EBITDA (ARR Selected)"
            else:
                final_valuation = ebitda_valuation
                valuation_method = "Higher of ARR/EBITDA (EBITDA Selected)"
        
        return {
            'arr_valuation': arr_valuation,
            'ebitda_valuation': ebitda_valuation,
            'final_valuation': final_valuation,
            'valuation_method': valuation_method
        }
    
    def calculate_debt_to_repay(self, exit_year: int) -> Dict[str, float]:
        """Calculate all debt that needs to be repaid at exit"""
        debt_obligations = {}
        
        # CLN 2024 - with rolled up interest
        if exit_year >= 2024:
            years_outstanding = exit_year - 2024
            cln_2024_balance = (self.assumptions.historical_funding.cln_2024 * 
                               (1 + self.assumptions.historical_funding.cln_2024_interest) ** years_outstanding)
            debt_obligations['CLN 2024'] = cln_2024_balance
        
        # CLN 2025 - with rolled up interest
        if exit_year >= 2025:
            years_outstanding = exit_year - 2025
            cln_2025_balance = (self.assumptions.historical_funding.cln_2025 * 
                               (1 + self.assumptions.historical_funding.cln_2025_interest) ** years_outstanding)
            debt_obligations['CLN 2025'] = cln_2025_balance
        
        # Series C debt component
        if exit_year >= self.assumptions.series_c.close_date.year:
            debt_component = self.assumptions.series_c.amount * self.assumptions.series_c.debt_pct
            if self.assumptions.series_c.debt_repayment_profile == "rolled_up":
                years_outstanding = exit_year - self.assumptions.series_c.close_date.year
                debt_balance = debt_component * (1 + self.assumptions.series_c.debt_interest_rate) ** years_outstanding
                debt_obligations['Series C Debt'] = debt_balance
            else:
                debt_obligations['Series C Debt'] = debt_component
        
        # Series C convertible component
        if exit_year >= self.assumptions.series_c.close_date.year:
            conv_component = self.assumptions.series_c.amount * self.assumptions.series_c.convertible_pct
            if self.assumptions.series_c.convertible_repayment_profile == "rolled_up":
                years_outstanding = exit_year - self.assumptions.series_c.close_date.year
                conv_balance = conv_component * (1 + self.assumptions.series_c.convertible_interest_rate) ** years_outstanding
                debt_obligations['Series C Convertible'] = conv_balance
            else:
                debt_obligations['Series C Convertible'] = conv_component
        
        return debt_obligations
    
    def calculate_waterfall(self, exit_year_arr: float, exit_year_ebitda: float, exit_year: int) -> pd.DataFrame:
        """
        Calculate complete exit waterfall
        Priority: 1) Debt, 2) Equity pro-rata by ownership
        
        Returns DataFrame with valuation details included
        """
        # Calculate exit valuation (returns dict with both valuations)
        valuation_data = self.calculate_exit_valuation(exit_year_arr, exit_year_ebitda)
        exit_valuation = valuation_data['final_valuation']
        
        # Calculate debt to repay
        debt_obligations = self.calculate_debt_to_repay(exit_year)
        total_debt = sum(debt_obligations.values())
        
        # Proceeds available to equity after debt repayment
        proceeds_to_equity = exit_valuation - total_debt
        
        # Calculate equity distribution
        ownership_df = self.cap_table.calculate_ownership_percentages()
        
        waterfall_data = []
        
        # Add debt repayments with original investment amounts and IRR
        # CLN 2024
        if 'CLN 2024' in debt_obligations:
            years_held = exit_year - 2024
            proceeds = debt_obligations['CLN 2024']
            invested = self.assumptions.historical_funding.cln_2024
            moic = proceeds / invested if invested > 0 else 0
            irr = ((moic ** (1/years_held)) - 1) * 100 if years_held > 0 and moic > 0 else 0
            
            waterfall_data.append({
                'Stakeholder': 'CLN 2024',
                'Type': 'Debt',
                'Amount Invested': invested,
                'Proceeds': proceeds,
                'Multiple (MoIC)': round(moic, 2),
                'IRR %': round(irr, 2)
            })
        
        # CLN 2025
        if 'CLN 2025' in debt_obligations:
            years_held = exit_year - 2025
            proceeds = debt_obligations['CLN 2025']
            invested = self.assumptions.historical_funding.cln_2025
            moic = proceeds / invested if invested > 0 else 0
            irr = ((moic ** (1/years_held)) - 1) * 100 if years_held > 0 and moic > 0 else 0
            
            waterfall_data.append({
                'Stakeholder': 'CLN 2025',
                'Type': 'Debt',
                'Amount Invested': invested,
                'Proceeds': proceeds,
                'Multiple (MoIC)': round(moic, 2),
                'IRR %': round(irr, 2)
            })
        
        # Series C Debt
        if 'Series C Debt' in debt_obligations:
            years_held = exit_year - self.assumptions.series_c.close_date.year
            proceeds = debt_obligations['Series C Debt']
            invested = self.assumptions.series_c.amount * self.assumptions.series_c.debt_pct
            moic = proceeds / invested if invested > 0 else 0
            irr = ((moic ** (1/years_held)) - 1) * 100 if years_held > 0 and moic > 0 else 0
            
            waterfall_data.append({
                'Stakeholder': 'Series C Debt',
                'Type': 'Debt',
                'Amount Invested': invested,
                'Proceeds': proceeds,
                'Multiple (MoIC)': round(moic, 2),
                'IRR %': round(irr, 2)
            })
        
        # Series C Convertible
        if 'Series C Convertible' in debt_obligations:
            years_held = exit_year - self.assumptions.series_c.close_date.year
            proceeds = debt_obligations['Series C Convertible']
            invested = self.assumptions.series_c.amount * self.assumptions.series_c.convertible_pct
            moic = proceeds / invested if invested > 0 else 0
            irr = ((moic ** (1/years_held)) - 1) * 100 if years_held > 0 and moic > 0 else 0
            
            waterfall_data.append({
                'Stakeholder': 'Series C Convertible',
                'Type': 'Debt',
                'Amount Invested': invested,
                'Proceeds': proceeds,
                'Multiple (MoIC)': round(moic, 2),
                'IRR %': round(irr, 2)
            })
        
        # Add equity distributions
        for _, row in ownership_df.iterrows():
            # Skip the TOTAL row
            if row['Stakeholder'] == 'TOTAL':
                continue
                
            stakeholder_name = row['Stakeholder']
            ownership_pct = row['Ownership %'] / 100
            proceeds = proceeds_to_equity * ownership_pct
            
            # Find investment amount and year for this stakeholder
            round_data = [r for r in self.cap_table.cap_table_history if r['round'] == stakeholder_name]
            if round_data:
                invested = round_data[0]['investment']
                invest_year = round_data[0]['year']
                moic = proceeds / invested if invested > 0 else 0
                
                # Calculate proper IRR
                years_held = exit_year - invest_year
                if years_held > 0 and moic > 0:
                    irr = ((moic ** (1/years_held)) - 1) * 100
                else:
                    irr = 0
            else:
                invested = 0
                moic = 0
                irr = 0
            
            waterfall_data.append({
                'Stakeholder': stakeholder_name,
                'Type': 'Equity',
                'Amount Invested': invested,
                'Proceeds': proceeds,
                'Multiple (MoIC)': round(moic, 2),
                'IRR %': round(irr, 2)
            })
        
        # Add summary rows
        total_debt_invested = sum([self.assumptions.historical_funding.cln_2024,
                                   self.assumptions.historical_funding.cln_2025,
                                   self.assumptions.series_c.amount * self.assumptions.series_c.debt_pct,
                                   self.assumptions.series_c.amount * self.assumptions.series_c.convertible_pct])
        
        waterfall_data.append({
            'Stakeholder': 'TOTAL DEBT',
            'Type': 'Summary',
            'Amount Invested': total_debt_invested,
            'Proceeds': total_debt,
            'Multiple (MoIC)': round(total_debt / total_debt_invested if total_debt_invested > 0 else 0, 2),
            'IRR %': 0
        })
        
        total_equity_invested = sum([r['investment'] for r in self.cap_table.cap_table_history])
        
        waterfall_data.append({
            'Stakeholder': 'TOTAL EQUITY',
            'Type': 'Summary',
            'Amount Invested': total_equity_invested,
            'Proceeds': proceeds_to_equity,
            'Multiple (MoIC)': round(proceeds_to_equity / total_equity_invested if total_equity_invested > 0 else 0, 2),
            'IRR %': 0
        })
        
        waterfall_data.append({
            'Stakeholder': 'TOTAL PROCEEDS',
            'Type': 'Summary',
            'Amount Invested': total_debt_invested + total_equity_invested,
            'Proceeds': exit_valuation,
            'Multiple (MoIC)': 0,
            'IRR %': 0
        })
        
        return pd.DataFrame(waterfall_data)
