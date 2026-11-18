import { AppShell } from "@/components/app-shell";
import { AssessmentInterview } from "@/components/assessment-interview";

export default function AssessmentPage() {
  return (
    <AppShell
      eyebrow="学习力测评"
      title="通过一场面谈，了解你的学习状态"
      subtitle="共 10 个问题，请像日常聊天一样自然作答。完成后将自动生成你的学习力报告。"
    >
      <AssessmentInterview />
    </AppShell>
  );
}
