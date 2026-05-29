# PPT Converter Implementation Guide

## Goal

This guide describes how to build a PPT-to-JSON converter that targets [`scenekit.slide/v1`](./ppt-slide-json-spec-v1.md).

The desired output pipeline is:

`pptx file -> parse page elements -> normalize -> write v1 JSON -> render with scene-content-kit`

This guide is intentionally practical and optimized for fast implementation.

---

## Recommended Output Strategy

Use the following rules:

1. Export one JSON file per PPT page.
2. Export page-linked assets into a predictable static directory.
3. Preserve page size and element positions in pixels.
4. Normalize unsupported PPT capabilities during conversion.
5. Prefer stable rendering over perfect visual parity.

Recommended output layout:

```text
/output
  /ppt-json
    slide-001.json
    slide-002.json
  /ppt-assets
    /deck-001
      image-1.png
      image-2.png
      bg-1.png
```

---

## Suggested Conversion Pipeline

### Step 1: Read deck metadata

Extract:

- deck title
- total slide count
- page size

For each page, determine:

- slide id
- page title
- page width
- page height

If the source format provides EMU, points, or inches, convert them into pixels before writing the final JSON.

---

### Step 2: Extract page background

Map backgrounds as follows:

- solid fill -> `background.type = "solid"`
- image background -> `background.type = "image"`
- simple gradient -> `background.type = "gradient"`
- unsupported background effects -> rasterize and emit as image background

If no explicit background exists, emit:

```json
{
  "type": "solid",
  "color": "#FFFFFF"
}
```

---

### Step 3: Build the page theme

The converter should always emit a complete theme:

```json
{
  "fontName": "Arial",
  "fontColor": "#111827",
  "backgroundColor": "#FFFFFF",
  "themeColors": ["#2563eb", "#0f766e", "#f59e0b"]
}
```

Theme population strategy:

- `fontName`: use PPT default theme font or first dominant text font
- `fontColor`: use a readable default if PPT theme color is missing
- `backgroundColor`: match the slide background fallback color
- `themeColors`: use source theme colors if available, otherwise generate a short fallback palette

---

### Step 4: Convert page elements

For each element on the page:

1. determine supported output type
2. convert position and size
3. normalize style
4. append to `elements` in z-order

Supported `v1` types:

- `text`
- `image`
- `shape`
- `line`
- `table`

Unsupported source types should be downgraded to:

- `image`, if visual fidelity matters
- omission, if decorative and non-essential

---

## Type Mapping Rules

### Text Box -> `text`

Use `text` when the PPT element is a standard text box, title, subtitle, or a shape whose primary role is text presentation.

Minimum mapping:

```json
{
  "id": "title-1",
  "type": "text",
  "left": 48,
  "top": 40,
  "width": 500,
  "height": 72,
  "rotate": 0,
  "content": "<p>Imported PPT Slide</p>",
  "defaultFontName": "Arial",
  "defaultColor": "#111827"
}
```

Implementation notes:

- Convert runs/paragraphs into safe HTML
- Start with `<p>...</p>` blocks
- Inline formatting can be included later if needed
- If precise formatting is hard, emit simplified paragraph HTML first

Recommended HTML safety policy:

- allow `p`, `br`, `strong`, `em`, `u`, `span`
- avoid unsupported CSS-heavy markup

---

### Image -> `image`

Use `image` for:

- embedded images
- cropped screenshots
- rasterized fallback output from unsupported PPT shapes or charts

Minimum mapping:

```json
{
  "id": "image-1",
  "type": "image",
  "left": 560,
  "top": 120,
  "width": 260,
  "height": 160,
  "rotate": 0,
  "src": "/ppt-assets/deck-001/image-1.png",
  "fixedRatio": true
}
```

Implementation notes:

- export binary assets into a stable directory
- use relative or web-servable paths in `src`
- if rounded corners are known, map them to `radius`

---

### Simple Shape -> `shape`

Use `shape` only for simple, stable shapes such as:

- filled rectangle
- outline rectangle
- highlight box

Minimum mapping:

```json
{
  "id": "shape-1",
  "type": "shape",
  "left": 60,
  "top": 140,
  "width": 220,
  "height": 100,
  "rotate": 0,
  "fill": "#DBEAFE",
  "opacity": 1,
  "outline": {
    "width": 1,
    "color": "#93C5FD"
  }
}
```

Implementation notes:

- if the source shape is complex, export it as an `image` instead
- do not try to preserve every PPT vector path in `v1`

---

### Connector Or Divider -> `line`

Use `line` for:

- straight horizontal or vertical dividers
- simple connectors that can be expressed with one start and one end point

Minimum mapping:

```json
{
  "id": "line-1",
  "type": "line",
  "left": 100,
  "top": 220,
  "width": 300,
  "height": 2,
  "rotate": 0,
  "start": [0, 0],
  "end": [300, 0],
  "color": "#2563EB",
  "style": "solid"
}
```

Implementation notes:

- `start` and `end` are relative to the element box
- unsupported arrowheads or multi-segment connectors should be rasterized into images if fidelity matters

---

### Table -> `table`

Use `table` for PPT tables that can be represented as cell text plus light styling.

Minimum mapping:

```json
{
  "id": "table-1",
  "type": "table",
  "left": 80,
  "top": 260,
  "width": 520,
  "height": 180,
  "rotate": 0,
  "data": [
    [
      { "id": "c1", "text": "Item" },
      { "id": "c2", "text": "Value" }
    ]
  ]
}
```

Implementation notes:

- emit plain text content first
- preserve `colspan` and `rowspan` when extractable
- normalize complex border styles into a simple outer `outline`

---

## Unsupported Capability Downgrade Table

| Source PPT feature | v1 handling |
|---|---|
| SmartArt | rasterize as `image` |
| native chart | rasterize as `image` |
| complex freeform shape | rasterize as `image` |
| text glow/shadow/3D | drop effect, keep text |
| animation | ignore |
| media playback | omit or use poster image |
| grouped object | flatten into ordered child elements or rasterize |

---

## Coordinate And Unit Rules

All final output values must use pixels.

Recommended approach:

1. read source units
2. normalize all geometry into one internal coordinate system
3. write px values into JSON

For each element, emit:

- `left`
- `top`
- `width`
- `height`
- `rotate`

Keep numeric precision practical. Integer pixels are preferred unless fractional values are necessary.

---

## Suggested Conversion Heuristics

### Text Heuristics

- merge neighboring text runs into paragraph HTML
- keep paragraph order
- preserve bold and italic only if easy
- fallback to plain `<p>` text when formatting extraction is hard

### Image Heuristics

- deduplicate identical binary assets when possible
- normalize file names using deterministic ids

### Shape Heuristics

- if the shape can be approximated as a rounded rectangle, keep it as `shape`
- otherwise rasterize

### Table Heuristics

- prefer semantic table extraction over image fallback
- if merged cell structure cannot be recovered reliably, flatten to a simple matrix and log a warning

---

## Suggested Converter Validation

Before writing each page JSON, validate:

- page id exists
- page width and height are positive
- theme fields are complete
- each element has required common fields
- type-specific required fields exist
- image `src` paths are non-empty
- line start/end arrays are length 2
- table data is a 2D array

Recommended behavior:

- hard fail on invalid page-level geometry
- soft warn and downgrade on unsupported element features

---

## Integration With `scene-content-kit`

When the JSON is ready, consume it like this:

```tsx
import slideJson from './slide-001.json';
import {
  SceneRenderer,
  createSlideScene,
  type KitSlideSceneData,
} from '@/scene-content-kit';
import '@/scene-content-kit/styles.css';

const page = slideJson.page;

const canvas: KitSlideSceneData = {
  id: page.id,
  viewportSize: page.width,
  viewportRatio: page.width / page.height,
  theme: page.theme,
  background: page.background,
  elements: page.elements,
};

const scene = createSlideScene(canvas, {
  id: page.id,
  title: page.title,
});

export default function PPTPreview() {
  return <SceneRenderer scene={scene} />;
}
```

---

## Recommended First Milestone

To move quickly, implement the converter in this order:

1. page size + background
2. text
3. image
4. simple shape
5. line
6. table
7. rasterized fallback for all unsupported content

This gives you a usable MVP early, while keeping room for later upgrades.
