from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import json

class ValidateString():

    def __init__(self):
#         self.prompt = PromptTemplate(
#                                     template=""" Your task is to validate a string provided by the user and return a JSON response.
#                                                     json
#                                                     {{
#                                                     "valid": "yes/no"
#                                                     }}

#                                                 valid: "yes" if the string is a recognized term in the finance or banking field.
#                                                 valid: "no" if the string is irrelevant, unrelated to finance or banking, or consists of random words or numbers.
#                                                 NOTE: only maintain above critiria to give final response. donot generate answer by your own 
#                                                 Examples:
#                                                     String: "Current Tax (Expense)"
#                                                     Response: {{"valid": "yes"}}

#                                                     String: "I got Profit from stock market"
#                                                     Response: {{"valid": "no"}}

#                                                     String: "093 840 9234 D"
#                                                     Response: {{"valid": "no"}}

#                                                     String: "Doiwer"
#                                                     Response: {{"valid": "no"}}

#                                                 Task:
#                                                 Generate a response for the following string:

#                                                 String: {string}

#                                                 Response:     
#  """,
# input_variables=["string"],
# )
        self.prompt = PromptTemplate(template=""" i will give you a string you will return yes or no. 
                                     if that string contains any meaning in the field of finance and banking say yes. would not any thing rather banking or finance term. like dates, amount or  currency name like dollar, taka would not allow
                                     otherwise say no  
                                     and the string is: {string}""",input_variables=["string"],
)
        self.model = ChatOpenAI(model="gpt-4",openai_api_key ="sk-EY3qD_mD09a3o_9kt9fUtCo8aVE8jqkmOUipDU59ObT3BlbkFJhi-nhV6xHfWmaPCWutItnWhpC95PK_7NJ8VBBuiM8A")
        self.chain = LLMChain(llm=self.model, prompt=self.prompt)


    def validate(self, string):
        response = self.chain.run(string=string)
        # json_resposne = json.loads(response)

        return response
    

if __name__=="__main__":
    cls = ValidateString()

    resposne = cls.validate("shareholders' equity\nchar	")
    print(resposne)



