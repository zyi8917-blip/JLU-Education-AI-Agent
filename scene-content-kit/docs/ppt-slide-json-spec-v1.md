# PPT Slide Intermediate JSON Specification v1

## Overview

This document defines the minimum viable intermediate JSON format for converting a single PPT page into a structure that `scene-content-kit` can render with its read-only `slide` component.

The goal of `v1` is stability and ease of implementation:

- One JSON file maps to one PPT page
- Only fields required by the current renderer are included
- Coordinates and sizes use pixels
- Unsupported PPT capabilities should be downgraded during conversion

This format is intended for the workflow:

`PPT page -> converter output JSON -> createSlideScene(...) -> SceneRenderer`

---

## Version

Top-level `version` must be:

```json
"scenekit.slide/v1"
```

---

## Design Principles

1. One page per file.
2. The converter is responsible for downgrading unsupported PPT features.
3. The renderer consumes only stable, presentation-oriented fields.
4. Element order in `elements` is the visual stacking order from back to front.
5. The format is optimized for rendering, not for editing.

---

## Top-Level Structure

```json
{
  "version": "scenekit.slide/v1",
  "page": {
    "id": "slide-001",
    "title": "Page 1",
    "width": 960,
    "height": 540,
    "background": {
      "type": "solid",
      "color": "#FFFFFF"
    },
    "theme": {
      "fontName": "Arial",
      "fontColor": "#111827",
      "backgroundColor": "#FFFFFF",
      "themeColors": ["#2563eb", "#0f766e", "#f59e0b"]
    },
    "elements": []
  }
}
```

---

## Top-Level Fields

### `version`

- Type: `string`
- Required: yes
- Fixed value: `scenekit.slide/v1`

### `page`

- Type: `object`
- Required: yes
- Meaning: one PPT page

---

## Page Object

```json
{
  "id": "slide-001",
  "title": "Page 1",
  "width": 960,
  "height": 540,
  "background": {
    "type": "solid",
    "color": "#FFFFFF"
  },
  "theme": {
    "fontName": "Arial",
    "fontColor": "#111827",
    "backgroundColor": "#FFFFFF",
    "themeColors": ["#2563eb", "#0f766e", "#f59e0b"]
  },
  "elements": []
}
```

### `page.id`

- Type: `string`
- Required: yes
- Meaning: unique page identifier

### `page.title`

- Type: `string`
- Required: recommended
- Meaning: display title for the page

### `page.width`

- Type: `number`
- Required: yes
- Unit: pixels
- Meaning: original PPT page width

### `page.height`

- Type: `number`
- Required: yes
- Unit: pixels
- Meaning: original PPT page height

### `page.background`

- Type: `object`
- Required: no
- Meaning: page background

### `page.theme`

- Type: `object`
- Required: yes
- Meaning: fallback theme values for the page

### `page.elements`

- Type: `array`
- Required: yes
- Meaning: page elements in visual stacking order

---

## Theme Object

```json
{
  "fontName": "Arial",
  "fontColor": "#111827",
  "backgroundColor": "#FFFFFF",
  "themeColors": ["#2563eb", "#0f766e", "#f59e0b"]
}
```

### Fields

- `fontName`: `string`, required
- `fontColor`: `string`, required, hex color
- `backgroundColor`: `string`, required, hex color
- `themeColors`: `string[]`, required, at least one hex color

---

## Background Object

Three background modes are supported in `v1`.

### Solid Background

```json
{
  "type": "solid",
  "color": "#FFFFFF"
}
```

### Image Background

```json
{
  "type": "image",
  "image": {
    "src": "/ppt-assets/deck-001/bg-1.png",
    "size": "cover"
  }
}
```

### Gradient Background

```json
{
  "type": "gradient",
  "gradient": {
    "type": "linear",
    "rotate": 90,
    "colors": [
      { "pos": 0, "color": "#FFFFFF" },
      { "pos": 1, "color": "#E0F2FE" }
    ]
  }
}
```

### Background Field Rules

- `type`: required, one of `solid | image | gradient`
- `color`: required when `type` is `solid`
- `image.src`: required when `type` is `image`
- `image.size`: optional, one of `cover | contain | repeat`
- `gradient.type`: required when `type` is `gradient`, one of `linear | radial`
- `gradient.rotate`: optional, degrees
- `gradient.colors`: required, array of color stops
- `gradient.colors[].pos`: number from `0` to `1`
- `gradient.colors[].color`: hex color string

---

## Common Element Fields

Every element must contain the following common fields:

```json
{
  "id": "el-001",
  "type": "text",
  "name": "Title",
  "left": 48,
  "top": 40,
  "width": 500,
  "height": 72,
  "rotate": 0
}
```

### Common Field Rules

- `id`: `string`, required, unique within the page
- `type`: `string`, required
- `name`: `string`, optional
- `left`: `number`, required, x position in px
- `top`: `number`, required, y position in px
- `width`: `number`, required, width in px
- `height`: `number`, required, height in px
- `rotate`: `number`, required, rotation angle in degrees

---

## Supported Element Types In v1

### 1. Text Element

```json
{
  "id": "title-1",
  "type": "text",
  "name": "Main Title",
  "left": 48,
  "top": 40,
  "width": 500,
  "height": 72,
  "rotate": 0,
  "content": "<p>Imported PPT Slide</p>",
  "defaultFontName": "Arial",
  "defaultColor": "#111827",
  "fill": "transparent",
  "opacity": 1,
  "lineHeight": 1.4
}
```

#### Rules

- `content`: required, HTML string
- The converter should output at least paragraph-safe HTML such as `<p>...</p>`
- Complex PPT text effects should be downgraded to plain rich text

---

### 2. Image Element

```json
{
  "id": "image-1",
  "type": "image",
  "name": "Product Photo",
  "left": 560,
  "top": 120,
  "width": 260,
  "height": 160,
  "rotate": 0,
  "src": "/ppt-assets/deck-001/image-1.png",
  "fixedRatio": true,
  "radius": 0
}
```

#### Rules

- `src`: required
- `fixedRatio`: optional
- `radius`: optional, in px

---

### 3. Shape Element

```json
{
  "id": "shape-1",
  "type": "shape",
  "name": "Highlight Box",
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

#### Rules

- `fill`: optional, hex color
- `opacity`: optional, `0` to `1`
- `outline.width`: optional
- `outline.color`: optional
- Complex PPT vector shapes should be downgraded to `image` when stable reproduction is not possible

---

### 4. Line Element

```json
{
  "id": "line-1",
  "type": "line",
  "name": "Divider",
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

#### Rules

- `start`: required, `[x, y]`
- `end`: required, `[x, y]`
- `color`: required
- `style`: optional, one of `solid | dashed | dotted`
- `start` and `end` are relative to the element box

---

### 5. Table Element

```json
{
  "id": "table-1",
  "type": "table",
  "name": "Summary Table",
  "left": 80,
  "top": 260,
  "width": 520,
  "height": 180,
  "rotate": 0,
  "outline": {
    "width": 1,
    "color": "#CBD5E1"
  },
  "data": [
    [
      { "id": "c1", "text": "Item", "style": { "bold": true, "align": "center" } },
      { "id": "c2", "text": "Value", "style": { "bold": true, "align": "center" } }
    ],
    [
      { "id": "c3", "text": "Revenue" },
      { "id": "c4", "text": "120" }
    ]
  ]
}
```

#### Table Cell Fields

- `id`: required
- `text`: required
- `colspan`: optional
- `rowspan`: optional
- `style.bold`: optional
- `style.color`: optional
- `style.backcolor`: optional
- `style.align`: optional, one of `left | center | right | justify`

#### Rules

- Table text should be downgraded to plain text
- Complex table borders should be normalized during conversion

---

## Unsupported Features In v1

The following features should not be encoded directly in `v1`:

- Animations
- Grouping
- Native chart semantics
- Video
- Audio
- SmartArt
- Complex SVG/path geometry
- Text shadow, glow, and 3D effects
- Page transition effects
- Notes page content

### Downgrade Strategy

- Complex chart: convert to `image`
- SmartArt: convert to `image`
- Complex shape/path: convert to `image`
- Unsupported media: omit or convert to preview image if needed

---

## Mapping To `scene-content-kit`

The converter output should be mapped into `KitSlideSceneData` using:

```ts
const canvas = {
  id: page.id,
  viewportSize: page.width,
  viewportRatio: page.width / page.height,
  theme: page.theme,
  background: page.background,
  elements: page.elements,
};
```

Then wrap it with:

```ts
const scene = createSlideScene(canvas, {
  id: page.id,
  title: page.title,
});
```

And render it with:

```tsx
<SceneRenderer scene={scene} />
```

---

## Recommended File Layout

### One JSON Per Page

- `slide-001.json`
- `slide-002.json`
- `slide-003.json`

### Asset Directory

- `/ppt-assets/<deck-id>/...`

### Recommended Manifest

If multiple pages belong to one PPT, add a deck-level manifest:

```json
{
  "version": "scenekit.deck/v1",
  "deckId": "deck-001",
  "title": "Sample Deck",
  "pages": [
    {
      "id": "slide-001",
      "title": "Cover",
      "file": "/ppt-json/slide-001.json",
      "order": 1
    },
    {
      "id": "slide-002",
      "title": "Agenda",
      "file": "/ppt-json/slide-002.json",
      "order": 2
    }
  ]
}
```

---

## Complete Example

```json
{
  "version": "scenekit.slide/v1",
  "page": {
    "id": "slide-001",
    "title": "Imported PPT Page 1",
    "width": 960,
    "height": 540,
    "background": {
      "type": "solid",
      "color": "#FFFFFF"
    },
    "theme": {
      "fontName": "Arial",
      "fontColor": "#111827",
      "backgroundColor": "#FFFFFF",
      "themeColors": ["#2563eb", "#0f766e", "#f59e0b"]
    },
    "elements": [
      {
        "id": "title-1",
        "type": "text",
        "name": "Title",
        "left": 48,
        "top": 40,
        "width": 500,
        "height": 72,
        "rotate": 0,
        "content": "<p>Imported PPT Slide</p>",
        "defaultFontName": "Arial",
        "defaultColor": "#111827",
        "fill": "transparent",
        "opacity": 1,
        "lineHeight": 1.4
      },
      {
        "id": "image-1",
        "type": "image",
        "name": "Example Image",
        "left": 560,
        "top": 120,
        "width": 260,
        "height": 160,
        "rotate": 0,
        "src": "/ppt-assets/deck-001/image-1.png",
        "fixedRatio": true,
        "radius": 0
      },
      {
        "id": "shape-1",
        "type": "shape",
        "name": "Callout",
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
      },
      {
        "id": "line-1",
        "type": "line",
        "name": "Divider",
        "left": 100,
        "top": 220,
        "width": 300,
        "height": 2,
        "rotate": 0,
        "start": [0, 0],
        "end": [300, 0],
        "color": "#2563EB",
        "style": "solid"
      },
      {
        "id": "table-1",
        "type": "table",
        "name": "Summary Table",
        "left": 80,
        "top": 260,
        "width": 520,
        "height": 180,
        "rotate": 0,
        "outline": {
          "width": 1,
          "color": "#CBD5E1"
        },
        "data": [
          [
            { "id": "c1", "text": "Item", "style": { "bold": true, "align": "center" } },
            { "id": "c2", "text": "Value", "style": { "bold": true, "align": "center" } }
          ],
          [
            { "id": "c3", "text": "Revenue" },
            { "id": "c4", "text": "120" }
          ]
        ]
      }
    ]
  }
}
```

---

## Validation Checklist

Before a converter emits `v1`, verify:

- `version` is `scenekit.slide/v1`
- `page.width` and `page.height` are present
- `theme` is complete
- every element has `id`, `type`, `left`, `top`, `width`, `height`, `rotate`
- every `text` element has `content`
- every `image` element has `src`
- every `line` element has `start`, `end`, `color`
- every `table` element has `data`
- unsupported features are downgraded or omitted
