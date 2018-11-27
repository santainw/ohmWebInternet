from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse as up
from urllib.parse import parse_qs as pq

form = '''<!DOCTYPE html>
    <title>Message Board</title>
        <form method="POST" action="http://localhost:9000/">
            <textarea name="message"></textarea>
            <br>
            <button type="submit">Post it!</button>
        </form>'''

class MessageHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-length', 0))
        data = self.rfile.read(length).decode()
        message = pq(data)["message"][0]
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(message.encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(form.encode())


if __name__ == '__main__':
    server_address = ('', 9000)
    httpd = HTTPServer(server_address, MessageHandler)
    httpd.serve_forever()