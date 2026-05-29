import type { KitSlideSceneData } from "scene-content-kit";
import slide001 from "../../demo-assets/ppt-slides-with-assets/slide-001.json";
import slide002 from "../../demo-assets/ppt-slides-with-assets/slide-002.json";

type SlidePage = {
  page: {
    id: string;
    title: string;
    width: number;
    height: number;
    background?: {
      type: "solid" | "gradient" | "image";
      color?: string;
    };
    theme: {
      fontName: string;
      fontColor: string;
      backgroundColor: string;
      themeColors: string[];
    };
    elements: Array<Record<string, unknown>>;
  };
};

function toKitSlideData(raw: SlidePage): KitSlideSceneData {
  const { page } = raw;
  return {
    id: page.id,
    viewportSize: page.width,
    viewportRatio: page.width / page.height,
    theme: page.theme,
    background: page.background,
    elements: page.elements as unknown as KitSlideSceneData["elements"],
  };
}

export const slideDeck = [
  {
    id: "course-slide-1",
    title: "从一只“龙虾”说起",
    data: toKitSlideData(slide001 as SlidePage),
  },
  {
    id: "course-slide-2",
    title: "拥抱人工智能时代",
    data: toKitSlideData(slide002 as SlidePage),
  },
];
