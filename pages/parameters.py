import streamlit as st
import json
import pandas as pd
# from streamlit_extras.switch_page_button import switch_page

# Load JSON Data
json_file = "json/indicators.json"  # Replace with your actual JSON file
with open(json_file, "r") as file:
    data = json.load(file)

# Function to Convert JSON into a Table Format
def json_to_dataframe(data):
    table_data = []
    for category, category_data in data["Quantitative Indicators (60)"].items():
        for indicator, indicator_data in category_data["Indicators"].items():
            indicator_scale = indicator_data["Scale"]
            excellent = indicator_data["Scoring"]["Excellent"]
            good = indicator_data["Scoring"]["Good"]
            marginal = indicator_data["Scoring"]["Marginal"]
            unacceptable = indicator_data["Scoring"]["Unacceptable"]
            table_data.append([category, indicator, indicator_scale, excellent, good, marginal, unacceptable])

    df = pd.DataFrame(table_data, columns=["Category", "Indicator", "Indicator Scale", "Excellent", "Good", "Marginal", "Unacceptable"])
    return df

# Convert JSON to DataFrame
df = json_to_dataframe(data)

# Streamlit App
st.title("Quantitative Indicators Table")

# Display Editable Dataframe (Without Category Scale)
edited_df = st.data_editor(df, use_container_width=True)

# Function to Save Updated Data Back to JSON
def dataframe_to_json(df, original_data):
    updated_data = {"Quantitative Indicators (60)": {}}
    for _, row in df.iterrows():
        category = row["Category"]
        if category not in updated_data["Quantitative Indicators (60)"]:
            updated_data["Quantitative Indicators (60)"][category] = {
                "Indicators": {}
            }
        updated_data["Quantitative Indicators (60)"][category]["Indicators"][row["Indicator"]] = {
            "Scale": row["Indicator Scale"],
            "Scoring": {
                "Excellent": row["Excellent"],
                "Good": row["Good"],
                "Marginal": row["Marginal"],
                "Unacceptable": row["Unacceptable"]
            }
        }
    return updated_data

# Save Button to Update JSON
if st.button("Save Changes"):
    updated_json = dataframe_to_json(edited_df, data)
    with open(json_file, "w") as file:
        json.dump(updated_json, file, indent=4)
    st.success("Changes saved successfully!")

    # Switch to graph.py after saving
    st.switch_page("pages/graph.py")  # Navigate to the graph.py page

# # Button to Navigate Back to Home
# if st.button("Go to Home Page"):
#     st.switch_page("home.py")  # Ensure you have a `home.py` for navigation
