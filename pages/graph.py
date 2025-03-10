
# graph.py
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_extras.switch_page_button import switch_page

# This must be the first Streamlit command in your script
# st.set_page_config(page_title="Graph Page", layout="wide")

from source.main_function import Main
# from source.qualitative_calc import Qualitative_Analysis
from source.file import graphPage as gp
from source.score_calc import ScoreCalculator

st.title("Graph")
st.write("Welcome to Graph Page")


#Quantitative Analysis
# Instantiate Quantitative_Analysis class

class QuantitativeFigure:

    def __init__(self, json_data, scores, label):
        # Initialize variables with default values
        self.dtn = self.dta = self.current_ratio = self.cash_ratio = self.npm = self.roa = 0.0
        self.opoa = self.ic = self.dscr = self.cdr = self.ccr = self.std = 0.0
        self.tdcd = self.at = self.cfs = self.car = 0.0

        self.label = label
        
        # Parse JSON data
        self.parse_json(json_data)
        
        # Perform calculations
        self.calculate_indicators()

        #score calc
        self.calculate_scores(scores)
        
        # Prepare the graph
        self.prepare_graph()

    def parse_json(self, json_data):
        for item in json_data:
            if item["item"] == "dtn":
                self.dtn = float(item["value"])
            elif item["item"] == "dta":
                self.dta = float(item["value"])
            elif item["item"] == "current_ratio":
                self.current_ratio = float(item["value"])
            elif item["item"] == "cash_ratio":
                self.cash_ratio = float(item["value"])
            elif item["item"] == "npm":
                self.npm = float(item["value"])
            elif item["item"] == "roa":
                self.roa = float(item["value"])
            elif item["item"] == "opoa":
                self.opoa = float(item["value"])
            elif item["item"] == "ic":
                self.ic = float(item["value"])
            elif item["item"] == "dscr":
                self.dscr = float(item["value"])
            elif item["item"] == "cdr":
                self.cdr = float(item["value"])
            elif item["item"] == "ccr":
                self.ccr = float(item["value"])
            elif item["item"] == "std":
                self.std = float(item["value"])
            elif item["item"] == "tdcd":
                self.tdcd = float(item["value"])
            elif item["item"] == "at":
                self.at = float(item["value"])
            elif item["item"] == "cfs":
                self.cfs = float(item["value"])
            elif item["item"] == "car":
                self.car = float(item["value"])

    def calculate_indicators(self):
        # Aggregate the values for different categories
        self.lev = self.dtn + self.dta
        self.liq = self.current_ratio + self.cash_ratio
        self.prof = self.npm + self.roa + self.opoa
        self.cov = self.ic + self.dscr + self.cdr + self.ccr
        self.op = self.std + self.tdcd + self.at
        self.ear = self.car + self.cfs
        
        # Sum of all categories
        self.total_indicators = self.lev + self.liq + self.prof + self.cov + self.op + self.ear



    def calculate_scores(self, scores):
        self.dtn_score = scores['dtn_score']
        self.dta_score = scores['dta_score']
        self.current_ratio_score = scores['current_ratio_score']
        self.cash_ratio_score = scores['cash_ratio_score']
        self.npm_score = scores['npm_score']
        self.roa_score = scores['roa_score']
        self.opoa_score = scores['opoa_score']
        self.ic_score = scores['ic_score']
        self.dscr_score = scores['dscr_score']
        self.cdr_score = scores['cdr_score']
        self.ccr_score = scores['ccr_score']
        self.std_score = scores['std_score']
        self.tdcd_score = scores['tdcd_score']
        self.at_score = scores['at_score']
        self.cfs_score = scores['cfs_score']
        self.car_score = scores['car_score']

        self.lev_score = self.dtn_score + self.dta_score
        self.liq_score = self.current_ratio_score + self.cash_ratio_score
        self.prof_score = self.npm_score + self.roa_score + self.opoa_score
        self.cov_score = self.ic_score + self.dscr_score + self.cdr_score + self.ccr_score
        self.op_score = self.std_score + self.tdcd_score + self.at_score
        self.ear_score = self.car_score + self.cfs_score

        self.total_score = self.lev_score + self.liq_score + self.prof_score + self.cov_score + self.op_score + self.ear_score



    def Percentage(self, part, whole):
        Percentage = 100 * float(part)/float(whole)
        Percentage = f"{Percentage:.1f}"
        return str(Percentage) + "%"


    def prepare_graph(self):
        # Define percentage for the pie chart
        percentage = (self.total_score/60)*100

        # Define criteria, scales, and actual parameters for the tables
        criteria = gp.criteria
        scales = gp.scales
        Parameter = gp.Parameter
        values = gp.values
        remark = gp.remarks

        # Placeholder values for actual parameters (replace with your actual data)
        actual_parameters = [
            self.lev, self.dtn, self.dta,
            self.liq, self.current_ratio, self.cash_ratio,
            self.prof, self.npm, self.roa, self.opoa,
            self.cov, self.ic, self.dscr, self.cdr, self.ccr,
            self.op, self.std, self.tdcd, self.at,
            self.ear, self.cfs, self.car,
            self.total_indicators, 0
        ]

        obtained_scores = [
            self.lev_score, self.dtn_score, self.dta_score,
            self.liq_score, self.current_ratio_score, self.cash_ratio_score,
            self.prof_score, self.npm_score, self.roa_score, self.opoa_score,
            self.cov_score, self.ic_score, self.dscr_score, self.cdr_score, self.ccr_score,
            self.op_score, self.std_score, self.tdcd_score, self.at_score,
            self.ear_score, self.cfs_score, self.car_score,
            self.total_score, f"{percentage:.1f}"
        ]

        if percentage >= 80:
            label.append("Excellent")
        elif 70 <= percentage < 80:
            label.append("Good")
        elif 60 <= percentage < 70:
            label.append("Marginal")
        else:
            label.append("Unacceptable")


        param_percent = []

        for i in range(len(scales)):
            param_percent.append(self.Percentage(obtained_scores[i], scales[i]))

        # Determine which rows to color 
        colors = ['#D5C0F2' if crit in gp.color_rows else '#FBF2FC' for crit in criteria]

        label_colors = [
            '#50d967' if labels == "Excellent" else
            "#db2e2e" if labels == "Unacceptable" else
            "#e8a62c" if labels == "Marginal" else
            '#2ca0e8' if labels == "Good" else
            '#FBF2FC'  # Add a default color if the label doesn't match any of the conditions
            for labels in self.label
        ]

        # Create subplots with two rows and two columns
        self.fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"type": "domain"}, {"type": "scatter"}],
                   [{"type": "table", "colspan": 2}, None]],
            subplot_titles=("Score Percentage", "Analysis Table")
        )

        # Add first pie chart to the first subplot
        # st.markdown("### The Percentage of Quantitative Indicators")
        self.fig.add_trace(
            go.Pie(labels=['Percentage', 'Remaining'],
                   values=[percentage, 100 - percentage],
                   marker=dict(colors=['#F1421C', '#540A9A']),
                   hole=0.7),
            row=1, col=1
        )

        # st.markdown("### Quantitative Indicators Weight Distribution")
        # Add scatter plot to the second subplot
        self.fig.add_trace(
            go.Bar(x=Parameter, y=values, marker=dict(color='#0BB0A3'), name='Bar Plot'),
            row=1, col=2
        )

        # st.markdown("## Details of Credit-worthiness through Quantitative Indicators")
        # Add table to the third subplot
        self.fig.add_trace(
            go.Table(
                header=dict(values=['Criteria', 'Scale', 'Actual Parameter', 'Obtained Score', 'Percentage', 'Status', 'Remarks'],
                            line_color='black',
                            fill_color='#E580BB',
                            font=dict(color='black'),
                            align='left',
                            font_size=16,
                            height=25),
                cells=dict(values=[criteria, scales, actual_parameters, obtained_scores, param_percent, self.label, remark],
                           line_color='darkslategray',
                           fill_color=[colors, colors, colors, colors, colors, label_colors, colors],
                           align='left',
                           font_size=14,
                           height=25)
            ),
            row=2, col=1
        )

        # Update layout
        self.fig.update_layout(width=1600, height=1000,
                                annotations=[
                                    (dict(text=f"{percentage:.1f}", x=0.24, y=0.78, font_size=48, showarrow=False, xref="paper", yref="paper", align="center")),
                                    (dict(text=str(self.total_score) + '/60', x=0.8, y=0.78, font_size=48, showarrow=False, xref="paper", yref="paper", align="center"))
                                ])
        
        


        

# Load the JSON data
main_program = Main()
# with open('output.json', 'r') as file:
#     data = json.load(file)

if 'output' in st.session_state:
    data = st.session_state.output

else:
    print("Output data not found")


if 'input' in st.session_state:
    input_data = st.session_state.input

else:
    print("Input data not found")


ob_score = ScoreCalculator(data)

score, label = ob_score.calculate_scores()

print(score)



# class Qualitative_figure:
    #Qualitative Analysis

    # obj2 = Qualitative_Analysis()

    # v=[]
    # PB=BIR=MR=SR=RR=CR= 0

    # for i in range(len(obj2.v)):
    #     v.append(obj2.v[i])

    #     if i<3:
    #         PB = PB+ v[i]
    #     elif i>=3 and i<7:
    #         BIR= BIR+ v[i]
    #     elif i>=7 and i<11:
    #         MR= MR+ v[i]
    #     elif i>=11 and i<15:
    #         SR= SR+ v[i]
    #     elif i==15:
    #         RR= v[i]
    #     else:
    #         CR= CR+ v[i]

    # sum = obj2.sum
    # q_score= round((sum/40)*100,2)

    # # # Call the function to load values into q
    # # q = obj3.save_values()
    # # print(q)

    #     # Access the qq value from session state
    # if 'qq' in st.session_state:
    #     q = st.session_state.qq

    # print(q)

    # # Ensure that q has enough elements before accessing them
    # if len(q) < 18:  # Check if there are enough values in q
    #     print(f"Error: Not enough values in q. Only {len(q)} values were loaded.")
    # else:
    #     # Proceed with your code that accesses q[0], q[1], ..., q[17]
    #     actual_parameters2 = ['', '', q[0], '', '', '', '', '', q[1], '', '', '', '', '', 
    #                           q[2], '', '', '', q[3], '', '', '', '', '', q[4], '', '', '', '', '',
    #                           q[5], '','','', '', q[6], '', '', '','','', q[7], '', '', '','','', q[8], '', '', '', '',
    #                           q[9], '', '', '', q[10], '', '','', q[11], '', '', '', '',q[12], '', '', '', '',
    #                           q[13], '', '', '','','', q[14], '', '', '', '', '', q[15], '', '', '', '','',q[16], 
    #                           '', '', q[17], '', '', '','']


    # # Now, q contains the values from selected_values.txt, so you can use it in your logic
    # Parameter2 = gp.Parameter2
    # values2 = [40, PB, BIR, MR, SR, RR, CR]
    # criteria2 = gp.criteria2
    # param = gp.param
    # score = gp.score

    # obtained = [
    #     PB, '', v[0], '', '', '', '', '', v[1], '', '', '', '', '', v[2], '', '', BIR, v[3], '', '', '', '', '', v[4], '', '', '', 
    #     '', '', v[5], '', '', '', '', v[6], '', '', '', '', '', MR, v[7], '', '', '', '', v[8], '', '', '', '', v[9], '', '', '', 
    #     v[10], '', '', SR, v[11], '', '', '', '', v[12], '', '', '', '', v[13], '', '', '', '', '', v[14], '', '', '', '', '', RR, 
    #     v[15], '', '', '', CR, v[16], '', '', v[17], '', '', sum, q_score
    # ]

    # colors = ['#D5C0F2' if crit in gp.Parameter2 else '#FBF2FC' for crit in criteria2]

    # # Create subplots with two rows and two columns
    # fig2 = make_subplots(
    #     rows=2, cols=2,
    #     specs=[[{"type": "domain"}, {"type": "scatter"}],
    #         [{"type": "table", "colspan": 2}, None]],
    #     subplot_titles=("Score Percentage", "Analysis Table")
    # )

    # # Add first pie chart to the first subplot
    # fig2.add_trace(
    #     go.Pie(labels=['Percentage', 'Remaining'],
    #         values=[q_score, 100 - q_score],
    #         marker=dict(colors=['#F1421C', '#540A9A']),
    #         hole=0.8),
    #     row=1, col=1
    # )

    # # Add scatter plot to the second subplot
    # fig2.add_trace(
    #     go.Bar(x=Parameter2, y=values2, marker=dict(color='#0BB0A3'), name='Bar Plot'),
    #     row=1, col=2
    # )

    # # Add table to the third subplot
    # fig2.add_trace(
    #     go.Table(
    #         header=dict(values=['Criteria', 'Parameter', 'Score', 'Actual Parameter', 'Score Obtained'],
    #                     line_color='black',
    #                     fill_color='#E580BB',
    #                     font=dict(color='white'),
    #                     align='left',
    #                     font_size=14,
    #                     height=25,
    #                     ),
    #         cells=dict(values=[criteria2, param, score, actual_parameters2, obtained],
    #                 line_color='black',
    #                 fill_color=[colors, colors, colors],
    #                 align='left',
    #                 font_size=11,
    #                 height=25
    #                 )
    #     ),
    #     row=2, col=1
    # )

    # sumS= str(sum)
    # # Update layout
    # fig2.update_layout(width=1600, height=1000,
    #                 #   annotations=[dict(text='17%', y=0.78, font_size=48, showarrow=False)]
    #                 annotations=[
    #                     (dict(text=q_score, x=0.24, y=0.78, font_size=48, showarrow=False, xref="paper", yref="paper", align="center")),
    #                     (dict(text=sumS+'/40', x=0.8, y=0.78, font_size=48, showarrow=False, xref="paper", yref="paper", align="center"))
    #                 ])


# Create instances of the classes
# f1 = QuantitativeFigure(data)  # Pass the required JSON data to the constructor
# f2 = Qualitative_figure  # This doesn't seem to need an instance

# def drawFigure():
#     # Center the elements using Streamlit columns
#     col1, col2 = st.columns(2)

#     with col1:
#         st.title("Quantitative Analysis")
#         st.plotly_chart(f1.fig, use_container_width=True)

#     with col2:
#         st.title("Qualitative Analysis")
#         st.plotly_chart(f2.fig2, use_container_width=True)

# drawFigure()


f1 = QuantitativeFigure(data, score, label)  # Pass the required JSON data to the constructor
# f2 = Qualitative_figure  # This doesn't seem to need an instance

def drawFigure():
    # Display Quantitative Analysis first
    st.title("Quantitative Analysis")
    st.plotly_chart(f1.fig, use_container_width=True)

    # # Convert to DataFrame
    # df = pd.DataFrame(input_data)

    # # Display DataFrame in Streamlit
    # st.markdown("## Extracted Financial Data")
    # st.write(df)

    # # Display Qualitative Analysis below
    # st.title("Qualitative Analysis")
    # st.plotly_chart(f2.fig2, use_container_width=True)

drawFigure()

