import Markdown from "react-markdown";

export function Feedback({ content }: { content: string }) {
    return (
        <div className="mt-6">
            <div className="leading-loose font-bold text-teal-500">
                Feedback
            </div>
            <div>
                <Markdown>{content}</Markdown>
            </div>
        </div>
    );
}
