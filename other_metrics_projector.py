"""
Other Metrics Projection Module
Projects operational metrics like employees, Rule of 40, etc.
"""

import pandas as pd
from config_assumptions import ModelAssumptions

class OtherMetricsProjector:
    """Project operational metrics"""
    
    def __init__(self, assumptions: ModelAssumptions, base_year_employees: float):
        self.assumptions = assumptions
        self.base_year_employees = base_year_employees
        self.years = list(range(2025, 2031))
    
    def project_employees(self) -> pd.Series:
        """Project employee headcount"""
        employees = {}
        prev_employees = self.base_year_employees
        
        for year in self.years:
            # Employee growth by year
            growth = self.assumptions.employee_growth.get_growth_rate(year)
            employees[year] = prev_employees * (1 + growth)
            prev_employees = employees[year]
        
        return pd.Series(employees)
    
    def calculate_rule_of_40(self, pl_df: pd.DataFrame) -> pd.Series:
        """
        Calculate Rule of 40: Revenue Growth % + EBITDA Margin %
        Should be > 40% for healthy SaaS companies
        """
        rule_of_40 = {}
        
        for _, row in pl_df.iterrows():
            year = int(row['Year'])
            revenue_growth = row['Revenue YoY Growth %']
            ebitda_margin = row['EBITDA Margin %']
            rule_of_40[year] = (revenue_growth + ebitda_margin) * 100  # Convert to percentage
        
        return pd.Series(rule_of_40)
    
    def calculate_revenue_per_employee(self, pl_df: pd.DataFrame, employees: pd.Series) -> pd.Series:
        """Calculate revenue per employee"""
        revenue_per_emp = {}
        
        for _, row in pl_df.iterrows():
            year = int(row['Year'])
            if year in employees.index:
                revenue_per_emp[year] = row['Revenue'] / employees[year]
        
        return pd.Series(revenue_per_emp)
    
    def calculate_opex_per_employee(self, pl_df: pd.DataFrame, employees: pd.Series) -> pd.Series:
        """Calculate opex per employee"""
        opex_per_emp = {}
        
        for _, row in pl_df.iterrows():
            year = int(row['Year'])
            if year in employees.index:
                opex_per_emp[year] = row['Operating Expenses'] / employees[year]
        
        return pd.Series(opex_per_emp)
    
    def project_other_metrics(self, pl_df: pd.DataFrame) -> pd.DataFrame:
        """Project all other metrics"""
        employees = self.project_employees()
        rule_of_40 = self.calculate_rule_of_40(pl_df)
        revenue_per_emp = self.calculate_revenue_per_employee(pl_df, employees)
        opex_per_emp = self.calculate_opex_per_employee(pl_df, employees)
        
        other_data = []
        
        for year in self.years:
            arr = pl_df[pl_df['Year'] == year]['ARR'].values[0]
            
            other_data.append({
                'Year': year,
                'Employee Numbers': employees[year],
                'ARR': arr,
                'Rule of 40': rule_of_40[year],
                'Revenue per Employee': revenue_per_emp[year],
                'Opex per Employee': opex_per_emp[year]
            })
        
        return pd.DataFrame(other_data)
