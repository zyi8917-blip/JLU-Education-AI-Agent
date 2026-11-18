"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { readSession } from "@/lib/demo-session";

export function RouteGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  const session = useMemo(() => readSession(), [pathname]);

  useEffect(() => {
    if (!session.isLoggedIn) {
      router.replace("/login");
      return;
    }

    if (
      !session.assessmentCompleted &&
      pathname !== "/assessment" &&
      pathname !== "/assessment/result" &&
      pathname !== "/portrait"
    ) {
      router.replace("/assessment");
      return;
    }

    setReady(true);
  }, [pathname, router, session.assessmentCompleted, session.isLoggedIn]);

  if (!ready) {
    return (
      <div className="center-screen">
        <div className="loading-card">正在载入学习空间...</div>
      </div>
    );
  }

  return <>{children}</>;
}
