import Link from "next/link";
import { Modal } from "@/components/modal";
import { projectScenario } from "@/data/demo-data";

type ProjectFeedbackModalProps = {
  open: boolean;
  onClose: () => void;
};

export function ProjectFeedbackModal({
  open,
  onClose,
}: ProjectFeedbackModalProps) {
  return (
    <Modal
      open={open}
      title="学习力提升反馈"
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
