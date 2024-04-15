import os
import time

from flask import Flask, Response, json, jsonify, request
from utils import Answer, Feedback, QuizData, StatusCode, compare_answers

API_ROOT = os.path.realpath(os.path.dirname(__file__))
data_url = os.path.join(API_ROOT, os.path.pardir, "data")
quiz_data = os.path.join(data_url, "quiz.json")
answers_data = os.path.join(data_url, "answers.json")
app = Flask(__name__)


@app.route("/api/data", methods=["GET"])
def get() -> tuple[QuizData, StatusCode]:
    """
    Retrieve the JSON quiz data.

    Returns:
        tuple[QuizData, StatusCode]: A tuple containing the loaded JSON data
        and an HTTP status code.
    """

    with open(quiz_data, encoding="utf-8") as f:
        data: QuizData = json.load(f)

    return data, 200


@app.route("/api/handler", methods=["POST"])
def handle_request() -> tuple[Response, StatusCode]:
    """
    Handle POST requests to the API and returns the feedback.

    Returns:
        tuple[Response, StatusCode]: A tuple containing the feedback and an
        HTTP status code.
    """

    data: Answer = request.get_json()
    if not data["answers"] or not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400

    with open(answers_data, encoding="utf-8") as f:
        answers = json.load(f)

    time.sleep(2)

    try:
        is_correct = compare_answers(answers, data)
    except KeyError:
        return jsonify({"error": "Invalid input"}), 400

    feedback: Feedback = {
        "feedback": is_correct and "Correct" or "Incorrect",
        "isCorrect": is_correct,
    }

    return jsonify(feedback), 200


if __name__ == "__main__":
    app.run(debug=True, port=3001, host="localhost")
