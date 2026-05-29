import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { StatusCard } from "@/components/status-card";
import { assessmentReport, demoUser } from "@/data/demo-data";

export default function HomePage() {
  return (
    <AppShell
      eyebrow="Step 03 / Learning Dashboard"
      title="欢迎进入你的个人学习空间"
      subtitle="这是一个克制的个人学习驾驶舱：保留状态感、任务感和下一步入口，不做花哨可视化。"
    >
      <section className="dashboard-grid">
        <StatusCard
          title="当前学习者"
          value={demoUser.name}
          description={`${demoUser.role} · ${demoUser.cohort}`}
        />
        <StatusCard
          title="当前课程"
          value={demoUser.currentCourse}
          description="课程内容聚焦人工智能的关键趋势、能力形态和应用场景。"
        />
        <StatusCard
          title="学习力状态"
          value={assessmentReport.basic_info.overall_grade}
          description={assessmentReport.basic_info.core_description}
          accent
        />
      </section>

      <section className="dashboard-grid">
        <StatusCard
          title="课程学习入口"
          description="进入课件学习页，一边看 PPT，一边与课堂 Agent 交流。"
        >
          <Link className="ghost-button" href="/course">
            进入课程学习
          </Link>
        </StatusCard>
        <StatusCard
          title="项目学习入口"
          description="进入 PBL 训练页，用一次课程内应用案例完成做中学闭环。"
        >
          <Link className="ghost-button" href="/project">
            进入项目学习
          </Link>
        </StatusCard>
      </section>
    </AppShell>
  );
}
