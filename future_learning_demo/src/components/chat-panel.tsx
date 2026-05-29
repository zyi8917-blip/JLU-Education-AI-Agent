export type ChatMessage = {
  id: string;
  role: "agent" | "user" | "system";
  speaker: string;
  content: string;
};

type ChatPanelProps = {
  title: string;
  description?: string;
  messages: ChatMessage[];
  composer?: React.ReactNode;
};

export function ChatPanel({
  title,
  description,
  messages,
  composer,
}: ChatPanelProps) {
  return (
    <section className="card chat-card">
      <div className="section-heading">
        <div>
          <h2>{title}</h2>
          {description ? <p>{description}</p> : null}
        </div>
      </div>

      <div className="chat-log">
        {messages.map((message) => (
          <article
            key={message.id}
            className={`chat-bubble chat-${message.role}`}
          >
            <p className="chat-speaker">{message.speaker}</p>
            <p>{message.content}</p>
          </article>
        ))}
      </div>

      {composer ? <div className="chat-composer">{composer}</div> : null}
    </section>
  );
}
