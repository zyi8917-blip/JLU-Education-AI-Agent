import { AppShell } from "@/components/app-shell";
import { CourseLearningClient } from "@/components/course-learning-client";

export default function CoursePage() {
  return (
    <AppShell
      eyebrow="课程学习"
      title="在课件与智能体陪伴下学习"
      subtitle="左侧浏览课件，右侧向课堂助手提问。支持推荐问题与自由对话。"
    >
      <CourseLearningClient />
    </AppShell>
  );
}
