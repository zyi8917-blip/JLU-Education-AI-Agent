import type { Metadata } from "next";
import "./globals.css";
import "scene-content-kit/styles.css";

export const metadata: Metadata = {
  title: "未来学习平台",
  description: "吉大未来学习 · AI 智能教育 Agent 平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
