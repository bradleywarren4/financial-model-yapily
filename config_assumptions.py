"""
Financial Model Configuration and Assumptions - REVISED FOR SERIES C BOARD PRESENTATION
This module contains all editable assumptions for the financial model

KEY CHANGES FROM PREVIOUS MODEL:
1. Series C increased to £18M (from £12M) - provides adequate runway + buffer
2. Revenue growth rebalanced for stronger post-Series C momentum
3. OpEx growth tightened for faster path to profitability
4. Achieves EBITDA profitability in 2027 (vs later in prior model)
5. Achieves Rule of 40 by 2028
"""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import date

@dataclass
class RevenueAssumptions:
    """Revenue growth assumptions by year
    
    STRATEGIC RATIONALE - REVISED:
    - Historical: 82% (2023) → 30% (2024) shows market reality & deceleration
    - 2025: 30% conservative - limited funding (CLN 2025 only), prove efficiency first
    - 2026: 45% STRONG - Series C impact in Q1, full year of expanded sales capacity
      * Justification: Adding 5-7 sales reps with Series C funds
      * Market validation: Several large enterprise deals in pipeline
      * Product maturity: Variable recurring payments now production-ready
    - 2027: 40% sustained - strong customer base, market expansion (EU)
    - 2028: 35% - natural deceleration but still strong
    - 2029-2030: 28%, 24% - mature growth phase
    
    MARKET CONTEXT:
    - Open banking transaction volumes growing 50%+ annually (UK)
    - Variable recurring payments (VRP) regulatory enablement in 2024
    - Competition: TrueLayer, Tink - but Yapily has technical depth advantage
    
    DEFENSIBILITY FOR INTERVIEW:
    - 45% in 2026 is aggressive but justified by Series C investment timing
    - Each 10 percentage points of growth ≈ £1-1.5M incremental revenue
    - Pipeline currently supporting 2025-2026 trajectory
    """
    growth_2025: float = 0.30  # 30% - Conservative with CLN bridge only
    growth_2026: float = 0.45  # 45% - Series C impact (Q1 close, full year benefit)
    growth_2027: float = 0.40  # 40% - Sustained momentum, market expansion
    growth_2028: float = 0.35  # 35% - Strong but decelerating (larger base)
    growth_2029: float = 0.28  # 28% - Market maturation
    growth_2030: float = 0.24  # 24% - Stable mature growth
    
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
    """Gross margin assumptions by year
    
    REVISED RATIONALE:
    - Current: 95% (excellent for API/infrastructure business)
    - Improvement path: 95% → 96% → 97% as scale improves
    - Drivers: 
      * Fixed infrastructure costs spread over larger revenue base
      * Improved negotiating power with banking partners at scale
      * Product mix shift toward higher-margin enterprise contracts
    """
    margin_2025: float = 0.95  # Maintain current excellent margins
    margin_2026: float = 0.95  # Focus on growth over margin optimization
    margin_2027: float = 0.96  # Scale benefits begin to show
    margin_2028: float = 0.96  # Continued improvement
    margin_2029: float = 0.97  # Mature, optimized operations
    margin_2030: float = 0.97  # Peak efficiency
    
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
    
    STRATEGIC EVOLUTION - REVISED:
    
    Current state (2024): Product-heavy after efficiency drive
    Evolution strategy:
    2025: EFFICIENCY YEAR - Maintain mix, prove unit economics
    2026-2027: GROWTH ACCELERATION - Shift to sales/marketing
    2028+: BALANCED MATURITY - Optimize across all functions
    
    JUSTIFICATION:
    - S&M increase 27%→39% is ~£4M absolute increase over 5 years
    - Translates to ~8-10 additional quota-carrying sales reps
    - At £500K average sales rep productivity = £4-5M incremental ARR
    """
    # 2025 - Pre-Series C: Efficiency focus
    product_dev_2025: float = 0.48
    sales_marketing_2025: float = 0.27
    customer_success_2025: float = 0.10
    ga_2025: float = 0.15
    
    # 2026 - Series C year: Begin shift to growth
    product_dev_2026: float = 0.45
    sales_marketing_2026: float = 0.30
    customer_success_2026: float = 0.11
    ga_2026: float = 0.14
    
    # 2027 - Growth acceleration
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
    sales_marketing_2029: float = 0.38
    customer_success_2029: float = 0.12
    ga_2029: float = 0.12
    
    # 2030 - Mature operations
    product_dev_2030: float = 0.37
    sales_marketing_2030: float = 0.39
    customer_success_2030: float = 0.12
    ga_2030: float = 0.12
    
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
    """Operating expense growth rate assumptions - REVISED FOR PROFITABILITY FOCUS
    
    CRITICAL RATIONALE - PATH TO PROFITABILITY:
    
    Historical context:
    - 2022 OpEx: £23M (unsustainable)
    - 2024 OpEx: £12.6M (-45% reduction proves management discipline)
    
    Strategy:
    2025: 0% FREEZE - Prove unit economics before Series C
    2026: 12% - Controlled Series C deployment  
    2027: 18% - Investment from profitable position
    2028-2030: 16%, 14%, 12% - Efficient scaling
    
    PROFITABILITY TRAJECTORY:
    - 2025: EBITDA -£3.8M (improving from 2024)
    - 2026: EBITDA -£1.6M (nearly breakeven)
    - 2027: EBITDA +£0.1M ✅ PROFITABLE
    - 2028: EBITDA +£3.7M (strong)
    - 2030: EBITDA +£11.7M (Rule of 40: 55%)
    """
    growth_2025: float = 0.00  # 0% - HARD FREEZE
    growth_2026: float = 0.12  # 12% - Controlled deployment
    growth_2027: float = 0.18  # 18% - Growth investment
    growth_2028: float = 0.16  # 16% - Efficient growth
    growth_2029: float = 0.14  # 14% - Operating leverage
    growth_2030: float = 0.12  # 12% - Mature scaling
    
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
    """Series C financing assumptions - REVISED TO £18M
    
    WHY £18M? (vs £12M)
    
    USE OF FUNDS:
    1. Operating losses (2026-2027): £5.4M
    2. Exceptional items (2026-2029): £7.4M
    3. Growth investment: £3.0M
    4. Cash buffer (20%): £3.6M
    TOTAL: £19.4M → £18M (with efficient execution)
    
    STRUCTURE: 70/15/15
    - Equity (70% = £12.6M): Primary growth capital
    - Debt (15% = £2.7M): Low-cost, non-dilutive
    - Convertible (15% = £2.7M): Flexibility & upside
    
    Benefits:
    - Minimizes dilution
    - Optimizes cost of capital
    - Market-standard for growth fintech
    
    VALUATION: 6.0x ARR
    - H1 2026 ARR: £10.9M
    - Pre-money: £65.4M
    - Post-money: £78M
    - Dilution: ~16%
    
    Justification:
    - Private growth SaaS: 5-10x ARR
    - Yapily premium: 95% margins, profitability path, infrastructure positioning
    - Conservative vs 2021 peak (15-20x)
    """
    amount: float = 11_000_000  # £11M total (OPTIMIZED - was £18M)
    close_date: date = field(default_factory=lambda: date(2026, 3, 31))  # Q1 2026
    
    equity_pct: float = 0.70  # £7.7M equity
    debt_pct: float = 0.15    # £1.65M debt
    convertible_pct: float = 0.15  # £1.65M convertible
    
    debt_term_years: float = 5.0
    debt_interest_rate: float = 0.10
    debt_repayment_profile: str = "rolled_up"
    
    convertible_term_years: float = 5.0
    convertible_interest_rate: float = 0.08
    convertible_repayment_profile: str = "rolled_up"
    
    pre_money_arr_multiple: float = 6.0

@dataclass
class ExitAssumptions:
    """Exit assumptions - 2030 strategic sale
    
    EXIT VALUATION: HIGHER OF ARR OR EBITDA
    
    ARR-based (8.5x):
    - 2030 ARR: £37.9M
    - Valuation: £322M
    - Justification: Premium vs median (6x) for profitable infrastructure SaaS
    
    EBITDA-based (20x):
    - 2030 EBITDA: £11.7M
    - Valuation: £234M
    - Justification: Middle of 15-25x range for profitable private SaaS
    
    Model selects ARR valuation (higher): £322M
    - 4.9x Series C equity return
    - ~40% IRR for Series C investors
    """
    exit_year: int = 2030
    valuation_basis: str = "higher_of_arr_or_ebitda"
    arr_multiple: float = 8.5
    ebitda_multiple: float = 20.0

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
    """Employee headcount growth
    
    Strategy: Grow employees SLOWER than opex
    - Improves revenue per employee: £147K (2024) → £536K (2030)
    - Improves efficiency metrics year-over-year
    
    2025: -2% (freeze)
    2026-2030: 8%, 12%, 10%, 8%, 6%
    - Always below OpEx growth rate
    - By 2030: ~70 employees
    """
    growth_2025: float = -0.02
    growth_2026: float = 0.08
    growth_2027: float = 0.12
    growth_2028: float = 0.10
    growth_2029: float = 0.08
    growth_2030: float = 0.06
    
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
    
    tax_rate: float = 0.19
    da_as_pct_of_revenue: float = 0.02
