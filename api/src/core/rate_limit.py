import re
from math import ceil
from time import monotonic

from starlette.responses import JSONResponse


_ANSWER_PATH = re.compile(r"^/api/quizzes/\d+/questions/\d+/answer$")
_QUIZ_ITEM_PATH = re.compile(r"^/api/quizzes/\d+(?:/admin)?$")
_MAX_BUCKETS = 20000


class InMemoryRateLimitMiddleware:
    def __init__(self, app):
        self.app = app
        self._buckets: dict[tuple[str, str], tuple[float, int]] = {}
        self._next_cleanup = monotonic() + 60

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] == "OPTIONS":
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_ip = str(client[0]) if client else "unknown"
        path = scope["path"]
        method = scope["method"]
        now = monotonic()
        self._cleanup(now)

        policies = [("global", 120, 60)]
        if method == "POST" and path == "/admin/login":
            policies.append(("admin-login", 5, 60))
        elif method == "POST" and _ANSWER_PATH.fullmatch(path):
            policies.append(("quiz-answer", 30, 60))
        elif path == "/health":
            policies.append(("health", 60, 60))
        elif method in {"POST", "PUT", "PATCH", "DELETE"} and (
            path.startswith("/admin/") or _QUIZ_ITEM_PATH.fullmatch(path)
        ):
            policies.append(("writes", 20, 60))

        for name, limit, window_seconds in policies:
            retry_after = self._consume(client_ip, name, limit, window_seconds, now)
            if retry_after is not None:
                response = JSONResponse(
                    {"detail": "Limite de requisições excedido. Tente novamente em breve."},
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    def _consume(
        self,
        client_ip: str,
        policy: str,
        limit: int,
        window_seconds: int,
        now: float,
    ) -> int | None:
        key = (client_ip, policy)
        if key not in self._buckets and len(self._buckets) >= _MAX_BUCKETS:
            return 60

        window_start, count = self._buckets.get(key, (now, 0))
        if now - window_start >= window_seconds:
            window_start, count = now, 0
        if count >= limit:
            return max(1, ceil(window_seconds - (now - window_start)))

        self._buckets[key] = (window_start, count + 1)
        return None

    def _cleanup(self, now: float) -> None:
        if now < self._next_cleanup:
            return
        self._buckets = {
            key: state
            for key, state in self._buckets.items()
            if now - state[0] < 60
        }
        self._next_cleanup = now + 60