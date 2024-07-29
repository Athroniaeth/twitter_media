import logging
from typing import Type, TypeVar

from langchain_core.language_models import BaseLLM
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from src import TEMPLATES_PATH
from src.parser.helper import get_helper_output_parser


class SummaryText(BaseModel):
    """
    Summary of the extracted text.

    Attributes:
        reasoning (str): Think about what information is useful and important, and what information is required for a good summary of the text.
        text_summary (str): Text summary of the extracted information, in a few sentences, more that 255 characters.
    """

    reasoning: str = Field(description="think about what information is useful and important, and what information is required for a good summary of the text")
    text_summary: str = Field(description="text summary of the extracted information, in a few sentences, more that 255 characters")

    def __repr__(self):
        return f"SummaryText(reasoning='{self.reasoning[:25]}..', text_summary='{self.text_summary[:25]}..')"


def summarize_text(
        content_text: str,
        llm_model: BaseLLM,
        language: str = "French",
) -> SummaryText:
    """
    Summarize the text extracted from the article.

    Args:
        content_text (str): Extracted text from the article.
        llm_model (BaseLLM): Language model to use to summarize the text.
        language (str): Language of the summary (the language in english like 'French', 'Spanish', 'German', etc.).

    Returns:
        SummaryText: Object containing the reasoning and the text summary.
    """
    template_path = TEMPLATES_PATH / "task.jinja2"
    template = template_path.read_text(encoding="utf-8")

    return task_to_json(
        task=SummaryText,
        template=template,
        content_text=content_text,
        llm_model=llm_model,
        content_type="text",
    )


T = TypeVar("T", bound=BaseModel)


def task_to_json(
        task: Type[T],
        template: str,
        content_text: str,
        llm_model: BaseLLM,
        content_type: str,
) -> T:
    """

    Args:
        task (Type[BaseModel]): Pydantic class representation of task (for llm)
        template (str): Template to use for the prompt
        content_text (str): Extracted text from the article.
        llm_model (BaseLLM): Language model to use.
        content_type (str): Type of content extracted.
        query (str): Query to prompt the language model.

    Returns:
        T: Class instance of the task from JSON output.

    """
    assert "{{content_text}}" in template, "The template must contain '{{content_text}}' to inject the content text."
    assert "{{content_type}}" in template, "The template must contain '{{content_type}}' to inject the content type."
    assert "{{format_instructions}}" in template, "The template must contain '{{format_instructions}}' to inject the format instructions."

    # Create OutputParser (JSON -> Python object)
    parser = PydanticOutputParser(pydantic_object=task)

    # Get the first attribute of the Pydantic object to start the JSON
    helper_output_parser = get_helper_output_parser(pydantic_object=task)

    # Create the prompt and inject the instructions into the prompt model.
    prompt = PromptTemplate(
        template_format="jinja2",
        template=template,
        partial_variables={
            "content_text": content_text,
            "content_type": content_type,
            "helper_output_parser": helper_output_parser,
            "format_instructions": parser.get_format_instructions(),
        },
    )

    # And a query intended to prompt a language model to populate the data structure.
    prompt_and_model = prompt | llm_model
    llm_output = prompt_and_model.invoke({})

    # Get start of JSON + Generated LLM output
    generated_llm_output = helper_output_parser + llm_output

    # Encapsulate the JSON in a code block
    processed_generated_llm_output = generated_llm_output.split("```")[1]
    processed_generated_llm_output = f"```{processed_generated_llm_output}```"

    output = parser.parse(processed_generated_llm_output)
    logging.debug(f"Output of '{task.__name__}' task: {output}")
    return output
