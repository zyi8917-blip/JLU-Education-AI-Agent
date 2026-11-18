"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { restartAssessment } from "@/lib/demo-session";

export function RestartAssessmentButton() {
  const router = useRouter();

  function handleRestart() {
    restartAssessment();
    router.push("/assessment");
    router.refresh();
  }

  return (
    <button className="ghost-button" onClick={handleRestart} type="button">
      重新测评
    </button>
  );
}

export function AssessmentLinks() {
  return (
    <div className="inline-actions">
      <Link className="ghost-button" href="/assessment/result">
        查看测评报告
      </Link>
      <RestartAssessmentButton />
    </div>
  );
}
