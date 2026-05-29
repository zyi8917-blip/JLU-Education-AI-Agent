import { RouteGuard } from "@/components/route-guard";

export default function DemoLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <RouteGuard>{children}</RouteGuard>;
}
