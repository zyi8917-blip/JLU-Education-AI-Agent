import type { CSSProperties, ReactNode } from 'react';

export type KitSceneType = 'slide' | 'quiz';
export type KitQuizQuestionType = 'single' | 'multiple' | 'short_answer';

export interface KitScene {
  id: string;
  title: string;
  type: KitSceneType;
  order?: number;
  content: KitSceneContent;
}

export type KitSceneContent = KitSlideContent | KitQuizContent;
export type KitSlideScene = KitScene & { type: 'slide'; content: KitSlideContent };
export type KitQuizScene = KitScene & { type: 'quiz'; content: KitQuizContent };

export interface KitTheme {
  backgroundColor: string;
  themeColors: string[];
  fontColor: string;
  fontName: string;
}

export interface KitSlideBackground {
  type: 'solid' | 'gradient' | 'image';
  color?: string;
  image?: {
    src: string;
    size?: 'cover' | 'contain' | 'repeat';
  };
  gradient?: {
    type: 'linear' | 'radial';
    rotate?: number;
    colors: Array<{ pos: number; color: string }>;
  };
}

interface KitBaseElement {
  id: string;
  type: string;
  left: number;
  top: number;
  width: number;
  height: number;
  rotate: number;
  name?: string;
}

export interface KitTextElement extends KitBaseElement {
  type: 'text';
  content: string;
  defaultFontName?: string;
  defaultColor?: string;
  fill?: string;
  opacity?: number;
  lineHeight?: number;
}

export interface KitImageElement extends KitBaseElement {
  type: 'image';
  src: string;
  fixedRatio?: boolean;
  radius?: number;
}

export interface KitShapeElement extends KitBaseElement {
  type: 'shape';
  fill?: string;
  opacity?: number;
  outline?: {
    width?: number;
    color?: string;
  };
}

export interface KitLineElement extends KitBaseElement {
  type: 'line';
  start: [number, number];
  end: [number, number];
  color: string;
  style?: 'solid' | 'dashed' | 'dotted';
}

export interface KitTableCell {
  id: string;
  text: string;
  colspan?: number;
  rowspan?: number;
  style?: {
    bold?: boolean;
    color?: string;
    backcolor?: string;
    align?: 'left' | 'center' | 'right' | 'justify';
  };
}

export interface KitTableElement extends KitBaseElement {
  type: 'table';
  data: KitTableCell[][];
  outline?: {
    width?: number;
    color?: string;
  };
}

export interface KitChartElement extends KitBaseElement {
  type: 'chart';
  chartType: 'bar' | 'column' | 'line' | 'pie' | 'ring' | 'area' | 'radar' | 'scatter';
  data: {
    labels: string[];
    legends: string[];
    series: number[][];
  };
  themeColors?: string[];
}

export interface KitLatexElement extends KitBaseElement {
  type: 'latex';
  latex: string;
}

export interface KitVideoElement extends KitBaseElement {
  type: 'video';
  src: string;
  poster?: string;
  autoplay?: boolean;
}

export interface KitAudioElement extends KitBaseElement {
  type: 'audio';
  src: string;
  autoplay?: boolean;
  loop?: boolean;
}

export type KitSlideElement =
  | KitTextElement
  | KitImageElement
  | KitShapeElement
  | KitLineElement
  | KitTableElement
  | KitChartElement
  | KitLatexElement
  | KitVideoElement
  | KitAudioElement;

export interface KitSlideSceneData {
  id: string;
  viewportSize: number;
  viewportRatio: number;
  theme: KitTheme;
  elements: KitSlideElement[];
  background?: KitSlideBackground;
}

export interface KitSlideContent {
  type: 'slide';
  canvas: KitSlideSceneData;
}

export interface CreateSlideSceneOptions {
  id?: string;
  title?: string;
  order?: number;
}

export interface KitQuizOption {
  label: string;
  value: string;
}

export interface KitQuizQuestion {
  id: string;
  type: KitQuizQuestionType;
  question: string;
  options?: KitQuizOption[];
  answer?: string[];
  analysis?: string;
  hasAnswer?: boolean;
  points?: number;
}

export interface KitQuizContent {
  type: 'quiz';
  questions: KitQuizQuestion[];
}

export type KitQuizAnswerMap = Record<string, string | string[]>;

export interface KitQuizQuestionResult {
  questionId: string;
  earned: number;
  correct: boolean | null;
  feedback?: string;
}

export interface KitQuizFeedback {
  heading?: string;
  summary?: string;
  footer?: ReactNode;
}

export interface KitQuizSubmitPayload {
  scene: KitQuizScene;
  answers: KitQuizAnswerMap;
}

export interface KitQuizSubmitResult {
  results: KitQuizQuestionResult[];
  feedback?: KitQuizFeedback;
}

export type KitQuizSubmitHandler = (
  payload: KitQuizSubmitPayload,
) => Promise<KitQuizSubmitResult> | KitQuizSubmitResult;

export interface KitSceneRendererProps {
  scene: KitScene;
  className?: string;
  style?: CSSProperties;
  quiz?: {
    submitLabel?: string;
    retryLabel?: string;
    onSubmit?: KitQuizSubmitHandler;
  };
  emptyState?: ReactNode;
}

export interface OpenMAICSceneLike {
  id: string;
  title: string;
  type: 'slide' | 'quiz' | 'interactive' | 'pbl';
  order?: number;
  stageId?: string;
  content: unknown;
}
