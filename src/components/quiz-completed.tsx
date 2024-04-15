import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";

export function QuizCompleted({ isVisible }: { isVisible: boolean }) {
    return (
        <Card
            className={`w-full max-w-xl mx-auto transition-opacity duration-500 ${
                isVisible ? "opacity-100" : "opacity-0"
            }`}
        >
            <CardContent className="text-center p-6">
                <div className="text-2xl font-bold">Quiz completed</div>
            </CardContent>
            <CardFooter className="mt-6 justify-center">
                <Button
                    variant="outline"
                    onClick={() => {
                        window.location.reload();
                    }}
                >
                    Restart
                </Button>
            </CardFooter>
        </Card>
    );
}
