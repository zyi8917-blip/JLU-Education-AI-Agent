import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { AssessmentReport } from "@/components/assessment-report";
import { assessmentReport } from "@/data/demo-data";

export default function AssessmentResultPage() {
  return (
    <AppShell
      eyebrow="Step 02 / Assessment Result"
      title="你的学习力画像已经生成"
      subtitle="这份结果报告会作为首页与后续项目反馈的起点，帮助讲清“测评后进入学习”的主线。"
      actions={
        <Link className="primary-button" href="/home">
          进入主页
        </Link>
      }
    >
      <AssessmentReport report={assessmentReport} />
    </AppShell>
  );
}
