import streamlit as st
import pandas as pd
from tabulate import tabulate  # Ensure tabulate is installed: pip install tabulate
from io import StringIO
from source.main_function import Main

# input_data = {'particulars': ['Assets', 'Property, plant and equipment', 'Right-of-use assets', 'Equity-accounted investees', 'Other investments', 'Intangible assets', 'Biological assets', 'Deferred tax assets', 'Non-current assets', 'Inventories', 'Trade receivables', 'Other receivables', 'Receivable from joint-ventures and associates', 'Advances, deposits and prepayments', 'Current tax assets', 'Short term investments', 'Cash and cash equivalents', 'Current assets', 'Total assets', 'Equity', 'Share capital', 'Share premium', 'Reserves', 'Retained earnings', 'Equity attributable to the owners of the Company', 'Non-controlling interests', 'Total equity', 'Liabilities', 'Employee benefits', 'Long term bank loans', 'Lease liabilities', 'Non-current liabilities', 'Bank overdraft', 'Loans and borrowings', 'Lease liabilities-current portion', 'Trade payables', 'Other payables', 'Unclaimed dividend account', 'Current liabilities', 'Total liabilities', 'Total equity and liabilities', 'Consolidated Net Asset Value (NAV) per share', 'Revenue', 'Cost of sales', 'Gross profit', 'Administrative, selling and distribution expenses', 'Other income', 'Operating profit', 'Gain on disposal of investment in equity accounted investees', 'Share of profit of equity accounted investees', 'Net finance costs', 'Profit before contribution to WPPF', 'Contribution to WPPF', 'Profit before tax', 'Income tax expense', 'Current tax expense', 'Deferred tax income/(expense)', 'Profit/(loss) after tax', 'Profit/(loss) attributable to', 'Owners of the Company', 'Non-controlling interests', 'Profit/(loss) attributable to', 'Basic and diluted earnings per share', 'Cash flows from operating activities', 'Cash receipts from customers and others', 'Cash paid to suppliers and employees', 'Cash generated from operating activities', 'Paid to WPPF', 'Interest paid', 'Income tax paid', 'Net cash from/(used in) operating activities', '', 'Cash flows from investing activities', 'Acquisition of property, plant and equipment', 'Payments for capital work-in-progress', 'Proceeds from sale of property, plant and equipment', 'Proceeds from disposal of investment in joint ventures and associates', 'Purchase of biological assets', 'Dividend received', 'Short term investments', 'Long term investments', 'Net cash from/(used in) investing activities', 'Cash flows from financing activities', 'Dividend paid to non-controlling interests', 'Inter-company debts received/(paid)', 'Dividend paid', 'Capital contribution by non-controlling interests in ACI AgroChem', 'Payment for lease liabilities', 'Equity investment received by ACI Motors Limited', 'Short-term bank loan received/(paid)', 'Long-term bank loan received/(paid)', 'Net cash from/(used in) financing activities', 'Net increase/(decrease) in cash and cash equivalents', 'Opening cash and cash equivalents', 'Effect of movements in exchange rate on cash held', 'Cash and cash equivalents at reporting date', '', '---', 'Cash and cash equivalents', 'Bank overdraft', 'Consolidated Net Operating Cash Flows Per Share (NOCFPS)'], '2023': ['', '31715817451', '3082581839', '2058056899', '1027172247', '1409150269', '36569791', '341108740', '39670457236', '21791856287', '16648869492', '1103490611', '965101', '3291523760', '343735757', '2784452098', '5272771904', '51237665010', '90908122246', '', '762056260', '1254115881', '6130774222', '515470230', '8662416593', '1884856391', '10547272984', '', '1720980000', '6047143695', '2392020059', '10160143754', '8427735948', '44885489976', '484099575', '7035969221', '9281693343', '85717445', '70200705508', '80360849262', '90908122246', '113.67', '115355397105', '-89483069654', '', '-20222196292', '488722566', '6138853725', '416029319', '450867732', '-5053581867', '1952168909', '-299481648', '1652687261', '', '-2139744182', '412171228', '-1727572954', '', '-493958862', '419073169', '-74885693', '37.1(a)', '', '111898296077', '-107404701258', '4493594819', '-250596660', '-3729917736', '-2380088122', '-6360602518', '-1867007699', '', '-800698103', '-3427460707', '13767961', '689284085', '-5573486', '280355906', '-2784452098', '-207381034', '-6242157477', '', '-202292723', '4647793', '-365684867', '1000000', '-472933351', '-', '8833028441', '-885621270', '6912144024', '-1197021152', '-1968368348', '10425456', '-3154964044', 'For the year ended 30 June 2023', '---', '5272771904', '-8427735948', '37.3(a)'], '2022': ['', '29154498292', '1720125531', '2157943932', '822290382', '1367550235', '31303261', '709841617', '35963553250', '20323249620', '12772253271', '832500769', '5612894', '2512497990', '103391819', '-', '3208757234', '39758263596', '75721816847', '', '725767870', '1231094113', '6950487337', '1397376137', '10304725457', '1899966715', '12204692172', '', '1583157153', '6408915381', '1384717849', '9376790384', '5177125582', '35271595114', '382470526', '5518327175', '7702734053', '88081841', '54140334291', '63517124675', '75721816847', '135.22', '96571641497', '-72717772659', '', '-17767565065', '347744046', '6434047819', '-', '444850102', '-3913281118', '2965616803', '-337886688', '2627730115', '', '-1942502635', '207775600', '-1734727035', '', '379644188', '513358892', '893003080', '4.98', '', '96351082929', '-90389500238', '5961582691', '-256873602', '-3256372716', '-2140637665', '-5653883983', '307698708', '', '-512334099', '-1668657993', '6158696', '-', '-14527787', '352839090', '1157334040', '-198355507', '-877543559', '', '-70504383', '157199', '-445609225', '-', '-417689912', '824728692', '-342181408', '-1262588190', '-1713687227', '-2283532078', '287985204', '27178526', '-1968368348', 'For the year ended 30 June 2022', '---', '3208757234', '-5177125582', '4.04']}


# Check if input data and files exist in session state
if 'input' in st.session_state:
    input_data = st.session_state.input
else:
    st.error("Input data not found")

if 'files' in st.session_state:
    files = st.session_state.files
else:
    st.error("Files not found")

# Function to convert data to a neatly formatted Markdown table
def convert_to_markdown_table(data):
    if not data:
        return "No data available"
    df = pd.DataFrame(data)  
    return tabulate(df, headers="keys", tablefmt="pipe", showindex=False)  # Clean format

# Function to convert Markdown table back to JSON
def markdown_to_json(markdown):
    try:
        # Read the Markdown table into a DataFrame
        df = pd.read_csv(StringIO(markdown), sep="|", skipinitialspace=True)
        
        # Remove empty columns
        df = df.dropna(axis=1, how="all")
        
        # Remove separator row and reset index
        df = df.iloc[1:].reset_index(drop=True)
        
        # Strip any leading/trailing spaces from column names and values
        df.columns = df.columns.str.strip()
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        
        # Convert DataFrame to a dictionary with column names as keys and lists as values
        return df.to_dict(orient="list")
    
    except Exception as e:
        return {"error": f"Could not convert Markdown to JSON: {e}"}


# Streamlit UI
st.title("Financial Data Table")

# Display images side by side in columns
col1, col2, col3 = st.columns(3)

if len(files) >= 3:
    with col1:
        st.image(files[0], caption=files[0].name, use_container_width=True)
    with col2:
        st.image(files[1], caption=files[1].name, use_container_width=True)
    with col3:
        st.image(files[2], caption=files[2].name, use_container_width=True)

# Convert input data to a markdown table
markdown_table = convert_to_markdown_table(input_data)

# **Improved Editable Text Area**
editable_markdown = st.text_area(
    "Modify the markdown table:", 
    value=markdown_table, 
    height=max(400, min(800, len(markdown_table.split("\n")) * 20))  # Auto-adjust height
)

# Save the Markdown button
if st.button("Save Markdown"):
    st.session_state.saved_markdown = editable_markdown
    st.success("Markdown saved successfully!")

# Convert to JSON and process
if st.button("Convert to JSON"):
    json_data = markdown_to_json(editable_markdown)

    print("IMPROVED INPUT_DATA: ")
    print(json_data)
    
    if "error" in json_data:
        st.error(json_data["error"])  # Show error if conversion fails
    else:
        st.session_state.input = json_data

        main_program = Main()
        intermediate_values = main_program.intermediate_values(json_data)
        inter_result = main_program.intermediate_result(json_data, intermediate_values)
        output = main_program.final_output(inter_result)

        st.session_state.output = output
        st.write("### Processed Output:")
        st.json(output)

# Display formatted markdown preview
st.write("### Markdown Preview:")
st.code(editable_markdown, language="markdown")

# Navigation Button
if st.button("Next"):
    st.switch_page("pages/parameters.py")
