"""
Financial Model Configuration and Assumptions
This module contains all editable assumptions for the financial model
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import date

@dataclass
class RevenueAssumptions:
    """Revenue growth assumptions by year
    
    Strategic rationale:
    - Historical deceleration: 82% (2023) → 30% (2024) 
    - Market reality: Open banking adoption slower than hoped (per industry reports)
    - 2025-2026: CLN funding + Series C enables sales expansion
    - Post-2026: Natural SaaS maturation curve
    - Conservative vs. bull case: Prioritizes achievability over optimism
    """
    growth_2025: float = 0.32  # Modest acceleration with CLN 2025 funding
    growth_2026: float = 0.38  # Series C impact - expanded sales team & marketing
    growth_2027: float = 0.35  # Sustained growth, strong customer base
    growth_2028: float = 0.30  # Market maturation, larger revenue base
    growth_2029: float = 0.25  # Continued deceleration as market matures
    growth_2030: float = 0.22  # Stable, sustainable growth rate
    
    def get_growth_rate(self, year: int) -> float:
        """Get growth rate for a specific year"""
        growth_map = {
            2025: self.growth_2025,
            2026: self.growth_2026,
            2027: self.growth_2027,
            2028: self.growth_2028,
            2029: self.growth_2029,
            2030: self.growth_2030
        }
        return growth_map.get(year, 0.0)

@dataclass
class GrossMarginAssumptions:
    """Gross margin assumptions by year"""
    margin_2025: float = 0.95
    margin_2026: float = 0.95
    margin_2027: float = 0.95
    margin_2028: float = 0.95
    margin_2029: float = 0.95
    margin_2030: float = 0.95
    
    def get_margin(self, year: int) -> float:
        """Get gross margin for a specific year"""
        margin_map = {
            2025: self.margin_2025,
            2026: self.margin_2026,
            2027: self.margin_2027,
            2028: self.margin_2028,
            2029: self.margin_2029,
            2030: self.margin_2030
        }
        return margin_map.get(year, 0.98)

@dataclass
class OpexMixAssumptions:
    """Operating expense mix as % of total opex by year
    
    Strategic rationale:
    - Product development: Maintain technical leadership in competitive market
    - Sales & marketing: Increase investment post-Series C to capture market share
    - Customer success: Critical for retention, maintain 10-12%
    - G&A: Efficient overhead, 12-15% range
    - Shift from product-heavy to growth-heavy reflects market capture strategy
    """
    # 2025 - Pre-Series C: Product focus
    product_dev_2025: float = 0.48
    sales_marketing_2025: float = 0.27
    customer_success_2025: float = 0.10
    ga_2025: float = 0.15
    
    # 2026 - Series C year: Begin shift to growth
    product_dev_2026: float = 0.45
    sales_marketing_2026: float = 0.30
    customer_success_2026: float = 0.11
    ga_2026: float = 0.14
    
    # 2027 - Post-Series C: Growth acceleration
    product_dev_2027: float = 0.42
    sales_marketing_2027: float = 0.34
    customer_success_2027: float = 0.11
    ga_2027: float = 0.13
    
    # 2028 - Market capture
    product_dev_2028: float = 0.40
    sales_marketing_2028: float = 0.36
    customer_success_2028: float = 0.12
    ga_2028: float = 0.12
    
    # 2029 - Sustained growth
    product_dev_2029: float = 0.38
    sales_marketing_2029: float = 0.37
    customer_success_2029: float = 0.12
    ga_2029: float = 0.13
    
    # 2030 - Mature operations
    product_dev_2030: float = 0.37
    sales_marketing_2030: float = 0.38
    customer_success_2030: float = 0.12
    ga_2030: float = 0.13
    
    def get_mix(self, year: int) -> Dict[str, float]:
        """Get opex mix for a specific year"""
        mix_map = {
            2025: {
                'product_dev': self.product_dev_2025,
                'sales_marketing': self.sales_marketing_2025,
                'customer_success': self.customer_success_2025,
                'ga': self.ga_2025
            },
            2026: {
                'product_dev': self.product_dev_2026,
                'sales_marketing': self.sales_marketing_2026,
                'customer_success': self.customer_success_2026,
                'ga': self.ga_2026
            },
            2027: {
                'product_dev': self.product_dev_2027,
                'sales_marketing': self.sales_marketing_2027,
                'customer_success': self.customer_success_2027,
                'ga': self.ga_2027
            },
            2028: {
                'product_dev': self.product_dev_2028,
                'sales_marketing': self.sales_marketing_2028,
                'customer_success': self.customer_success_2028,
                'ga': self.ga_2028
            },
            2029: {
                'product_dev': self.product_dev_2029,
                'sales_marketing': self.sales_marketing_2029,
                'customer_success': self.customer_success_2029,
                'ga': self.ga_2029
            },
            2030: {
                'product_dev': self.product_dev_2030,
                'sales_marketing': self.sales_marketing_2030,
                'customer_success': self.customer_success_2030,
                'ga': self.ga_2030
            }
        }
        return mix_map.get(year, mix_map[2030])

@dataclass
class OpexGrowthAssumptions:
    """Operating expense growth rate assumptions
    
    Strategic rationale:
    - Path to profitability is CRITICAL for Series C valuation and exit
    - Historical: Opex reduced from £23M (2022) to £12.6M (2024) - proven discipline
    - 2025-2026: Tight cost control to achieve EBITDA profitability
    - Post-profitability: Controlled investment in growth
    - Rule of 40: Balance growth + profitability
    """
    growth_2025: float = -0.05  # 5% reduction - cost discipline continues
    growth_2026: float = 0.05   # Minimal growth - prioritize profitability
    growth_2027: float = 0.18   # Post-profitability investment in growth
    growth_2028: float = 0.16   # Continued growth investment
    growth_2029: float = 0.14   # Moderate scaling
    growth_2030: float = 0.12   # Efficient scaling
    
    def get_growth_rate(self, year: int) -> float:
        """Get opex growth rate for a specific year"""
        growth_map = {
            2025: self.growth_2025,
            2026: self.growth_2026,
            2027: self.growth_2027,
            2028: self.growth_2028,
            2029: self.growth_2029,
            2030: self.growth_2030
        }
        return growth_map.get(year, 0.15)

@dataclass
class SeriesCAssumptions:
    """Series C financing assumptions
    
    Strategic rationale for £25M total with 70/15/15 structure:
    - Amount: £25M provides 18+ months runway to strong profitability
    - Equity (70%): Core strategic capital, aligns investors with long-term success
    - Debt (15%): Lower cost of capital, tax-advantaged, reduced dilution
    - Convertible (15%): Bridge instrument, investor optionality, moderate dilution
    - This structure optimizes: (1) Founder dilution, (2) Cost of capital, (3) Flexibility
    - Debt/convertible: Serviceable given improving EBITDA trajectory
    - Valuation multiple: 6.0x ARR is realistic for growth-stage fintech (vs. 8-10x in 2021 peak)
    """
    amount: float = 15_000_000  # £25M - sufficient for 18+ months to profitability
    close_date: date = field(default_factory=lambda: date(2026, 6, 30))
    
    # Optimal structure mix (must sum to 1.0)
    equity_pct: float = 0.60  # £17.5M equity - core strategic capital
    debt_pct: float = 0.20    # £3.75M debt - low-cost, tax-efficient
    convertible_pct: float = 0.20  # £3.75M convertible - flexibility & upside
    
    # Debt terms - market standard for growth-stage fintech
    debt_term_years: float = 5.0
    debt_interest_rate: float = 0.10  # 10% reflects 2025-2026 market conditions
    debt_repayment_profile: str = "rolled_up"  # Preserves cash for growth
    
    # Convertible terms
    convertible_term_years: float = 5.0
    convertible_interest_rate: float = 0.08
    convertible_repayment_profile: str = "rolled_up"
    
    # Valuation - Conservative but realistic for market conditions
    pre_money_arr_multiple: float = 6.0  # Realistic for growth fintech in 2026

@dataclass
class ExitAssumptions:
    """Exit/liquidity event assumptions
    
    Strategic rationale:
    - Exit year 2030: Allows time to achieve strong profitability & Rule of 40
    - Dual valuation approach: Model calculates BOTH ARR and EBITDA-based valuations, 
      then selects the HIGHER value (maximizing shareholder value)
    - ARR multiple 8.5x: Conservative vs. 10-15x peak market multiples
      * Reflects market maturation by 2030
      * Accounts for competitive landscape (TrueLayer, Tink, Plaid)
      * Still premium due to strong margins, profitability, infrastructure positioning
    - EBITDA multiple 20x: Based on 2024-2025 market research
      * Private SaaS median: 19.2x (2024)
      * 10-year average: 22.1x
      * Range for profitable SaaS: 15-25x
      * 20x is middle-of-range, conservative for 27% EBITDA margin business
    
    For Yapily in 2030:
    - ARR ~£39.5M × 8.5x = ~£335M
    - EBITDA ~£8.6M × 20x = ~£172M
    - Model selects ARR-based valuation (higher) = £335M
    
    Research sources (2024-2025):
    - Aventis Advisors: 10-yr median EBITDA multiple 22.1x for SaaS
    - Software Equity Group: Private SaaS 19.2x EBITDA (2024)
    - Public SaaS median: 38.2x (premium not applicable to private exit)
    - Fintech SaaS: 29.6x (Q4 2022, inflated by few profitable companies)
    """
    exit_year: int = 2030
    valuation_basis: str = "higher_of_arr_or_ebitda"  # Maximizes shareholder value
    arr_multiple: float = 8.5  # Conservative, achievable for profitable infrastructure SaaS
    ebitda_multiple: float = 20.0  # Middle of 15-25x range for profitable private SaaS

@dataclass
class HistoricalFunding:
    """Historical funding rounds"""
    founder_2018: float = 661000
    seed_2019: float = 3500000
    series_a_2020: float = 10300000
    series_b1_2021: float = 26500000
    series_b2_2022: float = 10400000
    cln_2024: float = 6000000
    cln_2024_interest: float = 0.08
    cln_2024_maturity: int = 2029
    cln_2024_discount: float = 0.20
    cln_2025: float = 4000000
    cln_2025_interest: float = 0.08
    cln_2025_maturity: int = 2030
    cln_2025_discount: float = 0.20

@dataclass
class EmployeeGrowthAssumptions:
    """Employee headcount growth assumptions by year
    
    Linked to opex growth but with improving efficiency:
    - Employee growth should be lower than opex growth to improve per-employee metrics
    - As the company scales, revenue per employee should increase
    """
    growth_2025: float = -0.02  # Slight reduction aligned with opex discipline
    growth_2026: float = 0.03   # Minimal growth, lower than opex (5%)
    growth_2027: float = 0.12   # Controlled growth, lower than opex (18%)
    growth_2028: float = 0.10   # Continued efficiency gains vs opex (16%)
    growth_2029: float = 0.08   # Improving leverage vs opex (14%)
    growth_2030: float = 0.06   # Strong efficiency vs opex (12%)
    
    def get_growth_rate(self, year: int) -> float:
        """Get employee growth rate for a specific year"""
        growth_map = {
            2025: self.growth_2025,
            2026: self.growth_2026,
            2027: self.growth_2027,
            2028: self.growth_2028,
            2029: self.growth_2029,
            2030: self.growth_2030
        }
        return growth_map.get(year, 0.10)

@dataclass
class ModelAssumptions:
    """Master assumptions container"""
    revenue: RevenueAssumptions = field(default_factory=RevenueAssumptions)
    gross_margin: GrossMarginAssumptions = field(default_factory=GrossMarginAssumptions)
    opex_mix: OpexMixAssumptions = field(default_factory=OpexMixAssumptions)
    opex_growth: OpexGrowthAssumptions = field(default_factory=OpexGrowthAssumptions)
    employee_growth: EmployeeGrowthAssumptions = field(default_factory=EmployeeGrowthAssumptions)
    series_c: SeriesCAssumptions = field(default_factory=SeriesCAssumptions)
    exit: ExitAssumptions = field(default_factory=ExitAssumptions)
    historical_funding: HistoricalFunding = field(default_factory=HistoricalFunding)
    
    # Other assumptions
    tax_rate: float = 0.19  # UK corporation tax
    da_as_pct_of_revenue: float = 0.02  # Depreciation & Amortization
