import json
from typing import Any, Dict, Optional, Tuple

from openai import OpenAI

client: Optional[OpenAI] = None


class OpenAIClientManager:
    """Client context manager for OpenAI."""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def __enter__(self) -> OpenAI:
        global client
        if client is None:
            client = OpenAI(api_key=self.api_key)
        return client

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        global client
        if client is not None:
            client.close()
            client = None

def count_tokens(text: str, model: str) -> int:
    """Count the number of tokens in a text."""
    enc = encoding_for_model(model)
    return len(enc.encode(text))

FrequenciesType = Dict[str, float]
ScoresType = Dict[Span, float]

DEFAULT_OPENAI_SETTINGS = {
    "max_tokens": 500,
    "temperature": 0.7,
}
ALLOWED_TOOLS = [
    "trading-offline",
    "trading-online",
    "trading-online-summarized-info",
]
MAX_TOKENS = {
    "gpt-4": 8192,
}
TOOL_TO_ENGINE = {tool: "gpt-3.5-turbo" for tool in ALLOWED_TOOLS}
# the default number of URLs to fetch online information for
DEFAULT_NUM_URLS = defaultdict(lambda: 3)
DEFAULT_NUM_URLS["trading-online-summarized-info"] = 7
# the default number of words to fetch online information for
DEFAULT_NUM_WORDS: Dict[str, Optional[int]] = defaultdict(lambda: 300)
DEFAULT_NUM_WORDS["trading-online-summarized-info"] = None
# how much of the initial content will be kept during summarization
DEFAULT_COMPRESSION_FACTOR = 0.05
# the vocabulary to use for the summarization
DEFAULT_VOCAB = "en_core_web_sm"

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
```
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
    tool = kwargs["tool"]
    prompt = kwargs["prompt"]
    max_tokens = kwargs.get("max_tokens", DEFAULT_OPENAI_SETTINGS["max_tokens"])
    temperature = kwargs.get("temperature", DEFAULT_OPENAI_SETTINGS["temperature"])
    api_keys = kwargs.get("api_keys", {})
    engine = TOOL_TO_ENGINE[tool]

    if tool not in ALLOWED_TOOLS:
        raise ValueError(f"Tool {tool} is not supported.")

    # Construct trading prompt for OpenAI API
    trading_prompt = TRADE_PROMPT.format(user_prompt=prompt)

    # Call OpenAI API for trading decision
    with OpenAIClientManager(api_keys["openai"]):
        moderation_result = client.moderations.create(input=trading_prompt)
        if moderation_result.results[0].flagged:
            return (
                "Moderation flagged the prompt as in violation of terms.",
                None,
                None,
                None,
            )

        messages = [
            {"role": "system", "content": "You are a helpful trading assistant."},
            {"role": "user", "content": trading_prompt},
        ]

        response = client.chat.completions.create(
            model=engine,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            n=1,
            timeout=150,
            stop=None,
        )

    # Return the result
    return (
        response.choices[0].message.content,
        trading_prompt,
        None,
        None,
    )

