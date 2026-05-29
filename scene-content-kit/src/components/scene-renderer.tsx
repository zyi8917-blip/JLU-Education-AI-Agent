'use client';

import type { KitQuizScene, KitSceneRendererProps, KitSlideScene } from '../types';
import { QuizScene } from './quiz-scene';
import { SlideScene } from './slide-scene';

export function SceneRenderer(props: KitSceneRendererProps) {
  const { scene, emptyState } = props;

  if (scene.type === 'slide' && scene.content.type === 'slide') {
    return <SlideScene {...props} scene={scene as KitSlideScene} />;
  }

  if (scene.type === 'quiz' && scene.content.type === 'quiz') {
    return <QuizScene {...props} scene={scene as KitQuizScene} />;
  }

  return emptyState ? <>{emptyState}</> : null;
}
