import json
import re
import streamlit as st
import requests
from source.conversion import ReadJSON, GetOutput, MarkDown
from source.config import AgentCall, InputList
from source.calculation import FinancialCalculator
# from Responses import main

class Main:

    def hit_fastapi(self, files):
        url = "http://192.168.10.50:8000/uploadfiles"

        if files:
            # Prepare the files for the API request
            files_to_upload = [
                ('files', files[0]),  # Balance sheet image
                ('files', files[1]),  # Cash flow sheet image
                ('files', files[2])   # Profit and loss sheet image
            ]

            try:
                # Send a POST request to the FastAPI endpoint with the uploaded files
                response = requests.post(url, files=files_to_upload)
                response.raise_for_status()  # Raise error for HTTP codes 4xx/5xx

                # print("Response JSON:")
                # print(response.json())
                return response.json()  # Return the JSON response directly

            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                st.error(f"Request failed: {e}")
                return None  # Return None if the request fails
        else:
            st.error("No files to upload.")
            return None
        

    def store_llm_data(self, database_url, markdown, results):

        sheet = InputList()

        with open('json/variables.json', 'r') as file:
            data = json.load(file)

        # Convert all required fields to strings
        transformed_data = {
            "system_prompt": str(data['system_prompt']),
            "required_params": str(sheet.item),
            "list_of_params": str(markdown),
            "response": str(results),  # Directly convert results to string
            "bs_id": data['balance_id'],
            "is_id": data['income_id'],
            "cfs_id": data['cash_id']
        }

        # Log the transformed data to verify it's correct
        print(f"Sending transformed data: {transformed_data}")

        # Sending transformed data to the database URL
        try:
            response = requests.post(database_url, json=transformed_data)
            response.raise_for_status()
            return {'status': 'success', 'response': response.json()}
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'error': str(e)}


        



    def intermediate_values(self, input_data):
        results = None  # Initialize results with a default value
        if not input_data:
            print("No valid input data provided.")
            return results

        # Assuming `input_data` is now a dictionary, not a file path
        json_reader = ReadJSON(input_data)  # Pass the JSON data directly

        # Get the required data from the JSON
        json_data = json_reader.get_table()

        md = MarkDown()

        if json_data:  # Check if json_data was found
            # Generate markdown from JSON data
            self.markdown_output = md.generate_markdown(json_data)
            # if "markdown" not in st.session_state:
            #     st.session_state.markdown = markdown_output

            print(self.markdown_output)

            # Create an instance of AgentCall with the markdown output
            # agent_prompt = AgentCall(markdown_output)

            # Initialize InputList to get the list of financial items
            sheet = InputList()
            # sheets = sheet.return_input()  # Get the list of financial items
            # print(sheets)

            # Initialize GetOutput with the agent and markdown table
            # get_output = GetOutput(markdown_output)

            agent = AgentCall(self.markdown_output)

            # Get and print results
            results = agent.generate_response(sheet.item)
            print(results)

        else:
            print("JSON data not found.")

        url = "http://192.168.10.50:8000/store_llm_data"
        storedb = self.store_llm_data(url, self.markdown_output, results)

        print(f"THE DATABASE RESPONSE IS: {storedb}")

        # Step 1: Load the JSON file
        with open('json/variables.json', 'r') as file:
            data = json.load(file)

        # Step 2: Modify the value of a specific key
        data['llm_id'] = storedb['response']['id']

        # Step 3: Save the modified data back to the JSON file
        with open('json/variables.json', 'w') as file:
            json.dump(data, file, indent=4)

        print("Key value updated successfully!")

        return results





    def intermediate_result(self, input_data, intermediate_extract):
        # input_data['particulars'] = input_data['particulars'].fillna('')

        print("intermediate_extract:", intermediate_extract)

        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)  # Convert string to JSON
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format received for input_data")

        if isinstance(input_data, list):
            if not input_data:
                raise ValueError("Empty input_data list received")
            if not isinstance(input_data[0], dict):
                raise TypeError("Expected a dictionary inside input_data list")
            input_data = input_data[0]  # Extract the first item

        if not isinstance(input_data, dict):
            raise TypeError("Expected input_data to be a dictionary after processing")

        if isinstance(intermediate_extract, str):
            try:
                intermediate_extract = json.loads(intermediate_extract)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format received for intermediate_extract")

        print("Keys in input_data:", list(input_data.keys()))

        year_key = next((key for key in input_data if re.search(r'2023', str(key))), None)

        if not year_key:
            print("Available keys:", list(input_data.keys()))
            raise ValueError("Year 2023 not found in response JSON")

        if 'particulars' not in input_data:
            raise KeyError("'particulars' key missing in input_data")

        particulars = [str(p).lower().strip() for p in input_data['particulars'] if isinstance(p, str)]

        values_2023 = {}
        for key, terms in intermediate_extract.items():
            if terms is None:
                values_2023[key] = 0
                continue

            matched_values = []
            for term in terms:
                if term is None:
                    continue
                term = term.strip().lower()  # Normalize term
                if term in particulars:
                    index = particulars.index(term)
                    value = input_data[year_key][index]
                    if isinstance(value, (int, float)) or str(value).replace("-", "").isdigit():
                        matched_values.append(float(value))

            values_2023[key] = sum(matched_values) if matched_values else 0

        print("values_2023 -------------------------------------")
        print(values_2023)

        return values_2023






    def final_output(self, input_file):
        if not input_file:
            print("No valid input data provided.")
            return None

        data = input_file

        calc = FinancialCalculator(data)

        if data:  
            output_data = []
            output = []

            try:
                dtn = calc.dtn_calc()
                if dtn is not None:
                    output_data.append({"item": "dtn", "value": dtn})
                    output.append(dtn)

                dta = calc.dta_calc()
                if dta is not None:
                    output_data.append({"item": "dta", "value": dta})
                    output.append(dta)

                current_ratio = calc.current_ratio_calc()
                if current_ratio is not None:
                    output_data.append({"item": "current_ratio", "value": current_ratio})
                    output.append(current_ratio)

                cash_ratio = calc.cash_ratio_calc()
                if cash_ratio is not None:
                    output_data.append({"item": "cash_ratio", "value": cash_ratio})
                    output.append(cash_ratio)

                npm = calc.npm_calc()
                if npm is not None:
                    output_data.append({"item": "npm", "value": npm})
                    output.append(npm)

                roa = calc.roa_calc()
                if roa is not None:
                    output_data.append({"item": "roa", "value": roa})
                    output.append(roa)

                opoa = calc.opoa_calc()
                if opoa is not None:
                    output_data.append({"item": "opoa", "value": opoa})
                    output.append(opoa)

                ic = calc.ic_calc()
                if ic is not None:
                    output_data.append({"item": "ic", "value": ic})
                    output.append(ic)

                dscr = calc.dscr_calc()
                if dscr is not None:
                    output_data.append({"item": "dscr", "value": dscr})
                    output.append(dscr)

                cdr = calc.cdr_calc()
                if cdr is not None:
                    output_data.append({"item": "cdr", "value": cdr})
                    output.append(cdr)

                ccr = calc.ccr_calc()
                if ccr is not None:
                    output_data.append({"item": "ccr", "value": ccr})
                    output.append(ccr)

                std = calc.std_calc()
                if std is not None:
                    output_data.append({"item": "std", "value": std})
                    output.append(std)

                tdcd = calc.tdcd_calc()
                if tdcd is not None:
                    output_data.append({"item": "tdcd", "value": tdcd})
                    output.append(tdcd)

                at = calc.at_calc()
                if at is not None:
                    output_data.append({"item": "at", "value": at})
                    output.append(at)

                cfs = calc.cfs_calc()
                if cfs is not None:
                    output_data.append({"item": "cfs", "value": cfs})
                    output.append(cfs)

                car = calc.car_calc()
                if car is not None:
                    output_data.append({"item": "car", "value": car})
                    output.append(car)

            except Exception as e:
                print(f"Error in calculations: {e}")

            # # Save the data to output.json
            # with open("output.json", "w") as outfile:
            #     json.dump(output_data, outfile, indent=4)

            # print("Data has been saved to output.json.")

        else:
            print("No data to process.")

        return output_data, output
    





