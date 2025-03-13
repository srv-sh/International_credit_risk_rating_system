import streamlit as st
import pandas as pd
import json
import requests

st.set_page_config(layout="wide")

# input_data = {'bs':{'processed_response':{'particulars':['Assets','Property, plant and equipment','Right-of-use assets','Equity-accounted investees','Other investments','Intangible assets','Biological assets','Deferred tax assets','Non-current assets','Inventories','Trade receivables','Other receivables','Receivable from joint-ventures and associates','Advances, deposits and prepayments','Current tax assets','Short term investments','Cash and cash equivalents','Current assets','Total assets','Equity','Share capital','Share premium','Reserves','Retained earnings','Equity attributable to the owners of the Company','Non-controlling interests','Total equity','Liabilities','Employee benefits','Long term bank loans','Lease liabilities','Non-current liabilities','Bank overdraft','Loans and borrowings','Lease liabilities-current portion','Trade payables','Other payables','Unclaimed dividend account','Current liabilities','Total liabilities','Total equity and liabilities','Consolidated Net Asset Value (NAV) per share'],'30 June 2023':['','31715817451','3082581839','2058056899','1027172247','1409150269','36569791','341108740','39670457236','21791856287','16648869492','1103490611','965101','3291523760','343735757','2784452098','5272771904','51237665010','90908122246','','762056260','1254115881','6130774222','515470230','8662416593','1884856391','10547272984','','1720980000','6047143695','2392020059','10160143754','8427735948','44885489976','484099575','7035969221','9281693343','85717445','70200705508','80360849262','90908122246','113.67'],'30 June 2022':['','29154498292','1720125531','2157943932','822290382','1367550235','31303261','709841617','35963553250','20323249620','12772253271','832500769','5612894','2512497990','103391819','-','3208757234','39758263596','75721816847','','725767870','1231094113','6950487337','1397376137','10304725457','1899966715','12204692172','','1583157153','6408915381','1384717849','9376790384','5177125582','35271595114','382470526','5518327175','7702734053','88081841','54140334291','63517124675','75721816847','135.22']},'pdf_url':'/workspace/CreditScoring-refined-/pdf/woUkU6wqom.pdf','prompt':'Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. Just return the plain text representation of this document as if you were reading it naturally.\nDo not hallucinate.\nRAW_TEXT_START\nPage dimensions: 790.0x890.0\n[Image 0x0 to 790x890]\n\nRAW_TEXT_END','raw_response':{'primary_language':'en','is_rotation_valid':True,'rotation_correction':0,'is_table':True,'is_diagram':False,'natural_text':'## Advanced Chemical Industries Limited\n### Consolidated Statement of Financial Position\n\n|                      | Notes | 30 June 2023       | 30 June 2022       |\n|----------------------|-------|--------------------|--------------------|\n| **Assets**           |       |                    |                    |\n| Property, plant and equipment | 8 (a) | 31,715,817,451     | 29,154,498,292     |\n| Right-of-use assets  | 9 (a) | 3,082,581,839      | 1,720,125,531      |\n| Equity-accounted investees | 10 (a).1 | 2,058,056,899     | 2,157,943,932     |\n| Other investments    | 10 (a).2 | 1,027,172,247     | 822,290,382       |\n| Intangible assets    | 11 (a) | 1,409,150,269      | 1,367,550,235      |\n| Biological assets    | 12 (a) | 36,569,791         | 31,303,261        |\n| Deferred tax assets  | 23 (a) | 341,108,740        | 709,841,617       |\n| **Non-current assets** |       | 39,670,457,236     | 35,963,553,250     |\n| Inventories          | 13 (a) | 21,791,856,287     | 20,323,249,620     |\n| Trade receivables    | 14 (a) | 16,648,869,492     | 12,772,253,271     |\n| Other receivables    | 15 (a) | 1,103,490,611      | 832,500,769        |\n| Receivable from joint-ventures and associates | 16 (a) | 965,101            | 5,612,894         |\n| Advances, deposits and prepayments | 17 (a) | 3,291,523,760     | 2,512,497,990      |\n| Current tax assets   | 30 (a) | 343,735,757        | 103,391,819        |\n| Short term investments | 18 (a) | 2,784,452,098      | -                  |\n| Cash and cash equivalents | 18 (b) | 5,272,771,904     | 3,208,757,234      |\n| **Current assets**   |       | 51,237,665,010     | 39,758,263,596     |\n| **Total assets**     |       | 90,908,122,246     | 75,721,816,847     |\n| **Equity**           |       |                    |                    |\n| Share capital        |       | 762,056,260        | 725,767,870        |\n| Share premium        |       | 1,254,115,881      | 1,231,094,113      |\n| Reserves             | 20 (a) | 6,130,774,222      | 6,950,487,337      |\n| Retained earnings    |       | 515,470,230        | 1,397,376,137      |\n| **Equity attributable to the owners of the Company** |       | 8,662,416,593     | 10,304,725,457     |\n| **Non-controlling interests** |       | 1,884,856,391     | 1,899,966,715      |\n| **Total equity**     |       | 10,547,272,984     | 12,204,692,172     |\n| **Liabilities**      |       |                    |                    |\n| Employee benefits    | 21 (a) | 1,720,980,000      | 1,583,157,153      |\n| Long term bank loans | 22 (a) | 6,047,143,695      | 6,408,915,381      |\n| Lease liabilities    | 9 (a)  | 2,392,020,059      | 1,384,717,849      |\n| **Non-current liabilities** |       | 10,160,143,754     | 9,376,790,384      |\n| Bank overdraft       | 24 (a) | 8,427,735,948      | 5,177,125,582      |\n| Loans and borrowings | 25 (a) | 44,885,489,976     | 35,271,595,114     |\n| Lease liabilities-current portion | 9 (a) | 484,099,575        | 382,470,526        |\n| Trade payables       | 26 (a) | 7,035,969,221      | 5,518,327,175      |\n| Other payables       | 27 (a) | 9,281,693,343      | 7,702,734,053      |\n| Unclaimed dividend account | 28 (a) | 85,717,445        | 88,081,841         |\n| **Current liabilities** |       | 70,200,705,508     | 54,140,334,291     |\n| **Total liabilities** |       | 80,360,849,262     | 63,517,124,675     |\n| **Total equity and liabilities** |       | 90,908,122,246     | 75,721,816,847     |\n| **Consolidated Net Asset Value (NAV) per share** | 37.3(a) | 113.67            | 135.22             |\n\nThe annexed notes 1 to 45 form an integral part of these financial statements.'}},'is':{'processed_response':{'particulars':['Revenue','Cost of sales','Gross profit','Administrative, selling and distribution expenses','Other income','Operating profit','Gain on disposal of investment in equity accounted investees','Share of profit of equity accounted investees','Net finance costs','Profit before contribution to WPPF','Contribution to WPPF','Profit before tax','Income tax expense','Current tax expense','Deferred tax income/(expense)','Profit/(loss) after tax','Profit/(loss) attributable to','Owners of the Company','Non-controlling interests','Profit/(loss) attributable to','Basic and diluted earnings per share'],'For the year ended 30 June 2023':['115355397105','-89483069654','','-20222196292','488722566','6138853725','416029319','450867732','-5053581867','1952168909','-299481648','1652687261','','-2139744182','412171228','-1727572954','','-493958862','419073169','-74885693','37.1(a)'],'For the year ended 30 June 2022':['96571641497','-72717772659','','-17767565065','347744046','6434047819','-','444850102','-3913281118','2965616803','-337886688','2627730115','','-1942502635','207775600','-1734727035','','379644188','513358892','893003080','4.98']},'pdf_url':'/workspace/CreditScoring-refined-/pdf/w4cUdPdkQ4.pdf','prompt':'Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. Just return the plain text representation of this document as if you were reading it naturally.\nDo not hallucinate.\nRAW_TEXT_START\nPage dimensions: 783.0x786.0\n[Image 0x0 to 783x786]\n\nRAW_TEXT_END','raw_response':{'primary_language':'en','is_rotation_valid':True,'rotation_correction':0,'is_table':True,'is_diagram':False,'natural_text':'## Advanced Chemical Industries Limited\n### Consolidated Statement of Profit or Loss\n\n| In Taka                                      | For the year ended 30 June 2023 | For the year ended 30 June 2022 |\n|----------------------------------------------|---------------------------------|---------------------------------|\n| Revenue                                      | 115,355,397,105                 | 96,571,641,497                  |\n| Cost of sales                                | (89,483,069,654)                | (72,717,772,659)                |\n| **Gross profit**                             |                                 |                                 |\n| Administrative, selling and distribution expenses | (20,222,196,292)               | (17,767,565,065)                |\n| Other income                                 | 488,722,566                     | 347,744,046                     |\n| **Operating profit**                         | 6,138,853,725                   | 6,434,047,819                   |\n| Gain on disposal of investment in equity accounted investees | 416,029,319                     | -                               |\n| Share of profit of equity accounted investees | 450,867,732                     | 444,850,102                     |\n| Net finance costs                           | (5,053,581,867)                 | (3,913,281,118)                 |\n| **Profit before contribution to WPPF**       | 1,952,168,909                   | 2,965,616,803                   |\n| Contribution to WPPF                         | (299,481,648)                   | (337,886,688)                   |\n| **Profit before tax**                        | 1,652,687,261                   | 2,627,730,115                   |\n| Income tax expense                          |                                 |                                 |\n| Current tax expense                         | (2,139,744,182)                 | (1,942,502,635)                 |\n| Deferred tax income/(expense)               | 412,171,228                     | 207,775,600                     |\n| **Profit/(loss) after tax**                 | (1,727,572,954)                 | (1,734,727,035)                 |\n| **Profit/(loss) attributable to**           |                                 |                                 |\n| Owners of the Company                       | (493,958,862)                   | 379,644,188                     |\n| Non-controlling interests                   | 419,073,169                     | 513,358,892                     |\n| **Profit/(loss) attributable to**           | (74,885,693)                    | 893,003,080                     |\n\n### Earnings per share\n\n| Basic and diluted earnings per share | 37.1(a) | 4.98 |\n\nThe annexed notes 1 to 45 form an integral part of these financial statements.'}},'cfs':{'processed_response':{'particulars':['Cash flows from operating activities','Cash receipts from customers and others','Cash paid to suppliers and employees','Cash generated from operating activities','Paid to WPPF','Interest paid','Income tax paid','','Net cash from/(used in) operating activities','Cash flows from investing activities','Acquisition of property, plant and equipment','Payments for capital work-in-progress','Proceeds from sale of property, plant and equipment','Proceeds from disposal of investment in joint ventures and associates','Purchase of biological assets','Dividend received','Short term investments','Long term investments','Net cash from/(used in) investing activities','Cash flows from financing activities','Dividend paid to non-controlling interests','Inter-company debts received/(paid)','Dividend paid','Capital contribution by non-controlling interests in ACI AgroChem','Payment for lease liabilities','Equity investment received by ACI Motors Limited','Short-term bank loan received/(paid)','Long-term bank loan received/(paid)','Net cash from/(used in) financing activities','Net increase/(decrease) in cash and cash equivalents','Opening cash and cash equivalents','Effect of movements in exchange rate on cash held','Cash and cash equivalents at reporting date','','---','Cash and cash equivalents','Bank overdraft','Consolidated Net Operating Cash Flows Per Share (NOCFPS)'],'For the year ended 30 June 2023':['','111898296077','-107404701258','4493594819','-250596660','-3729917736','-2380088122','-6360602518','-1867007699','','-800698103','-3427460707','13767961','689284085','-5573486','280355906','-2784452098','-207381034','-6242157477','','-202292723','4647793','-365684867','1000000','-472933351','-','8833028441','-885621270','6912144024','-1197021152','-1968368348','10425456','-3154964044','For the year ended 30 June 2023','---','5272771904','-8427735948','37.3(a)'],'For the year ended 30 June 2022':['','96351082929','-90389500238','5961582691','-256873602','-3256372716','-2140637665','-5653883983','307698708','','-512334099','-1668657993','6158696','-','-14527787','352839090','1157334040','-198355507','-877543559','','-70504383','157199','-445609225','-','-417689912','824728692','-342181408','-1262588190','-1713687227','-2283532078','287985204','27178526','-1968368348','For the year ended 30 June 2022','---','3208757234','-5177125582','4.04']},'pdf_url':'/workspace/CreditScoring-refined-/pdf/mpOD7kwLim.pdf','prompt':'Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. Just return the plain text representation of this document as if you were reading it naturally.\nDo not hallucinate.\nRAW_TEXT_START\nPage dimensions: 647.0x847.0\n[Image 0x0 to 647x847]\n\nRAW_TEXT_END','raw_response':{'primary_language':'en','is_rotation_valid':True,'rotation_correction':0,'is_table':True,'is_diagram':False,'natural_text':'## Advanced Chemical Industries Limited\n\n### Consolidated Statement of Cash Flows\n\n| In Taka | Note | For the year ended 30 June 2023 | For the year ended 30 June 2022 |\n|---------|------|---------------------------------|---------------------------------|\n| **Cash flows from operating activities** | | | |\n| Cash receipts from customers and others | | 111,898,296,077 | 96,351,082,929 |\n| Cash paid to suppliers and employees | | (107,404,701,258) | (90,389,500,238) |\n| **Cash generated from operating activities** | | 4,493,594,819 | 5,961,582,691 |\n| Paid to WPPF | | (250,596,660) | (256,873,602) |\n| Interest paid | | (3,729,917,736) | (3,256,372,716) |\n| Income tax paid | | (2,380,088,122) | (2,140,637,665) |\n| | | (6,360,602,518) | (5,653,883,983) |\n| **Net cash from/(used in) operating activities** | 18 (c) | (1,867,007,699) | 307,698,708 |\n| **Cash flows from investing activities** | | | |\n| Acquisition of property, plant and equipment | | (800,698,103) | (512,334,099) |\n| Payments for capital work-in-progress | | (3,427,460,707) | (1,668,657,993) |\n| Proceeds from sale of property, plant and equipment | | 13,767,961 | 6,158,696 |\n| Proceeds from disposal of investment in joint ventures and associates | | 689,284,085 | - |\n| Purchase of biological assets | | (5,573,486) | (14,527,787) |\n| Dividend received | | 280,355,906 | 352,839,090 |\n| Short term investments | | (2,784,452,098) | 1,157,334,040 |\n| Long term investments | | (207,381,034) | (198,355,507) |\n| **Net cash from/(used in) investing activities** | | (6,242,157,477) | (877,543,559) |\n| **Cash flows from financing activities** | | | |\n| Dividend paid to non-controlling interests | | (202,292,723) | (70,504,383) |\n| Inter-company debts received/(paid) | | 4,647,793 | 157,199 |\n| Dividend paid | | (365,684,867) | (445,609,225) |\n| Capital contribution by non-controlling interests in ACI AgroChem | | 1,000,000 | - |\n| Payment for lease liabilities | | (472,933,351) | (417,689,912) |\n| Equity investment received by ACI Motors Limited | | - | 824,728,692 |\n| Short-term bank loan received/(paid) | | 8,833,028,441 | (342,181,408) |\n| Long-term bank loan received/(paid) | | (885,621,270) | (1,262,588,190) |\n| **Net cash from/(used in) financing activities** | | 6,912,144,024 | (1,713,687,227) |\n| **Net increase/(decrease) in cash and cash equivalents** | | (1,197,021,152) | (2,283,532,078) |\n| Opening cash and cash equivalents | | (1,968,368,348) | 287,985,204 |\n| Effect of movements in exchange rate on cash held | | 10,425,456 | 27,178,526 |\n| **Cash and cash equivalents at reporting date** | | (3,154,964,044) | (1,968,368,348) |\n\n### Closing balance represents\n\n| | For the year ended 30 June 2023 | For the year ended 30 June 2022 |\n|---|---|---|\n| Cash and cash equivalents | 5,272,771,904 | 3,208,757,234 |\n| Bank overdraft | (8,427,735,948) | (5,177,125,582) |\n| **Consolidated Net Operating Cash Flows Per Share (NOCFPS)** | 37.3(a) | 4.04 |'}}}



# files = ["aci1.png", "aci2.png", "aci3.png"]

# Function to display the DataFrame and allow editing
def display_editable_dataframe(data):
    if data:
        is_df = pd.DataFrame(data['is']['processed_response'])  # Assuming 'is' is the data of interest
        return is_df
    else:
        return None
    

def json_to_markdown_table(json_data):
    """
    Converts a JSON object with column names as keys to a Markdown table.
    
    Args:
        json_data (dict): A dictionary where keys are column names and values are lists of row values.

    Returns:
        str: A Markdown formatted table as a string.
    """
    # Extract column names and rows
    columns = list(json_data.keys())
    rows = zip(*[json_data[col] for col in columns])

    # Prepare the header row
    markdown = "| " + " | ".join(columns) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    
    # Prepare data rows
    for row in rows:
        row_values = [str(cell) if cell != '' else ' ' for cell in row]
        markdown += "| " + " | ".join(row_values) + " |\n"
    
    return markdown


st.title("Financial Data Table")

# Load session state data
if 'input' not in st.session_state:
    st.error("Input data not found")
else:
    input_data = st.session_state.input

if 'files' not in st.session_state:
    st.error("Files not found")
else:
    files = st.session_state.files

# Display image and DataFrame
col1, col2 = st.columns(2)

with col1:
    st.write("### Income Sheet")
    image = files[1]
    st.image(image, caption="Income Sheet", use_container_width=True)

with col2:
    is_df = display_editable_dataframe(input_data)

    if is_df is not None:
        st.write("### Edit Financial Data")

        # Check if the dataframe is already stored in session state
        if 'is_df' not in st.session_state:
            st.session_state.is_df = is_df
        else:
            is_df = st.session_state.is_df

        # Adding row position bar and "Add Row" button above the table
        row_col1, row_col2 = st.columns([1, 1])

        # Option to add a row
        with row_col1:
            if 'selected_index' not in st.session_state:
                st.session_state.selected_index = len(is_df)

            # Input box for index display (editable)
            selected_index = st.text_input(
                "Index to add row:", 
                value=str(st.session_state.selected_index)
            )

            # Update session state when the index is edited manually
            if selected_index.isdigit():
                st.session_state.selected_index = int(selected_index)

            # Add the row at the selected index when button is clicked
            if st.button("Add Row"):
                # Create an empty row with the same columns as the DataFrame
                empty_row = {col: '' for col in is_df.columns}
                new_row_df = pd.DataFrame([empty_row])

                # Split the DataFrame and insert the new row at the specified index
                top_part = is_df.iloc[:st.session_state.selected_index]
                bottom_part = is_df.iloc[st.session_state.selected_index:]

                edited_df = pd.concat([top_part, new_row_df, bottom_part], ignore_index=True)

                # Save changes to session state
                st.session_state.is_df = edited_df
                st.session_state.pls = edited_df.to_dict(orient='list')

                st.success(f"Empty row added successfully at index {st.session_state.selected_index}!")

            
        # Option to add a column
        with row_col2:
            column_name_input = st.text_input("Enter new column name:", "New Column")
            if st.button("Add Column"):
                # Use the input name for the new column
                new_column_name = column_name_input.strip() or f"New Column {len(is_df.columns) + 1}"
                
                # Create a new column with empty values for all rows
                is_df[new_column_name] = ''

                # Save changes to session state
                st.session_state.is_df = is_df
                st.session_state.pls = is_df.to_dict(orient='list')

                st.success(f"New column '{new_column_name}' added successfully!")

        

        # Option to delete a column
        column_to_delete = st.selectbox("Select a column to delete:", is_df.columns)

        if st.button("Delete Column"):
            # Delete the selected column
            if column_to_delete:
                is_df.drop(columns=[column_to_delete], inplace=True)
                st.session_state.is_df = is_df
                st.session_state.pls = is_df.to_dict(orient='list')

                st.success(f"Column '{column_to_delete}' deleted successfully!")

        # Reset index for display in the table
        edited_df_with_index = is_df.reset_index()  # Reset index so it's included as a column

        # Display editable DataFrame
        edited_df = st.data_editor(edited_df_with_index, use_container_width=True, height=800, num_rows="dynamic")

        # Track the clicked index and update selected_index in session state
        if edited_df is not None and 'selected_index' in st.session_state:
            # Capture index click event
            row_click = st.session_state.selected_index
            st.session_state.selected_index = row_click
            selected_index = row_click

        # Save changes
        if st.button("Save Changes"):
            edited_df_no_index = edited_df.drop(columns=['index'], errors='ignore')  # Drop 'index' column if present

            # Convert to JSON without the index
            edited_json = edited_df_no_index.to_dict(orient='list')
            md = json_to_markdown_table(edited_json)

            input_data['is']['raw_response']['natural_text'] = md
            st.session_state.is_df = edited_df
            st.session_state.pls = edited_json
            st.success("Changes saved successfully as JSON!")

            def transform_and_send(data: dict, database_url: str):
                # Transforming data
                transformed_data = {
                    "url": data['is']['pdf_url'],       
                    "prompt": data['is']['prompt'],     
                    "page_number": 1,                   
                    "response": json.dumps(data['is']['raw_response'])  # Serialize the raw response as a JSON string
                }

                # Log the transformed data to verify it's correct
                print(f"Sending transformed data: {json.dumps(transformed_data, indent=2)}")

                # Sending transformed data to the database URL
                try:
                    response = requests.post(database_url, json=transformed_data)
                    response.raise_for_status()
                    return {'status': 'success', 'response': response.json()}
                except requests.exceptions.RequestException as e:
                    return {'status': 'error', 'error': str(e)}

            # Example URL
            url = "http://192.168.10.50:8000/store_ocr_data"

            storedb = transform_and_send(input_data, url)
            print(f"THE DATABASE RESPONSE IS: {storedb}")

            # Step 1: Load the JSON file
            with open('json/variables.json', 'r') as file:
                data = json.load(file)

            # Step 2: Modify the value of a specific key
            data['income_id'] = storedb['response']['id']

            # Step 3: Save the modified data back to the JSON file
            with open('json/variables.json', 'w') as file:
                json.dump(data, file, indent=4)

            print("Key value updated successfully!")

        if st.button("Next"):
            st.switch_page("pages/cfs.py")
