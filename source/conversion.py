import json
import re
from source.config import AgentCall

import json

class ReadJSON:
    def __init__(self, json_input):
        if isinstance(json_input, dict):
            self.json_data = json_input  # If input is already a dictionary
        elif isinstance(json_input, list) and len(json_input) > 0:
            self.json_data = json_input[0]  # Use the first element if it's a list
        elif isinstance(json_input, str):  # If input is a string, attempt to load it as a file
            try:
                with open(json_input, "r", encoding="utf-8") as json_file:
                    self.json_data = json.load(json_file)
            except FileNotFoundError:
                print(f"File not found: {json_input}")
                self.json_data = None
            except json.JSONDecodeError:
                print(f"Invalid JSON format in file: {json_input}")
                self.json_data = None
            except Exception as e:
                print(f"Error reading file {json_input}: {e}")
                self.json_data = None
        else:
            print("Invalid input provided. Expected a dictionary, list, or file path.")
            self.json_data = None

    def get_table(self):
        if self.json_data is not None:
            return self.json_data
        else:
            print("No valid JSON data.")
            return None




class MarkDown:
    def generate_markdown(self, data):
        pattern = re.compile(r'2023')
        markdown = "| Particulars | 2023 |\n"
        markdown += "|-------------|------|\n"
        
        if data:
            particulars = data.get(list(data.keys())[0], [])
            values = []
            for key in data.keys():
                if pattern.search(key):
                    values = data[key]
                    break

            if len(particulars) == len(values):
                for i in range(len(particulars)):
                    particular = particulars[i]
                    value = values[i]
                    value = " " if value == "nan" else value
                    markdown += f"| {particular} | {value} |\n"
            else:
                print("Error: Mismatched lengths of particulars and values.")
        
        return markdown


class GetOutput:
    def __init__(self, markdown_table):
        self.markdown_table = markdown_table
        print(self.markdown_table)
        self.agent_prompt = AgentCall(markdown_table)


    # def get_financial_data_value(self, items):
    #     try:
    #         # Join the list of items into a comma-separated string
    #         items_str = ", ".join(items)

    #         # Format the input for the agent call with the markdown output and the combined list of items
    #         input_text = self.prompt.format(markdown_output=self.markdown_output, item_list=items_str)

    #         # Call the agent with the formatted input text
    #         output = self.llm.invoke(input_text)
    #         print("Agent Output:", output)

    #         # Parse the output assuming it's a JSON string or JSON-like structure
    #         try:
    #             outputs = json.loads(output)
    #         except json.JSONDecodeError:
    #             print(f"Error decoding JSON from output: {output}")
    #             outputs = []

    #         # Map each item to its corresponding value
    #         results = []
    #         for item in items:
    #             matched_item = next((entry for entry in outputs if entry['item'] == item), None)
    #             if matched_item:
    #                 results.append({"item": item, "value": matched_item['value']})
    #             else:
    #                 results.append({"item": item, "value": None})
    #         return results

    #     except Exception as e:
    #         print(f"Error processing items: {e}")
    #         return [{"item": item, "value": f"Error: {e}"} for item in items]



