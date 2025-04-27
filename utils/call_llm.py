from google import genai
import os
import logging
import json
from datetime import datetime
import abc
import tiktoken
import anthropic
import google.generativeai as genai
import openai

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log")

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"

# class Chain(abc.ABC):
#     @abc.abstractmethod
#     def call_llm(self, next: 'Chain', prompt, use_cache: bool = True) -> 'Chain':
#         pass

def call_llm(prompt, use_cache: bool = True):
    # By default, we Google Gemini 2.5 pro, as it shows great performance for code understanding
    # api_key = os.environ.get("GEMINI_API_KEY")
    # print(f"Using Gemini API key: {api_key}")
    # gemini_flash = GeminiModel(api_key=api_key, model="gemini-2.5-flash-preview-04-17")
    # gemini_pro = GeminiModel(api_key=api_key, model="gemini-2.5-pro-preview-03-25")
    # gpt = OpenAIModel(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-4.1")
    # anthropic = AnthropicModel(api_key=os.environ.get("ANTHROPIC_API_KEY"), model="claude-3-7-sonnet-20250219")

    api_key = os.environ.get("REQUESTY_API_KEY")
    requesty_pro = RequetyAiModel(name="requesty", api_key=api_key, model="coding/gemini-2.5-pro-preview-03-25")
    requesty_flash = RequetyAiModel(name="requesty", api_key=api_key, model="google/gemini-2.5-flash-preview-04-17")
    requesty_llama = RequetyAiModel(name="requesty", api_key=api_key, model="novita/meta-llama/llama-4-maverick-17b-128e-instruct-fp8")
    requesty_gpt41 = RequetyAiModel(name="requesty", api_key=api_key, model="openai/gpt-4.1")

    try:
        # tokens = gemini_pro.count_tokens(prompt)
        return requesty_pro.call_llm(prompt, use_cache)
    except Exception as e:
        try:
            return requesty_flash.call_llm(prompt, use_cache)
        except Exception as e:
            try:
                return requesty_llama.call_llm(prompt, use_cache)
            except Exception as e:
                try:
                    return requesty_gpt41.call_llm(prompt, use_cache)
                except Exception as e:
                    print(f"Error: {e}")
                    raise Exception(f"Error: {e}")
        # try:
        #     print(f"Error: {e}")
        #     tokens = gpt.count_tokens(prompt)
        #     if tokens > 200000:
        #         # throw error if prompt is too long
        #         raise Exception(f"Prompt with {tokens} tokens is too long for GPT-4.1")
        #     return gpt.call_llm(prompt, use_cache)
        # except Exception as e:
        #     print(f"Error: {e}")
        #     tokens = anthropic.count_tokens(prompt)
        #     if tokens > 200000:
        #         # throw error if prompt is too long
        #         raise Exception(f"Prompt with {tokens} tokens is too long for Anthropic Claude 3.7")
        #     return anthropic.call_llm(prompt, use_cache)

class Model:
    def __init__(self, name, api_key):
        self.name = name
        self.api_key = api_key
    
    def call_llm(self, prompt: str, use_cache: bool = True) -> str:
        pass

    def count_tokens(self, prompt: str) -> int:
        pass

class RequetyAiModel:
    def __init__(self, name, api_key, model):
        self.client = None
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://router.requesty.ai/v1",
            default_headers={"Authorization": f"Bearer {api_key}"}
        )
    
    def call_llm(self, prompt: str, use_cache: bool = True) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        if not response.choices:
            raise Exception("No response choices found.")

        return response.choices[0].message.content

    def count_tokens(self, prompt: str) -> int:
        return -1

# Use Anthropic Claude 3.7 Sonnet Extended Thinking
class AnthropicModel(Model):
    def __init__(self, api_key: str, model: str):
        self.client = None
        self.api_key = api_key
        self.model = model
        super().__init__(model, api_key)
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
    
    def call_llm(self, prompt: str, use_cache: bool = True) -> str:
        print(f"Calling Anthropic model {self.model}")
        response = self.client.messages.create(
            model=self.model,
            max_tokens=21000,
            thinking={
                "type": "enabled",
                "budget_tokens": 20000
            },
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[1].text
    
    def count_tokens(self, prompt: str) -> int:
        """
        Counts the number of tokens in a prompt using the Anthropic tokenizer.

        Args:
            prompt: The text prompt to count tokens for.

        Returns:
            The number of tokens in the prompt.
        """
        # Anthropic's tokenizer is accessible through their client library.
        # You don't need to instantiate the main client if you only need the tokenizer.
        # The tokenizer is typically model-agnostic for recent Claude models.
        # If a future Anthropic model uses a different tokenizer, you might need
        # to specify it, but for Claude 2 and newer, this should work.

        try:
            # Get the tokenizer object from the anthropic library
            tokenizer = anthropic.get_tokenizer()

            # Encode the prompt to get the list of tokens
            # The encode method takes the text and returns a list of integers
            tokens = tokenizer.encode(prompt)

            # Return the number of tokens
            return len(tokens)
        except Exception as e:
            # Catch any potential errors during the tokenization process
            print(f"An error occurred during tokenization: {e}")
            return -1 # Indicate an error

class OpenAIModel(Model):
    def __init__(self, api_key: str, model: str):
        self.client = None
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def call_llm(self, prompt: str, use_cache: bool = True) -> str:
        print(f"Calling OpenAI model {self.model}")
        r = self.client.chat.completions.create(
            model="o1",
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "text"
            },
            reasoning_effort="medium",
            store=False
        )
        return r.choices[0].message.content

    def count_tokens(self, prompt: str) -> int:
        """
        Counts the number of tokens in a prompt for a given OpenAI model.

        Args:
            prompt: The text prompt to count tokens for.

        Returns:
            The number of tokens in the prompt.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            tokens = encoding.encode(prompt)
            return len(tokens)
        except KeyError:
            print(f"Error: Could not find encoding for model '{self.model}'.")
            print("Please check the model name or use tiktoken.list_models()")
            print("to see available models with registered encodings.")
            return -1 # Indicate an error

class GeminiModel(Model):
    def __init__(self, api_key: str, model: str):
        self.client = None
        self.api_key = api_key
        self.model = model
        super().__init__(model, api_key)
        from google import genai
        self.client = genai.Client(api_key="GEMINI_API_KEY")

    def call_llm(self, prompt: str, use_cache: bool = True) -> str:
        print(f"Calling Gemini model {self.model}")
        response = self.client.models.generate_content(
            model=self.model, 
            contents=prompt
        )
        return response.text

    def count_tokens(self, prompt: str) -> int:
        """
        Counts the number of tokens in a prompt for a given Gemini model.

        Args:
            prompt: The text prompt to count tokens for.

        Returns:
            The number of tokens in the prompt, or None if an error occurred.
        """
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.count_tokens(prompt)
            return response.total_tokens
        except Exception as e:
            print(f"An error occurred during token counting: {e}")
            return -1

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    
    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
    
