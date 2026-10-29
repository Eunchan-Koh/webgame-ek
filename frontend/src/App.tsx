import { useState } from "react";
import { createGame, type Game } from "./api";
import GameScreen from "./GameScreen";

type Screen = "start" | "playing" | "result";

export default function App() {
  const [screen, setScreen] = useState<Screen>("start");
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function start() {
    setLoading(true);
    setError(null);
    try {
      setGame(await createGame());
      setScreen("playing");
    } catch {
      setError("게임을 시작하지 못했습니다. 잠시 후 다시 시도해 주세요.");
      setScreen("start");
    } finally {
      setLoading(false);
    }
  }

  function finish(finished: Game) {
    setGame(finished);
    setScreen("result");
  }

  function fail() {
    setError("서버와 연결이 끊겼습니다. 다시 시작해 주세요.");
    setGame(null);
    setScreen("start");
  }

  if (screen === "playing" && game) {
    return <GameScreen key={game.game_id} initialGame={game} onFinish={finish} onError={fail} />;
  }

  return (
    <div className="center-screen">
      {screen === "result" && game ? (
        <>
          <h1>게임 종료</h1>
          <p className="score">점수: {game.score ?? "-"}</p>
          <p>
            찾은 아이템: {game.found_item_ids.length} / {game.items.length}
          </p>
          <button onClick={start} disabled={loading}>
            다시 하기
          </button>
        </>
      ) : (
        <>
          <h1>물건 찾기</h1>
          <p>어두운 방에서 손전등(마우스)으로 비추며 숨겨진 물건을 찾아 클릭하세요.</p>
          <button onClick={start} disabled={loading}>
            게임 시작
          </button>
        </>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
