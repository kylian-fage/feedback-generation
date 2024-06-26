import { Feedback } from "@/components/feedback";
import { LoadingSpinner } from "@/components/loading-spinner";
import { ModeToggle } from "@/components/mode-toggle";
import { QuizCompleted } from "@/components/quiz-completed";
import { QuizLoader } from "@/components/quiz-loader";
import { ThemeProvider } from "@/components/theme-provider";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import {
    ChevronRight,
    CircleCheck,
    CircleHelp,
    CircleX,
    RotateCcw,
} from "lucide-react";
import Markdown from "react-markdown";

import { useEffect, useState } from "react";
import { ErrorMessage } from "@/components/error-message";

type Option = string;
type Question = string;
type Answer = string;
interface QuestionData {
    question: Question;
    options: Option[];
}
interface Answers {
    question: string;
    answers: Answer[];
    start: boolean;
}
interface QuizData {
    quiz: QuestionData[];
}

/**
 * Render the main App component.
 *
 * @returns The main page component.
 */
export default function App() {
    return (
        <ThemeProvider>
            <div className="flex min-h-screen items-center justify-center relative">
                <div className="absolute top-4 right-4">
                    <ModeToggle />
                </div>
                <Quiz />
            </div>
        </ThemeProvider>
    );
}

/**
 * Render a quiz component with interactive features.
 *
 * @returns The main quiz component.
 */
function Quiz() {
    const [selectedAnswers, setSelectedAnswers] = useState<Answer[]>([]);
    const [answers, setAnswers] = useState<Answers>({
        question: "",
        answers: [],
        start: false,
    });
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [isVisible, setIsVisible] = useState(true);
    const [isCorrect, setIsCorrect] = useState(false);
    const [quizCompleted, setQuizCompleted] = useState(false);
    const [quizData, setQuizData] = useState<QuizData>({
        quiz: [],
    });
    const [isLoading, setIsLoading] = useState(false);
    const [feedback, setFeedback] = useState("");
    const [start, setStart] = useState(false);
    const [dataFetchingFailed, setDataFetchingFailed] = useState(false);
    const [feedbackGenerationFailed, setFeedbackGenerationFailed] =
        useState(false);
    const [attempts, setAttempts] = useState(1);
    const [score, setScore] = useState(0);

    const maxAttempts = 2;
    const points = 10;

    useEffect(() => {
        setTimeout(() => {
            fetch("/api/data")
                .then((response) => {
                    if (response.status !== 200 && response.status !== 500) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    if (data.error) {
                        console.error("API Error:", data.error);
                        setDataFetchingFailed(true);
                    } else if (data["quiz"] === undefined) {
                        throw new Error("Network response was not ok");
                    } else {
                        setQuizData(data);
                        setStart(true);
                    }
                })
                .catch((error) => {
                    console.error(
                        "An error occurred while fetching the quiz data",
                        error
                    );
                    setDataFetchingFailed(true);
                });
        }, 1000);
    }, []);

    /**
     * Handle feedback submission.
     *
     * @returns A promise that resolves once the feedback is submitted.
     */
    const handleFeedback = async (): Promise<void> => {
        if (!quizCompleted) {
            setAnswers({
                question: quizData.quiz[currentQuestionIndex].question,
                answers: selectedAnswers,
                start: start,
            });
            setStart(false);
        }
        setIsLoading(true);
    };

    /**
     * Handle the next view.
     *
     * @returns A promise that resolves once the next view is rendered.
     */
    const handleNextView = async (): Promise<void> => {
        setTimeout(() => {
            if (
                (isCorrect || attempts >= maxAttempts) &&
                currentQuestionIndex < quizData.quiz.length - 1
            ) {
                setIsVisible(false);
                setCurrentQuestionIndex(currentQuestionIndex + 1);
                setSelectedAnswers([]);
                setFeedback("");
                setIsCorrect(false);
                setAnswers({
                    question: "",
                    answers: [],
                    start: false,
                });
                setScore(isCorrect ? points / attempts + score : 0 + score);
                setAttempts(1);
            } else if (
                !isCorrect &&
                currentQuestionIndex < quizData.quiz.length &&
                attempts < maxAttempts
            ) {
                setIsVisible(false);
                setFeedback("");
                setAnswers({
                    question: "",
                    answers: [],
                    start: false,
                });
                setAttempts(attempts + 1);
            } else {
                setIsLoading(true);
                setQuizCompleted(true);
                setScore(isCorrect ? points / attempts + score : 0 + score);
                setAttempts(1);
            }
            setIsVisible(true);
        }, 500);
    };

    /**
     * Generate feedback based on answers sent to the server.
     *
     * @returns A promise that resolves once the feedback is generated.
     */
    const generateFeedback = async (): Promise<void> => {
        if (answers.answers.length > 0) {
            await fetch("/api/handler", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(answers),
            })
                .then((response) => {
                    if (response.status !== 200 && response.status !== 500) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then((data) => {
                    if (data.error) {
                        console.error("API Error:", data.error);
                        setIsCorrect(
                            data["isCorrect"] === undefined
                                ? true
                                : data["isCorrect"]
                        );
                        setFeedback(
                            "We're sorry, but an unexpected error occurred while generating feedback."
                        );
                        setFeedbackGenerationFailed(true);
                    } else if (data["feedback"] === undefined) {
                        throw new Error("Network response was not ok");
                    } else {
                        setFeedback(data["feedback"]);
                        setIsCorrect(data["isCorrect"]);
                        setFeedbackGenerationFailed(false);
                    }
                })
                .catch((error) => {
                    console.error(
                        "An error occurred while sending the answers",
                        error
                    );
                    setFeedback(
                        "We're sorry, but an unexpected error occurred while generating feedback."
                    );
                    setIsCorrect(true);
                    setFeedbackGenerationFailed(true);
                });
        }
    };

    /**
     * Generate final feedback based on the history of feedbacks.
     *
     * @returns A promise that resolves once the feedback is generated.
     */
    const generateFinalFeedback = async (): Promise<void> => {
        await fetch("/api/final")
            .then((response) => {
                if (response.status !== 200 && response.status !== 500) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then((data) => {
                if (data.error) {
                    console.error("API Error:", data.error);
                    setFeedback("");
                    setFeedbackGenerationFailed(true);
                } else if (data["feedback"] === undefined) {
                    throw new Error("Network response was not ok");
                } else {
                    setFeedback(data["feedback"]);
                    setFeedbackGenerationFailed(false);
                }
            })
            .catch((error) => {
                console.error(
                    "An error occurred while sending the answers",
                    error
                );
                setFeedback("");
                setFeedbackGenerationFailed(true);
            });
    };

    useEffect(() => {
        if (isLoading && !quizCompleted) {
            generateFeedback().then(() => {
                setIsLoading(false);
            });
        } else if (isLoading && quizCompleted) {
            generateFinalFeedback().then(() => {
                setIsLoading(false);
            });
        }
    }, [isLoading]);

    if (quizCompleted && !isLoading) {
        return (
            <QuizCompleted
                isVisible={isVisible}
                score={Math.round(
                    (score / (quizData.quiz.length * points)) * 100
                )}
                feedback={feedback}
                failed={feedbackGenerationFailed}
            />
        );
    }

    if (dataFetchingFailed) {
        return (
            <ErrorMessage
                className="max-w-xl mx-auto p-4"
                error="An error occurred while fetching the quiz data. Please try again later."
            />
        );
    }

    /**
     * Handle option click.
     *
     * @param answer - The option that was clicked.
     */
    const handleOptionClick = (answer: Option) => {
        if (selectedAnswers.includes(answer)) {
            setSelectedAnswers(selectedAnswers.filter((a) => a !== answer));
            return;
        }
        setSelectedAnswers([...selectedAnswers, answer]);
    };

    if (quizData.quiz.length === 0) return <QuizLoader />;

    return (
        <Card
            key="1"
            className={`w-full max-w-xl h-[32rem] mx-auto transition-opacity duration-500 grid grid-cols-1 content-between ${
                isVisible ? "opacity-100" : "opacity-0"
            }`}
        >
            <CardContent className="p-6 pb-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        {isCorrect && feedback ? (
                            <CircleCheck className="h-6 w-6 text-lime-500 animate-pulsing" />
                        ) : null}
                        {!isCorrect && feedback ? (
                            <CircleX className="h-6 w-6 text-red-500 animate-wobble" />
                        ) : null}
                        {!feedback ? (
                            <CircleHelp className="h-6 w-6 text-teal-500" />
                        ) : null}
                        <div className="font-bold text-teal-500">
                            Question {currentQuestionIndex + 1}
                        </div>
                    </div>
                    <div className="text-sm">
                        {currentQuestionIndex + 1} of {quizData.quiz.length}
                    </div>
                </div>
                <hr className="mt-4" />
                {feedback ? (
                    <Feedback
                        content={feedback}
                        failed={feedbackGenerationFailed}
                    />
                ) : (
                    <div>
                        <div className="mt-4">
                            <div className="leading-loose text-sm text-gray-500 dark:text-gray-400">
                                Select the correct answer(s) for the following
                                question.
                            </div>
                        </div>
                        <div className="mt-6">
                            <div className="leading-loose font-bold text-teal-500">
                                <Markdown>
                                    {
                                        quizData.quiz[currentQuestionIndex]
                                            .question
                                    }
                                </Markdown>
                            </div>
                        </div>
                        <div className="mt-6">
                            <div className="space-y-2">
                                {quizData.quiz[
                                    currentQuestionIndex
                                ].options.map((option, index) => (
                                    <div key={index}>
                                        <Button
                                            variant={`${
                                                selectedAnswers.includes(option)
                                                    ? "default"
                                                    : "outline"
                                            }`}
                                            className="w-full text-wrap h-fit border"
                                            onClick={() =>
                                                handleOptionClick(option)
                                            }
                                        >
                                            <Markdown>{option}</Markdown>
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
            <CardFooter className="flex justify-end gap-2 pr-6 pb-6 pt-2">
                <Button
                    variant="outline"
                    size="icon"
                    className="rounded-full"
                    onClick={feedback ? handleNextView : handleFeedback}
                    disabled={selectedAnswers.length === 0 || isLoading}
                >
                    {isLoading ? <LoadingSpinner className="h-4 w-4" /> : null}
                    {(isCorrect && !isLoading) ||
                    (!feedback && !isCorrect && !isLoading) ||
                    (attempts >= maxAttempts && !isLoading) ? (
                        <ChevronRight className="h-4 w-4" />
                    ) : null}
                    {!isCorrect &&
                    feedback &&
                    attempts < maxAttempts &&
                    !isLoading ? (
                        <RotateCcw className="h-4 w-4" />
                    ) : null}
                </Button>
            </CardFooter>
        </Card>
    );
}
