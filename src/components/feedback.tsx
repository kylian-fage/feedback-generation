import Markdown from "react-markdown";
import { ScrollArea } from "@/components/ui/scroll-area";

export function Feedback({ content }: { content: string }) {
    return (
        <div className="mt-6">
            <div className="leading-loose font-bold text-teal-500">
                Feedback
            </div>
            <ScrollArea className="h-[19rem]">
                <Markdown>{content}</Markdown>
            </ScrollArea>
        </div>
    );
}
