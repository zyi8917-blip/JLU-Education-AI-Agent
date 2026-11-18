"use client";

import type {
  PortraitData,
  StoredAssessmentReport,
} from "@/lib/assessment/transform-report";

export type DemoSession = {
  isLoggedIn: boolean;
  assessmentCompleted: boolean;
  projectCompleted: boolean;
  projectDeliverable?: string;
  assessmentReport?: StoredAssessmentReport;
  portraitData?: PortraitData;
  assessmentSource?: string;
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
    assessmentCompleted: false,
  };
  writeSession(nextSession);
  return nextSession;
}

export function logout() {
  writeSession(defaultSession);
  return defaultSession;
}

export function restartAssessment() {
  const nextSession = {
    ...readSession(),
    assessmentCompleted: false,
    assessmentReport: undefined,
    portraitData: undefined,
    assessmentSource: undefined,
  };
  writeSession(nextSession);
  return nextSession;
}

export function saveAssessmentResult(input: {
  report: StoredAssessmentReport;
  portrait_data: PortraitData;
  source?: string;
}) {
  const nextSession = {
    ...readSession(),
    assessmentCompleted: true,
    assessmentReport: input.report,
    portraitData: input.portrait_data,
    assessmentSource: input.source,
  };
  writeSession(nextSession);
  return nextSession;
}

export function completeProject(deliverable?: string) {
  const nextSession = {
    ...readSession(),
    projectCompleted: true,
    projectDeliverable: deliverable,
  };
  writeSession(nextSession);
  return nextSession;
}
