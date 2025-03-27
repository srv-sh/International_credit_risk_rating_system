import streamlit as st
import pandas as pd

# Sample data (original table content)
data = {
    "Key": ["Total assets", "Total liabilities", "Equity"],
    "Particulars": ["assets", "property, plant and equipment", "right-of-use assets"]
}

df = pd.DataFrame(data)

# Dropdown options
options = [
    "assets",
    "property, plant and equipment",
    "right-of-use assets",
    "equity",
    "intangible assets"
]

# Display the table and dropdowns
st.title("Interactive Table with Dropdowns in Each Cell")

# Create empty list to store updated values
updated_particulars = []

for index, row in df.iterrows():
    # Displaying the key (column 1)
    st.write(f"### Row {index + 1}: {row['Key']}")

    # Creating the dropdown for 'Particulars' column for each row
    selected_particular = st.selectbox(
        f"Select Particular for {row['Key']}",
        options=options,
        index=options.index(row['Particulars']),  # Setting the current value as the default option
        key=f"dropdown_{index}"  # Use a unique key for each dropdown
    )
    
    # Add the selected particular to the updated list
    updated_particulars.append(selected_particular)

# After all rows are updated, display the updated table
st.write("### Updated Table with Selected Particulars")
updated_df = df.copy()
updated_df['Particulars'] = updated_particulars
st.dataframe(updated_df)
