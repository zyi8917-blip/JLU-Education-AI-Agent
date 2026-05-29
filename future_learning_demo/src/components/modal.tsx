type ModalProps = {
  open: boolean;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
};

export function Modal({ open, title, children, footer }: ModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div className="section-heading">
          <h2>{title}</h2>
        </div>
        <div className="modal-body">{children}</div>
        {footer ? <div className="modal-footer">{footer}</div> : null}
      </div>
    </div>
  );
}
