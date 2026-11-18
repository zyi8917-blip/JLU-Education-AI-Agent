import Link from "next/link";
import { Modal } from "@/components/modal";
import { projectScenario } from "@/data/demo-data";

type ProjectFeedbackModalProps = {
  open: boolean;
  onClose: () => void;
  deliverable?: string;
};

export function ProjectFeedbackModal({
  open,
  onClose,
  deliverable,
}: ProjectFeedbackModalProps) {
  return (
    <Modal
      open={open}
      title="PBL 成果与学习力反馈"
      footer={
        <>
          <button className="ghost-button" onClick={onClose} type="button">
            继续查看
          </button>
          <Link className="primary-button" href="/home">
            返回主页
          </Link>
        </>
      }
    >
      {deliverable ? (
        <div className="deliverable-block">
          <p className="card-label">你的方案摘要</p>
          <pre className="deliverable-pre">{deliverable}</pre>
        </div>
      ) : null}
      <div className="feedback-list">
        {projectScenario.feedback.map((item) => (
          <section className="feedback-item" key={item.title}>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </section>
        ))}
      </div>
    </Modal>
  );
}
