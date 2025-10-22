"""
Main Financial Model Class
Orchestrates all projections and calculations
"""

import pandas as pd
from config_assumptions import ModelAssumptions
from data_loader import HistoricalDataLoader
from pl_projector import PLProjector
from cf_projector import CashFlowProjector
from bs_projector import BalanceSheetProjector
from other_metrics_projector import OtherMetricsProjector
from cap_table import CapTableManager
from exit_waterfall import ExitWaterfallCalculator

class FinancialModel:
    """Main financial model orchestrator"""
    
    def __init__(self, assumptions: ModelAssumptions, historical_data_path: str):
        self.assumptions = assumptions
        self.historical_data_path = historical_data_path
        
        # Load historical data
        self.data_loader = HistoricalDataLoader(historical_data_path)
        self.historical_data = self.data_loader.get_latest_values()
        
        # Initialize projectors
        self.pl_projector = PLProjector(
            assumptions,
            self.historical_data['revenue'],
            self.historical_data['opex_total'],
            self.historical_data['arr']
        )
        
        self.cf_projector = CashFlowProjector(
            assumptions,
            self.historical_data['cash_balance']
        )
        
        self.bs_projector = BalanceSheetProjector(
            assumptions,
            self.data_loader.get_balance_sheet_history()[2024]['total_assets'],
            self.data_loader.get_balance_sheet_history()[2024]['total_liabilities'],
            self.data_loader.get_balance_sheet_history()[2024]['net_assets']
        )
        
        self.other_projector = OtherMetricsProjector(
            assumptions,
            self.historical_data['employees']
        )
        
        # Cap table and exit
        self.cap_table = CapTableManager(assumptions)
        
        # Results storage
        self.pl_df = None
        self.cf_df = None
        self.bs_df = None
        self.other_df = None
        self.cap_table_df = None
        self.exit_waterfall_df = None
    
    def run_projections(self):
        """Run all projections"""
        # Project P&L
        self.pl_df = self.pl_projector.project_full_pl()
        
        # Get Series C year ARR for cap table
        series_c_year = self.assumptions.series_c.close_date.year
        series_c_row = self.pl_df[self.pl_df['Year'] == series_c_year]
        arr_at_series_c = series_c_row['ARR'].values[0] if len(series_c_row) > 0 else 0
        
        # Add Series C to cap table
        self.cap_table.add_series_c_round(arr_at_series_c)
        self.cap_table_df = self.cap_table.generate_cap_table_summary()
        
        # Project cash flow
        self.cf_df = self.cf_projector.project_cash_flow(self.pl_df)
        
        # Project balance sheet
        self.bs_df = self.bs_projector.project_balance_sheet(self.cf_df, self.pl_df)
        
        # Project other metrics
        self.other_df = self.other_projector.project_other_metrics(self.pl_df)
        
        # Calculate exit waterfall
        exit_year = self.assumptions.exit.exit_year
        exit_row = self.pl_df[self.pl_df['Year'] == exit_year]
        exit_arr = exit_row['ARR'].values[0] if len(exit_row) > 0 else 0
        exit_ebitda = exit_row['EBITDA'].values[0] if len(exit_row) > 0 else 0
        
        exit_calculator = ExitWaterfallCalculator(self.assumptions, self.cap_table)
        self.exit_valuation_data = exit_calculator.calculate_exit_valuation(exit_arr, exit_ebitda)
        self.exit_waterfall_df = exit_calculator.calculate_waterfall(exit_arr, exit_ebitda, exit_year)
    
    def get_historical_pl(self) -> pd.DataFrame:
        """Get historical P&L data"""
        historical_years = [2021, 2022, 2023, 2024]
        revenue_hist = self.data_loader.get_revenue_history()
        opex_hist = self.data_loader.get_opex_history()
        ebitda_hist = self.data_loader.get_ebitda_history()
        interest_hist = self.data_loader.get_interest_history()
        da_hist = self.data_loader.get_da_history()
        exc_hist = self.data_loader.get_exceptional_items_history()
        tax_hist = self.data_loader.get_tax_history()
        ni_hist = self.data_loader.get_net_income_history()
        gp_hist = self.data_loader.get_gross_profit_history()
        gm_hist = self.data_loader.get_gross_margin_history()
        
        data = []
        for year in historical_years:
            revenue = revenue_hist[year]
            if year > 2021:
                rev_growth = (revenue / revenue_hist[year-1]) - 1
            else:
                rev_growth = 0
            
            ebitda = ebitda_hist[year]
            ebitda_margin = ebitda / revenue if revenue > 0 else 0
            
            data.append({
                'Year': year,
                'Revenue': revenue,
                'Revenue YoY Growth %': rev_growth,
                'Cost of Sales': -(revenue - gp_hist[year]),  # Make negative
                'Gross Profit': gp_hist[year],
                'Gross Margin %': gm_hist[year],
                'Product Development': opex_hist[year]['product_dev'],
                'Sales & Marketing': opex_hist[year]['sales_marketing'],
                'Customer Success': opex_hist[year]['customer_success'],
                'G&A': opex_hist[year]['ga'],
                'Operating Expenses': opex_hist[year]['total'],
                'EBITDA': ebitda,
                'EBITDA Margin %': ebitda_margin,
                'Interest Payable': interest_hist[year],
                'DA': da_hist[year],
                'Exceptional Items': exc_hist[year],
                'Profit Before Tax': ebitda + interest_hist[year] + da_hist[year] + exc_hist[year],
                'Tax': tax_hist[year],
                'Net Income': ni_hist[year],
                'ARR': self.data_loader.get_other_metrics_history()[year]['arr']
            })
        
        return pd.DataFrame(data)
    
    def get_historical_cf(self) -> pd.DataFrame:
        """Get historical cash flow data"""
        cf_hist = self.data_loader.get_cash_flow_history()
        data = []
        
        for year in [2021, 2022, 2023, 2024]:
            data.append({
                'Year': year,
                'Operating Cash Flow': cf_hist[year]['operating'],
                'Investing Cash Flow': cf_hist[year]['investing'],
                'Financing Cash Flow': cf_hist[year]['financing'],
                'Net Change in Cash': cf_hist[year]['net_change'],
                'Cash Balance b/f': cf_hist[year]['cash_bf'],
                'Cash Balance c/f': cf_hist[year]['cash_cf']
            })
        
        return pd.DataFrame(data)
    
    def get_historical_bs(self) -> pd.DataFrame:
        """Get historical balance sheet data"""
        bs_hist = self.data_loader.get_balance_sheet_history()
        cf_hist = self.data_loader.get_cash_flow_history()
        data = []
        
        for year in [2021, 2022, 2023, 2024]:
            # Calculate historical debt
            if year == 2024:
                total_debt = 6000000  # CLN 2024
            else:
                total_debt = 0
            
            data.append({
                'Year': year,
                'Total Assets': bs_hist[year]['total_assets'],
                'Total Liabilities': bs_hist[year]['total_liabilities'],
                'Net Assets': bs_hist[year]['net_assets'],
                'Cash': cf_hist[year]['cash_cf'],
                'Total Debt': total_debt
            })
        
        return pd.DataFrame(data)
    
    def get_historical_other(self) -> pd.DataFrame:
        """Get historical other metrics"""
        other_hist = self.data_loader.get_other_metrics_history()
        revenue_hist = self.data_loader.get_revenue_history()
        ebitda_hist = self.data_loader.get_ebitda_history()
        
        data = []
        
        for year in [2021, 2022, 2023, 2024]:
            revenue = revenue_hist[year]
            ebitda = ebitda_hist[year]
            ebitda_margin = ebitda / revenue if revenue > 0 else 0
            
            if year > 2021:
                rev_growth = (revenue / revenue_hist[year-1]) - 1
            else:
                rev_growth = 0
            
            rule_of_40 = (rev_growth + ebitda_margin) * 100
            
            data.append({
                'Year': year,
                'Employee Numbers': other_hist[year]['employee_numbers'],
                'ARR': other_hist[year]['arr'],
                'Rule of 40': rule_of_40,
                'Revenue per Employee': other_hist[year]['revenue_per_employee'],
                'Opex per Employee': other_hist[year]['opex_per_employee']
            })
        
        return pd.DataFrame(data)
    
    def get_combined_pl(self) -> pd.DataFrame:
        """Get historical + projected P&L"""
        hist_pl = self.get_historical_pl()
        return pd.concat([hist_pl, self.pl_df], ignore_index=True)
    
    def get_combined_cf(self) -> pd.DataFrame:
        """Get historical + projected cash flow"""
        hist_cf = self.get_historical_cf()
        return pd.concat([hist_cf, self.cf_df], ignore_index=True)
    
    def get_combined_bs(self) -> pd.DataFrame:
        """Get historical + projected balance sheet"""
        hist_bs = self.get_historical_bs()
        return pd.concat([hist_bs, self.bs_df], ignore_index=True)
    
    def get_combined_other(self) -> pd.DataFrame:
        """Get historical + projected other metrics"""
        hist_other = self.get_historical_other()
        return pd.concat([hist_other, self.other_df], ignore_index=True)
