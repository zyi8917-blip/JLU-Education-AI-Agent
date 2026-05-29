# Scene Content Kit

`scene-content-kit` is the phase 1 extraction of OpenMAIC's `SceneContent` module for reuse in other Next.js applications.

## Scope

This first phase ships:

- Portable `slide` and `quiz` scene types
- A public `SceneRenderer` entry point
- A lightweight OpenMAIC-to-kit adapter
- Read-only slide rendering
- Quiz rendering with optional submit/grading injection
- A standalone CSS file instead of Tailwind-only styling

This first phase does **not** ship:

- OpenMAIC stage store integration
- Playback engine or scene actions
- Whiteboard integration
- Multi-agent orchestration
- The full PPT editor interaction layer

## Files

- `index.ts`: public exports
- `styles.css`: reusable styles
- `src/types.ts`: portable scene contracts
- `src/adapters/openmaic.ts`: adapter for current OpenMAIC scene data
- `src/components/*`: reusable renderers

## Basic Usage

Import the CSS once in your Next.js app:

```tsx
import '@/scene-content-kit/styles.css';
```

Render a scene:

```tsx
import { SceneRenderer, adaptOpenMAICScene } from '@/scene-content-kit';

export function PortableScene({ openmaicScene }: { openmaicScene: unknown }) {
  const scene = adaptOpenMAICScene(openmaicScene as Parameters<typeof adaptOpenMAICScene>[0]);

  return <SceneRenderer scene={scene} />;
}
```

## Render A Structured Slide File

If your PPT conversion step outputs a JSON file that matches `KitSlideSceneData`, the current module can already render it with the `slide` component.

Expected shape:

```json
{
  "id": "slide-001",
  "viewportSize": 960,
  "viewportRatio": 1.7777777778,
  "theme": {
    "backgroundColor": "#ffffff",
    "themeColors": ["#2563eb", "#0f766e"],
    "fontColor": "#111827",
    "fontName": "Arial"
  },
  "background": {
    "type": "solid",
    "color": "#ffffff"
  },
  "elements": [
    {
      "id": "title-1",
      "type": "text",
      "left": 48,
      "top": 40,
      "width": 500,
      "height": 72,
      "rotate": 0,
      "content": "<p>Imported PPT Slide</p>",
      "defaultColor": "#111827",
      "defaultFontName": "Arial"
    },
    {
      "id": "image-1",
      "type": "image",
      "left": 560,
      "top": 120,
      "width": 260,
      "height": 160,
      "rotate": 0,
      "src": "/images/example.png"
    }
  ]
}
```

Quick usage with a local JSON file:

```tsx
import slideJson from './ppt-slide.json';
import {
  SceneRenderer,
  createSlideScene,
  type KitSlideSceneData,
} from '@/scene-content-kit';
import '@/scene-content-kit/styles.css';

const scene = createSlideScene(slideJson as KitSlideSceneData, {
  id: 'ppt-scene-1',
  title: 'PPT Page 1',
});

export default function PPTPreviewPage() {
  return <SceneRenderer scene={scene} />;
}
```

If your converter produces one JSON file per PPT page, you can loop through them and call `createSlideScene(...)` for each page, then render them one by one.

## Quiz Grading Injection

If you want custom grading behavior, inject it through `quiz.onSubmit`:

```tsx
<SceneRenderer
  scene={scene}
  quiz={{
    submitLabel: '提交答案',
    retryLabel: '重新作答',
    onSubmit: async ({ scene, answers }) => {
      const res = await fetch('/api/quiz-grade-batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scene, answers }),
      });

      return res.json();
    },
  }}
/>
```

## Integration Notes

- The extracted slide renderer is intentionally read-only.
- The kit keeps its own quiz state and does not depend on OpenMAIC stores.
- If your target app needs OpenMAIC's full slide editing pipeline, treat that as phase 2 work.
