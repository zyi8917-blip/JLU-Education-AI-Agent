# Future Learning Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable Next.js + TypeScript defense demo for the Future Learning Platform with a complete static learning loop from login to project-completion feedback.

**Architecture:** Create a standalone App Router Next.js app inside `future_learning_demo`, backed by local static demo assets and lightweight browser persistence. Reuse `scene-content-kit` for slide rendering where practical, mirror `learning_power` report structure for assessment output, and keep all AI interactions deterministic through scripted data and simple keyword matching.

**Tech Stack:** Next.js, React, TypeScript, CSS Modules / global CSS, localStorage/session utilities, local static JSON/TS data

---

### Task 1: App Skeleton And Dependencies

**Files:**
- Create: `future_learning_demo/package.json`
- Create: `future_learning_demo/tsconfig.json`
- Create: `future_learning_demo/next.config.ts`
- Create: `future_learning_demo/next-env.d.ts`
- Create: `future_learning_demo/app/layout.tsx`
- Create: `future_learning_demo/app/page.tsx`
- Create: `future_learning_demo/app/globals.css`

- [ ] **Step 1: Create the minimal app manifest**

```json
{
  "name": "future-learning-demo",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }
}
```

- [ ] **Step 2: Add the root layout and redirecting index page**

```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```

```tsx
import { redirect } from "next/navigation";

export default function IndexPage() {
  redirect("/login");
}
```

- [ ] **Step 3: Run the build once dependencies are installed**

Run: `npm run build`
Expected: Next.js build starts and confirms the app compiles successfully.

### Task 2: Structured Demo Data Layer

**Files:**
- Create: `future_learning_demo/src/data/assessment-result.json`
- Create: `future_learning_demo/src/data/course-qa.json`
- Create: `future_learning_demo/src/data/assessment-questions.ts`
- Create: `future_learning_demo/src/data/pbl-project.json`
- Create: `future_learning_demo/src/data/slides.ts`
- Modify: `future_learning_demo/demo-assets/class_agent_QA.md`

- [ ] **Step 1: Convert the existing course QA markdown into structured JSON**

```json
{
  "suggestedQuestions": [],
  "entries": []
}
```

- [ ] **Step 2: Create fixed assessment question data for 10 interview-style prompts**

```ts
export const assessmentQuestions = [
  {
    id: "motivation-1",
    dimension: "学习动机",
    prompt: "..."
  }
];
```

- [ ] **Step 3: Add a fixed course-internal PBL scenario**

```json
{
  "title": "为《人工智能基础》课程设计一个课堂助教 Agent 应用方案",
  "goal": "...",
  "agents": [],
  "milestones": []
}
```

- [ ] **Step 4: Run a type-check/build after importing the data**

Run: `npm run build`
Expected: Static data imports compile with no JSON or TypeScript import issues.

### Task 3: Shared Design System And Layout Primitives

**Files:**
- Create: `future_learning_demo/src/components/app-shell.tsx`
- Create: `future_learning_demo/src/components/status-card.tsx`
- Create: `future_learning_demo/src/components/chat-panel.tsx`
- Create: `future_learning_demo/src/components/modal.tsx`
- Modify: `future_learning_demo/app/globals.css`

- [ ] **Step 1: Add global design tokens reflecting DESIGN.md**

```css
:root {
  --bg: #050507;
  --surface: #101010;
  --border: #3d3a39;
  --accent: #00d992;
  --text: #f2f2f2;
}
```

- [ ] **Step 2: Build reusable shells for cards, chat rows, and modal content**

```tsx
export function StatusCard(...) {
  return <section>...</section>;
}
```

- [ ] **Step 3: Run build to verify shared components compile**

Run: `npm run build`
Expected: Shared UI primitives compile without type or CSS import errors.

### Task 4: Flow State And Route Guards

**Files:**
- Create: `future_learning_demo/src/lib/demo-session.ts`
- Create: `future_learning_demo/src/components/route-guard.tsx`
- Create: `future_learning_demo/app/(demo)/layout.tsx`
- Create: `future_learning_demo/app/login/page.tsx`

- [ ] **Step 1: Write session helpers for localStorage-backed login and progress flags**

```ts
export type DemoSession = {
  isLoggedIn: boolean;
  assessmentCompleted: boolean;
  projectCompleted: boolean;
};
```

- [ ] **Step 2: Gate protected routes and leave `/login` public**

```tsx
if (!session.isLoggedIn) {
  router.replace("/login");
}
```

- [ ] **Step 3: Implement the login page with a simple form and persistent login**

```tsx
<form onSubmit={handleLogin}>
  <input />
  <input type="password" />
  <button type="submit">登录</button>
</form>
```

- [ ] **Step 4: Run build and manually verify login redirects**

Run: `npm run build`
Expected: Protected routes render in build output, login page compiles, no client/server boundary errors.

### Task 5: Assessment Flow And Report Page

**Files:**
- Create: `future_learning_demo/app/assessment/page.tsx`
- Create: `future_learning_demo/app/assessment/result/page.tsx`
- Create: `future_learning_demo/src/components/assessment-chat.tsx`
- Create: `future_learning_demo/src/components/assessment-report.tsx`

- [ ] **Step 1: Render one assessment question at a time in a chat-like flow**

```tsx
const currentQuestion = questions[currentIndex];
```

- [ ] **Step 2: Move to the next question after each answer and finish after 10 prompts**

```tsx
if (nextIndex >= questions.length) {
  completeAssessment();
  router.push("/assessment/result");
}
```

- [ ] **Step 3: Build the fixed result page using the imported report JSON**

```tsx
<AssessmentReport report={assessmentReport} />
```

- [ ] **Step 4: Run build and manually verify question progression**

Run: `npm run build`
Expected: Assessment route compiles and the result page imports the report data correctly.

### Task 6: Home Dashboard

**Files:**
- Create: `future_learning_demo/app/home/page.tsx`

- [ ] **Step 1: Implement a concise personal-learning dashboard**

```tsx
<main>
  <StatusCard title="当前课程" />
  <StatusCard title="学习力画像" />
  <Link href="/course">进入课程学习</Link>
  <Link href="/project">进入项目学习</Link>
</main>
```

- [ ] **Step 2: Run build to verify navigation and styling**

Run: `npm run build`
Expected: Home page compiles and both entry links are valid.

### Task 7: Course Learning Page With Slides And QA

**Files:**
- Create: `future_learning_demo/app/course/page.tsx`
- Create: `future_learning_demo/src/components/course-slide-viewer.tsx`
- Create: `future_learning_demo/src/components/course-qa-panel.tsx`

- [ ] **Step 1: Adapt the slide asset data into a left-column slide viewer**

```tsx
<CourseSlideViewer slides={slides} />
```

- [ ] **Step 2: Build the right-column QA panel with suggested prompts and fallback replies**

```tsx
<CourseQaPanel data={courseQaData} />
```

- [ ] **Step 3: Run build and manually verify slide assets resolve**

Run: `npm run build`
Expected: Course page compiles and static slide asset references resolve during build.

### Task 8: Project Learning Page And Completion Feedback

**Files:**
- Create: `future_learning_demo/app/project/page.tsx`
- Create: `future_learning_demo/src/components/project-chat.tsx`
- Create: `future_learning_demo/src/components/project-feedback-modal.tsx`

- [ ] **Step 1: Build the project page with task summary, participating agents, and guided chat**

```tsx
<ProjectChat scenario={projectScenario} />
```

- [ ] **Step 2: Mark the project complete when the user submits the final plan**

```tsx
setShowFeedback(true);
markProjectCompleted();
```

- [ ] **Step 3: Show a fixed learning-improvement modal**

```tsx
<ProjectFeedbackModal open={showFeedback} />
```

- [ ] **Step 4: Run build and manually verify project completion state**

Run: `npm run build`
Expected: Project page compiles, modal mounts correctly, and completion flow persists.

### Task 9: Final Verification

**Files:**
- Modify: any touched files as needed from verification fixes

- [ ] **Step 1: Run the full build**

Run: `npm run build`
Expected: Build exits with code 0.

- [ ] **Step 2: Run the app and click through the full demo**

Run: `npm run dev`
Expected: Login → assessment → result → home → course → project completes without blocking errors.
