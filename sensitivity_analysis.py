"""
Sensitivity Analysis Module
Performs scenario analysis on key assumptions
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from config_assumptions import ModelAssumptions
from financial_model import FinancialModel
import copy

class SensitivityAnalyzer:
    """Perform sensitivity analysis on financial model"""
    
    def __init__(self, base_assumptions: ModelAssumptions, historical_data_path: str):
        self.base_assumptions = base_assumptions
        self.historical_data_path = historical_data_path
    
    def run_scenario(self, scenario_name: str, assumption_changes: Dict) -> Dict:
        """Run a single scenario with modified assumptions"""
        # Create a copy of assumptions
        scenario_assumptions = copy.deepcopy(self.base_assumptions)
        
        # Apply changes
        for key_path, value in assumption_changes.items():
            keys = key_path.split('.')
            obj = scenario_assumptions
            for key in keys[:-1]:
                obj = getattr(obj, key)
            setattr(obj, keys[-1], value)
        
        # Run model
        model = FinancialModel(scenario_assumptions, self.historical_data_path)
        model.run_projections()
        
        # Extract key metrics
        pl_df = model.pl_df
        cf_df = model.cf_df
        
        # Find profitability year (EBITDA > 0)
        profitable_years = pl_df[pl_df['EBITDA'] > 0]
        profitability_year = profitable_years.iloc[0]['Year'] if len(profitable_years) > 0 else None
        
        # Series C valuation
        series_c_year = scenario_assumptions.series_c.close_date.year
        series_c_row = pl_df[pl_df['Year'] == series_c_year]
        series_c_arr = series_c_row['ARR'].values[0] if len(series_c_row) > 0 else 0
        series_c_valuation = series_c_arr * scenario_assumptions.series_c.pre_money_arr_multiple
        
        # Exit metrics
        exit_row = pl_df[pl_df['Year'] == scenario_assumptions.exit.exit_year]
        exit_arr = exit_row['ARR'].values[0] if len(exit_row) > 0 else 0
        exit_ebitda = exit_row['EBITDA'].values[0] if len(exit_row) > 0 else 0
        
        if scenario_assumptions.exit.valuation_basis == "arr":
            exit_valuation = exit_arr * scenario_assumptions.exit.arr_multiple
        else:
            exit_valuation = exit_ebitda * scenario_assumptions.exit.ebitda_multiple
        
        # Final cash position
        final_cash = cf_df.iloc[-1]['Cash Balance c/f']
        
        # Rule of 40 in exit year
        rule_of_40 = model.other_df.iloc[-1]['Rule of 40']
        
        return {
            'scenario': scenario_name,
            'profitability_year': profitability_year,
            'series_c_pre_money_val': series_c_valuation,
            'exit_valuation': exit_valuation,
            'exit_arr': exit_arr,
            'exit_ebitda': exit_ebitda,
            'exit_ebitda_margin': exit_row['EBITDA Margin %'].values[0] if len(exit_row) > 0 else 0,
            'final_cash_position': final_cash,
            'rule_of_40_at_exit': rule_of_40
        }
    
    def run_revenue_growth_sensitivity(self) -> pd.DataFrame:
        """Test sensitivity to revenue growth rates"""
        scenarios = []
        
        # Base case
        base_result = self.run_scenario('Base Case', {})
        scenarios.append(base_result)
        
        # Bull case: Higher growth
        bull_changes = {
            'revenue.growth_2025': 0.45,
            'revenue.growth_2026': 0.50,
            'revenue.growth_2027': 0.45,
            'revenue.growth_2028': 0.40,
            'revenue.growth_2029': 0.35,
            'revenue.growth_2030': 0.30
        }
        scenarios.append(self.run_scenario('Bull Case (High Growth)', bull_changes))
        
        # Bear case: Lower growth
        bear_changes = {
            'revenue.growth_2025': 0.25,
            'revenue.growth_2026': 0.30,
            'revenue.growth_2027': 0.25,
            'revenue.growth_2028': 0.20,
            'revenue.growth_2029': 0.15,
            'revenue.growth_2030': 0.10
        }
        scenarios.append(self.run_scenario('Bear Case (Low Growth)', bear_changes))
        
        return pd.DataFrame(scenarios)
    
    def run_margin_sensitivity(self) -> pd.DataFrame:
        """Test sensitivity to gross margins"""
        scenarios = []
        
        # Base case
        base_result = self.run_scenario('Base Case', {})
        scenarios.append(base_result)
        
        # Higher margins
        high_margin_changes = {
            'gross_margin.margin_2025': 0.97,
            'gross_margin.margin_2026': 0.98,
            'gross_margin.margin_2027': 0.98,
            'gross_margin.margin_2028': 0.99,
            'gross_margin.margin_2029': 0.99,
            'gross_margin.margin_2030': 0.99
        }
        scenarios.append(self.run_scenario('High Margins', high_margin_changes))
        
        # Lower margins
        low_margin_changes = {
            'gross_margin.margin_2025': 0.94,
            'gross_margin.margin_2026': 0.94,
            'gross_margin.margin_2027': 0.95,
            'gross_margin.margin_2028': 0.95,
            'gross_margin.margin_2029': 0.96,
            'gross_margin.margin_2030': 0.96
        }
        scenarios.append(self.run_scenario('Low Margins', low_margin_changes))
        
        return pd.DataFrame(scenarios)
    
    def run_opex_efficiency_sensitivity(self) -> pd.DataFrame:
        """Test sensitivity to opex growth"""
        scenarios = []
        
        # Base case
        base_result = self.run_scenario('Base Case', {})
        scenarios.append(base_result)
        
        # High efficiency (lower opex growth)
        efficient_changes = {
            'opex_growth.growth_2025': 0.00,
            'opex_growth.growth_2026': 0.10,
            'opex_growth.growth_2027': 0.15,
            'opex_growth.growth_2028': 0.15,
            'opex_growth.growth_2029': 0.12,
            'opex_growth.growth_2030': 0.10
        }
        scenarios.append(self.run_scenario('High Efficiency', efficient_changes))
        
        # Low efficiency (higher opex growth)
        inefficient_changes = {
            'opex_growth.growth_2025': 0.10,
            'opex_growth.growth_2026': 0.30,
            'opex_growth.growth_2027': 0.35,
            'opex_growth.growth_2028': 0.30,
            'opex_growth.growth_2029': 0.25,
            'opex_growth.growth_2030': 0.20
        }
        scenarios.append(self.run_scenario('Low Efficiency', inefficient_changes))
        
        return pd.DataFrame(scenarios)
    
    def run_exit_multiple_sensitivity(self) -> pd.DataFrame:
        """Test sensitivity to exit multiples"""
        scenarios = []
        
        # Test different EBITDA multiples
        for multiple in [15, 20, 25, 30, 35]:
            changes = {'exit.ebitda_multiple': float(multiple)}
            result = self.run_scenario(f'{multiple}x EBITDA', changes)
            scenarios.append(result)
        
        return pd.DataFrame(scenarios)
    
    def run_comprehensive_scenarios(self) -> Dict[str, pd.DataFrame]:
        """Run all sensitivity analyses"""
        return {
            'Revenue Growth': self.run_revenue_growth_sensitivity(),
            'Gross Margin': self.run_margin_sensitivity(),
            'Opex Efficiency': self.run_opex_efficiency_sensitivity(),
            'Exit Multiples': self.run_exit_multiple_sensitivity()
        }
