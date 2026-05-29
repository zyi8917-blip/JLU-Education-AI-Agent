export { SceneRenderer } from './src/components/scene-renderer';
export { SlideScene } from './src/components/slide-scene';
export { QuizScene } from './src/components/quiz-scene';
export { adaptOpenMAICScene, adaptOpenMAICScenes, isPortableSceneType } from './src/adapters/openmaic';
export { createSlideScene } from './src/factories/slide';
export type {
  CreateSlideSceneOptions,
  KitScene,
  KitSceneContent,
  KitSceneType,
  KitSceneRendererProps,
  KitQuizAnswerMap,
  KitQuizContent,
  KitQuizFeedback,
  KitQuizOption,
  KitQuizQuestion,
  KitQuizScene,
  KitQuizQuestionResult,
  KitQuizSubmitHandler,
  KitQuizSubmitPayload,
  KitQuizSubmitResult,
  KitSlideBackground,
  KitSlideContent,
  KitSlideElement,
  KitSlideScene,
  KitSlideSceneData,
  KitTheme,
  OpenMAICSceneLike,
} from './src/types';
