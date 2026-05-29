"use client";

import { useMemo } from "react";
import { createSlideScene, SceneRenderer } from "scene-content-kit";
import { slideDeck } from "@/data/slides";

type CourseSlideViewerProps = {
  slideIndex: number;
  onSlideIndexChange: (index: number) => void;
};

export function CourseSlideViewer({
  slideIndex: index,
  onSlideIndexChange,
}: CourseSlideViewerProps) {
  const scene = useMemo(() => {
    const current = slideDeck[index];
    return createSlideScene(current.data, {
      id: current.id,
      title: current.title,
      order: index + 1,
    });
  }, [index]);

  return (
    <section className="card course-slide-card">
      <div className="section-heading">
        <div>
          <h2>课程课件</h2>
          <p>
            当前第 {index + 1} / {slideDeck.length} 页
          </p>
        </div>
        <div className="inline-actions">
          <button
            className="ghost-button"
            disabled={index === 0}
            onClick={() => onSlideIndexChange(Math.max(0, index - 1))}
            type="button"
          >
            上一页
          </button>
          <button
            className="ghost-button"
            disabled={index === slideDeck.length - 1}
            onClick={() =>
              onSlideIndexChange(Math.min(slideDeck.length - 1, index + 1))
            }
            type="button"
          >
            下一页
          </button>
        </div>
      </div>
      <div className="slide-frame">
        <SceneRenderer scene={scene} />
      </div>
    </section>
  );
}
