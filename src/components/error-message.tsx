import { Card, CardContent } from "@/components/ui/card";
import { CircleAlert } from "lucide-react";

export function ErrorMessage({
    error,
    className,
}: {
    error: string;
    className?: string;
}) {
    return (
        <Card
            className={`w-full bg-red-500 bg-opacity-10 border border-red-500 ${className}`}
        >
            <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-4 text-red-500">
                    <CircleAlert />
                    <h3 className="font-bold">Error</h3>
                </div>
                <p>{error}</p>
            </CardContent>
        </Card>
    );
}
