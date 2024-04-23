import os
import re

from dotenv import load_dotenv
from langchain_community.chat_message_histories.in_memory import (
    ChatMessageHistory,
)
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from api.mistral_patch import PatchedChatMistralAI
from api.utils import MessageDetails, SystemDetails

load_dotenv()

API_ROOT = os.path.realpath(os.path.dirname(__file__))
data_url = os.path.join(API_ROOT, os.path.pardir, "data")
store: dict[str, ChatMessageHistory] = {}
PREFERRED_MODEL = os.environ.get("PREFERRED_MODEL", "gpt")
llm: ChatOpenAI | PatchedChatMistralAI

match PREFERRED_MODEL:
    case "gpt":
        try:
            llm = ChatOpenAI(
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
                model="open-mixtral-8x22b",
                temperature=0.5,
            )
        except KeyError as e:
            raise ValueError(
                "MISTRAL_API_KEY environment variable not set"
            ) from e
    case _:
        raise ValueError(f"Unsupported model: {PREFERRED_MODEL}")


class FeedbackOutputParser(BaseOutputParser[str]):
    """Feedback output parser."""

    def parse(self, text: str) -> str:
        pattern = r"<feedback>([\s\S]*?)</feedback>"
        feedback = re.search(pattern, text)
        if not feedback:
            raise OutputParserException(
                f"Expected output value to contain a <feedback> tag. "
                f"Received {text}."
            )
        return feedback.group(1).strip()

    @property
    def _type(self) -> str:
        return "feedback_output_parser"


def get_system_template() -> str:
    with open(
        os.path.join(data_url, "system_template.txt"), "r", encoding="utf-8"
    ) as file:
        system_template = file.read()

    return system_template


def get_message_template() -> str:
    with open(
        os.path.join(data_url, "message_template.txt"), "r", encoding="utf-8"
    ) as file:
        message_template = file.read()

    return message_template


def get_runnable(
    history_store: dict[str, ChatMessageHistory],
    system_details: SystemDetails,
) -> RunnableWithMessageHistory:
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
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )

    parser = FeedbackOutputParser()

    chain = prompt | llm | parser

    runnable = RunnableWithMessageHistory(
        chain,  # type: ignore
        get_session_history,
        history_messages_key="history",
    )

    return runnable


def generate_feedback(
    runnable: RunnableWithMessageHistory,
    session_id: str,
    message_details: MessageDetails,
) -> str:

    message_template = get_message_template()

    message = HumanMessagePromptTemplate.from_template(
        message_template
    ).format(
        question=message_details.question,
        correctness=message_details.correctness,
        correct_answers="; ".join(message_details.correct_answers),
        answers="; ".join(message_details.answers),
    )

    try:
        feedback = runnable.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}},
        )
    except ValidationError as exc:
        raise ValueError("Runnable did not return feedback") from exc

    return str(feedback)
