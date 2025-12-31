import streamlit as st
from source.main_function import Main
import json
import requests
import pandas as pd

# Set page configuration
# st.set_page_config(layout="wide")
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

# # Load session state data
# if 'intermediate' not in st.session_state:
#     st.error("Data not found in intermediate session state. Using default values.")
# else:
#     if isinstance(st.session_state.intermediate, str):
#         try:
#             intermediate_data = json.loads(st.session_state.intermediate)
#         except json.JSONDecodeError:
#             st.error("Invalid JSON format in session state. Using default values.")
#     else:
#         intermediate_data = st.session_state.intermediate


# if 'input' not in st.session_state:
#     st.error("Data not found in session state. Using default values.")
# else:
#     if isinstance(st.session_state.input, str):
#         try:
#             input_data = json.loads(st.session_state.input)
#         except json.JSONDecodeError:
#             st.error("Invalid JSON format in session state. Using default values.")
#     else:
#         input_data = st.session_state.input

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
        st.latex(rf"DTN = \frac{{\text{{total liabilities}}}}{{\text{{Tangible Net Worth}}}}")
        st.latex(rf"\text{{Tangible Net Worth}} = \text{{total assets}} - \text{{total liabilities}} - \text{{intangible assets}}")

        st.subheader("Debt to Total Assets (DTA)")
        st.latex(rf"DTA = \frac{{\text{{total liabilities}}}}{{\text{{total assets}}}}")

        # Liquidity
        st.header("2. Liquidity (Maximized)")
        st.subheader("Current Ratio (CR)")
        st.latex(rf"CR = \frac{{\text{{current assets}}}}{{\text{{current liabilities}}}}")
        
        st.subheader("Cash Ratio")
        st.latex(rf"Cash\ Ratio = \frac{{\text{{cash and cash equivalents at end of year}}}}{{\text{{current liabilities}}}}")

        # Profitability
        st.header("3. Profitability (Maximized)")
        st.subheader("Net Profit Margin (NPM)")
        st.latex(rf"NPM = \left( \frac{{\text{{net profit after tax}}}}{{\text{{revenue}}}} \right) \times 100")
        
        st.subheader("Return on Assets (ROA)")
        st.latex(rf"ROA = \left( \frac{{\text{{net profit after tax}}}}{{\text{{total assets}}}} \right) \times 100")
        
        st.subheader("OPOA")
        st.latex(rf"OPOA = \left( \frac{{\text{{operating profit}}}}{{\text{{total assets}}}} \right) \times 100")

        # Coverage
        st.header("4. Coverage (Maximized)")
        st.subheader("Interest Coverage (IC)")
        st.latex(rf"IC = \frac{{\text{{earnings before tax}}}}{{\text{{finance cost}}}}")
        
        st.subheader("Debt Service Coverage Ratio (DSCR)")
        st.latex(rf"DSCR = \frac{{\text{{operating profit}}}}{{\text{{Total Debt Service}}}}")
        # # Handle 'long term loan-current portion' safely
        # long_term_loan = intermediate_data.get("long term loan-current portion", 0)
        # if isinstance(long_term_loan, list) and len(long_term_loan) > 0:
        #     long_term_loan_str = long_term_loan[0]
        # else:
        #     long_term_loan_str = str(long_term_loan)
        # finance_cost_str = intermediate_data.get("finance cost", ["0"])[0]
        st.latex(rf"Total Debt Service = \text{{long term loan-current portion}} + \text{{finance cost}}")

        st.subheader("Operating Cash Flow to Debt Ratio (CDR)")
        st.latex(rf"CDR = \frac{{\text{{cash flows from operating activities}}}}{{\text{{total liabilities}}}}")
        
        st.subheader("Cash Flow Coverage Ratio (CCR)")
        st.latex(rf"CCR = \frac{{\text{{cash flows from operating activities}}}}{{\text{{Total Debt Service}}}}")

        # Operational Efficiency
        st.header("5. Operational Efficiency (Minimized / Maximized)")
        st.subheader("Stock Turnover Days (STD)")
        st.latex(rf"STD = \frac{{\text{{inventories}}}}{{\text{{cost of sales}}}}")
        
        st.subheader("Trade Days Collection Period (TDCD)")
        st.latex(rf"TDCD = \frac{{\text{{accounts receivables}}}}{{\text{{Average Daily Credit Sales}}}}")
        st.latex(rf"Average Daily Credit Sales = \text{{revenue}} / 360")
        
        st.subheader("Asset Turnover (AT)")
        st.latex(rf"AT = \frac{{\text{{revenue}}}}{{\text{{total assets}}}}")

        # Earning Quality
        st.header("6. Earning Quality (Minimized / Maximized)")
        st.subheader("Operating Cash Flow to Sales (CFS)")
        st.latex(rf"CFS = \frac{{\text{{cash flows from operating activities}}}}{{\text{{revenue}}}}")
        
        st.subheader("Cash Flow-based Accrual Ratio (CFAR)")
        st.latex(rf"CFAR = \frac{{\text{{net profit after tax}} - \text{{cash flows from operating activities}}}}{{\text{{total assets}}}}")



    with right_col:
        st.write("### Dictionary Updater")

        # Step 1: Select a key from the available options
        key_options = list(intermediate_data.keys())
        key_choice = st.selectbox("Select Key", key_options)

        # Step 2: Display the current values for the selected key
        if key_choice:
            st.write(f"Current values for '{key_choice}':")
            st.write(', '.join([str(item) for item in intermediate_data[key_choice] if item is not None]))


        # Step 3: Select a particular from the available options
        particular_choice = st.selectbox("Select Particular", particulars)

        # Step 4: Dropdown to add more values
        if st.button("Add Value"):
            if key_choice and particular_choice:
                # Ensure the value for the key is a list, or initialize it as a list
                if key_choice not in intermediate_data or not isinstance(intermediate_data[key_choice], list):
                    intermediate_data[key_choice] = []

                # Add the particular if it's not already present
                if particular_choice not in intermediate_data[key_choice]:
                    intermediate_data[key_choice].append(particular_choice)
                    st.success(f"'{particular_choice}' added to '{key_choice}'.")

        # Step 5: Display the updated dictionary in a table
        st.write("### Table Data")

        # Convert the dictionary to a DataFrame for table display
        table_data = [
            (key, ', '.join([str(v) for v in values if v is not None]) if isinstance(values, list) else str(values))
            for key, values in intermediate_data.items()
        ]


        df = pd.DataFrame(table_data, columns=["Key", "Particulars"])

        # Show the table
        st.table(df)



        if st.button("Next"):  
            st.session_state.intermediate = json.dumps(intermediate_data)

            main_program = Main()

            inter_result = main_program.intermediate_result(input_data, intermediate_data)
            output_data, output = main_program.final_output(inter_result)

            url = "http://192.168.10.50:8000/store_scoring_data"

            print(output)

            def store_scoring_data(scoring_data, url):
                with open('json/variables.json', 'r') as file:
                    data = json.load(file)

                # Check if scoring_data is a dictionary
                if isinstance(scoring_data, dict):
                    total_score = sum([score for score in scoring_data.values() if isinstance(score, (int, float))])
                    scoring_data_dict = scoring_data
                # If it's a list, assume the values are in the same order as the dictionary keys
                elif isinstance(scoring_data, list):
                    scoring_data_dict = {
                        "dtn_score": scoring_data[0] if len(scoring_data) > 0 else 0,
                        "dta_score": scoring_data[1] if len(scoring_data) > 1 else 0,
                        "current_ratio_score": scoring_data[2] if len(scoring_data) > 2 else 0,
                        "cash_ratio_score": scoring_data[3] if len(scoring_data) > 3 else 0,
                        "npm_score": scoring_data[4] if len(scoring_data) > 4 else 0,
                        "roa_score": scoring_data[5] if len(scoring_data) > 5 else 0,
                        "opoa_score": scoring_data[6] if len(scoring_data) > 6 else 0,
                        "ic_score": scoring_data[7] if len(scoring_data) > 7 else 0,
                        "dscr_score": scoring_data[8] if len(scoring_data) > 8 else 0,
                        "cdr_score": scoring_data[9] if len(scoring_data) > 9 else 0,
                        "ccr_score": scoring_data[10] if len(scoring_data) > 10 else 0,
                        "std_score": scoring_data[11] if len(scoring_data) > 11 else 0,
                        "tdcd_score": scoring_data[12] if len(scoring_data) > 12 else 0,
                        "at_score": scoring_data[13] if len(scoring_data) > 13 else 0,
                        "cfs_score": scoring_data[14] if len(scoring_data) > 14 else 0,
                        "car_score": scoring_data[15] if len(scoring_data) > 15 else 0
                    }
                    total_score = sum([score for score in scoring_data_dict.values() if isinstance(score, (int, float))])
                else:
                    total_score = 0
                    scoring_data_dict = {}

                # Prepare transformed data for submission
                transformed_data = {**scoring_data_dict, "total_score": total_score, 
                                    "bs_id": data['balance_id'],
                                    "is_id": data['income_id'],
                                    "cfs_id": data['cash_id'],
                                    "llm_id": data["llm_id"]}

                # Log the transformed data to verify it's correct
                print(f"Sending transformed data: {transformed_data}")

                # Sending transformed data to the database URL
                try:
                    response = requests.post(url, json=transformed_data)
                    response.raise_for_status()
                    return {'status': 'success', 'response': response.json()}
                except requests.exceptions.RequestException as e:
                    return {'status': 'error', 'error': str(e)}
                
            
            final = store_scoring_data(output, url)

            print("Printing final DaTABASE Message-------------")
            print(final)

            st.session_state.output = output_data
            print(" Processed Output------------------")
            print(output_data)
            # st.write("### Processed Output:")
            # st.json(output_data)
            
            st.switch_page("pages/parameters.py")



if __name__ == "__main__":
    main()
