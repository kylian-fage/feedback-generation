from typing import TypedDict

type StatusCode = int


class QuizQuestion(TypedDict):
    """
    Represents a single question in the quiz, along with its options and the
    correct answer.

    Attributes:
        question (str): The text of the question.
        options (list[str]): A list of answer options.
    """

    question: str
    options: list[str]


class QuizData(TypedDict):
    """
    QuizData represents the structure of the quiz data.

    Attributes:
        quiz (dict[str, list[QuizQuestion]]): A list of questions, each with
        their options.
    """

    quiz: list[QuizQuestion]


class Answer(TypedDict):
    """
    Represents an answer to a question.

    Attributes:
        question (str): The text of the question.
        answers (list[str]): A list of answers.
    """

    question: str
    answers: list[str]


class QuizAnswers(TypedDict):
    """
    Represents the structure of the quiz answers.

    Attributes:
        answers (list[Answer]): A list of answers to questions.
    """

    answers: list[Answer]


class Feedback(TypedDict):
    """
    Represents the structure of the feedback.

    Attributes:
        feedback (str): The text of the feedback.
        isCorrect (bool): Whether the user's answer is correct or not.
    """

    feedback: str
    isCorrect: bool


def compare_answers(
    quiz_answers_dict: QuizAnswers,
    user_answers_dict: Answer,
) -> bool:
    """
    Compares the user's answers to the quiz correct answers.

    Args:
        quiz_answers_dict (QuizAnswers): The quiz answers.
        user_answers_dict (Answer): The user's answers to a question.

    Returns:
        bool: Whether the user's answers are correct or not.
    """

    user_answers = user_answers_dict["answers"]
    quiz_answers = quiz_answers_dict["answers"]

    index: int | None = next(
        (
            index
            for (index, dict) in enumerate(quiz_answers)
            if dict["question"] == user_answers_dict["question"]
        ),
        None,
    )

    if index is None:
        raise KeyError("Question not found")

    return quiz_answers[index]["answers"] == user_answers
