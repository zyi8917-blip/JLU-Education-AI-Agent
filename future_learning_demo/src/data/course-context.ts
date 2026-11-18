import { slideDeck } from "@/data/slides";

function joinParts(parts: Array<string | undefined>): string {
  return parts.filter(Boolean).join("\n");
}

export function buildSlideContext(slideIndex: number): string {
  const slide = slideDeck[slideIndex];
  if (!slide) return "";

  const spec = slide.spec;
  const bullets = spec.bullets?.map((b, i) => `${i + 1}. ${b}`).join("\n");
  const cards = spec.cards
    ?.map((c) => `- ${c.title}: ${c.body}`)
    .join("\n");

  return joinParts([
    `Page ${slideIndex + 1} of ${slideDeck.length}`,
    `id: ${slide.id}`,
    `title: ${slide.title}`,
    spec.subtitle ? `subtitle: ${spec.subtitle}` : undefined,
    bullets ? `key_points:\n${bullets}` : undefined,
    cards ? `cards:\n${cards}` : undefined,
    spec.footer ? `footer: ${spec.footer}` : undefined,
  ]);
}

export function buildCourseOutline(): string {
  return slideDeck
    .map((s, i) => `${i + 1}. ${s.title}${s.spec.subtitle ? ` — ${s.spec.subtitle}` : ""}`)
    .join("\n");
}
