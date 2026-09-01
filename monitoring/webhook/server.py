from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        print("\n=== ALERT RECEIVED ===", flush=True)

        try:
            data = json.loads(body)

            print("Receiver:", data.get("receiver"), flush=True)
            print("Overall Status:", data.get("status"), flush=True)

            for alert in data.get("alerts", []):
                print(
                    "Alert:",
                    alert.get("labels", {}).get("alertname"),
                    flush=True
                )

                print(
                    "Status:",
                    alert.get("status"),
                    flush=True
                )

                print(
                    "Severity:",
                    alert.get("labels", {}).get("severity"),
                    flush=True
                )

                print(
                    "Summary:",
                    alert.get("annotations", {}).get("summary"),
                    flush=True
                )

                print(
                    "Description:",
                    alert.get("annotations", {}).get("description"),
                    flush=True
                )

        except Exception as e:
            print("ERROR:", str(e), flush=True)
            print(body.decode(errors="replace"), flush=True)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
