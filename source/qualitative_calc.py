import os
import json
import streamlit as st
from home import QualitativeQuestions

qualitative_analysis= QualitativeQuestions()
# def read_from_file(filename):
#     with open(filename, "r") as file:
#         lines = file.read().splitlines()
#     return lines

# # Read the values from the text file
# selected_values = read_from_file("selected_values.txt")

# q=[]
# # Assign the values to variables
# q = selected_values

if 'qq' in st.session_state:
    q = st.session_state.qq

# print(q)


class Qualitative_Analysis: 
    v=[]
    sum=0

    file_path= os.getenv('JSON_PATH')

    with open(file_path, 'r') as file:
        Q = json.load(file)

    for i in range(len(Q["Q"])):
        v.append(Q["Q"][i][q[i]])
        sum= sum+ v[i]