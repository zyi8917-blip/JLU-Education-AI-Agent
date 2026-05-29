import { AppShell } from "@/components/app-shell";
import { ProjectChat } from "@/components/project-chat";
import { projectScenario } from "@/data/demo-data";

export default function ProjectPage() {
  return (
    <AppShell
      eyebrow="Step 05 / Project Learning"
      title="用一次课程内 PBL 训练，完成从理解到设计的闭环"
      subtitle="项目页通过固定主题、固定智能体角色和对话式推进，让“做中学”在答辩中更容易被讲清楚。"
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
