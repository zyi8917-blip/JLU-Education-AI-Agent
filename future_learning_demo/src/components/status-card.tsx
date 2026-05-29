type StatusCardProps = {
  title: string;
  value?: string;
  description: string;
  accent?: boolean;
  children?: React.ReactNode;
};

export function StatusCard({
  title,
  value,
  description,
  accent = false,
  children,
}: StatusCardProps) {
  return (
    <section className={accent ? "card card-accent" : "card"}>
      <p className="card-label">{title}</p>
      {value ? <h3 className="card-value">{value}</h3> : null}
      <p className="card-description">{description}</p>
      {children}
    </section>
  );
}
