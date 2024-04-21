import Markdown from "react-markdown";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ErrorMessage } from "@/components/error-message";

export function Feedback({
    content,
    failed = false,
}: {
    content: string;
    failed: boolean;
}) {
    return (
        <div className="mt-6">
            <div className="leading-loose font-bold text-teal-500">
                Feedback
            </div>
            <ScrollArea className="h-[19rem]">
                {failed ? (
                    <ErrorMessage error={content} className="mt-4" />
                ) : (
                    <Markdown className="space-y-2 mt-2">{content}</Markdown>
                )}
            </ScrollArea>
        </div>
    );
}
