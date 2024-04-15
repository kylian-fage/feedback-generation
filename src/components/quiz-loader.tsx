import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function QuizLoader() {
    return (
        <Card
            key="1"
            className={`w-full max-w-xl h-[32rem] mx-auto flex flex-col justify-between`}
        >
            <CardContent className="p-6">
                <div className="flex items-center justify-between">
                    <Skeleton className="h-[2.5ex] w-[15em]" />
                    <Skeleton className="h-[2ex] w-[4em]" />
                </div>
                <hr className="mt-4" />
                <Skeleton className="h-[2ex] w-[20em] mt-4" />
                <Skeleton className="h-[2.5ex] w-[30em] mt-10 mb-4 leading-loose" />
                <div className="mt-6 space-y-2">
                    <Skeleton className="h-[5ex] w-full" />
                    <Skeleton className="h-[5ex] w-full" />
                    <Skeleton className="h-[5ex] w-full" />
                    <Skeleton className="h-[5ex] w-full" />
                </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-2 p-6">
                <Skeleton className="h-9 w-9 rounded-full" />
            </CardFooter>
        </Card>
    );
}
