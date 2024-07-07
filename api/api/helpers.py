import os
import re

from dotenv import load_dotenv
from langchain_community.chat_message_histories.in_memory import (
    ChatMessageHistory,
)
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables.base import Runnable
from langchain_core.runnables.config import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_together import Together
from pydantic import ValidationError

from api.mistral_patch import PatchedChatMistralAI
from api.utils import MessageDetails, SystemDetails

load_dotenv()

API_ROOT = os.path.realpath(os.path.dirname(__file__))
data_url = os.path.join(API_ROOT, os.path.pardir, "data")
store: dict[str, ChatMessageHistory] = {}
PREFERRED_MODEL = os.environ.get("PREFERRED_MODEL", "gpt")

match PREFERRED_MODEL:
    case "gpt":
        try:
            llm: BaseLanguageModel = ChatOpenAI(
                model="gpt-4-turbo",
                temperature=0.5,
            )
        except KeyError as e:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set"
            ) from e
    case "mixtral":
        try:
            llm = PatchedChatMistralAI(
                model_name="open-mixtral-8x22b",
                temperature=0.5,
            )
        except KeyError as e:
            raise ValueError(
                "MISTRAL_API_KEY environment variable not set"
            ) from e
    case "olmo":
        try:
            llm = Together(
                model="allenai/OLMo-7B-Instruct",
                temperature=0.5,
                top_k=1,
                top_p=1.0,
                max_tokens=1000,
            )  # type: ignore [call-arg]
        except KeyError as e:
            raise ValueError(
                "TOGETHER_API_KEY environment variable not set"
            ) from e
    case _:
        raise ValueError(
            f"""Unsupported model: {
                PREFERRED_MODEL
            }. Valid models: gpt, mixtral, olmo"""
        )


class FeedbackOutputParser(BaseOutputParser[str]):
    """Feedback output parser."""

    def parse(self, text: str) -> str:
        pattern = r"<feedback>([\s\S]*?)</feedback>"
        feedback = re.search(pattern, text)
        if not feedback:
            return text
        return feedback.group(1).strip()

    @property
    def _type(self) -> str:
        return "feedback_output_parser"


def get_system_template() -> str:
    """
    Return the template for the system message.

    Returns:
        str: The template for the system message.
    """

    with open(
        os.path.join(data_url, "system_template.txt"), "r", encoding="utf-8"
    ) as file:
        system_template = file.read()

    return system_template


def get_message_template() -> str:
    """
    Return the template for the human message.

    Returns:
        str: The template for the human message.
    """

    with open(
        os.path.join(data_url, "message_template.txt"), "r", encoding="utf-8"
    ) as file:
        message_template = file.read()

    return message_template


def get_runnable(
    history_store: dict[str, ChatMessageHistory],
    system_details: SystemDetails,
) -> Runnable:
    """
    Return the runnable.

    Args:
        history_store (dict[str, ChatMessageHistory]): The history store.
        system_details (SystemDetails): The system details.

    Returns:
        Runnable: The runnable.
    """

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in history_store:
            history_store[session_id] = ChatMessageHistory()
        return history_store[session_id]

    system_template = get_system_template()

    system_message = SystemMessagePromptTemplate.from_template(
        system_template,
    ).format(
        theme=system_details.theme,
        description=system_details.description,
        goal=system_details.goal,
        level=system_details.user_level,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            system_message,
            (
                MessagesPlaceholder(variable_name="history")
                if PREFERRED_MODEL != "olmo"
                else ""
            ),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    parser = FeedbackOutputParser()

    if PREFERRED_MODEL == "olmo":
        return prompt | llm

    chain = prompt | llm | parser

    runnable = RunnableWithMessageHistory(
        chain,  # type: ignore
        get_session_history,
        history_messages_key="history",
    )

    return runnable


def generate_feedback(
    runnable: Runnable,
    session_id: str,
    message_details: MessageDetails,
) -> str:
    """
    Generate feedback.

    Args:
        runnable (Runnable): The runnable.
        session_id (str): The session ID.
        message_details (MessageDetails): The message details.

    Returns:
        str: The feedback.
    """

    message_template = get_message_template()

    message = HumanMessagePromptTemplate.from_template(
        message_template
    ).format(
        question=message_details.question,
        correctness=message_details.correctness.value,
        correct_answers="; ".join(message_details.correct_answers),
        answers="; ".join(message_details.answers),
    )

    config: RunnableConfig | None = (
        {"configurable": {"session_id": session_id}}
        if PREFERRED_MODEL != "olmo"
        else None
    )

    try:
        feedback: str = runnable.invoke(
            {"input": message},
            config=config,
        )
    except ValidationError as exc:
        raise ValueError("Runnable did not return feedback") from exc

    if PREFERRED_MODEL == "olmo":
        feedback = feedback.replace("<feedback>", "").replace(
            "</feedback>", ""
        )

    return str(feedback)


def generate_final_feedback(
    runnable: Runnable,
    session_id: str,
) -> str | None:
    """
    Generate final feedback.

    Args:
        runnable (RunnableWithMessageHistory): The runnable.
        session_id (str): The session ID.

    Returns:
        str | None: The final feedback.
    """

    if PREFERRED_MODEL == "olmo":
        return None

    message = """From the feedback history, generate a final feedback
that reflects the user's level of understanding of the topic, progress
towards the goal, and overall satisfaction with the task. It should
mention the points to be worked on. Write it between <feedback> tags:"""

    config: RunnableConfig | None = (
        {"configurable": {"session_id": session_id}}
        if PREFERRED_MODEL != "olmo"
        else None
    )

    try:
        feedback: str = runnable.invoke(
            {"input": message},
            config=config,
        )
    except ValidationError as exc:
        raise ValueError("Runnable did not return feedback") from exc

    if PREFERRED_MODEL == "olmo":
        feedback = feedback.replace("<feedback>", "").replace(
            "</feedback>", ""
        )

    return str(feedback)
