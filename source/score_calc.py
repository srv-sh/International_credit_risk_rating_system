import streamlit as st
# from source.main_function import Main



if 'output' in st.session_state:
    data = st.session_state.output

else:
    print("Output data not found")




class ScoreCalculator:
    def __init__(self, data):
        # Initialize the class with the data dictionary
        for entry in data:
            item_name = entry['item']  # Get the item name
            value = entry['value']     # Get the value
            # Dynamically assign an attribute to the class instance
            setattr(self, item_name, value)

    # Method to calculate score based on the conditions
    def calculate_scores(self):
        # Create a dictionary to store the scores
        scores = {}
        label = []

        label.append(" ")

        # Scoring for dtn (Financial Debt to Tangible Net Worth)
        if self.dtn < 0.50:
            scores['dtn_score'] = 7
            label.append("Excellent")
        elif 0.50 <= self.dtn < 0.65:
            scores['dtn_score'] = 6
            label.append("Good")
        elif 0.65 <= self.dtn < 0.80:
            scores['dtn_score'] = 4
            label.append("Marginal")
        else:
            scores['dtn_score'] = 0
            label.append("Unacceptable")

        # Scoring for dta (Financial Debt to Total Assets)
        if self.dta < 0.50:
            scores['dta_score'] = 3
            label.append("Excellent")
        elif 0.50 <= self.dta < 0.80:
            scores['dta_score'] = 2.5
            label.append("Good")
        elif 0.80 <= self.dta < 1.00:
            scores['dta_score'] = 2
            label.append("Marginal")
        else:
            scores['dta_score'] = 0
            label.append("Unacceptable")


        label.append(" ")
        # Scoring for current_ratio (Current Ratio)
        if self.current_ratio > 3:
            scores['current_ratio_score'] = 7
            label.append("Excellent")
        elif 1.5 <= self.current_ratio <= 3:
            scores['current_ratio_score'] = 6
            label.append("Good")
        elif 1 <= self.current_ratio < 1.5:
            scores['current_ratio_score'] = 4
            label.append("Marginal")
        else:
            scores['current_ratio_score'] = 0
            label.append("Unacceptable")

        # Scoring for cash_ratio (Cash Ratio)
        if self.cash_ratio > 1:
            scores['cash_ratio_score'] = 3
            label.append("Excellent")
        elif 0.5 <= self.cash_ratio <= 1:
            scores['cash_ratio_score'] = 2.5
            label.append("Good")
        elif 0 <= self.cash_ratio < 0.5:
            scores['cash_ratio_score'] = 2
            label.append("Marginal")
        else:
            scores['cash_ratio_score'] = 0
            label.append("Unacceptable")


        label.append(" ")
        # Scoring for npm (Net Profit Margin)
        if self.npm > 0.20:
            scores['npm_score'] = 5
            label.append("Excellent")
        elif 0.10 <= self.npm <= 0.20:
            scores['npm_score'] = 4
            label.append("Good")
        elif 0.05 <= self.npm < 0.10:
            scores['npm_score'] = 3
            label.append("Marginal")
        else:
            scores['npm_score'] = 0
            label.append("Unacceptable")

        # Scoring for roa (Return on Assets)
        if self.roa > 0.20:
            scores['roa_score'] = 3
            label.append("Excellent")
        elif 0.10 <= self.roa <= 0.20:
            scores['roa_score'] = 2.5
            label.append("Good")
        elif 0.05 <= self.roa < 0.10:
            scores['roa_score'] = 1.5
            label.append("Marginal")
        else:
            scores['roa_score'] = 0
            label.append("Unacceptable")

        # Scoring for opoa (Operating Profit to Operating Assets)
        if self.opoa > 0.20:
            scores['opoa_score'] = 2
            label.append("Excellent")
        elif 0.10 <= self.opoa <= 0.20:
            scores['opoa_score'] = 1.5
            label.append("Good")
        elif 0.05 <= self.opoa < 0.10:
            scores['opoa_score'] = 1
            label.append("Marginal")
        else:
            scores['opoa_score'] = 0
            label.append("Unacceptable")


        label.append(" ")
        # Scoring for ic (Interest Coverage)
        if self.ic > 3:
            scores['ic_score'] = 3
            label.append("Excellent")
        elif 1.5 <= self.ic <= 3:
            scores['ic_score'] = 2.5
            label.append("Good")
        elif 1 <= self.ic < 1.5:
            scores['ic_score'] = 1
            label.append("Marginal")
        else:
            scores['ic_score'] = 0
            label.append("Unacceptable")

        # Scoring for dscr (Debt Service Coverage Ratio)
        if self.dscr > 2:
            scores['dscr_score'] = 5
            label.append("Excellent")
        elif 1.25 <= self.dscr <= 2:
            scores['dscr_score'] = 4
            label.append("Good")
        elif 1 <= self.dscr < 1.25:
            scores['dscr_score'] = 3
            label.append("Marginal")
        else:
            scores['dscr_score'] = 0
            label.append("Unacceptable")

        # Scoring for cdr (Operating Cashflow to Debt Ratio)
        if self.cdr > 0.20:
            scores['cdr_score'] = 4
            label.append("Excellent")
        elif 0.10 <= self.cdr <= 0.20:
            scores['cdr_score'] = 3
            label.append("Good")
        elif 0 <= self.cdr < 0.10:
            scores['cdr_score'] = 2
            label.append("Marginal")
        else:
            scores['cdr_score'] = 0
            label.append("Unacceptable")

        # Scoring for ccr (Cashflow Coverage Ratio)
        if self.ccr > 3:
            scores['ccr_score'] = 3
            label.append("Excellent")
        elif 1.5 <= self.ccr <= 3:
            scores['ccr_score'] = 2.5
            label.append("Good")
        elif 1 <= self.ccr < 1.5:
            scores['ccr_score'] = 2
            label.append("Marginal")
        else:
            scores['ccr_score'] = 0
            label.append("Unacceptable")



        label.append(" ")
        # Scoring for std (Stock Turnover Days)
        if self.std < 30:
            scores['std_score'] = 4
            label.append("Excellent")
        elif 30 <= self.std < 50:
            scores['std_score'] = 3
            label.append("Good")
        elif 50 <= self.std < 80:
            scores['std_score'] = 2
            label.append("Marginal")
        else:
            scores['std_score'] = 0
            label.append("Unacceptable")

        # Scoring for tdcd (Trade Debtor Collection Days)
        if self.tdcd < 30:
            scores['tdcd_score'] = 3
            label.append("Excellent")
        elif 30 <= self.tdcd < 50:
            scores['tdcd_score'] = 2.5
            label.append("Good")
        elif 50 <= self.tdcd < 80:
            scores['tdcd_score'] = 2
            label.append("Marginal")
        else:
            scores['tdcd_score'] = 0
            label.append("Unacceptable")

        # Scoring for at (Asset Turnover)
        if self.at > 2:
            scores['at_score'] = 3
            label.append("Excellent")
        elif 1 <= self.at <= 2:
            scores['at_score'] = 2.5
            label.append("Good")
        elif 0.5 <= self.at < 1:
            scores['at_score'] = 2
            label.append("Marginal")
        else:
            scores['at_score'] = 0
            label.append("Unacceptable")


        label.append(" ")    
        # Scoring for cfs (Operating Cash Flow to Sales)
        if self.cfs >= 0.30:
            scores['cfs_score'] = 3
            label.append("Excellent")
        elif 0.20 <= self.cfs < 0.30:
            scores['cfs_score'] = 2.5
            label.append("Good")
        elif 0.10 <= self.cfs < 0.20:
            label.append("Marginal")
            scores['cfs_score'] = 2
        else:
            scores['cfs_score'] = 0
            label.append("Unacceptable")

        # Scoring for car (Cashflow Based Accrual Ratio)
        if self.car < 0.05:
            scores['car_score'] = 2
            label.append("Excellent")
        elif 0.05 <= self.car < 0.10:
            scores['car_score'] = 1.5
            label.append("Good")
        elif 0.10 <= self.car < 0.20:
            scores['car_score'] = 1
            label.append("Marginal")
        else:
            scores['car_score'] = 0
            label.append("Unacceptable")

        return scores, label

