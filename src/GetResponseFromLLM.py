from openai import OpenAI
import pandas as pd
import re
from io import StringIO

class GetResponseFromOpenAI:
    def __init__(self):
        # Initialize OpenAI client with your API key
        self.client = OpenAI(api_key='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')  # Replace with your actual API key
        self.model = "gpt-4-turbo"  # or "gpt-4-turbo" if needed

    def extract_markdown_table_to_df(self,text):

        markdown = text.split("```markdown")[1]
        markdown = markdown.split("```")[0]
        df = pd.read_csv(StringIO(markdown), sep='|', engine='python')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df.columns = df.columns.str.strip()
        df.dropna(how='all', inplace=True)
        return df
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
        # """
    
    def prepare_prompt(self, markdown_table):
         
        prompt = """You are a Markdown table cleaning assistant. 
                    Your task is to correct a poorly formatted Markdown table by:

                    - Fixing broken headers.
                    - Splitting rows or columns that were mistakenly merged.
                    - Correcting misspelled headers or entries.
                    - Removing or correcting duplicated or invalid columns and rows.
                    - Preserving the original data structure without hallucinating any new content.
                    - Always maintain the sequence of the rows and columns in the correct markdown.
                    
                    Return only the cleaned and properly formatted Markdown table. Do not add explanations.
                    Incorrect Markdown table:
                    {}

                    Corrected Markdown table:
        """
        final_prompt = prompt.format(markdown_table)
        return final_prompt


    def get_response(self, incorrect_markdown):
        try:

            print(incorrect_markdown)
            prompt = self.prepare_prompt(incorrect_markdown)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=3000
            )
            resposne =  response.choices[0].message.content.strip()
            # print(resposne)
            df  = self.extract_markdown_table_to_df(resposne)
        

            return df
        except Exception as e:
            return f"Error: {e}"

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
