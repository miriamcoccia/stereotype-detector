"""
This file sends requests to OpenAI, Nebius, and Anthropic APIs using the prompts defined in `prompts.py`. 
The responses are parsed according to a Pydantic Schema and stored locally. 
"""
from src.prompts import Prompt
from src.output_parser import ValidationSchema
from openai import OpenAI
from anthropic import Anthropic
from pathlib import Path
import os
from dotenv import load_dotenv

env_path = Path(__file__).parent / "secrets.env"
load_dotenv(env_path, override=True)

# Anthropic structured outputs is a beta feature — this header enables it.
ANTHROPIC_STRUCTURED_OUTPUTS_BETA = "structured-outputs-2025-11-13"


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
        model_lower = self.selected_model.lower()
        if model_lower.startswith("gpt"):
            return "openai"
        elif model_lower.startswith("claude"):
            return "anthropic"
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
        elif self.provider_name == "anthropic":
            return Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )

    def _build_anthropic_messages(self):
        """
        Converts self.prompt.messages (OpenAI format) into Anthropic's format:
        - system prompt becomes its own top-level argument, not a message
        - image blocks use type='image' + base64 source, not image_url
        """
        system_prompt = None
        user_content = []

        for message in self.prompt.messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            elif message["role"] == "user":
                for block in message["content"]:
                    if block["type"] == "text":
                        user_content.append({"type": "text", "text": block["text"]})
                    elif block["type"] == "image_url":
                        data_url = block["image_url"]["url"]
                        # data_url looks like: "data:image/png;base64,<b64string>"
                        header, b64_data = data_url.split(",", 1)
                        media_type = header.split(":")[1].split(";")[0]  # e.g. "image/png"
                        user_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": b64_data
                            }
                        })

        anthropic_messages = [{"role": "user", "content": user_content}]
        return system_prompt, anthropic_messages

    def execute_llm_call(self):
        """Uses the prompt and image to evaluate the image according to the selected trait(s)."""
        if self.provider_name == "anthropic":
            system_prompt, anthropic_messages = self._build_anthropic_messages()
            response = self.client.beta.messages.parse(
                model=self.selected_model,
                max_tokens=2048,
                betas=[ANTHROPIC_STRUCTURED_OUTPUTS_BETA],
                system=system_prompt,
                messages=anthropic_messages,
                output_format=ValidationSchema
            )
            return response.parsed_output

        response = self.client.chat.completions.parse(
            model=self.selected_model,
            messages=self.prompt.messages,
            response_format=ValidationSchema
        )
        return response.choices[0].message.parsed