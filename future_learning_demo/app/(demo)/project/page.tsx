import { AppShell } from "@/components/app-shell";
import { ProjectChat } from "@/components/project-chat";
import { projectScenario } from "@/data/demo-data";

export default function ProjectPage() {
  return (
    <AppShell
      eyebrow="项目实践"
      title="完成一次课程内的 PBL 项目训练"
      subtitle="与教练、设计、评估三位智能体协作，按里程碑推进「课堂助教 Agent」方案并提交成果。"
    >
      <section className="split-layout project-layout">
        <section className="card sidebar-card">
          <div className="section-heading">
            <h2>项目任务</h2>
            <p>{projectScenario.summary}</p>
          </div>
          <div className="milestone-block">
            <p className="card-label">目标</p>
            <p>{projectScenario.goal}</p>
          </div>
          <div className="milestone-block">
            <p className="card-label">里程碑</p>
            <ul className="plain-list">
              {projectScenario.milestones.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="milestone-block">
            <p className="card-label">参与智能体</p>
            <ul className="plain-list">
              {projectScenario.agents.map((agent) => (
                <li key={agent.name}>
                  <strong>{agent.name}</strong>
                  <span>{agent.role}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
        <ProjectChat />
      </section>
    </AppShell>
  );
}
