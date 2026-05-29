'use client';

import type { CSSProperties } from 'react';
import type {
  KitAudioElement,
  KitChartElement,
  KitImageElement,
  KitLatexElement,
  KitLineElement,
  KitSlideScene,
  KitSceneRendererProps,
  KitShapeElement,
  KitSlideBackground,
  KitSlideElement,
  KitTableCell,
  KitTableElement,
  KitTextElement,
  KitVideoElement,
} from '../types';

function joinClassNames(...values: Array<string | undefined>) {
  return values.filter(Boolean).join(' ');
}

function createElementBoxStyle(element: KitSlideElement): CSSProperties {
  return {
    position: 'absolute',
    left: `${element.left}px`,
    top: `${element.top}px`,
    width: `${element.width}px`,
    height: `${element.height}px`,
    transform: `rotate(${element.rotate}deg)`,
    transformOrigin: 'top left',
  };
}

function createBackgroundStyle(background?: KitSlideBackground, fallback = '#ffffff'): CSSProperties {
  if (!background || background.type === 'solid') {
    return {
      background: background?.color ?? fallback,
    };
  }

  if (background.type === 'image' && background.image) {
    return {
      backgroundImage: `url(${background.image.src})`,
      backgroundSize: background.image.size ?? 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: background.image.size === 'repeat' ? 'repeat' : 'no-repeat',
    };
  }

  if (background.type === 'gradient' && background.gradient) {
    const stops = background.gradient.colors
      .map((stop) => `${stop.color} ${Math.round(stop.pos * 100)}%`)
      .join(', ');

    if (background.gradient.type === 'radial') {
      return { background: `radial-gradient(circle, ${stops})` };
    }

    return {
      background: `linear-gradient(${background.gradient.rotate ?? 0}deg, ${stops})`,
    };
  }

  return { background: fallback };
}

function stripHtml(content: string) {
  return content.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
}

function renderTextElement(element: KitTextElement) {
  return (
    <div
      key={element.id}
      className="scenekit-slide__text"
      style={{
        ...createElementBoxStyle(element),
        color: element.defaultColor,
        fontFamily: element.defaultFontName,
        background: element.fill,
        opacity: element.opacity,
        lineHeight: element.lineHeight,
      }}
      dangerouslySetInnerHTML={{ __html: element.content }}
    />
  );
}

function renderImageElement(element: KitImageElement) {
  return (
    <img
      key={element.id}
      className="scenekit-slide__image"
      style={{
        ...createElementBoxStyle(element),
        objectFit: 'cover',
        borderRadius: element.radius ? `${element.radius}px` : undefined,
      }}
      src={element.src}
      alt={element.name ?? element.id}
    />
  );
}

function renderShapeElement(element: KitShapeElement) {
  return (
    <div
      key={element.id}
      className="scenekit-slide__shape"
      style={{
        ...createElementBoxStyle(element),
        background: element.fill ?? '#cbd5e1',
        opacity: element.opacity ?? 1,
        border: `${element.outline?.width ?? 0}px solid ${element.outline?.color ?? 'transparent'}`,
        borderRadius: '18px',
      }}
      aria-label={element.name ?? element.id}
    />
  );
}

function renderLineElement(element: KitLineElement) {
  const deltaX = element.end[0] - element.start[0];
  const deltaY = element.end[1] - element.start[1];
  const length = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  const angle = (Math.atan2(deltaY, deltaX) * 180) / Math.PI;

  return (
    <div
      key={element.id}
      className="scenekit-slide__line"
      style={{
        position: 'absolute',
        left: `${element.left + element.start[0]}px`,
        top: `${element.top + element.start[1]}px`,
        width: `${length}px`,
        borderTop: `2px ${element.style ?? 'solid'} ${element.color}`,
        transform: `rotate(${angle}deg)`,
        transformOrigin: 'top left',
      }}
      aria-hidden="true"
    />
  );
}

function renderTableCell(cell: KitTableCell) {
  return (
    <td
      key={cell.id}
      colSpan={cell.colspan}
      rowSpan={cell.rowspan}
      style={{
        padding: '10px 12px',
        border: '1px solid #cbd5e1',
        background: cell.style?.backcolor,
        color: cell.style?.color,
        textAlign: cell.style?.align,
        fontWeight: cell.style?.bold ? 700 : 400,
      }}
    >
      {cell.text}
    </td>
  );
}

function renderTableElement(element: KitTableElement) {
  return (
    <div key={element.id} className="scenekit-slide__table" style={createElementBoxStyle(element)}>
      <table>
        <tbody>
          {element.data.map((row, rowIndex) => (
            <tr key={`${element.id}-row-${rowIndex}`}>{row.map(renderTableCell)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderChartElement(element: KitChartElement) {
  const primarySeries = element.data.series[0] ?? [];
  const max = Math.max(...primarySeries, 1);

  return (
    <div key={element.id} className="scenekit-slide__chart" style={createElementBoxStyle(element)}>
      <div className="scenekit-slide__chart-title">{element.chartType.toUpperCase()}</div>
      <div className="scenekit-slide__chart-bars">
        {element.data.labels.map((label, index) => {
          const value = primarySeries[index] ?? 0;
          const color = element.themeColors?.[index % (element.themeColors.length || 1)] ?? '#2563eb';
          return (
            <div key={`${element.id}-${label}`} className="scenekit-slide__chart-row">
              <span>{label}</span>
              <div className="scenekit-slide__chart-track">
                <div
                  className="scenekit-slide__chart-fill"
                  style={{ width: `${(value / max) * 100}%`, background: color }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function renderLatexElement(element: KitLatexElement) {
  return (
    <pre key={element.id} className="scenekit-slide__latex" style={createElementBoxStyle(element)}>
      <code>{element.latex}</code>
    </pre>
  );
}

function renderVideoElement(element: KitVideoElement) {
  return (
    <video
      key={element.id}
      className="scenekit-slide__video"
      style={createElementBoxStyle(element)}
      src={element.src}
      poster={element.poster}
      controls
      autoPlay={element.autoplay}
    />
  );
}

function renderAudioElement(element: KitAudioElement) {
  return (
    <div key={element.id} className="scenekit-slide__audio" style={createElementBoxStyle(element)}>
      <audio src={element.src} controls autoPlay={element.autoplay} loop={element.loop} />
    </div>
  );
}

function renderUnsupportedElement(element: KitSlideElement) {
  return (
    <div key={element.id} className="scenekit-slide__unsupported" style={createElementBoxStyle(element)}>
      Unsupported element: {element.type}
    </div>
  );
}

function renderElement(element: KitSlideElement) {
  switch (element.type) {
    case 'text':
      return renderTextElement(element);
    case 'image':
      return renderImageElement(element);
    case 'shape':
      return renderShapeElement(element);
    case 'line':
      return renderLineElement(element);
    case 'table':
      return renderTableElement(element);
    case 'chart':
      return renderChartElement(element);
    case 'latex':
      return renderLatexElement(element);
    case 'video':
      return renderVideoElement(element);
    case 'audio':
      return renderAudioElement(element);
    default:
  return renderUnsupportedElement(element);
  }
}

type SlideSceneProps = Omit<KitSceneRendererProps, 'scene'> & {
  scene: KitSlideScene;
};

export function SlideScene({ scene, className, style }: SlideSceneProps) {
  const { canvas } = scene.content;
  const viewportHeight = Math.round(canvas.viewportSize / canvas.viewportRatio);
  const backgroundStyle = createBackgroundStyle(canvas.background, canvas.theme.backgroundColor);

  return (
    <section className={joinClassNames('scenekit-slide-shell', className)} style={style}>
      <div
        className="scenekit-slide"
        style={{
          width: `${canvas.viewportSize}px`,
          height: `${viewportHeight}px`,
          color: canvas.theme.fontColor,
          fontFamily: canvas.theme.fontName,
          ...backgroundStyle,
        }}
        aria-label={scene.title}
      >
        <div className="scenekit-slide__meta">
          <span className="scenekit-slide__badge">Slide</span>
          <h2>{scene.title}</h2>
        </div>
        {canvas.elements.map(renderElement)}
        {!canvas.elements.length && (
          <div className="scenekit-slide__empty">{stripHtml(scene.title) || 'Empty slide'}</div>
        )}
      </div>
    </section>
  );
}
