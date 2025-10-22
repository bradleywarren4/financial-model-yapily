"""
Historical Data Loading Module
Loads and processes historical financial data from Excel
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

class HistoricalDataLoader:
    """Load and process historical financial data"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load data from Excel file"""
        self.data = pd.read_excel(self.excel_path, sheet_name='Financial Model Structure')
    
    def get_revenue_history(self) -> Dict[int, float]:
        """Get historical revenue by year"""
        revenue_row = self.data[self.data['Period'] == 'Revenue']
        return {
            2021: float(revenue_row[2021].values[0]),
            2022: float(revenue_row[2022].values[0]),
            2023: float(revenue_row[2023].values[0]),
            2024: float(revenue_row[2024].values[0])
        }
    
    def get_gross_profit_history(self) -> Dict[int, float]:
        """Get historical gross profit by year"""
        gp_row = self.data[self.data['Period'] == 'Gross Profit']
        return {
            2021: float(gp_row[2021].values[0]),
            2022: float(gp_row[2022].values[0]),
            2023: float(gp_row[2023].values[0]),
            2024: float(gp_row[2024].values[0])
        }
    
    def get_gross_margin_history(self) -> Dict[int, float]:
        """Get historical gross margin by year"""
        margin_row = self.data[self.data['Period'] == 'Gross Margin %']
        return {
            2021: float(margin_row[2021].values[0]),
            2022: float(margin_row[2022].values[0]),
            2023: float(margin_row[2023].values[0]),
            2024: float(margin_row[2024].values[0])
        }
    
    def get_opex_history(self) -> Dict[int, Dict[str, float]]:
        """Get historical operating expenses breakdown"""
        opex_data = {}
        
        for year in [2021, 2022, 2023, 2024]:
            opex_data[year] = {
                'total': float(self.data[self.data['Period'] == 'Operating Expenses'][year].values[0]),
                'sales_marketing': float(self.data[self.data['Period'] == '  Sales & Marketing'][year].values[0]),
                'product_dev': float(self.data[self.data['Period'] == '  Product Development'][year].values[0]),
                'customer_success': float(self.data[self.data['Period'] == '  Customer Success'][year].values[0]),
                'ga': float(self.data[self.data['Period'] == '  G&A'][year].values[0])
            }
        
        return opex_data
    
    def get_ebitda_history(self) -> Dict[int, float]:
        """Get historical EBITDA"""
        ebitda_row = self.data[self.data['Period'] == 'EBITDA']
        return {
            2021: float(ebitda_row[2021].values[0]),
            2022: float(ebitda_row[2022].values[0]),
            2023: float(ebitda_row[2023].values[0]),
            2024: float(ebitda_row[2024].values[0])
        }
    
    def get_interest_history(self) -> Dict[int, float]:
        """Get historical interest payable"""
        interest_row = self.data[self.data['Period'] == 'Interest Payable']
        return {
            2021: float(interest_row[2021].values[0]),
            2022: float(interest_row[2022].values[0]),
            2023: float(interest_row[2023].values[0]),
            2024: float(interest_row[2024].values[0])
        }
    
    def get_da_history(self) -> Dict[int, float]:
        """Get historical depreciation & amortization"""
        da_row = self.data[self.data['Period'] == 'DA']
        return {
            2021: float(da_row[2021].values[0]),
            2022: float(da_row[2022].values[0]),
            2023: float(da_row[2023].values[0]),
            2024: float(da_row[2024].values[0])
        }
    
    def get_exceptional_items_history(self) -> Dict[int, float]:
        """Get historical exceptional items"""
        exc_row = self.data[self.data['Period'] == 'Exceptional Items']
        return {
            2021: float(exc_row[2021].values[0]),
            2022: float(exc_row[2022].values[0]),
            2023: float(exc_row[2023].values[0]),
            2024: float(exc_row[2024].values[0])
        }
    
    def get_tax_history(self) -> Dict[int, float]:
        """Get historical tax"""
        tax_row = self.data[self.data['Period'] == 'Tax']
        return {
            2021: float(tax_row[2021].values[0]),
            2022: float(tax_row[2022].values[0]),
            2023: float(tax_row[2023].values[0]),
            2024: float(tax_row[2024].values[0])
        }
    
    def get_net_income_history(self) -> Dict[int, float]:
        """Get historical net income"""
        ni_row = self.data[self.data['Period'] == 'Net Income']
        return {
            2021: float(ni_row[2021].values[0]),
            2022: float(ni_row[2022].values[0]),
            2023: float(ni_row[2023].values[0]),
            2024: float(ni_row[2024].values[0])
        }
    
    def get_cash_flow_history(self) -> Dict[int, Dict[str, float]]:
        """Get historical cash flow"""
        cf_data = {}
        
        for year in [2021, 2022, 2023, 2024]:
            cf_data[year] = {
                'operating': float(self.data[self.data['Period'] == 'Operating Cash Flow'][year].values[0]),
                'investing': float(self.data[self.data['Period'] == 'Investing Cash Flow'][year].values[0]),
                'financing': float(self.data[self.data['Period'] == 'Financing Cash Flow'][year].values[0]),
                'net_change': float(self.data[self.data['Period'] == 'Net Change in Cash'][year].values[0]),
                'cash_bf': float(self.data[self.data['Period'] == 'Cash Balance b/f'][year].values[0]),
                'cash_cf': float(self.data[self.data['Period'] == 'Cash Balance c/f'][year].values[0])
            }
        
        return cf_data
    
    def get_balance_sheet_history(self) -> Dict[int, Dict[str, float]]:
        """Get historical balance sheet"""
        bs_data = {}
        
        for year in [2021, 2022, 2023, 2024]:
            bs_data[year] = {
                'total_assets': float(self.data[self.data['Period'] == 'Total Assets'][year].values[0]),
                'total_liabilities': float(self.data[self.data['Period'] == 'Total Liabilities'][year].values[0]),
                'net_assets': float(self.data[self.data['Period'] == 'Net Assets'][year].values[0])
            }
        
        return bs_data
    
    def get_other_metrics_history(self) -> Dict[int, Dict[str, float]]:
        """Get other operational metrics"""
        other_data = {}
        
        for year in [2021, 2022, 2023, 2024]:
            
            # Handle ARR which might be NaN for earlier years
            arr_val = self.data[self.data['Period'] == 'ARR'][year].values[0]
            arr = float(arr_val) if pd.notna(arr_val) else np.nan
            
            other_data[year] = {
                'employee_numbers': float(self.data[self.data['Period'] == 'Employee Numbers'][year].values[0]),
                'arr': arr,
                'revenue_per_employee': float(self.data[self.data['Period'] == 'Revenue per Employee'][year].values[0]),
                'opex_per_employee': float(self.data[self.data['Period'] == 'Opex per Employee'][year].values[0])
            }
        
        return other_data
    
    def get_latest_values(self) -> Dict[str, float]:
        """Get latest (2024) values for forecasting base"""
        return {
            'revenue': self.get_revenue_history()[2024],
            'gross_margin': self.get_gross_margin_history()[2024],
            'opex_total': abs(self.get_opex_history()[2024]['total']),
            'employees': self.get_other_metrics_history()[2024]['employee_numbers'],
            'arr': self.get_other_metrics_history()[2024]['arr'],
            'cash_balance': self.get_cash_flow_history()[2024]['cash_cf']
        }
