type AssessmentReportProps = {
  report: {
    report_title: string;
    basic_info: {
      user_name: string;
      overall_grade: string;
      overall_level: number;
      max_level: number;
      core_description: string;
    };
    macro_ability_map: {
      radar_data: Array<{
        dimension: string;
        value: number;
      }>;
    };
    challenges_and_experience: {
      items: Array<{
        name: string;
        score: number;
        label: string;
      }>;
    };
  };
};

export function AssessmentReport({ report }: AssessmentReportProps) {
  return (
    <div className="report-grid">
      <section className="card card-accent report-summary">
        <p className="card-label">{report.report_title}</p>
        <h2>{report.basic_info.overall_grade}</h2>
        <p className="report-score">
          综合水平 {report.basic_info.overall_level} / {report.basic_info.max_level}
        </p>
        <p className="card-description">{report.basic_info.core_description}</p>
      </section>

      <section className="card">
        <div className="section-heading">
          <h2>五维学习力画像</h2>
          <p>严格沿用现有学习力报告的展示口径</p>
        </div>
        <div className="metric-list">
          {report.macro_ability_map.radar_data.slice(0, 5).map((item) => (
            <div className="metric-row" key={item.dimension}>
              <span>{item.dimension}</span>
              <strong>{item.value.toFixed(1)}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="card">
        <div className="section-heading">
          <h2>当前挑战与体验</h2>
          <p>这部分内容用于引导用户进入下一阶段的课程与项目学习</p>
        </div>
        <div className="metric-list">
          {report.challenges_and_experience.items.map((item) => (
            <div className="metric-row" key={item.name}>
              <span>{item.name}</span>
              <strong>
                {item.score.toFixed(1)} / {item.label}
              </strong>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
