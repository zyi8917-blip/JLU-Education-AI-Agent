"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { AssessmentLinks } from "@/components/assessment-actions";
import { StatusCard } from "@/components/status-card";
import { demoUser } from "@/data/demo-data";
import { readSession, type DemoSession } from "@/lib/demo-session";

export function HomeDashboard() {
  const [session, setSession] = useState<DemoSession | null>(null);

  useEffect(() => {
    setSession(readSession());
  }, []);

  if (!session) {
    return (
      <div className="center-screen">
        <div className="loading-card">正在载入个人学习空间...</div>
      </div>
    );
  }

  const report = session.assessmentReport;
  const assessmentStatus = session.assessmentCompleted ? "已完成" : "待完成";
  const projectStatus = session.projectCompleted ? "已完成" : "待开始";
  const grade = report?.basic_info.overall_grade ?? "—";
  const description =
    report?.basic_info.core_description ??
    "完成测评后，这里会展示你的学习力综合描述。";

  return (
    <AppShell
      eyebrow="个人学习空间"
      title={`欢迎回来，${demoUser.name}`}
      subtitle="在这里查看学习进度，并进入测评、画像对话、课程学习与项目实践。"
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
          description="人工智能基础：OpenClaw、大模型、Agent 与 RAG 等核心主题。"
        />
        <StatusCard
          title="学习力状态"
          value={grade}
          description={description.length > 96 ? `${description.slice(0, 96)}…` : description}
          accent
        />
      </section>

      <section className="dashboard-grid">
        <StatusCard
          title="学习力测评"
          value={assessmentStatus}
          description={
            session.assessmentCompleted
              ? "测评报告已生成，可查看详情或进入画像对话。"
              : "通过 10 道面谈题了解你的学习状态，约需 10–15 分钟。"
          }
          accent={session.assessmentCompleted}
        >
          {session.assessmentCompleted ? (
            <div className="inline-actions">
              <AssessmentLinks />
              <Link className="ghost-button" href="/portrait">
                画像对话
              </Link>
            </div>
          ) : (
            <Link className="ghost-button" href="/assessment">
              开始测评
            </Link>
          )}
        </StatusCard>

        <StatusCard
          title="课程学习"
          value={session.assessmentCompleted ? "可进入" : "需先完成测评"}
          description="八页互动课件，右侧智能体可解答课程相关问题。"
        >
          <Link className="ghost-button" href="/course">
            进入课程学习
          </Link>
        </StatusCard>

        <StatusCard
          title="项目实践"
          value={projectStatus}
          description="完成「课堂助教 Agent」方案设计，在对话中推进里程碑并提交成果。"
        >
          <Link className="ghost-button" href="/project">
            进入项目学习
          </Link>
        </StatusCard>
      </section>
    </AppShell>
  );
}
