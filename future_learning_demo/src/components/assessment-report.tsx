type AssessmentReportProps = {
  report: {
    report_title: string;
    basic_info: {
      user_name: string;
      assessment_date?: string;
      overall_grade: string;
      overall_level: number;
      max_level: number;
      core_description: string;
    };
    macro_ability_map: {
      title?: string;
      radar_data: Array<{
        dimension: string;
        value: number;
      }>;
    };
    challenges_and_experience: {
      title?: string;
      items: Array<{
        name: string;
        score: number;
        label: string;
      }>;
    };
  };
};

function MetricBar({ value, max = 5 }: { value: number; max?: number }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="metric-bar-track" aria-hidden="true">
      <div className="metric-bar-fill" style={{ width: `${pct}%` }} />
    </div>
  );
}

export function AssessmentReport({ report }: AssessmentReportProps) {
  const { basic_info, macro_ability_map, challenges_and_experience } = report;

  return (
    <div className="report-grid">
      <section className="card card-accent report-summary">
        <p className="card-label">{report.report_title}</p>
        <p className="report-user-line">
          {basic_info.user_name}
          {basic_info.assessment_date ? ` · ${basic_info.assessment_date}` : ""}
        </p>
        <h2>{basic_info.overall_grade}</h2>
        <p className="report-score">
          综合水平 {basic_info.overall_level.toFixed(1)} / {basic_info.max_level}
        </p>
        <p className="card-description">{basic_info.core_description}</p>
      </section>

      <section className="card">
        <div className="section-heading">
          <h2>{macro_ability_map.title ?? "多维能力画像"}</h2>
          <p>各维度得分（满分 5 分），数值越高表示该方面表现越稳定</p>
        </div>
        <div className="metric-list metric-list-bars">
          {macro_ability_map.radar_data.map((item) => (
            <div className="metric-row metric-row-bar" key={item.dimension}>
              <div className="metric-row-head">
                <span>{item.dimension}</span>
                <strong>{item.value.toFixed(1)}</strong>
              </div>
              <MetricBar value={item.value} />
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="section-heading">
          <h2>{challenges_and_experience.title ?? "重点关注维度"}</h2>
          <p>建议优先在这些方面制定小步快跑的提升计划</p>
        </div>
        <div className="metric-list">
          {challenges_and_experience.items.map((item) => (
            <div className="metric-row" key={item.name}>
              <span>{item.name}</span>
              <strong>
                {item.score.toFixed(0)} 分 · {item.label}
              </strong>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
