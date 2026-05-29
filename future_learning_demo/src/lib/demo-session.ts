"use client";

export type DemoSession = {
  isLoggedIn: boolean;
  assessmentCompleted: boolean;
  projectCompleted: boolean;
};

const STORAGE_KEY = "future-learning-demo-session";

export const defaultSession: DemoSession = {
  isLoggedIn: false,
  assessmentCompleted: false,
  projectCompleted: false,
};

export function readSession(): DemoSession {
  if (typeof window === "undefined") {
    return defaultSession;
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return defaultSession;
    }

    return {
      ...defaultSession,
      ...JSON.parse(raw),
    } as DemoSession;
  } catch {
    return defaultSession;
  }
}

export function writeSession(session: DemoSession) {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function login() {
  const nextSession = {
    ...readSession(),
    isLoggedIn: true,
  };
  writeSession(nextSession);
  return nextSession;
}

export function logout() {
  writeSession(defaultSession);
  return defaultSession;
}

export function completeAssessment() {
  const nextSession = {
    ...readSession(),
    assessmentCompleted: true,
  };
  writeSession(nextSession);
  return nextSession;
}

export function completeProject() {
  const nextSession = {
    ...readSession(),
    projectCompleted: true,
  };
  writeSession(nextSession);
  return nextSession;
}
