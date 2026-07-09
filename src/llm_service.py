"""
This file sends requests to OpenAI and Nebius APIs using the prompts defined in `prompts.py`. 
The responses are parsed according to a Pydantic Schema and stored locally. 
"""
from src.prompts import Prompt
from src.output_parser import ValidationSchema
from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv

env_path = Path(__file__).parent / "secrets.env"
load_dotenv(env_path, override=True)

class LLMService:
    def __init__(self, selected_model, selected_traits, selected_image):
        self.selected_model = selected_model
        self.selected_traits = selected_traits
        self.selected_image = selected_image
        self.prompt = Prompt(trait_names=self.selected_traits, pil_image=self.selected_image)
        self.provider_name = self._identify_provider()
        self.client = self._identify_client()

    def _identify_provider(self):
        """Chooses the correct provider based on the model selected. Returns the provider."""
        if self.selected_model.lower().startswith("gpt"):
            return "openai"
        else:
            return "nebius"

    def _identify_client(self):
        """Prepares a client for the correct provider."""
        if self.provider_name == "openai":
            return OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY")  
            )
        elif self.provider_name == "nebius":
            return OpenAI(
                base_url="https://api.tokenfactory.nebius.com/v1/",
                api_key=os.environ.get("NEBIUS_API_KEY")
            )

    def execute_llm_call(self):
        """Uses the prompt and image to evaluate the image according to the selected trait(s)."""
        response = self.client.chat.completions.parse(
            model=self.selected_model,
            messages=self.prompt.messages,
            response_format=ValidationSchema
        )
        return response.choices[0].message.parsed
    
