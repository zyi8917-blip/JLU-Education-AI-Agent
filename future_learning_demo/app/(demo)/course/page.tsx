import { AppShell } from "@/components/app-shell";
import { CourseLearningClient } from "@/components/course-learning-client";

export default function CoursePage() {
  return (
    <AppShell
      eyebrow="Step 04 / Course Learning"
      title="在课件与问答之间，体验被智能体陪伴的学习过程"
      subtitle="左侧展示固定 PPT，右侧支持脚本答疑或大模型流式答疑（见右侧开关与 .env.local）。"
    >
      <CourseLearningClient />
    </AppShell>
  );
}
