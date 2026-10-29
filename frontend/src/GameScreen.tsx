import { useEffect, useRef, useState } from "react";
import { ApiError, getGame, sendClick, type Game } from "./api";
import GameCanvas from "./GameCanvas";

type Props = {
  initialGame: Game;
  onFinish: (game: Game) => void;
  onError: () => void;
};

function formatTime(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export default function GameScreen({ initialGame, onFinish, onError }: Props) {
  const [game, setGame] = useState(initialGame);
  // 서버가 준 remaining_sec로 끝나는 시각을 잡고, 서버 응답을 받을 때마다 다시 맞춘다.
  const deadlineRef = useRef(Date.now() + initialGame.remaining_sec * 1000);
  const [remaining, setRemaining] = useState(initialGame.remaining_sec);
  const busyRef = useRef(false);

  function applyGame(next: Game) {
    if (next.status === "finished") {
      onFinish(next);
      return;
    }
    deadlineRef.current = Date.now() + next.remaining_sec * 1000;
    setRemaining(next.remaining_sec);
    setGame(next);
  }

  async function refresh() {
    try {
      applyGame(await getGame(game.game_id));
    } catch {
      onError();
    }
  }

  // 1초마다 카운트다운. 0이 되면 서버에서 끝난 상태를 받아 온다.
  const refreshRef = useRef(refresh);
  refreshRef.current = refresh;
  useEffect(() => {
    const timer = setInterval(() => {
      const left = Math.max(0, Math.ceil((deadlineRef.current - Date.now()) / 1000));
      setRemaining(left);
      if (left === 0 && !busyRef.current) {
        busyRef.current = true;
        refreshRef.current().finally(() => {
          busyRef.current = false;
        });
      }
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  async function handleClick(x: number, y: number) {
    // 응답 순서가 뒤섞이지 않도록 요청 중에는 다음 클릭을 보내지 않는다.
    if (busyRef.current) return;
    busyRef.current = true;
    try {
      const result = await sendClick(game.game_id, x, y);
      applyGame(result.game);
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        await refresh();
      } else {
        onError();
      }
    } finally {
      busyRef.current = false;
    }
  }

  const found = new Set(game.found_item_ids);

  return (
    <div className="game-screen">
      <div className="canvas-area">
        <GameCanvas game={game} onClick={handleClick} />
      </div>
      <aside className="panel">
        <div className="timer">{formatTime(remaining)}</div>
        <h2>
          찾을 물건 ({found.size}/{game.items.length})
        </h2>
        <ul className="item-list">
          {game.items.map((item) => (
            <li key={item.id} className={found.has(item.id) ? "found" : ""}>
              <img src={item.image} alt="" width={40} height={40} />
              <span className="name">{item.name}</span>
              {found.has(item.id) && <span className="check">찾음</span>}
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
