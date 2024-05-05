import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { ErrorMessage } from "@/components/error-message";
import { ScrollArea } from "@/components/ui/scroll-area";
import Markdown from "react-markdown";

export function QuizCompleted({
    isVisible,
    score,
    feedback,
    failed,
}: {
    isVisible: boolean;
    score: number;
    feedback: string;
    failed: boolean;
}) {
    return (
        <Card
            className={`w-full max-w-xl mx-auto transition-opacity duration-500 ${
                isVisible ? "opacity-100" : "opacity-0"
            }`}
        >
            <CardContent className="p-6 pb-2">
                <div className="text-center text-3xl font-bold mb-6">
                    Your score
                </div>
                <div className="text-center text-6xl font-bold">
                    {score} <span className="text-4xl">%</span>
                </div>
                {feedback && !failed ? (
                    <ScrollArea
                        className="mt-6 p-4 border rounded-lg"
                        maxHeight="15rem"
                    >
                        <Markdown className={"space-y-2"}>{feedback}</Markdown>
                    </ScrollArea>
                ) : failed ? (
                    <ErrorMessage
                        error={
                            "We're sorry, but an unexpected error occurred while generating feedback."
                        }
                        className="mt-4"
                    />
                ) : null}
            </CardContent>
            <CardFooter className="mt-4 justify-center">
                <Button
                    onClick={() => {
                        window.location.reload();
                    }}
                    className="w-full"
                >
                    Retake quiz
                </Button>
            </CardFooter>
        </Card>
    );
}
