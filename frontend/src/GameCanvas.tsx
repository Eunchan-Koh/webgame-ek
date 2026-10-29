import { useEffect, useRef } from "react";
import type { Game } from "./api";

const BACKGROUND_SRC = "/assets/background.svg";
const LIGHT_RADIUS = 120; // 논리 좌표 기준 손전등 반경
const DARKNESS = 0.97; // 어두운 부분 불투명도 (완전히 검게 하지 않음)

type Props = {
  game: Game;
  onClick: (x: number, y: number) => void;
};

export default function GameCanvas({ game, onClick }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef<{ x: number; y: number } | null>(null);
  const imagesRef = useRef(new Map<string, HTMLImageElement>());
  const gameRef = useRef(game);
  gameRef.current = game;

  const { width: mapW, height: mapH } = game.map;

  // 이미지 로드: 배경 1장 + 아이템별 이미지
  useEffect(() => {
    const images = imagesRef.current;
    for (const src of [BACKGROUND_SRC, ...game.items.map((i) => i.image)]) {
      if (images.has(src)) continue;
      const img = new Image();
      img.src = src;
      images.set(src, img);
    }
  }, [game.items]);

  // 캔버스 크기: 영역 안에서 맵 비율을 유지하며 확대·축소
  useEffect(() => {
    const wrap = wrapRef.current!;
    const canvas = canvasRef.current!;
    const resize = () => {
      const scale = Math.min(wrap.clientWidth / mapW, wrap.clientHeight / mapH);
      const w = Math.floor(mapW * scale);
      const h = Math.floor(mapH * scale);
      const dpr = window.devicePixelRatio || 1;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(wrap);
    return () => ro.disconnect();
  }, [mapW, mapH]);

  // 그리기 루프 (모든 그리기는 논리 좌표로)
  useEffect(() => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    let frame = 0;

    const imageFor = (src: string) => {
      const img = imagesRef.current.get(src);
      return img && img.complete && img.naturalWidth > 0 ? img : null;
    };

    const draw = () => {
      const g = gameRef.current;
      const found = new Set(g.found_item_ids);

      ctx.setTransform(canvas.width / mapW, 0, 0, canvas.height / mapH, 0, 0);
      ctx.fillStyle = "#000";
      ctx.fillRect(0, 0, mapW, mapH);

      const bg = imageFor(BACKGROUND_SRC);
      if (bg) ctx.drawImage(bg, 0, 0, mapW, mapH);

      for (const item of g.items) {
        if (found.has(item.id)) continue;
        const img = imageFor(item.image);
        if (img) ctx.drawImage(img, item.x, item.y, item.size, item.size);
      }

      // 손전등: 커서 주변만 밝고 바깥은 아주 어둡게
      const m = mouseRef.current;
      if (m) {
        const grad = ctx.createRadialGradient(m.x, m.y, 0, m.x, m.y, LIGHT_RADIUS);
        grad.addColorStop(0, "rgba(0,0,0,0)");
        grad.addColorStop(0.6, "rgba(0,0,0,0)");
        grad.addColorStop(1, `rgba(0,0,0,${DARKNESS})`);
        ctx.fillStyle = grad;
      } else {
        ctx.fillStyle = `rgba(0,0,0,${DARKNESS})`;
      }
      ctx.fillRect(0, 0, mapW, mapH);

      // 찾은 아이템은 어둠 위에 밝게 그리고 초록 테두리 + 체크 표시
      ctx.strokeStyle = "#3ddc84";
      ctx.lineWidth = 4;
      for (const item of g.items) {
        if (!found.has(item.id)) continue;
        const img = imageFor(item.image);
        if (img) ctx.drawImage(img, item.x, item.y, item.size, item.size);
        ctx.strokeRect(item.x - 4, item.y - 4, item.size + 8, item.size + 8);
        const cx = item.x + item.size;
        const cy = item.y;
        ctx.beginPath();
        ctx.moveTo(cx - 10, cy);
        ctx.lineTo(cx - 3, cy + 7);
        ctx.lineTo(cx + 10, cy - 8);
        ctx.stroke();
      }

      frame = requestAnimationFrame(draw);
    };
    frame = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(frame);
  }, [mapW, mapH]);

  function toLogical(e: React.MouseEvent<HTMLCanvasElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    return {
      x: ((e.clientX - rect.left) / rect.width) * mapW,
      y: ((e.clientY - rect.top) / rect.height) * mapH,
    };
  }

  return (
    <div ref={wrapRef} className="canvas-wrap">
      <canvas
        ref={canvasRef}
        onMouseMove={(e) => {
          mouseRef.current = toLogical(e);
        }}
        onMouseLeave={() => {
          mouseRef.current = null;
        }}
        onClick={(e) => {
          const p = toLogical(e);
          onClick(p.x, p.y);
        }}
      />
    </div>
  );
}
