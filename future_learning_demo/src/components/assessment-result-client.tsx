"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { AssessmentReport } from "@/components/assessment-report";
import { readSession } from "@/lib/demo-session";
import type { StoredAssessmentReport } from "@/lib/assessment/transform-report";

export function AssessmentResultClient() {
  const [report, setReport] = useState<StoredAssessmentReport | null>(null);

  useEffect(() => {
    const session = readSession();
    setReport(session.assessmentReport ?? null);
  }, []);

  if (!report) {
    return (
      <AppShell
        eyebrow="测评结果"
        title="尚未找到测评报告"
        subtitle="请先完成学习力测评，系统将根据你的回答生成专属报告。"
        actions={
          <Link className="primary-button" href="/assessment">
            开始测评
          </Link>
        }
      >
        <div className="card empty-state-card">
          <p>如果你刚刚完成测评，请尝试刷新页面；也可点击「重新测评」再答一遍。</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell
      eyebrow="测评结果"
      title="你的学习力画像已经生成"
      subtitle="以下是基于面谈回答形成的综合分析。你可以继续与画像助手对话，或进入课程与项目实践。"
      actions={
        <div className="inline-actions">
          <Link className="ghost-button" href="/portrait">
            进入画像对话
          </Link>
          <Link className="primary-button" href="/home">
            进入主页
          </Link>
        </div>
      }
    >
      <AssessmentReport report={report} />
    </AppShell>
  );
}
