import streamlit as st
import json

# Set page configuration
st.set_page_config(layout="wide")
st.title("Calculation of Quantitative Indicators")

# Default input data
intermediate_data = {
    "total assets": ["Total assets"],
    "total liabilities": ["Total liabilities"],
    "current assets": ["Current assets"],
    "current liabilities": ["Current liabilities"],
    "intangible assets": ["Intangible assets"],
    "long term loan-current portion": [],
    "inventories": ["Inventories"],
    "accounts receivables": ["Trade receivables", "Other receivables"],
    "capital work in progress": ["Payments for capital work-in-progress"],
    "non-current assets": ["Non-current assets"],
    "revenue": ["Revenue"],
    "net profit after tax": ["Profit/(loss) after tax"],
    "operating profit": ["Operating profit"],
    "earnings before tax": ["Profit before tax"],
    "finance cost": ["Net finance costs"],
    "cost of sales": ["Cost of sales"],
    "cash and cash equivalents at end of year": ["Cash and cash equivalents at reporting date"],
    "cash flows from operating activities": ["Net cash from/(used in) operating activities"],
    "cash flows from financing activities": ["Net cash from/(used in) financing activities"]
}

input_data = {'particulars': ['Assets', 'Property, plant and equipment', 'Right-of-use assets', 'Equity-accounted investees', 'Other investments', 'Intangible assets', 'Biological assets', 'Deferred tax assets', 'Non-current assets', 'Inventories', 'Trade receivables', 'Other receivables', 'Receivable from joint-ventures and associates', 'Advances, deposits and prepayments', 'Current tax assets', 'Short term investments', 'Cash and cash equivalents', 'Current assets', 'Total assets', 'Equity', 'Share capital', 'Share premium', 'Reserves', 'Retained earnings', 'Equity attributable to the owners of the Company', 'Non-controlling interests', 'Total equity', 'Liabilities', 'Employee benefits', 'Long term bank loans', 'Lease liabilities', 'Non-current liabilities', 'Bank overdraft', 'Loans and borrowings', 'Lease liabilities-current portion', 'Trade payables', 'Other payables', 'Unclaimed dividend account', 'Current liabilities', 'Total liabilities', 'Total equity and liabilities', 'Consolidated Net Asset Value (NAV) per share', 'Revenue', 'Cost of sales', 'Gross profit', 'Administrative, selling and distribution expenses', 'Other income', 'Operating profit', 'Gain on disposal of investment in equity accounted investees', 'Share of profit of equity accounted investees', 'Net finance costs', 'Profit before contribution to WPPF', 'Contribution to WPPF', 'Profit before tax', 'Income tax expense', 'Current tax expense', 'Deferred tax income/(expense)', 'Profit/(loss) after tax', 'Profit/(loss) attributable to', 'Owners of the Company', 'Non-controlling interests', 'Profit/(loss) attributable to', 'Basic and diluted earnings per share', 'Cash flows from operating activities', 'Cash receipts from customers and others', 'Cash paid to suppliers and employees', 'Cash generated from operating activities', 'Paid to WPPF', 'Interest paid', 'Income tax paid', '', 'Net cash from/(used in) operating activities', 'Cash flows from investing activities', 'Acquisition of property, plant and equipment', 'Payments for capital work-in-progress', 'Proceeds from sale of property, plant and equipment', 'Proceeds from disposal of investment in joint ventures and associates', 'Purchase of biological assets', 'Dividend received', 'Short term investments', 'Long term investments', 'Net cash from/(used in) investing activities', 'Cash flows from financing activities', 'Dividend paid to non-controlling interests', 'Inter-company debts received/(paid)', 'Dividend paid', 'Capital contribution by non-controlling interests in ACI AgroChem', 'Payment for lease liabilities', 'Equity investment received by ACI Motors Limited', 'Short-term bank loan received/(paid)', 'Long-term bank loan received/(paid)', 'Net cash from/(used in) financing activities', 'Net increase/(decrease) in cash and cash equivalents', 'Opening cash and cash equivalents', 'Effect of movements in exchange rate on cash held', 'Cash and cash equivalents at reporting date', '', '---', 'Cash and cash equivalents', 'Bank overdraft', 'Consolidated Net Operating Cash Flows Per Share (NOCFPS)'], '30 June 2023': ['', '31715817451', '3082581839', '2058056899', '1027172247', '1409150269', '36569791', '341108740', '39670457236', '21791856287', '16648869492', '1103490611', '965101', '3291523760', '343735757', '2784452098', '5272771904', '51237665010', '90908122246', '', '762056260', '1254115881', '6130774222', '515470230', '8662416593', '1884856391', '10547272984', '', '1720980000', '6047143695', '2392020059', '10160143754', '8427735948', '44885489976', '484099575', '7035969221', '9281693343', '85717445', '70200705508', '80360849262', '90908122246', '113.67', '115355397105', '-89483069654', '', '-20222196292', '488722566', '6138853725', '416029319', '450867732', '-5053581867', '1952168909', '-299481648', '1652687261', '', '-2139744182', '412171228', '-1727572954', '', '-493958862', '419073169', '-74885693', '37.1(a)', '', '111898296077', '-107404701258', '4493594819', '-250596660', '-3729917736', '-2380088122', '-6360602518', '-1867007699', '', '-800698103', '-3427460707', '13767961', '689284085', '-5573486', '280355906', '-2784452098', '-207381034', '-6242157477', '', '-202292723', '4647793', '-365684867', '1000000', '-472933351', '-', '8833028441', '-885621270', '6912144024', '-1197021152', '-1968368348', '10425456', '-3154964044', 'For the year ended 30 June 2023', '---', '5272771904', '-8427735948', '37.3(a)'], '30 June 2022': ['', '29154498292', '1720125531', '2157943932', '822290382', '1367550235', '31303261', '709841617', '35963553250', '20323249620', '12772253271', '832500769', '5612894', '2512497990', '103391819', '-', '3208757234', '39758263596', '75721816847', '', '725767870', '1231094113', '6950487337', '1397376137', '10304725457', '1899966715', '12204692172', '', '1583157153', '6408915381', '1384717849', '9376790384', '5177125582', '35271595114', '382470526', '5518327175', '7702734053', '88081841', '54140334291', '63517124675', '75721816847', '135.22', '96571641497', '-72717772659', '', '-17767565065', '347744046', '6434047819', '-', '444850102', '-3913281118', '2965616803', '-337886688', '2627730115', '', '-1942502635', '207775600', '-1734727035', '', '379644188', '513358892', '893003080', '4.98', '', '96351082929', '-90389500238', '5961582691', '-256873602', '-3256372716', '-2140637665', '-5653883983', '307698708', '', '-512334099', '-1668657993', '6158696', '-', '-14527787', '352839090', '1157334040', '-198355507', '-877543559', '', '-70504383', '157199', '-445609225', '-', '-417689912', '824728692', '-342181408', '-1262588190', '-1713687227', '-2283532078', '287985204', '27178526', '-1968368348', 'For the year ended 30 June 2022', '---', '3208757234', '-5177125582', '4.04']}

# Load session state data
if 'intermediate' not in st.session_state:
    st.error("Data not found in session state. Using default values.")
else:
    if isinstance(st.session_state.intermediate, str):
        try:
            intermediate_data = json.loads(st.session_state.intermediate)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in session state. Using default values.")
    else:
        intermediate_data = st.session_state.intermediate


if 'input' not in st.session_state:
    st.error("Data not found in session state. Using default values.")
else:
    if isinstance(st.session_state.input, str):
        try:
            input_data = json.loads(st.session_state.input)
        except json.JSONDecodeError:
            st.error("Invalid JSON format in session state. Using default values.")
    else:
        input_data = st.session_state.input

particulars = [str(p).lower().strip() for p in input_data['particulars'] if isinstance(p, str)]


def process_data(data):
    processed_data = {}
    for key, value in data.items():
        if not isinstance(value, list):
            value = [value]
        if len(value) == 0:
            processed_data[key] = 0
        elif len(value) == 2:
            processed_data[key] = [f"{value[0]}+{value[1]}"]
        else:
            processed_data[key] = value
    return processed_data

intermediate_data = process_data(intermediate_data)

def main():
    left_col, right_col = st.columns(2)

    with left_col:  # Formulas Section
        st.write("### Formulas")

        # Leverage
        st.header("1. Leverage (Minimized)")
        st.subheader("Debt to Tangible Net Worth (DTN)")
        st.latex(rf"DTN = \frac{{\text{{{intermediate_data['total liabilities'][0]}}}}}{{\text{{{intermediate_data['total assets'][0]}}} - \text{{{intermediate_data['total liabilities'][0]}}} - \text{{{intermediate_data['intangible assets'][0]}}}}}")
        st.latex(rf"\text{{Tangible Net Worth}} = \text{{{intermediate_data['total assets'][0]}}} - \text{{{intermediate_data['total liabilities'][0]}}} - \text{{{intermediate_data['intangible assets'][0]}}}")

        st.subheader("Debt to Total Assets (DTA)")
        st.latex(rf"DTA = \frac{{\text{{{intermediate_data['total liabilities'][0]}}}}}{{\text{{{intermediate_data['total assets'][0]}}}}}")

        # Liquidity
        st.header("2. Liquidity (Maximized)")
        st.subheader("Current Ratio (CR)")
        st.latex(rf"CR = \frac{{\text{{{intermediate_data['current assets'][0]}}}}}{{\text{{{intermediate_data['current liabilities'][0]}}}}}")
        
        st.subheader("Cash Ratio")
        st.latex(rf"Cash\ Ratio = \frac{{\text{{{intermediate_data['cash and cash equivalents at end of year'][0]}}}}}{{\text{{{intermediate_data['current liabilities'][0]}}}}}")

        # Profitability
        st.header("3. Profitability (Maximized)")
        st.subheader("Net Profit Margin (NPM)")
        st.latex(rf"NPM = \left( \frac{{\text{{{intermediate_data['net profit after tax'][0]}}}}}{{\text{{{intermediate_data['revenue'][0]}}}}} \right) \times 100")
        
        st.subheader("Return on Assets (ROA)")
        st.latex(rf"ROA = \left( \frac{{\text{{{intermediate_data['net profit after tax'][0]}}}}}{{\text{{{intermediate_data['total assets'][0]}}}}} \right) \times 100")
        
        st.subheader("OPOA")
        st.latex(rf"OPOA = \left( \frac{{\text{{{intermediate_data['operating profit'][0]}}}}}{{\text{{{intermediate_data['total assets'][0]}}}}} \right) \times 100")

        # Coverage
        st.header("4. Coverage (Maximized)")
        st.subheader("Interest Coverage (IC)")
        st.latex(rf"IC = \frac{{\text{{{intermediate_data['earnings before tax'][0]}}}}}{{\text{{{intermediate_data['finance cost'][0]}}}}}")
        
        st.subheader("Debt Service Coverage Ratio (DSCR)")
        st.latex(rf"DSCR = \frac{{\text{{{intermediate_data['operating profit'][0]}}}}}{{\text{{Total Debt Service}}}}")
        # Handle 'long term loan-current portion' safely
        long_term_loan = intermediate_data.get("long term loan-current portion", 0)
        if isinstance(long_term_loan, list) and len(long_term_loan) > 0:
            long_term_loan_str = long_term_loan[0]
        else:
            long_term_loan_str = str(long_term_loan)
        finance_cost_str = intermediate_data.get("finance cost", ["0"])[0]
        st.latex(rf"Total Debt Service = \text{{{long_term_loan_str}}} + \text{{{finance_cost_str}}}")

        st.subheader("Operating Cash Flow to Debt Ratio (CDR)")
        st.latex(rf"CDR = \frac{{\text{{{intermediate_data['cash flows from operating activities'][0]}}}}}{{\text{{{intermediate_data['total liabilities'][0]}}}}}")
        
        st.subheader("Cash Flow Coverage Ratio (CCR)")
        st.latex(rf"CCR = \frac{{\text{{{intermediate_data['cash flows from operating activities'][0]}}}}}{{\text{{Total Debt Service}}}}")

        # Operational Efficiency
        st.header("5. Operational Efficiency (Minimized / Maximized)")
        st.subheader("Stock Turnover Days (STD)")
        st.latex(rf"STD = \frac{{\text{{{intermediate_data['inventories'][0]}}}}}{{\text{{{intermediate_data['cost of sales'][0]}}}}}")
        
        st.subheader("Trade Days Collection Period (TDCD)")
        st.latex(rf"TDCD = \frac{{\text{{{intermediate_data['accounts receivables'][0]}}}}}{{\text{{Average Daily Credit Sales}}}}")
        st.latex(rf"Average Daily Credit Sales = \text{{{intermediate_data['revenue'][0]}}} / 360")
        
        st.subheader("Asset Turnover (AT)")
        st.latex(rf"AT = \frac{{\text{{{intermediate_data['revenue'][0]}}}}}{{\text{{{intermediate_data['total assets'][0]}}}}}")

        # Earning Quality
        st.header("6. Earning Quality (Minimized / Maximized)")
        st.subheader("Operating Cash Flow to Sales (CFS)")
        st.latex(rf"CFS = \frac{{\text{{{intermediate_data['cash flows from operating activities'][0]}}}}}{{\text{{{intermediate_data['revenue'][0]}}}}}")
        
        st.subheader("Cash Flow-based Accrual Ratio (CFAR)")
        st.latex(rf"CFAR = \frac{{\text{{{intermediate_data['net profit after tax'][0]}}} - \text{{{intermediate_data['cash flows from operating activities'][0]}}}}}{{\text{{{intermediate_data['total assets'][0]}}}}}")



    with right_col:  # Dictionary Updater Section
        st.write("### Dictionary Updater")
        key_options = list(intermediate_data.keys())
        key_choice = st.selectbox("Select Key", key_options)
        particular_choice = st.selectbox("Select Particular", particulars)

        if st.button("Save"):
            if key_choice and particular_choice:
                if particular_choice not in intermediate_data[key_choice]:
                    intermediate_data[key_choice].append(particular_choice)
                    st.success(f"'{particular_choice}' added to '{key_choice}'.")

        st.write("### JSON Data")
        st.json(intermediate_data)

        if st.button("Next"):  
            st.session_state.intermediate = json.dumps(intermediate_data)
            st.switch_page("pages/parameters.py")


if __name__ == "__main__":
    main()
