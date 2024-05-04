import os
from datetime import datetime
from uuid import uuid4

from flask import Flask, Response, json, jsonify, request
from langchain_community.chat_message_histories.in_memory import (
    ChatMessageHistory,
)
from loguru import logger
from pydantic import ValidationError

from .helpers import (
    API_ROOT,
    data_url,
    generate_feedback,
    generate_final_feedback,
    get_runnable,
)
from .utils import (
    AnswerRequest,
    Correctness,
    Feedback,
    FinalFeedback,
    MessageDetails,
    QuizAnswers,
    QuizData,
    StatusCode,
    SystemDetails,
    compare_answers,
)

quiz_data = os.path.join(data_url, "quiz.json")
answers_data = os.path.join(data_url, "answers.json")

with open(os.path.join(data_url, "details.json"), encoding="utf-8") as f:
    details = SystemDetails(**json.load(f)["details"])

history_store: dict[str, ChatMessageHistory] = {}
runnable = get_runnable(history_store, details)
session_id = ""

log_url = os.path.join(API_ROOT, os.path.pardir, "log")
logger.add(
    os.path.join(
        log_url,
        f"api_dev_{datetime.now().strftime('%Y%m%dT%H%M%S')}_error.log",
    )
)

app = Flask(__name__)


@app.route("/api/data", methods=["GET"])
def get() -> tuple[Response, StatusCode]:
    """
    Retrieve the JSON quiz data.

    Returns:
        tuple[Response, StatusCode]: A tuple containing the loaded JSON
        data and an HTTP status code or an error message and
        an HTTP status code.
    """

    with open(quiz_data, encoding="utf-8") as file:
        try:
            data: QuizData = QuizData(**json.load(file))
        except ValidationError as exc:
            logger.error(exc)
            return jsonify({"error": "Invalid data"}), 500

    return jsonify(data.model_dump()), 200


@app.route("/api/handler", methods=["POST"])
def handle_request() -> tuple[Response, StatusCode]:
    """
    Handle POST requests to the API and returns the feedback.

    Returns:
        tuple[Response, StatusCode]: A tuple containing the feedback or,
        in case of an error, an error message and an HTTP status code.
    """

    data = AnswerRequest(**request.get_json())
    if not data.answers:
        logger.error("Received an empty answer list.")
        return jsonify({"error": "Invalid input"}), 400

    with open(answers_data, encoding="utf-8") as file:
        answers = QuizAnswers(**json.load(file))

    try:
        is_correct, correct_answers = compare_answers(answers, data)
    except KeyError:
        logger.error("Received an invalid answer list.")
        return jsonify({"error": "Invalid input"}), 400

    global session_id

    if data.start:
        session_id = str(uuid4()).split("-")[0]

    message_details = MessageDetails(
        question=data.question,
        correctness=is_correct
        and Correctness.correct
        or Correctness.incorrect,
        correct_answers=correct_answers,
        answers=data.answers,
    )

    try:
        feedback = Feedback(
            feedback=generate_feedback(runnable, session_id, message_details),
            is_correct=is_correct,
        )
    except Exception as e:
        logger.error(e)
        return jsonify({"error": str(e), "isCorrect": is_correct}), 500

    return jsonify(feedback.model_dump()), 200


@app.route("/api/final", methods=["GET"])
def final_feedback() -> tuple[Response, StatusCode]:
    """
    Generate the final feedback.

    Returns:
        tuple[Response, StatusCode]: A tuple containing the final
        feedback or, in case of an error, an error message and an
        HTTP status code.
    """

    try:
        final_feedback = FinalFeedback(
            feedback=generate_final_feedback(runnable, session_id)
        )
    except Exception as e:
        logger.error(e)
        return jsonify({"error": str(e)}), 500

    return jsonify(final_feedback.model_dump()), 200


def main() -> None:
    app.run(debug=True, port=3001, host="localhost")
