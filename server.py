from http.server import HTTPServer, SimpleHTTPRequestHandler

from ptouch import PTouch
import config
import io
class MyRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server, directory='./ui/')

    def do_POST(self):
        if self.path == "/print":
            try:
                content_len = int(self.headers.get('Content-Length'))
                post_body = self.rfile.read(content_len)
                self.do_print(post_body)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
            except Exception as ex:
                self.send_response(500)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(str(ex), "utf-8"))
                
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()

    def do_print(self, file_bytes):
        pt = PTouch(config.serialPort)
        text_stream = io.StringIO(file_bytes.decode('ascii'))
        pt.readBufferPBM(text_stream)

        if not pt.showBufferTk():
            return

        pt.printBuffer()
        pt.print(True)



handler = MyRequestHandler
httpd = HTTPServer(('localhost', 8000), handler)
httpd.serve_forever()
