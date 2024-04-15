export function Feedback({ content }: { content: string }) {
    return (
        <div className="mt-6">
            <div className="leading-loose font-bold text-teal-500">
                Feedback
            </div>
            <div>{content}</div>
        </div>
    );
}
