from google import genai
import os
import logging
import json
from datetime import datetime

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

def call_llm(prompt, use_cache: bool = True):
    # By default, we Google Gemini 2.5 pro, as it shows great performance for code understanding
    gemini = GeminiModel(api_key=os.environ.get("GEMINI_API_KEY"), model="gemini-2.5-pro-exp-03-25")
    try:
        return gemini.call_llm(prompt, use_cache)
    except Exception as e:
        try:
            gpt = OpenAIModel(api_key=os.environ.get("OPENAI_API_KEY"), model="o1")
            return gpt.call_llm(prompt, use_cache)
        except Exception as e:
            anthropic = AnthropicModel(api_key=os.environ.get("ANTHROPIC_API_KEY"), model="claude-3-7-sonnet-20250219")
            return anthropic.call_llm(prompt, use_cache)

class Model:
    def __init__(self, name, api_key):
        self.name = name
        self.api_key = api_key
    
    def call_llm(self, prompt: str, use_cache: bool = True) -> str:
        pass

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

class OpenAIModel(Model):
    def __init__(self, api_key: str, model: str):
        self.client = None
        self.api_key = api_key
        self.model = model
        from openai import OpenAI
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

class GeminiModel(Model):
    def __init__(self, api_key: str, model: str):
        self.client = None
        self.api_key = api_key
        self.model = model
        super().__init__(model, api_key)
        from google import genai
        self.client = genai.Client(
            vertexai=True, 
            # TODO: change to your own project id and location
            project=os.getenv("GEMINI_PROJECT_ID", "your-project-id"),
            location=os.getenv("GEMINI_LOCATION", "us-central1")
        )
    
    def call_llm(self, prompt: str, use_cache: bool = True) -> str:
        print(f"Calling Gemini model {self.model}")
        # Check cache if enabled
        if use_cache:
            # Load cache from disk
            cache = {}
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cache = json.load(f)
                except:
                    logger.warning(f"Failed to load cache, starting with empty cache")
            
            # Return from cache if exists
            if prompt in cache:
                logger.info(f"RESPONSE: {cache[prompt]}")
                return cache[prompt]
        
        # Call the LLM if not in cache or cache disabled
        client = genai.Client(
            vertexai=True, 
            # TODO: change to your own project id and location
            project=os.getenv("GEMINI_PROJECT_ID", "your-project-id"),
            location=os.getenv("GEMINI_LOCATION", "us-central1")
        )
        # You can comment the previous line and use the AI Studio key instead:
        # client = genai.Client(
        #     api_key=os.getenv("GEMINI_API_KEY"),
        # )
        response = client.models.generate_content(
            model=self.model,
            contents=[prompt]
        )
        response_text = response.text
        
        # Log the response
        logger.info(f"RESPONSE: {response_text}")
        
        # Update cache if enabled
        if use_cache:
            # Load cache again to avoid overwrites
            cache = {}
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cache = json.load(f)
                except:
                    pass
            
            # Add to cache and save
            cache[prompt] = response_text
            try:
                with open(cache_file, 'w') as f:
                    json.dump(cache, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")
        
        return response_text


if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    
    # First call - should hit the API
    print("Making call...")
    response1 = call_llm(test_prompt, use_cache=False)
    print(f"Response: {response1}")
    
