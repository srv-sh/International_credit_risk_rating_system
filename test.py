import streamlit as st
import pandas as pd

# Your data (replace with actual data)
data = {
    "bs": {
        "particulars": ["Assets", "Property, plant and equipment", "Right-of-use assets", "Equity-accounted investees", "Other investments"],
        "2023": [31715817451, 3082581839, 2058056899, 1027172247, 1409150269],
        "2022": [29154498292, 1720125531, 2157943932, 822290382, 1367550235],
    }
}

# Convert the data into a DataFrame
df = pd.DataFrame(data['bs'])

# Display the dataframe in Streamlit (editable)
st.write("Editable DataFrame")

# Display Editable Dataframe (Without Category Scale)
edited_df = st.data_editor(df, use_container_width=True)

# To make it editable, we can use st.text_input for each value (this could be a manual process)
# Here's a simple example to edit a specific row and column (e.g., 2023 and "Property, plant and equipment")
edit_row = st.selectbox('Select a Row', df['particulars'].values)
edit_col = st.selectbox('Select a Year', ['2023', '2022'])

# Get the current value to edit
current_value = df.loc[df['particulars'] == edit_row, edit_col].values[0]
new_value = st.number_input(f"Edit {edit_row} for {edit_col}", value=current_value)

# Update the dataframe with the new value
df.loc[df['particulars'] == edit_row, edit_col] = new_value

# Display the updated dataframe
st.write("Updated DataFrame")
st.write(df)

# To save the edited DataFrame to a file, you can use:
if st.button('Save Changes'):
    df.to_csv('edited_data.csv', index=False)
    st.success('Changes saved to "edited_data.csv"')
