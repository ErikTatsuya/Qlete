import unittest

from starlette.responses import JSONResponse

from src.core.rate_limit import InMemoryRateLimitMiddleware


class RateLimitMiddlewareTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async def app(scope, receive, send):
            await JSONResponse({"status": "ok"})(scope, receive, send)

        self.middleware = InMemoryRateLimitMiddleware(app)

    async def request(self, client_ip: str, method: str = "POST", path: str = "/admin/login"):
        messages = []
        raw_path = path.encode()
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": raw_path,
            "query_string": b"",
            "headers": [],
            "client": (client_ip, 50000),
            "server": ("testserver", 80),
        }

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            messages.append(message)

        await self.middleware(scope, receive, send)
        start = next(message for message in messages if message["type"] == "http.response.start")
        return start["status"], dict(start["headers"])

    async def test_admin_login_is_limited_to_five_requests_per_minute(self):
        responses = [await self.request("192.0.2.1") for _ in range(6)]

        self.assertEqual([status for status, _ in responses], [200, 200, 200, 200, 200, 429])
        self.assertIn(b"retry-after", responses[-1][1])

    async def test_limits_are_isolated_by_client_ip(self):
        for _ in range(5):
            await self.request("192.0.2.1")

        status, _ = await self.request("192.0.2.2")

        self.assertEqual(status, 200)

    async def test_cors_preflight_does_not_consume_rate_limit(self):
        responses = [await self.request("192.0.2.1", method="OPTIONS") for _ in range(8)]

        self.assertTrue(all(status == 200 for status, _ in responses))


if __name__ == "__main__":
    unittest.main()