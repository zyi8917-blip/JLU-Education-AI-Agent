"use client";

import {
  detectCompletedMilestones,
  projectMilestones,
} from "@/lib/chat/project-prompts";
import type { ChatMessage } from "@/components/chat-panel";

type ProjectMilestoneListProps = {
  messages: ChatMessage[];
};

export function ProjectMilestoneList({ messages }: ProjectMilestoneListProps) {
  const completed = detectCompletedMilestones(messages);

  return (
    <ul className="milestone-checklist">
      {projectMilestones.map((item) => {
        const done = completed.includes(item.id);
        return (
          <li className={done ? "milestone-done" : undefined} key={item.id}>
            <span className="milestone-dot" aria-hidden="true">
              {done ? "✓" : "○"}
            </span>
            <span>{item.label}</span>
          </li>
        );
      })}
    </ul>
  );
}
