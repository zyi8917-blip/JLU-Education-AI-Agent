import type { KitSlideSceneData } from "scene-content-kit";

const W = 1280;
const H = 720;

const theme = {
  fontName: "PingFang SC, Microsoft YaHei, Arial, sans-serif",
  fontColor: "#111827",
  backgroundColor: "#FFFFFF",
  themeColors: ["#2563eb", "#0f766e", "#f59e0b", "#7c3aed"],
};

type TextBlock = {
  id: string;
  html: string;
  left: number;
  top: number;
  width: number;
  height: number;
  color?: string;
};

function text(block: TextBlock) {
  return {
    id: block.id,
    type: "text" as const,
    name: block.id,
    left: block.left,
    top: block.top,
    width: block.width,
    height: block.height,
    rotate: 0,
    content: block.html,
    defaultFontName: theme.fontName,
    defaultColor: block.color ?? theme.fontColor,
    fill: "transparent",
    opacity: 1,
    lineHeight: 1.45,
  };
}

function bar(id: string, top: number, color: string, width = 180) {
  return {
    id,
    type: "shape" as const,
    name: id,
    left: 56,
    top,
    width,
    height: 8,
    rotate: 0,
    fill: color,
    opacity: 1,
    outline: { width: 0, color: "transparent" },
  };
}

function card(
  id: string,
  left: number,
  top: number,
  width: number,
  height: number,
  fill: string,
) {
  return {
    id,
    type: "shape" as const,
    name: id,
    left,
    top,
    width,
    height,
    rotate: 0,
    fill,
    opacity: 1,
    outline: { width: 1, color: "#dbe3ee" },
  };
}

export type CourseSlideSpec = {
  id: string;
  title: string;
  subtitle?: string;
  bullets?: string[];
  cards?: Array<{ title: string; body: string; color: string }>;
  table?: { headers: string[]; rows: string[][] };
  footer?: string;
  accent?: string;
};

export function buildCourseSlide(spec: CourseSlideSpec): KitSlideSceneData {
  const elements: Array<Record<string, unknown>> = [];
  const accent = spec.accent ?? theme.themeColors[0];

  elements.push(
    text({
      id: `${spec.id}-title`,
      html: `<p style="font-size:34px;font-weight:700;line-height:1.25">${spec.title}</p>`,
      left: 56,
      top: 36,
      width: 1168,
      height: 90,
    }),
  );
  elements.push(bar(`${spec.id}-bar`, 128, accent));

  if (spec.subtitle) {
    elements.push(
      text({
        id: `${spec.id}-subtitle`,
        html: `<p style="font-size:22px;color:#526071">${spec.subtitle}</p>`,
        left: 56,
        top: 152,
        width: 1168,
        height: 48,
      }),
    );
  }

  let bulletTop = spec.subtitle ? 220 : 180;
  for (const [index, bullet] of (spec.bullets ?? []).entries()) {
    elements.push(
      text({
        id: `${spec.id}-bullet-${index}`,
        html: `<p style="font-size:20px">• ${bullet}</p>`,
        left: 72,
        top: bulletTop + index * 58,
        width: 1120,
        height: 52,
      }),
    );
  }

  if (spec.cards?.length) {
    const gap = 24;
    const cardWidth = (1168 - gap * (spec.cards.length - 1)) / spec.cards.length;
    spec.cards.forEach((item, index) => {
      const left = 56 + index * (cardWidth + gap);
      const top = spec.bullets?.length ? 220 + spec.bullets.length * 58 + 12 : 200;
      elements.push(card(`${spec.id}-card-bg-${index}`, left, top, cardWidth, 250, "#f8fafc"));
      elements.push(
        text({
          id: `${spec.id}-card-title-${index}`,
          html: `<p style="font-size:22px;font-weight:700;color:${item.color}">${item.title}</p>`,
          left: left + 20,
          top: top + 20,
          width: cardWidth - 40,
          height: 40,
        }),
      );
      elements.push(
        text({
          id: `${spec.id}-card-body-${index}`,
          html: `<p style="font-size:17px;color:#526071">${item.body}</p>`,
          left: left + 20,
          top: top + 72,
          width: cardWidth - 40,
          height: 160,
        }),
      );
    });
  }

  if (spec.table) {
    const top = 360;
    elements.push({
      id: `${spec.id}-table`,
      type: "table",
      name: `${spec.id}-table`,
      left: 56,
      top,
      width: 1168,
      height: 260,
      rotate: 0,
      data: [
        spec.table.headers.map((cell, colIndex) => ({
          id: `${spec.id}-th-${colIndex}`,
          colspan: 1,
          rowspan: 1,
          text: cell,
          style: {
            bold: true,
            align: "center" as const,
            backcolor: "#edf3ff",
            color: "#1e3a8a",
          },
        })),
        ...spec.table.rows.map((row, rowIndex) =>
          row.map((cell, colIndex) => ({
            id: `${spec.id}-td-${rowIndex}-${colIndex}`,
            colspan: 1,
            rowspan: 1,
            text: cell,
            style: { align: "left" as const },
          })),
        ),
      ],
    });
  }

  if (spec.footer) {
    elements.push(
      text({
        id: `${spec.id}-footer`,
        html: `<p style="font-size:18px;color:#526071">${spec.footer}</p>`,
        left: 56,
        top: H - 88,
        width: 1168,
        height: 56,
      }),
    );
  }

  return {
    id: spec.id,
    viewportSize: W,
    viewportRatio: W / H,
    theme,
    background: { type: "solid", color: "#FFFFFF" },
    elements: elements as unknown as KitSlideSceneData["elements"],
  };
}
