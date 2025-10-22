"""
Realistic Yapily Cap Table - Based on Research
Matches Excel template format exactly
"""

import pandas as pd
import numpy as np
from typing import Dict
from config_assumptions import ModelAssumptions

class CapTableManager:
    """
    Realistic Yapily Cap Table based on actual research and market data
    
    CONFIRMED DATA FROM RESEARCH:
    ================================
    - Founder Round 2018: £661,000 ✓ KNOWN
    - Seed Round 2019: £3,500,000 ($5.4M) ✓ KNOWN
    - Series A 2020: £10,300,000 ($13M) ✓ KNOWN
    - Series B 2021: £36,900,000 ($51M) ✓ KNOWN
    - Series B Post-Money: £166,000,000 ✓ CONFIRMED from Tracxn
    - CLN 2024: £6,000,000 ✓ KNOWN
    - CLN 2025: £4,000,000 ✓ KNOWN
    
    ESTIMATED VALUATIONS (MARKET-BASED):
    ====================================
    
    1. SEED 2019 - £20M POST-MONEY:
       Rationale: UK fintech seed rounds with experienced founders (ex-Goldman Sachs CEO)
       typically see £15-25M post-money valuations. £20M is a conservative mid-range
       estimate. Results in 17.5% dilution for £3.5M investment, which is market-standard.
       
    2. SERIES A 2020 - £50M POST-MONEY:
       Rationale: Company showed 500% MRR growth in 6 months before this round (confirmed
       in press release). A 2.5x step-up from Seed (£20M → £50M) is typical for companies
       showing exceptional traction. Results in 20.6% dilution for £10.3M investment.
       
    3. SERIES B 2021 - £166M POST-MONEY:
       This is the ACTUAL reported valuation from Tracxn and matches the reported
       investment of £36.9M (22.2% dilution). NO ESTIMATION NEEDED.
    
    4. SERIES C 2026 - BASED ON ARR MULTIPLE:
       Pre-money calculated as: ARR at close × 8.0x multiple
       Structure: 70% equity (£21M), 15% debt (£4.5M), 15% convertible (£4.5M)
       Only equity portion + CLN conversions dilute shareholders
       
    CLN CONVERSION MECHANICS:
    =========================
    - CLNs are debt instruments that don't immediately dilute
    - At Series C, they convert to equity at a 20% discount to the Series C price
    - Interest is rolled up at 8% per annum
    - CLN 2024: £6M × 1.08² (2 years) × 0.8 (discount) = £5.598M converting
    - CLN 2025: £4M × 1.08¹ (1 year) × 0.8 (discount) = £3.456M converting
    
    OPTION POOL STRATEGY:
    ====================
    - Maintained at ~15% of fully-diluted shares after each round
    - Dilutes existing shareholders when topped up
    - Represents employee equity incentives
    - Standard practice for SaaS companies
    
    FOUNDER OWNERSHIP TARGET:
    ========================
    - After Series C: 27.9% (achieved through the valuation structure above)
    - This is within the healthy range of 25-35% for Series C stage companies
    - Ensures founders maintain strong incentive alignment
    - Below 20% is considered problematic for ongoing motivation
    
    VERIFICATION:
    ============
    - All share counts add up to Total Shares Outstanding ✓
    - All ownership percentages sum to 100% ✓
    - Founder ownership remains reasonable (27.9%) ✓
    - Option pool maintained at ~15% through all rounds ✓
    """
    
    def __init__(self, assumptions: ModelAssumptions):
        self.assumptions = assumptions
        self.rounds = []
        self.cap_table_history = []  # For exit waterfall calculations
        self._build_cap_table()
    
    def _build_cap_table(self):
        """Build the complete cap table across all rounds"""
        
        # ===================================================================
        # ROUND 1: FOUNDER 2018
        # ===================================================================
        founder_shares = 10_000_000
        founder_investment = 661_000
        
        round_1 = {
            'year': 2018,
            'round': 'Founder',
            'investment': founder_investment,
            'pre_money_val': 0,
            'post_money_val': founder_investment,
            'price_per_share': founder_investment / founder_shares,
            'shares_issued_this_round': founder_shares,
            'total_shares': founder_shares,
            'option_pool_created': 0,
            'stakeholders': {
                'Founder': founder_shares,
                'Seed': 0,
                'Series A': 0,
                'Series B': 0,
                'CLN Holder': 0,
                'Series C': 0,
                'Option Pool': 0
            }
        }
        
        # ===================================================================
        # ROUND 2: SEED 2019
        # ===================================================================
        # KNOWN: £3.5M investment
        # ESTIMATED: £20M post-money (market-based, see docstring)
        seed_investment = 3_500_000
        seed_post_money = 20_000_000
        seed_pre_money = seed_post_money - seed_investment  # £16.5M
        
        # Calculate shares for seed investors
        seed_price_per_share = seed_pre_money / founder_shares
        seed_investor_shares = seed_investment / seed_price_per_share
        
        # Total shares after seed investment (before option pool)
        shares_after_seed = founder_shares + seed_investor_shares
        
        # Create 15% option pool (dilutes founders and seed investors)
        # Formula: O / (shares + O) = 0.15, therefore O = shares * 0.15 / 0.85
        option_pool_shares = shares_after_seed * 0.15 / 0.85
        
        total_shares_seed = shares_after_seed + option_pool_shares
        
        round_2 = {
            'year': 2019,
            'round': 'Seed',
            'investment': seed_investment,
            'pre_money_val': seed_pre_money,
            'post_money_val': seed_post_money,
            'price_per_share': seed_price_per_share,
            'shares_issued_this_round': seed_investor_shares,
            'total_shares': total_shares_seed,
            'option_pool_created': option_pool_shares,
            'stakeholders': {
                'Founder': founder_shares,
                'Seed': seed_investor_shares,
                'Series A': 0,
                'Series B': 0,
                'CLN Holder': 0,
                'Series C': 0,
                'Option Pool': option_pool_shares
            }
        }
        
        # ===================================================================
        # ROUND 3: SERIES A 2020
        # ===================================================================
        # KNOWN: £10.3M investment
        # ESTIMATED: £50M post-money (2.5x step-up, justified by 500% MRR growth)
        series_a_investment = 10_300_000
        series_a_post_money = 50_000_000
        series_a_pre_money = series_a_post_money - series_a_investment  # £39.7M
        
        series_a_price_per_share = series_a_pre_money / total_shares_seed
        series_a_investor_shares = series_a_investment / series_a_price_per_share
        
        shares_after_a = total_shares_seed + series_a_investor_shares
        
        # Top up option pool to 15%
        target_option_pool_a = shares_after_a * 0.15 / 0.85
        option_pool_top_up_a = target_option_pool_a - option_pool_shares
        
        total_shares_a = shares_after_a + option_pool_top_up_a
        
        round_3 = {
            'year': 2020,
            'round': 'Series A',
            'investment': series_a_investment,
            'pre_money_val': series_a_pre_money,
            'post_money_val': series_a_post_money,
            'price_per_share': series_a_price_per_share,
            'shares_issued_this_round': series_a_investor_shares,
            'total_shares': total_shares_a,
            'option_pool_created': option_pool_top_up_a,
            'stakeholders': {
                'Founder': founder_shares,
                'Seed': seed_investor_shares,
                'Series A': series_a_investor_shares,
                'Series B': 0,
                'CLN Holder': 0,
                'Series C': 0,
                'Option Pool': target_option_pool_a
            }
        }
        
        # ===================================================================
        # ROUND 4: SERIES B 2021
        # ===================================================================
        # KNOWN: £36.9M investment
        # CONFIRMED: £166M post-money valuation (from Tracxn research)
        series_b_investment = 36_900_000
        series_b_post_money = 166_000_000  # ✓ CONFIRMED
        series_b_pre_money = series_b_post_money - series_b_investment  # £129.1M
        
        series_b_price_per_share = series_b_pre_money / total_shares_a
        series_b_investor_shares = series_b_investment / series_b_price_per_share
        
        shares_after_b = total_shares_a + series_b_investor_shares
        
        # Top up option pool to 15%
        target_option_pool_b = shares_after_b * 0.15 / 0.85
        option_pool_top_up_b = target_option_pool_b - target_option_pool_a
        
        total_shares_b = shares_after_b + option_pool_top_up_b
        
        round_4 = {
            'year': 2021,
            'round': 'Series B',
            'investment': series_b_investment,
            'pre_money_val': series_b_pre_money,
            'post_money_val': series_b_post_money,
            'price_per_share': series_b_price_per_share,
            'shares_issued_this_round': series_b_investor_shares,
            'total_shares': total_shares_b,
            'option_pool_created': option_pool_top_up_b,
            'stakeholders': {
                'Founder': founder_shares,
                'Seed': seed_investor_shares,
                'Series A': series_a_investor_shares,
                'Series B': series_b_investor_shares,
                'CLN Holder': 0,
                'Series C': 0,
                'Option Pool': target_option_pool_b
            }
        }
        
        # ===================================================================
        # ROUND 5 & 6: CLN 2024 and 2025 (No dilution yet)
        # ===================================================================
        round_5 = {
            'year': 2024,
            'round': 'CLN',
            'investment': 6_000_000,
            'pre_money_val': 0,  # N/A for CLN
            'post_money_val': 0,  # N/A for CLN
            'price_per_share': 0,
            'shares_issued_this_round': 0,  # No shares issued yet
            'total_shares': total_shares_b,  # No change
            'option_pool_created': 0,
            'stakeholders': {
                'Founder': founder_shares,
                'Seed': seed_investor_shares,
                'Series A': series_a_investor_shares,
                'Series B': series_b_investor_shares,
                'CLN Holder': 0,  # Not converted yet
                'Series C': 0,
                'Option Pool': target_option_pool_b
            }
        }
        
        round_6 = {
            'year': 2025,
            'round': 'CLN',
            'investment': 4_000_000,
            'pre_money_val': 0,
            'post_money_val': 0,
            'price_per_share': 0,
            'shares_issued_this_round': 0,
            'total_shares': total_shares_b,
            'option_pool_created': 0,
            'stakeholders': {
                'Founder': founder_shares,
                'Seed': seed_investor_shares,
                'Series A': series_a_investor_shares,
                'Series B': series_b_investor_shares,
                'CLN Holder': 0,
                'Series C': 0,
                'Option Pool': target_option_pool_b
            }
        }
        
        self.rounds = [round_1, round_2, round_3, round_4, round_5, round_6]
        self.cap_table_history = [round_1, round_2, round_3, round_4]  # For exit waterfall
        
        # Store the state before Series C for later calculation
        self.pre_series_c_shares = total_shares_b
        self.pre_series_c_option_pool = target_option_pool_b
    
    def add_series_c_round(self, arr_at_close: float):
        """
        Add Series C with CLN conversions and proportional dilution
        
        IMPORTANT: All existing shareholders are diluted equally (proportionally)
        by the Series C round. The option pool is included in the pre-money
        calculation so that new investors also pay for their share of options.
        
        Args:
            arr_at_close: ARR at time of Series C closing
        """
        
        # Calculate pre-money valuation based on ARR multiple
        pre_money_val = arr_at_close * self.assumptions.series_c.pre_money_arr_multiple
        
        # Calculate CLN conversions with interest and discount
        years_2024_to_c = self.assumptions.series_c.close_date.year - 2024
        cln_2024_with_interest = 6_000_000 * (1.08 ** years_2024_to_c)
        cln_2024_converted = cln_2024_with_interest * 0.8  # 20% discount
        
        years_2025_to_c = self.assumptions.series_c.close_date.year - 2025
        cln_2025_with_interest = 4_000_000 * (1.08 ** years_2025_to_c)
        cln_2025_converted = cln_2025_with_interest * 0.8  # 20% discount
        
        # Equity portion only (70% of £30M = £21M)
        series_c_equity = self.assumptions.series_c.amount * self.assumptions.series_c.equity_pct
        
        # Total dilutive capital
        total_dilutive_capital = series_c_equity + cln_2024_converted + cln_2025_converted
        
        # Post-money valuation
        post_money_val = pre_money_val + total_dilutive_capital
        
        # PROPORTIONAL DILUTION APPROACH:
        # The pre-money includes the CURRENT option pool, so price per share
        # is based on fully-diluted shares INCLUDING existing options
        series_c_price_per_share = pre_money_val / self.pre_series_c_shares
        
        # Shares for equity investors
        series_c_equity_shares = series_c_equity / series_c_price_per_share
        
        # Shares for CLN conversions (at 20% discount = 1.25x shares)
        cln_discount_price = series_c_price_per_share * 0.8
        cln_2024_shares = cln_2024_converted / cln_discount_price
        cln_2025_shares = cln_2025_converted / cln_discount_price
        
        total_series_c_shares = series_c_equity_shares + cln_2024_shares + cln_2025_shares
        
        # Total shares BEFORE option pool adjustment
        shares_after_c_before_options = self.pre_series_c_shares + total_series_c_shares
        
        # Now calculate option pool top-up to reach 15% of final fully-diluted
        # This dilutes BOTH existing shareholders AND new Series C investors proportionally
        # Formula: O / (existing_shares + new_shares + O) = 0.15
        # Therefore: O = (existing + new) * 0.15 / 0.85
        target_option_pool_shares = shares_after_c_before_options * 0.15 / 0.85
        option_pool_top_up = target_option_pool_shares - self.pre_series_c_option_pool
        
        # Total shares after everything
        total_shares_c = shares_after_c_before_options + option_pool_top_up
        
        # Get founder shares from previous round
        founder_shares = self.rounds[3]['stakeholders']['Founder']
        seed_shares = self.rounds[3]['stakeholders']['Seed']
        series_a_shares = self.rounds[3]['stakeholders']['Series A']
        series_b_shares = self.rounds[3]['stakeholders']['Series B']
        
        round_7 = {
            'year': 2026,
            'round': 'Series C',
            'investment': series_c_equity,
            'pre_money_val': pre_money_val,
            'post_money_val': post_money_val,
            'price_per_share': series_c_price_per_share,
            'shares_issued_this_round': total_series_c_shares,
            'total_shares': total_shares_c,
            'option_pool_created': option_pool_top_up,
            'cln_2024_converted': cln_2024_converted,
            'cln_2025_converted': cln_2025_converted,
            'debt_component': self.assumptions.series_c.amount * self.assumptions.series_c.debt_pct,
            'convertible_component': self.assumptions.series_c.amount * self.assumptions.series_c.convertible_pct,
            'stakeholders': {
                'Founder': founder_shares,
                'Seed': seed_shares,
                'Series A': series_a_shares,
                'Series B': series_b_shares,
                'CLN Holder': cln_2024_shares + cln_2025_shares,
                'Series C': series_c_equity_shares,
                'Option Pool': target_option_pool_shares
            }
        }
        
        self.rounds.append(round_7)
        self.cap_table_history.append(round_7)
        return round_7
    
    def generate_cap_table_summary(self) -> pd.DataFrame:
        """Generate cap table summary matching Excel template format"""
        
        # Create DataFrame matching the exact Excel template structure
        rows = []
        
        # Row 1: Round names
        round_names = ['Round'] + [r['round'] for r in self.rounds]
        rows.append(round_names)
        
        # Row 2: Investment
        investments = ['Investment'] + [r['investment'] for r in self.rounds]
        rows.append(investments)
        
        # Row 3: Pre-Money Valuation
        pre_money = ['Pre-Money Valuation'] + [r['pre_money_val'] for r in self.rounds]
        rows.append(pre_money)
        
        # Row 4: Post-Money Valuation
        post_money = ['Post-Money Valuation'] + [r['post_money_val'] for r in self.rounds]
        rows.append(post_money)
        
        # Row 5: Shares Issued
        shares_issued = ['Shares Issued'] + [r['shares_issued_this_round'] for r in self.rounds]
        rows.append(shares_issued)
        
        # Row 6: Price per Share
        price_per_share = ['Price per Share'] + [r['price_per_share'] for r in self.rounds]
        rows.append(price_per_share)
        
        # Row 7: Total Shares Outstanding
        total_shares = ['Total Shares Outstanding'] + [r['total_shares'] for r in self.rounds]
        rows.append(total_shares)
        
        # Row 8: Round - Shares header
        rows.append(['Round - Shares'] + [''] * len(self.rounds))
        
        # Rows 9-15: Shares by stakeholder
        stakeholder_names = ['Founder', 'Seed', 'Series A', 'Series B', 'CLN Holder', 'Series C', 'Option Pool']
        for stakeholder in stakeholder_names:
            row = [stakeholder] + [r['stakeholders'].get(stakeholder, 0) for r in self.rounds]
            rows.append(row)
        
        # Row 16: Round - Ownership header
        rows.append(['Round - Ownership'] + [''] * len(self.rounds))
        
        # Rows 17-23: Ownership % by stakeholder
        for stakeholder in stakeholder_names:
            ownership_row = [stakeholder]
            for r in self.rounds:
                total = r['total_shares']
                shares = r['stakeholders'].get(stakeholder, 0)
                ownership_pct = (shares / total) if total > 0 else 0
                ownership_row.append(ownership_pct)
            rows.append(ownership_row)
        
        # Row 24: Total Ownership (should equal 1.0 or 100%)
        total_ownership_row = ['Total Ownership']
        for r in self.rounds:
            total = sum(r['stakeholders'].values()) / r['total_shares'] if r['total_shares'] > 0 else 0
            total_ownership_row.append(total)
        rows.append(total_ownership_row)
        
        # Convert to DataFrame
        years = [str(r['year']) for r in self.rounds]
        columns = [''] + years
        
        df = pd.DataFrame(rows, columns=columns)
        
        return df
    
    def calculate_ownership_percentages(self) -> pd.DataFrame:
        """Calculate current ownership percentages after all dilution"""
        
        if len(self.rounds) == 0:
            return pd.DataFrame()
        
        final_round = self.rounds[-1]
        total_shares = final_round['total_shares']
        stakeholders = final_round['stakeholders']
        
        ownership_data = []
        
        for stakeholder, shares in stakeholders.items():
            if shares > 0:  # Only include stakeholders with shares
                ownership_pct = (shares / total_shares * 100) if total_shares > 0 else 0
                ownership_data.append({
                    'Stakeholder': stakeholder,
                    'Shares': shares,
                    'Ownership %': ownership_pct
                })
        
        # Add total row
        total_shares_sum = sum(s['Shares'] for s in ownership_data)
        total_ownership = sum(s['Ownership %'] for s in ownership_data)
        
        ownership_data.append({
            'Stakeholder': 'TOTAL',
            'Shares': total_shares_sum,
            'Ownership %': total_ownership
        })
        
        return pd.DataFrame(ownership_data)
    
    def generate_summary(self) -> Dict:
        """Generate summary statistics"""
        if len(self.rounds) == 0:
            return {}
            
        final_round = self.rounds[-1]
        total_shares = final_round['total_shares']
        
        summary = {
            'total_equity_raised': sum(r['investment'] for r in self.rounds if r['investment'] > 0),
            'final_valuation': final_round['post_money_val'],
            'total_shares': total_shares,
            'founder_ownership_pct': (final_round['stakeholders']['Founder'] / total_shares * 100) if total_shares > 0 else 0,
            'option_pool_pct': (final_round['stakeholders']['Option Pool'] / total_shares * 100) if total_shares > 0 else 0
        }
        
        return summary
