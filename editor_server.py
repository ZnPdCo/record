import os
import json
import subprocess
import re
import sys
import webbrowser
import socketserver
from http.server import HTTPServer, SimpleHTTPRequestHandler

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
DATA_PATH = os.path.join(BASE_DIR, 'public', 'data.json')

INJECT_SCRIPT = r'''
<script>
(function(){
  var _createObjectURL = URL.createObjectURL;
  var _revokeObjectURL = URL.revokeObjectURL;
  var _createElement = document.createElement.bind(document);
  var blobs = {};

  URL.createObjectURL = function(blob){
    var url = _createObjectURL(blob);
    if (blob instanceof Blob) blobs[url] = blob;
    return url;
  };
  URL.revokeObjectURL = function(url){
    delete blobs[url];
    _revokeObjectURL(url);
  };

  document.createElement = function(tag, opts){
    var el = _createElement(tag, opts);
    if (tag && tag.toLowerCase() === 'a'){
      var _click = el.click.bind(el);
      el.click = function(){
        if (el.download === 'data.json' && el.href && blobs[el.href]){
          var data = blobs[el.href];
          delete blobs[el.href];
          data.text().then(function(txt){
            fetch('/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:txt });
          });
          return;
        }
        _click();
      };
    }
    return el;
  };
})();
</script>
'''

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def translate_path(self, path):
        if path.startswith('/record/'):
            path = '/' + path[len('/record/'):]
        return super().translate_path(path)

    def send_index(self):
        path = os.path.join(DIST_DIR, 'index.html')
        if not os.path.isfile(path):
            self.send_error(404)
            return
        content = open(path, 'r', encoding='utf-8').read()
        content = content.replace('</body>', INJECT_SCRIPT + '</body>')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_GET(self):
        if self.path == '/data.json':
            if not os.path.isfile(DATA_PATH):
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            with open(DATA_PATH, 'rb') as f:
                self.wfile.write(f.read())
            return

        req = self.path.split('?')[0]
        if req in ('/', '/record/', '/record'):
            self.send_index()
            return

        file_path = self.translate_path(req)
        if not os.path.isfile(file_path):
            self.send_index()
            return

        ext = os.path.splitext(file_path)[1]
        ct = {
            '.js': 'application/javascript', '.css': 'text/css',
            '.html': 'text/html', '.json': 'application/json',
            '.png': 'image/png', '.svg': 'image/svg+xml',
            '.woff': 'font/woff', '.woff2': 'font/woff2',
        }.get(ext, 'application/octet-stream')
        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            with open(DATA_PATH, 'wb') as f:
                f.write(data)
            ok, err = git_push()
            if ok:
                self.send_response(200)
            else:
                self.send_response(500)
            self.end_headers()
            self.wfile.write(b'OK' if ok else str(err).encode('utf-8'))
            return
        self.send_error(404)

def git_pull():
    try:
        subprocess.run(['git', 'pull'], cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
        print('✓ git pull 完成')
    except Exception as e:
        print(f'! git pull 失败: {e}')

def git_push():
    try:
        subprocess.run(['git', 'add', 'public/data.json'], cwd=BASE_DIR, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Update data.json via editor'], cwd=BASE_DIR, capture_output=True)
        subprocess.run(['git', 'push'], cwd=BASE_DIR, capture_output=True, timeout=30)
        return True, None
    except subprocess.TimeoutExpired:
        return False, '推送超时'
    except subprocess.CalledProcessError as e:
        return False, e.stderr or e.stdout or '推送失败'
    except Exception as e:
        return False, str(e)

def main():
    git_pull()

    port = 8765
    server = HTTPServer(('localhost', port), Handler)
    url = f'http://localhost:{port}/record/#/edit'
    print(f'打开 {url}')
    webbrowser.open(url)
    print('按 Ctrl+C 停止')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

if __name__ == '__main__':
    main()
