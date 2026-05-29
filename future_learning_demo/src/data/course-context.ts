import { slideDeck } from "@/data/slides";

export function buildSlideContext(slideIndex: number): string {
  const slide = slideDeck[slideIndex];
  if (!slide) return "";
  return `Page ${slideIndex + 1} of ${slideDeck.length}\nid: ${slide.id}\ntitle: ${slide.title}`;
}
