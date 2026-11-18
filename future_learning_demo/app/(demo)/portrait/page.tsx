import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { PortraitChat } from "@/components/portrait-chat";

export default function PortraitPage() {
  return (
    <AppShell
      eyebrow="画像对话"
      title="与学习力画像助手对话"
      subtitle="基于你的测评结果，获取个性化的学习策略、薄弱项分析与行动计划。"
      actions={
        <div className="inline-actions">
          <Link className="ghost-button" href="/assessment/result">
            查看测评报告
          </Link>
          <Link className="primary-button" href="/course">
            进入课程学习
          </Link>
        </div>
      }
    >
      <PortraitChat />
    </AppShell>
  );
}
