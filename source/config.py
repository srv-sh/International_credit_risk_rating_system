import os
import re
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

        # Adjust the prompt template to match the expected output format
        self.prompt_template = """
            Given this markdown table of financial particulars:

            {markdown_output},

            For each of the following items, try to match the terms exactly or with clear synonyms.
            If found or synonymous, return the result in JSON format as a dictionary like:

            {{
                "total assets": ["total assets"],
                "total liabilities": ["total liabilities"],
                ...
            }}

            If the item could not be matched, return the value as null.

            Here's an example:
            {{
                "total assets": ["total assets"],
                "net profit after tax": ["profit/(loss) after tax"],
                "capital work in progress": []
            }}

            NOTE: No numeric values are needed in the output.
            NOTE: The output should be a single JSON object.
            NOTE: output json key would be {item}
            NOTE: Do not hallucinate and come up with json key excludeing in item 
            NOTE: Just give the json, no extra sentences or anything else should be there. 
            NOTE: If any value is not found, send empty list like: "capital work in progress": []. Do not send null. 
        """

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