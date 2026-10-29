export type Item = {
  id: number;
  name: string;
  image: string;
  x: number;
  y: number;
  size: number;
};

export type Game = {
  game_id: string;
  status: "playing" | "finished";
  map: { width: number; height: number };
  time_limit_sec: number;
  remaining_sec: number;
  items: Item[];
  found_item_ids: number[];
  score: number | null;
};

export type ClickResult = {
  hit: boolean;
  item_id: number | null;
  game: Game;
};

export class ApiError extends Error {
  constructor(public status: number) {
    super(`API error ${status}`);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new ApiError(res.status);
  return res.json() as Promise<T>;
}

export function createGame(): Promise<Game> {
  return request<Game>("/games", { method: "POST" });
}

export function getGame(gameId: string): Promise<Game> {
  return request<Game>(`/games/${encodeURIComponent(gameId)}`);
}

export function sendClick(gameId: string, x: number, y: number): Promise<ClickResult> {
  return request<ClickResult>(`/games/${encodeURIComponent(gameId)}/clicks`, {
    method: "POST",
    body: JSON.stringify({ x, y }),
  });
}
