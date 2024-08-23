# config/__init__.py
from .prompt import *
from .config import ENDPOINT_NAME, PARAMETERS, OUTPUT_BUCKET_NAME
from .templates import llama_template

preset_prompts = {
    'predict': PRESET_PROMPT_1,
    'update': PRESET_PROMPT_2
}

__all__ = ["ENDPOINT_NAME", "OUTPUT_BUCKET_NAME", "preset_prompts", "llama_template"]
