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
      router.replace("/assessment");
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
          登录后将先完成一场学习力面谈，再进入课程学习与项目实践。
        </p>

        <form className="login-form" onSubmit={handleSubmit}>
          <label>
            账号
            <input
              value={account}
              onChange={(event) => setAccount(event.target.value)}
              placeholder="请输入账号"
            />
          </label>
          <label>
            密码
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="请输入密码"
            />
          </label>
          <button className="primary-button" type="submit">
            登录并开始测评
          </button>
        </form>

        <p className="login-footnote">演示环境：任意账号密码均可登录体验完整流程。</p>
      </section>
    </main>
  );
}
