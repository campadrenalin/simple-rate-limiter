from src.rate_limit import RateLimiter, LimitExceeded
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import json

rl = RateLimiter(5, 60)

class GetTime(BaseHTTPRequestHandler):
    def send_json(self, code, status_message, data):
        if code == 200:
            self.send_response(code)
        else:
            self.send_error(code, explain=status_message)

        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        try:
            rl.check()
            self.send_json(200, "OK", {
                "status": "ok",
                "current_time": str(datetime.now())
            })
        except LimitExceeded as e:
            self.send_json(429, str(e), {
                "status": "failed",
                "error": str(e)
            })

if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, GetTime)
    print("Serving on http://locahost:8000/ ...")
    httpd.serve_forever()