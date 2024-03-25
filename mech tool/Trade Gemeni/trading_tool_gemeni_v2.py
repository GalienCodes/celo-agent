import json
from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from heapq import nlargest
from itertools import islice
from string import punctuation
from typing import Any, Dict, Generator, List, Optional, Tuple, Callable

import google.generativeai as genai

# Configure GenerativeAI model (replace with your API key)
genai.configure(api_key="YOUR_API_KEY")

# Set up the model with desired configuration
generation_config = {
    "temperature": 0.8,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

#TOOL_TO_ENGINE = {tool: "gemini-1.0-pro" for tool in ALLOWED_TOOLS}

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

TRADE_PROMPT = """
You are a trading AI inside a multi-agent system that takes in a prompt of a user requesting trading advice for two tokens.
You are provided with an input under the label "USER_PROMPT". You must follow the instructions
under the label "INSTRUCTIONS". You must provide your response in the format specified under "OUTPUT_FORMAT".

INSTRUCTIONS
* Read the input under the label "USER_PROMPT" delimited by three backticks.
* The "USER_PROMPT" specifies two tokens for trading advice.
* Provide the latest market data for the two tokens such as current prices, trading volume, and trends.
* Using the Pairs Trading Strategy, You must provide advice on whether to hold and not sell or buy, to buy more of token 1 and sell token 2, or to buy token 2 and sell token 1.
* You must provide your response in the format specified under "OUTPUT_FORMAT".
* Do not include any other contents in your response.

USER_PROMPT:
```
{user_prompt}

OUTPUT_FORMAT
* Your output response must be only a single JSON object to be parsed by Python's "json.loads()".
* The JSON must contain three fields: "decision", "confidence", and "info_utility".
   - "decision": Your advice decision. It can be "hold", "buy_token1_sell_token2", or "buy_token2_sell_token1".
   - "confidence": A value between 0 and 1 indicating the confidence in the decision. 0 indicates lowest
     confidence value; 1 maximum confidence value.
   - "info_utility": Utility of the information provided in "ADDITIONAL_INFORMATION" to help you make the decision.
     0 indicates lowest utility; 1 maximum utility.
* Output only the JSON object. Do not include any other contents in your response.
"""



def run(**kwargs) -> Tuple[str, Optional[str], Optional[Dict[str, Any]], Any]:
    """Run the trading task"""
    #tool = kwargs["tool"]
    prompt = kwargs["prompt"]
    api_key = kwargs.get("api_keys")
    #max_tokens = kwargs.get("max_tokens", generation_config["max_output_tokens"])
    #temperature = kwargs.get("temperature", generation_config["temperature"])
    #engine = TOOL_TO_ENGINE[tool]
    
  
    # Configure GenerativeAI model with API key
    genai.configure(api_key=api_key)
    
    # Construct trading prompt for Gemeni API
    #trading_prompt = TRADE_PROMPT.format(user_prompt=prompt)
    
    chat = model.start_chat(history=[
      {
    "role": "user",
    "parts": ["You are a trading AI inside a multi-agent system that takes in a prompt of a user requesting trading advice for two tokens.You are provided with an input under the label \"USER_PROMPT\". You must follow the instructionsunder the label \"INSTRUCTIONS\". You must provide your response in the format specified under \"OUTPUT_FORMAT\".INSTRUCTIONS* Read the input under the label \"USER_PROMPT\" delimited by three backticks.* The \"USER_PROMPT\" specifies two tokens for trading advice.* Provide the latest market data for the two tokens such as current prices, trading volume, and trends.* Using the Pairs Trading Strategy, You must provide advice on whether to hold and not sell or buy, to buy more of token 1 and sell token 2, or to buy token 2 and sell token 1.* You must provide your response in the format specified under \"OUTPUT_FORMAT\".* Do not include any other contents in your response.USER_PROMPT:```{trade olame vs Celo}```OUTPUT_FORMAT* Your output response must be only a single JSON object to be parsed by Python's \"json.loads()\".* The JSON must contain three fields: \"decision\", \"confidence\", and \"info_utility\".   - \"decision\": Your advice decision. It can be \"hold\", \"buy_token1_sell_token2\", or \"buy_token2_sell_token1\".   - \"confidence\": A value between 0 and 1 indicating the confidence in the decision. 0 indicates lowest     confidence value; 1 maximum confidence value.   - \"info_utility\": Utility of the information provided in \"ADDITIONAL_INFORMATION\" to help you make the decision.     0 indicates lowest utility; 1 maximum utility.* Output only the JSON object. Do not include any other contents in your response."]
      },
      {
    "role": "model",
    "parts": ["```json\n{\n  \"decision\": \"hold\",\n  \"confidence\": 0.5,\n  \"info_utility\": 0.5\n}\n```"]
      },
      {
    "role": "user",
    "parts": ["You are a trading AI inside a multi-agent system that takes in a prompt of a user requesting trading advice for two tokens.You are provided with an input under the label \"USER_PROMPT\". You must follow the instructionsunder the label \"INSTRUCTIONS\". You must provide your response in the format specified under \"OUTPUT_FORMAT\".INSTRUCTIONS* Read the input under the label \"USER_PROMPT\" delimited by three backticks.* The \"USER_PROMPT\" specifies two tokens for trading advice.* Provide the latest market data for the two tokens such as current prices, trading volume, and trends.* Using the Pairs Trading Strategy, You must provide advice on whether to hold and not sell or buy, to buy more of token 1 and sell token 2, or to buy token 2 and sell token 1.* You must provide your response in the format specified under \"OUTPUT_FORMAT\".* Do not include any other contents in your response.USER_PROMPT:```{trade bitcoin vs Celo}```OUTPUT_FORMAT* Your output response must be only a single JSON object to be parsed by Python's \"json.loads()\".* The JSON must contain three fields: \"decision\", \"confidence\", and \"info_utility\".   - \"decision\": Your advice decision. It can be \"hold\", \"buy_token1_sell_token2\", or \"buy_token2_sell_token1\".   - \"confidence\": A value between 0 and 1 indicating the confidence in the decision. 0 indicates lowest     confidence value; 1 maximum confidence value.   - \"info_utility\": Utility of the information provided in \"ADDITIONAL_INFORMATION\" to help you make the decision.     0 indicates lowest utility; 1 maximum utility.* Output only the JSON object. Do not include any other contents in your response."]
      },
      {
    "role": "model",
    "parts": ["```json\n{\n  \"decision\": \"buy_token1_sell_token2\",\n  \"confidence\": 0.7,\n  \"info_utility\": 0.8\n}\n```"]
      },
    ])
    response = chat.send_message(
    prompt,
    stream=False)

    #print(convo.last.text)
    return response.text

dict_1 = dict( prompt = "celo vs olame", api_keys={"genai": "AIzaSyA7KSV2cttyczsSy3rPQSpWJiCJ7CnMACc"})

run(**dict_1)