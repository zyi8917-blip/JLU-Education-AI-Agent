"use client";

import { useMemo, useState } from "react";
import { CourseQaPanel } from "@/components/course-qa-panel";
import { CourseSlideViewer } from "@/components/course-slide-viewer";
import { buildSlideContext } from "@/data/course-context";

export function CourseLearningClient() {
  const [slideIndex, setSlideIndex] = useState(0);
  const slideContext = useMemo(
    () => buildSlideContext(slideIndex),
    [slideIndex],
  );

  return (
    <section className="split-layout">
      <CourseSlideViewer
        slideIndex={slideIndex}
        onSlideIndexChange={setSlideIndex}
      />
      <CourseQaPanel slideContext={slideContext} />
    </section>
  );
}
