import os
from openai import OpenAI
import pandas as pd
import re
from io import StringIO
import traceback

class GetResponseFromOpenAI:
    def __init__(self):
        # Initialize OpenAI client from the OPENAI_API_KEY environment variable
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.model = "gpt-4-turbo"  # or "gpt-4-turbo" if needed

    def remove_markdown_separator(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Removes markdown-style separator rows like:
        | --- | --- | --- |
        from a DataFrame by detecting rows where most/all columns contain only dashes.
        """
        # Define a function to check if a value looks like a markdown separator
        def is_dash(val):
            return isinstance(val, str) and val.strip().strip('-') == ''

        # Check each row: if all (or nearly all) values are dashes, mark for deletion
        mask = df.applymap(is_dash).sum(axis=1) >= (df.shape[1] - 1)  # allow 1 exception
        return df[~mask].reset_index(drop=True)

    def extract_markdown_table_to_df(self, text):
        print("_________")
        print(text)
        print("___________")

        match = re.search(r"```(?:markdown)?(.*?)```", text, re.DOTALL)
        markdown_table = match.group(1).strip() if match else  text

        # Step 2: Load it into DataFrame
        df = pd.read_csv(StringIO(markdown_table), sep='|', engine='python')

        # Step 3: Clean up DataFrame
        df = df.dropna(how='all')  # drop empty rows
        df.columns = [col.strip() for col in df.columns]  # clean column names
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # drop unnamed cols
        first_row_has_alpha = df.iloc[0].astype(str).str.contains(r'[A-Za-z]').any()
        if not first_row_has_alpha:
            df = df.iloc[1:].reset_index(drop=True)
        return df

        # print("------------")
        # print(text)
        # print("------------")
        # try:
        #     if "```markdown" in text:
        #         markdown_block = text.split("```markdown", 1)[1]
        #     else:
        #         markdown_block = text.split("```", 1)[1]

        #     markdown = markdown_block.split("```", 1)[0].strip()

        #     # Remove unwanted leading/trailing pipes and whitespace
        #     markdown_lines = [line.strip().strip('|') for line in markdown.splitlines() if line.strip()]
        #     cleaned_markdown = '\n'.join(markdown_lines)

        #     # Try to read as CSV
        #     df = pd.read_csv(StringIO(cleaned_markdown), sep='|', engine='python')
        #     df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        #     df.columns = df.columns.str.strip()
        #     df.dropna(how='all', inplace=True)

        #     return df

        # except Exception as e:
        #     print("Failed to parse markdown table. Raw text:")
        #     print(text)
        #     print("Error:", e)
        #     raise e  # Optional: raise again or return an error response
        # else:
        #     raise ValueError("No markdown table found in the input text.")
        # prompt = """You are a Markdown table cleaning assistant. 
        #             Your task is to correct a poorly formatted Markdown table by:

        #             - Fixing broken headers.
        #             - Splitting rows or columns that were mistakenly merged.
        #             - Correcting misspelled headers or entries.
        #             - Removing or correcting duplicated or invalid columns and rows.
        #             - Preserving the original data structure without hallucinating any new content.
        #             - Always maintain the sequence of the rows and columns in the correct markdown.
                    
        #             Return only the cleaned and properly formatted Markdown table. Do not add explanations.
        #             Incorrect Markdown table:
        #             {}

        #             Corrected Markdown table:

        # You are a Markdown table cleaning assistant. 
        #             Your task is to correct a poorly formatted Markdown table by:

        #             - Fixing broken headers.
        #             - Correcting misspelled headers or entries.
        #             - Removing or correcting duplicated or invalid columns and rows.
        #             - Multiple rows may have empty values. You should include those rows as well. 
        #             - Preserving the original data structure without hallucinating any new content.
        #             - Always maintain the sequence of rows in the correct markdown the same as in the incorrect markdown.
                    
        #             Return only the cleaned and properly formatted Markdown table. Do not add explanations.
        #             Incorrect Markdown table:
        #             {}

        #             Corrected Markdown table:
        # """
    
    def prepare_prompt(self, markdown_table):
         
        # prompt = """You are a Markdown table cleaning assistant.
        #     Your task is to correct a poorly formatted Markdown table by:
 
        #     - Fixing broken headers.
        #     - Detect headers that has all the empty values and removing them.
        #     - Splitting rows or columns that were mistakenly merged.
        #     - Correcting misspelled headers or entries.
        #     - Removing or correcting duplicated or invalid columns and rows.
        #     - Preserving the original data structure without hallucinating any new content.
        #     - Always maintain the sequence of the rows and columns in the correct markdown.
        #     - Auto removing the duplicate columns.
            
        #     Return only the cleaned and properly formatted Markdown table. Do not add explanations.
        #     Incorrect Markdown table:
        #     {}
 
        #     Corrected Markdown table:
        
        # """

        prompt = """You are a Markdown table cleaning assistant. 
                    Your task is to correct a poorly formatted Markdown table by:

                    - Fixing broken headers.
                    - Correcting misspelled headers or entries.
                    - Removing or correcting duplicated or invalid columns and rows.
                    - Multiple rows may have empty values. You should include those rows as well. 
                    - Preserving the original data structure without hallucinating any new content.
                    - Always maintain the sequence of rows in the correct markdown the same as in the incorrect markdown.
                    - Auto removing the duplicate columns.
                    Return only the cleaned and properly formatted Markdown table. Do not add explanations.
                    Incorrect Markdown table:
                    {}

                    Corrected Markdown table:
        """
        final_prompt = prompt.format(markdown_table)
        return final_prompt


    def get_response(self, incorrect_markdown):
        try:
            prompt = self.prepare_prompt(incorrect_markdown)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=4000
            )
            response_text = response.choices[0].message.content.strip()
            df = self.extract_markdown_table_to_df(response_text)
        

            return df
        except Exception as e:
            print("Traceback:", traceback.format_exc())
            return f"Error from llm : {e}"

# Interactive prompt loop
if __name__ == "__main__":
    llm_cls = GetResponseFromOpenAI()
    prompt =  llm_cls.prepare_prompt("hello")
    print(prompt)

    # while True:
    #     user_prompt = input("Enter your prompt (or 'quit' to exit): ")
    #     if user_prompt.lower() == "quit":
    #         break
    #     answer = llm_cls.get_response(user_prompt)
    #     print(f"Response:\n{answer}\n")
