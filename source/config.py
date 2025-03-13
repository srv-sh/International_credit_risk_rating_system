import os
import re
import requests
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
# from langchain_ollama import ChatOllama


class AgentCall:
    def __init__(self, markdown_output):
        # Initialize the OpenAI LLM
        self.llm = ChatOpenAI(
            openai_api_base=os.environ.get("OPENAI_API_BASE_URL"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            model_name=os.environ.get("MODEL_NAME"),
            temperature=0.3
        )

        # self.llm = ChatOllama(
        #     model="llama3.3",
        #     temperature=1
        # )


        self.markdown_output = markdown_output

        # # Adjust the prompt template to match the expected output format
        # self.prompt_template = """
        #     Given this markdown table of financial particulars:

        #     {markdown_output},

        #     For each of the following items, try to match the terms exactly or with clear synonyms.
        #     If found or synonymous, return the result in JSON format as a dictionary like:

        #     {{
        #         "total assets": ["total assets"],
        #         "total liabilities": ["total liabilities"],
        #         ...
        #     }}

        #     If the items can be calculated with more than one terms in the table, give a list of those terms. 
        #     If the item could not be matched, return the value as null.

        #     Here's an example:
        #     {{
        #         "total assets": ["total assets"],
        #         "net profit after tax": ["profit/(loss) after tax"],
        #         "capital work in progress": [],
        #         ...
        #     }}

        #     If a term does not have a numeric value in the markdown table, try not to include that term in the output even if it matches.

        #     Here's an example:
        #     {{
        #         "total liabilities": ["total current liabilities", "total non-current liabilities"],
        #     }}

        #     NOTE: No numeric values are needed in the output.
        #     NOTE: The output should be a single JSON object.
        #     NOTE: output json key would be {item}
        #     NOTE: Do not hallucinate and come up with json key excludeing in item 
        #     NOTE: Just give the json, no extra sentences or anything else should be there. 
        # """

        # Adjust the prompt template to match the expected output format
        self.prompt_template = """
            You are provided with a markdown table of financial particulars:

            {markdown_output}

            Instructions:
            - For each item listed below, find exact matches or clear synonyms in the table. 
            - Return the results as a JSON object where each key is the item and the value is:
            - A list of matching terms if found. 
            - Null if no matching term or its synonyms are found with a value.
            - A list of terms if the item requires multiple terms for calculation.
            - If an exact match is found but has no value, and a synonym with a value exists, prioritize the synonym instead.
            - Exclude items without numeric values even if they match.
            - If a term partially matches another term (e.g., "equity and liabilities" for "liabilities"), do not consider it a valid match unless it is a direct synonym.
            - Terms should only be matched if they clearly represent the item. Avoid partial matches where the meaning is altered.

            Example Scenario:
            Suppose the markdown table is:

            | Term                                  | Value       |
            |------------------------------------- |-------------|
            | total assets                         | 5000000      |
            | cash flows from operating activities|              |
            | cash generated from operating activities | 100000     |
            | total current liabilities            | 3000000      |
            | total non-current liabilities        | 2000000      |
            | profit/(loss) after tax              | 150000       |
            | capital work in progress             |              |
            | total equity and liabilities         | 8000000      |

            And the items to match are:
            - total assets  
            - net profit after tax  
            - capital work in progress  
            - cash flows from operating activities  
            - total liabilities  

            The expected output should be:

            {{
                "total assets": ["total assets"],
                "net profit after tax": ["profit/(loss) after tax"],
                "capital work in progress": null,
                "cash flows from operating activities": ["cash generated from operating activities"],
                "total liabilities": ["total current liabilities", "total non-current liabilities"],
            }}

            The bad output would be:
            {{
                ...
                "cash flows from operating activities": ["cash flows from operating activities"],
                ...
            }}


            Rules:
            - The output must be a single JSON object.
            - The JSON keys must match the provided items exactly. 
            - Apply the prioritization rule consistently for all items.
            - If a synonym with a value is found while the original term is empty, include the synonym in the output.
            - Do not hallucinate or include irrelevant keys.
            - Provide only the JSON output, NO ADDITIONAL TEXT
            - There should not be anything in the output other than just the json.

            Items to match: {item}
        """

        # Open the JSON file for reading
        with open('json/variables.json', 'r') as json_file:
            data = json.load(json_file)

        # Clean the system_prompt by removing extra spaces, newlines, and escaping quotes
        cleaned_prompt = ' '.join(data.get("system_prompt", "").split())  # Removes extra spaces and newlines
        cleaned_prompt = cleaned_prompt.replace('"', '\\"')  # Escape double quotes

        # Remove any unwanted brackets (both first and second sets)
        cleaned_prompt = cleaned_prompt.replace("{", "").replace("}", "")  # Remove curly braces

        # Update the system_prompt in the loaded data with the cleaned prompt
        data["system_prompt"] = cleaned_prompt

        # Save the updated JSON back to the file
        with open('json/variables.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)


        # Create the prompt template with proper input variables
        self.prompt = PromptTemplate(
            input_variables=["markdown_output"],
            template=self.prompt_template
        )

        # Define the chain that will process the prompt and invoke the model
        self.chain = self.prompt | self.llm


    def extract_content(self, ai_message):
        print("DEBUG: ai_message =", ai_message)

        if isinstance(ai_message, str):
            # Use regex to extract the first valid JSON object
            match = re.search(r'\{.*?\}', ai_message, re.DOTALL)
            if match:
                json_str = match.group()
                try:
                    return json.loads(json_str)  # Convert to dictionary
                except json.JSONDecodeError:
                    return json_str  # If JSON decoding fails, return the raw string

        return ""



    def generate_response(self, items):
        # Prepare the input mapping (dictionary) for the prompt
        formatted_prompt = {
            "markdown_output": self.markdown_output,
            "item": items
        }

        try:
            # Send the formatted prompt to the LLM for response
            response = self.chain.invoke(formatted_prompt)
              # Print raw response to understand its structure
            print("DEBUG: Raw response =", response)
            print("DEBUG: Type of response =", type(response))

            
            content = response.content

            # content = self.extract_content(content)

            print("DEBUG: Extracted content =", content)
            # # Parse the response if needed
            # response_dict = json.loads(response.content)
            # print(response_dict)
            
            
            # return response_dict
            return content
        except Exception as e:
            return f"Error generating response: {e}"


class InputList:
    def __init__(self):
        self.item = [
            'total assets', 'total liabilities', 'current assets', 'current liabilities', 'intangible assets',
            'long term loan-current portion', 'inventories', 'accounts receivables', 'capital work in progress', 
            'non-current assets', 'revenue', 'net profit after tax', 'operating profit', 'earnings before tax',
            'finance cost', 'cost of sales', 'cash and cash equivalents at end of year', 
            'cash flows from operating activities', 'cash flows from financing activities'
        ]
        
    def return_input(self):
        return self.item
    