import streamlit as st
import json

# Set page configuration
st.set_page_config(layout="wide")
st.title("Calculation of Quantitative Indicators")

# # Default input data
# input_data = {
#     "total assets": ["Total assets"],
#     "total liabilities": ["Total liabilities"],
#     "current assets": ["Current assets"],
#     "current liabilities": ["Current liabilities"],
#     "intangible assets": ["Intangible assets"],
#     "long term loan-current portion": [],  # Empty list instead of None
#     "inventories": ["Inventories"],
#     "accounts receivables": ["Trade receivables", "Other receivables"],
#     "capital work in progress": ["Payments for capital work-in-progress"],
#     "non-current assets": ["Non-current assets"],
#     "revenue": ["Revenue"],
#     "net profit after tax": ["Profit/(loss) after tax"],
#     "operating profit": ["Operating profit"],
#     "earnings before tax": ["Profit before tax"],
#     "finance cost": ["Net finance costs"],
#     "cost of sales": ["Cost of sales"],
#     "cash and cash equivalents at end of year": ["Cash and cash equivalents at reporting date"],
#     "cash flows from operating activities": ["Net cash from/(used in) operating activities"],
#     "cash flows from financing activities": ["Net cash from/(used in) financing activities"]
# }

# Load session state data
if 'intermediate' not in st.session_state:
    st.error("Data not found in session state. Using default values.")
    # input_data = default_input_data
else:
    # Convert string to dictionary if it's a string
    if isinstance(st.session_state.intermediate, str):
        try:
            input_data = json.loads(st.session_state.intermediate)  # Parse JSON string
        except json.JSONDecodeError:
            st.error("Invalid JSON format in session state. Using default values.")
            # input_data = default_input_data
    else:
        input_data = st.session_state.intermediate


# Function to process data
def process_data(data):
    processed_data = {}
    for key, value in data.items():
        # Ensure value is a list
        if not isinstance(value, list):
            value = [value]
        # Process based on list length
        if len(value) == 0:
            processed_data[key] = 0
        elif len(value) == 2:
            processed_data[key] = [f"{value[0]}+{value[1]}"]
        else:
            processed_data[key] = value
    return processed_data

# Process input data
input_data = process_data(input_data)

# Main function
def main():
    st.write("### Formulas")

    # Leverage
    st.header("1. Leverage (Minimized)")
    st.subheader("Debt to Tangible Net Worth (DTN)")
    st.latex(rf"DTN = \frac{{\text{{{input_data['total liabilities'][0]}}}}}{{\text{{{input_data['total assets'][0]}}} - \text{{{input_data['total liabilities'][0]}}} - \text{{{input_data['intangible assets'][0]}}}}}")
    st.latex(rf"\text{{Tangible Net Worth}} = \text{{{input_data['total assets'][0]}}} - \text{{{input_data['total liabilities'][0]}}} - \text{{{input_data['intangible assets'][0]}}}")

    st.subheader("Debt to Total Assets (DTA)")
    st.latex(rf"DTA = \frac{{\text{{{input_data['total liabilities'][0]}}}}}{{\text{{{input_data['total assets'][0]}}}}}")

    # Liquidity
    st.header("2. Liquidity (Maximized)")
    st.subheader("Current Ratio (CR)")
    st.latex(rf"CR = \frac{{\text{{{input_data['current assets'][0]}}}}}{{\text{{{input_data['current liabilities'][0]}}}}}")
    
    st.subheader("Cash Ratio")
    st.latex(rf"Cash\ Ratio = \frac{{\text{{{input_data['cash and cash equivalents at end of year'][0]}}}}}{{\text{{{input_data['current liabilities'][0]}}}}}")

    # Profitability
    st.header("3. Profitability (Maximized)")
    st.subheader("Net Profit Margin (NPM)")
    st.latex(rf"NPM = \left( \frac{{\text{{{input_data['net profit after tax'][0]}}}}}{{\text{{{input_data['revenue'][0]}}}}} \right) \times 100")
    
    st.subheader("Return on Assets (ROA)")
    st.latex(rf"ROA = \left( \frac{{\text{{{input_data['net profit after tax'][0]}}}}}{{\text{{{input_data['total assets'][0]}}}}} \right) \times 100")
    
    st.subheader("OPOA")
    st.latex(rf"OPOA = \left( \frac{{\text{{{input_data['operating profit'][0]}}}}}{{\text{{{input_data['total assets'][0]}}}}} \right) \times 100")

    # Coverage
    st.header("4. Coverage (Maximized)")
    st.subheader("Interest Coverage (IC)")
    st.latex(rf"IC = \frac{{\text{{{input_data['earnings before tax'][0]}}}}}{{\text{{{input_data['finance cost'][0]}}}}}")
    
    st.subheader("Debt Service Coverage Ratio (DSCR)")
    st.latex(rf"DSCR = \frac{{\text{{{input_data['operating profit'][0]}}}}}{{\text{{Total Debt Service}}}}")
    # Handle 'long term loan-current portion' safely
    long_term_loan = input_data.get("long term loan-current portion", 0)
    if isinstance(long_term_loan, list) and len(long_term_loan) > 0:
        long_term_loan_str = long_term_loan[0]
    else:
        long_term_loan_str = str(long_term_loan)
    finance_cost_str = input_data.get("finance cost", ["0"])[0]
    st.latex(rf"Total Debt Service = \text{{{long_term_loan_str}}} + \text{{{finance_cost_str}}}")

    st.subheader("Operating Cash Flow to Debt Ratio (CDR)")
    st.latex(rf"CDR = \frac{{\text{{{input_data['cash flows from operating activities'][0]}}}}}{{\text{{{input_data['total liabilities'][0]}}}}}")
    
    st.subheader("Cash Flow Coverage Ratio (CCR)")
    st.latex(rf"CCR = \frac{{\text{{{input_data['cash flows from operating activities'][0]}}}}}{{\text{{Total Debt Service}}}}")

    # Operational Efficiency
    st.header("5. Operational Efficiency (Minimized / Maximized)")
    st.subheader("Stock Turnover Days (STD)")
    st.latex(rf"STD = \frac{{\text{{{input_data['inventories'][0]}}}}}{{\text{{{input_data['cost of sales'][0]}}}}}")
    
    st.subheader("Trade Days Collection Period (TDCD)")
    st.latex(rf"TDCD = \frac{{\text{{{input_data['accounts receivables'][0]}}}}}{{\text{{Average Daily Credit Sales}}}}")
    st.latex(rf"Average Daily Credit Sales = \text{{{input_data['revenue'][0]}}} / 360")
    
    st.subheader("Asset Turnover (AT)")
    st.latex(rf"AT = \frac{{\text{{{input_data['revenue'][0]}}}}}{{\text{{{input_data['total assets'][0]}}}}}")

    # Earning Quality
    st.header("6. Earning Quality (Minimized / Maximized)")
    st.subheader("Operating Cash Flow to Sales (CFS)")
    st.latex(rf"CFS = \frac{{\text{{{input_data['cash flows from operating activities'][0]}}}}}{{\text{{{input_data['revenue'][0]}}}}}")
    
    st.subheader("Cash Flow-based Accrual Ratio (CFAR)")
    st.latex(rf"CFAR = \frac{{\text{{{input_data['net profit after tax'][0]}}} - \text{{{input_data['cash flows from operating activities'][0]}}}}}{{\text{{{input_data['total assets'][0]}}}}}")



# Run the app
if __name__ == "__main__":
    main()

    # Create a container to center the button
    with st.container():
        # Add a little space before the button
        st.write("")  # Adds an empty line
        st.write("")  # Adds another empty line for more space

        # Use columns to center the button
        col1, col2 = st.columns([1, 1])  # Adjust the ratio to center the button
        with col2:
            if st.button("Next"):
                st.switch_page("pages/parameters.py")