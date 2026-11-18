"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { createSlideScene, SceneRenderer } from "scene-content-kit";
import { slideDeck } from "@/data/slides";

const SLIDE_WIDTH = 1280;
const SLIDE_HEIGHT = 720;

type CourseSlideViewerProps = {
  slideIndex: number;
  onSlideIndexChange: (index: number) => void;
};

export function CourseSlideViewer({
  slideIndex: index,
  onSlideIndexChange,
}: CourseSlideViewerProps) {
  const frameRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const node = frameRef.current;
    if (!node) return;

    const updateScale = () => {
      const available = node.clientWidth - 36;
      setScale(Math.min(1, Math.max(0.42, available / SLIDE_WIDTH)));
    };

    updateScale();
    const observer = new ResizeObserver(updateScale);
    observer.observe(node);
    window.addEventListener("resize", updateScale);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", updateScale);
    };
  }, []);

  const scene = useMemo(() => {
    const current = slideDeck[index];
    return createSlideScene(current.data, {
      id: current.id,
      title: current.title,
      order: index + 1,
    });
  }, [index]);

  const scaledHeight = SLIDE_HEIGHT * scale;

  return (
    <section className="card course-slide-card">
      <div className="section-heading">
        <div>
          <h2>课程课件</h2>
          <p>
            当前第 {index + 1} / {slideDeck.length} 页 · {slideDeck[index]?.title}
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
      <div className="slide-frame" ref={frameRef}>
        <div
          className="slide-scale-wrap"
          style={{ height: scaledHeight, width: SLIDE_WIDTH * scale }}
        >
          <div
            className="slide-scale-inner"
            style={{
              transform: `scale(${scale})`,
              width: SLIDE_WIDTH,
              height: SLIDE_HEIGHT,
            }}
          >
            <SceneRenderer scene={scene} className="course-slide-renderer" />
          </div>
        </div>
      </div>
    </section>
  );
}
