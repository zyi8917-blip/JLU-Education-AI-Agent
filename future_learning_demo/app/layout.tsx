import type { Metadata } from "next";
import "./globals.css";
import "scene-content-kit/styles.css";

export const metadata: Metadata = {
  title: "未来学习平台 Demo",
  description: "用于答辩演示的未来学习平台最小闭环 Demo",
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
