import json
import streamlit as st

# class JSONReader:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         self.data = self.read_json()

#     def read_json(self):
#         try:
#             with open(self.file_path, 'r') as file:
#                 data = json.load(file)
#             return data
#         except FileNotFoundError:
#             print(f"File {self.file_path} not found.")
#             return None
#         except json.JSONDecodeError:
#             print("Error decoding JSON.")
#             return None

class FinancialCalculator:

    def __init__(self, data):
        self.data = data

        # Initialize all attributes with default values of 0
        # Initialize all attributes with default values of 0 or use values from JSON
        self.total_assets = data.get("total assets", 0)
        # print(f"the value of : {self.total_assets}")
        self.total_liabilities = data.get("total liabilities", 0)
        self.current_assets = data.get("current assets", 0)
        self.current_liabilities = data.get("current liabilities", 0)
        self.intangible_assets = data.get("intangible assets", 0)
        self.long_term_loan_current_portion = data.get("long term loan-current portion", 0)
        self.inventories = data.get("inventories", 0)
        self.accounts_receivables = data.get("accounts receivables", 0)
        self.capital_work_in_progress = data.get("capital work in progress", 0)
        self.noncurrent_assets = data.get("non-current assets", 0)
        self.revenue = data.get("revenue", 0)
        self.net_profit_after_tax = data.get("net profit after tax", 0)
        self.operating_profit = data.get("operating profit", 0)
        self.earnings_before_tax = data.get("earnings before tax", 0)
        self.finance_cost = data.get("finance cost", 0)
        self.cost_of_sales = data.get("cost of sales", 0)
        self.cash_and_cash_equivalents_at_end_of_year = data.get("cash and cash equivalents at end of year", 0)
        self.cash_flows_from_operating_activities = data.get("cash flows from operating activities", 0)
        self.cash_flows_from_financing_activities = data.get("cash flows from financing activities", 0)

        # # Assign values from the input data
        # for item in self.data:
        #     if item["item"] == "total assets":
        #         self.total_assets = float(item["value"])  
        #     elif item["item"] == "total liabilities":
        #         self.total_liabilities = float(item["value"])
        #     elif item["item"] == "current assets":
        #         self.current_assets = float(item["value"])
        #     elif item["item"] == "current liabilities":
        #         self.current_liabilities = float(item["value"])
        #     elif item["item"] == "intangible assets":
        #         self.intangible_assets = float(item["value"])
        #     elif item["item"] == "long term loan-current portion":
        #         self.long_term_loan_current_portion = float(item["value"])
        #     elif item["item"] == "inventories":
        #         self.inventories = float(item["value"])
        #     elif item["item"] == "accounts receivables":
        #         self.accounts_receivables = float(item["value"])
        #     elif item["item"] == "capital work in progress":
        #         self.capital_work_in_progress = float(item["value"])
        #     elif item["item"] == "non-current assets":
        #         self.noncurrent_assets = float(item["value"])
        #     elif item["item"] == "revenue":
        #         self.revenue = float(item["value"])
        #     elif item["item"] == "net profit after tax":
        #         self.net_profit_after_tax = float(item["value"])
        #     elif item["item"] == "operating profit":
        #         self.operating_profit = float(item["value"])
        #     elif item["item"] == "earnings before tax":
        #         self.earnings_before_tax = float(item["value"])
        #     elif item["item"] == "finance cost":
        #         self.finance_cost = float(item["value"])
        #     elif item["item"] == "cost of sales":
        #         self.cost_of_sales = float(item["value"])
        #     elif item["item"] == "cash and cash equivalents at end of year":
        #         self.cash_and_cash_equivalents_at_end_of_year = float(item["value"])
        #     elif item["item"] == "cash flows from operating activities":
        #         self.cash_flows_from_operating_activities = float(item["value"])
        #     elif item["item"] == "cash flows from financing activities":
        #         self.cash_flows_from_financing_activities = float(item["value"])


        # mark = st.session_state.markdown_output

        

    def dtn_calc(self):
        try:
            denominator = self.total_assets - self.total_liabilities - self.intangible_assets
            if denominator == 0:
                return float('inf')  # Return infinity to indicate division by zero
            dtn = self.total_liabilities / denominator
            return dtn
        except AttributeError:
            return None  # Handle missing attributes

    def dta_calc(self):
        try:
            if self.total_assets == 0:
                return float('inf')
            dta = self.total_liabilities / self.total_assets
            return dta
        except AttributeError:
            return None

    def current_ratio_calc(self):
        try:
            if self.current_liabilities == 0:
                return float('inf')
            current_ratio = self.current_assets / self.current_liabilities
            return current_ratio
        except AttributeError:
            return None

    def cash_ratio_calc(self):
        try:
            if self.current_liabilities == 0:
                return float('inf')
            cash_ratio = self.cash_and_cash_equivalents_at_end_of_year / self.current_liabilities
            return cash_ratio
        except AttributeError:
            return None

    def npm_calc(self):
        try:
            if self.revenue == 0:
                return 0
            npm = (self.net_profit_after_tax / self.revenue) * 100
            return npm
        except AttributeError:
            return None

    def roa_calc(self):
        try:
            if self.total_assets == 0:
                return 0
            roa = (self.net_profit_after_tax / self.total_assets) * 100
            return roa
        except AttributeError:
            return None

    def opoa_calc(self):
        try:
            if self.total_assets == 0:
                return 0
            opoa = (self.operating_profit / self.total_assets) * 100
            return opoa
        except AttributeError:
            return None

    def ic_calc(self):
        try:
            if self.finance_cost == 0:
                return float('inf')
            ic = self.earnings_before_tax / self.finance_cost
            return ic
        except AttributeError:
            return None

    def dscr_calc(self):
        try:
            denominator = self.long_term_loan_current_portion + self.finance_cost
            if denominator == 0:
                return float('inf')
            dscr = self.operating_profit / denominator
            return dscr
        except AttributeError:
            return None

    def cdr_calc(self):
        try:
            if self.total_liabilities == 0:
                return 0
            cdr = self.cash_flows_from_operating_activities / self.total_liabilities
            return cdr
        except AttributeError:
            return None

    def ccr_calc(self):
        try:
            if self.total_liabilities == 0:
                return float('inf')
            ccr = (self.noncurrent_assets + self.capital_work_in_progress + self.total_assets) / self.total_liabilities
            return ccr
        except AttributeError:
            return None

    def std_calc(self):
        try:
            if self.cost_of_sales == 0:
                return float('inf')
            std = self.inventories / (self.cost_of_sales / 360)
            return std
        except AttributeError:
            return None

    def tdcd_calc(self):
        try:
            if self.revenue == 0:
                return float('inf')
            tdcd = self.accounts_receivables / (self.revenue / 360)
            return tdcd
        except AttributeError:
            return None

    def at_calc(self):
        try:
            if self.total_assets == 0:
                return 0
            at = self.revenue / self.total_assets
            return at
        except AttributeError:
            return None

    def cfs_calc(self):
        try:
            if self.revenue == 0:
                return 0
            cfs = self.cash_flows_from_operating_activities / self.revenue
            return cfs
        except AttributeError:
            return None

    def car_calc(self):
        try:
            if self.total_assets == 0:
                return float('inf')
            car = (self.revenue + self.cash_flows_from_financing_activities) / self.total_assets
            return car
        except AttributeError:
            return None