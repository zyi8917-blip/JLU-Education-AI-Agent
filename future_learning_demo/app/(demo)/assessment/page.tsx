import { AppShell } from "@/components/app-shell";
import { AssessmentInterview } from "@/components/assessment-interview";

export default function AssessmentPage() {
  return (
    <AppShell
      eyebrow="Step 01 / Learning Assessment"
      title="先用一场对话式测评，了解你的学习状态"
      subtitle="这里不再使用聊天气泡，而是参考 learning_power 的一对一语音面谈形态，让学习者专注当前问题与回答。"
    >
      <AssessmentInterview />
    </AppShell>
  );
}
