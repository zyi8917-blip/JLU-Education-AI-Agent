"use client";

import { useRouter } from "next/navigation";
import { logout } from "@/lib/demo-session";

export function LogoutButton() {
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
    router.refresh();
  }

  return (
    <button className="ghost-button logout-button" onClick={handleLogout} type="button">
      退出登录
    </button>
  );
}
