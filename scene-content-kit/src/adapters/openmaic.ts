import type {
  KitQuizContent,
  KitScene,
  KitSceneContent,
  KitSceneType,
  KitSlideContent,
  OpenMAICSceneLike,
} from '../types';

const PORTABLE_TYPES: KitSceneType[] = ['slide', 'quiz'];

export function isPortableSceneType(type: OpenMAICSceneLike['type']): type is KitSceneType {
  return PORTABLE_TYPES.includes(type as KitSceneType);
}

export function adaptOpenMAICScene(scene: OpenMAICSceneLike): KitScene {
  if (!isPortableSceneType(scene.type)) {
    throw new Error(`Scene type "${scene.type}" is not supported by scene-content-kit phase 1.`);
  }

  return {
    id: scene.id,
    title: scene.title,
    type: scene.type,
    order: scene.order,
    content: adaptContent(scene.type, scene.content),
  };
}

export function adaptOpenMAICScenes(scenes: OpenMAICSceneLike[]): KitScene[] {
  return scenes.filter((scene) => isPortableSceneType(scene.type)).map(adaptOpenMAICScene);
}

function adaptContent(type: KitSceneType, content: unknown): KitSceneContent {
  if (!content || typeof content !== 'object') {
    throw new Error(`Scene content for "${type}" must be an object.`);
  }

  if (type === 'slide') {
    return content as KitSlideContent;
  }

  return content as KitQuizContent;
}
