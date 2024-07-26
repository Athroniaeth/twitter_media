import logging
import os
import time
from functools import lru_cache, wraps
from typing import Optional

from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain_core.language_models import BaseLLM


@lru_cache(maxsize=1)
def get_llm_model(
    model_id: str,
    quantization_int4: bool = True,
    local: bool = False,
    hf_token: Optional[str] = None,
) -> BaseLLM:
    """
    Load a CausalLM model (local or cloud).

    Args:
        model_id (str): Model ID to load.
        hf_token (Optional[str]): Hugging Face API access token.
        quantization_int4 (bool): Use 4-bit quantization.
        local (bool): Use local mode to load the model.

    Returns:
        BaseLLM: Language model.
    """
    if local:
        logging.warning("Mode 'local' is not supported for Hugging Face Cloud models. Switching to 'local=False'.")

    if quantization_int4:
        logging.warning("4-bit quantization is not supported for Hugging Face Cloud models. Switching to 'quantization_int4=False'.")

    if hf_token is None:
        hf_token = os.environ["HF_TOKEN"]

    llm_model = _get_llm_model_hf_cloud(
        model_id=model_id,
        hf_token=hf_token,
    )

    logging.debug(f'Model "{model_id}" loaded successfully.')
    llm_model.name = model_id

    return llm_model


def _get_llm_model_hf_cloud(
    model_id: str,
    hf_token: str,
):
    """Load a model from Hugging Face Cloud."""
    logging.debug(f"Loading model '{model_id}' from Hugging Face Cloud.")

    llm_model = HuggingFaceHub(
        repo_id=model_id,
        huggingfacehub_api_token=hf_token,
    )
    return llm_model


def log_inference(model_id: str):
    """Décorateur pour logger l'exécution d'un modèle."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.debug(f"Inference of model '{model_id}' started. (function: {func.__name__})")
            time_start = time.time()

            result = func(*args, **kwargs)

            time_end = time.time()
            logging.debug(f"Inference takes {time_end - time_start:.2f} seconds.")
            return result

        return wrapper

    return decorator
