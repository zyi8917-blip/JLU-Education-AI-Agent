"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { login, readSession } from "@/lib/demo-session";

export default function LoginPage() {
  const router = useRouter();
  const [account, setAccount] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    const session = readSession();
    if (session.isLoggedIn) {
      router.replace(session.assessmentCompleted ? "/home" : "/assessment");
    }
  }, [router]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!account.trim() || !password.trim()) {
      return;
    }

    login();
    router.push("/assessment");
  }

  return (
    <main className="login-shell">
      <section className="login-card">
        <p className="eyebrow">未来学习平台</p>
        <h1>登录后开始你的 AI 学习闭环</h1>
        <p className="login-subtitle">
          用一场简化学习力测评，进入《人工智能基础》的课程学习与项目实践。
        </p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            账号
            <input
              value={account}
              onChange={(event) => setAccount(event.target.value)}
              placeholder="输入任意账号即可进入 Demo"
            />
          </label>
          <label>
            密码
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="输入任意密码"
            />
          </label>
          <button className="primary-button" type="submit">
            登录并开始测评
          </button>
        </form>

        <div className="code-strip">
          <span>Demo Mode</span>
          <code>local-static-flow / no backend / deterministic agents</code>
        </div>
      </section>
    </main>
  );
}
