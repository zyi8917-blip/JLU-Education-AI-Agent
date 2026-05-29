import type { CreateSlideSceneOptions, KitSlideScene, KitSlideSceneData } from '../types';

export function createSlideScene(
  canvas: KitSlideSceneData,
  options: CreateSlideSceneOptions = {},
): KitSlideScene {
  return {
    id: options.id ?? canvas.id,
    title: options.title ?? 'Imported Slide',
    type: 'slide',
    order: options.order,
    content: {
      type: 'slide',
      canvas,
    },
  };
}
