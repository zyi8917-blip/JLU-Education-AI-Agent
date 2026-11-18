import Link from "next/link";
import { LogoutButton } from "@/components/logout-button";

type AppShellProps = {
  eyebrow?: string;
  title: string;
  subtitle: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
};

export function AppShell({
  eyebrow,
  title,
  subtitle,
  actions,
  children,
}: AppShellProps) {
  return (
    <main className="page-shell">
      <header className="topbar">
        <div>
          <div className="brand-mark">未来学习平台</div>
          <p className="topbar-note">AI Learning Loop · 吉大未来学习</p>
        </div>
        <nav className="topbar-nav">
          <Link href="/home">主页</Link>
          <Link href="/assessment">学习力测评</Link>
          <Link href="/portrait">画像对话</Link>
          <Link href="/course">课程学习</Link>
          <Link href="/project">项目学习</Link>
          <LogoutButton />
        </nav>
      </header>

      <section className="page-hero">
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <div className="page-hero-row">
          <div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>
          {actions ? <div className="hero-actions">{actions}</div> : null}
        </div>
      </section>

      {children}
    </main>
  );
}
