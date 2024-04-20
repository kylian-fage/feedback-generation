from enum import Enum
from typing import List

from pydantic import BaseModel, Field, PositiveInt

StatusCode = PositiveInt
Answers = List[str]


class Correctness(Enum):
    correct = "correct"
    incorrect = "incorrect"


class QuizQuestion(BaseModel):
    """
    Represents a single question in the quiz, along with its options and the
    correct answer.

    Attributes:
        question (str): The text of the question.
        options (Answers): A list of answer options.
    """

    question: str
    options: Answers


class QuizData(BaseModel):
    """
    QuizData represents the structure of the quiz data.

    Attributes:
        quiz (List[QuizQuestion]): A list of questions, each with
        their options.
    """

    quiz: List[QuizQuestion]


class QuestionAnswers(BaseModel):
    """
    Represents answers to a question.

    Attributes:
        question (str): The text of the question.
        answers (Answers): A list of answers.
    """

    question: str
    answers: Answers


class QuizAnswers(BaseModel):
    """
    Represents the structure of the quiz answers.

    Attributes:
        answers (List[QuestionAnswers]): A list of answers to questions.
    """

    answers: List[QuestionAnswers]


class Feedback(BaseModel):
    """
    Represents the structure of the feedback.

    Attributes:
        feedback (str): The text of the feedback.
        isCorrect (bool): Whether the user's answer is correct or not.
    """

    feedback: str = Field(..., description="The text of the feedback.")
    isCorrect: bool = Field(
        ...,
        description="Whether the user's answer is correct or not.",
        alias="is_correct",
    )


class MessageDetails(BaseModel):
    """
    Represents the structure of the message details.

    Attributes:
        question (str): The text of the question.
        correctness (Correctness): Whether the user's answer is correct
        or not.
        correct_answers (Answers): The correct answers to the question.
        answers (Answers): The user's answers to the question.
    """

    question: str = Field(..., description="The text of the question.")
    correctness: Correctness = Field(
        ..., description="Whether the user's answer is correct or not."
    )
    correct_answers: Answers = Field(
        ..., description="The correct answers to the question."
    )
    answers: Answers = Field(
        ..., description="The user's answers to the question."
    )


class SystemDetails(BaseModel):
    """
    Represents the structure of the system details.

    Attributes:
        theme (str): The theme of the task.
        description (str): The description of the task.
        goal (str): The goal of the task.
        user_level (PositiveInt): The level of the user.
    """

    theme: str = Field(
        ..., description="The theme of the task.", alias="task_theme"
    )
    description: str = Field(
        ...,
        description="The description of the task.",
        alias="task_description",
    )
    goal: str = Field(
        ..., description="The goal of the task.", alias="task_goal"
    )
    user_level: PositiveInt = Field(..., description="The level of the user.")


class AnswerRequest(BaseModel):
    """
    Represents the structure of the answer request.

    Attributes:
        question (str): The text of the question.
        answers (Answers): A list of answers.
        start (bool): Whether the quiz has just started.
    """

    question: str = Field(..., description="The text of the question.")
    answers: Answers = Field(
        ..., description="The user's answers to the question."
    )
    start: bool = Field(..., description="Whether the quiz has just started.")


def compare_answers(
    quiz_answers_obj: QuizAnswers,
    user_answers_obj: AnswerRequest,
) -> tuple[bool, Answers]:
    """
    Compares the user's answers to the quiz correct answers.

    Args:
        quiz_answers_dict (QuizAnswers): The quiz answers.
        user_answers_dict (AnswerRequest): The user's answers to a
        question.

    Returns:
        tuple[bool, Answers]: A tuple containing the correctness of the
        user's answers and the correct answers.
    """

    user_answers = user_answers_obj.answers
    quiz_answers = quiz_answers_obj.answers

    index: PositiveInt | None = next(
        (
            index
            for (index, dict) in enumerate(quiz_answers)
            if dict.question == user_answers_obj.question
        ),
        None,
    )

    if index is None:
        raise KeyError("Question not found")

    return (
        quiz_answers[index].answers == user_answers,
        quiz_answers[index].answers,
    )
