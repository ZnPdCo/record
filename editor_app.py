import os
import sys
import subprocess
import threading
import webview

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'public', 'data.json')

INJECT_JS = r'''
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
          var blob = blobs[el.href];
          delete blobs[el.href];
          blob.text().then(function(txt){
            pywebview.api.save(txt).then(function(msg){
              if (typeof $ !== 'undefined')
                $('body').toast({ message: msg || '已保存并推送到 GitHub', class: 'success', position: 'bottom right', displayTime: 2500 });
            }).catch(function(err){
              if (typeof $ !== 'undefined')
                $('body').toast({ message: '保存失败: ' + err, class: 'error', position: 'bottom right', displayTime: 5000 });
            });
          });
          return;
        }
        _click();
      };
    }
    return el;
  };
})();
'''


class Api:
    def save(self, data):
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            f.write(data)
        try:
            subprocess.run(['git', 'add', 'public/data.json'], cwd=BASE_DIR,
                           capture_output=True, text=True, check=True)
            subprocess.run(['git', 'commit', '-m', 'Update data.json via editor'],
                           cwd=BASE_DIR, capture_output=True, text=True)
            subprocess.run(['git', 'push'], cwd=BASE_DIR,
                           capture_output=True, text=True, timeout=30, check=True)
            return '已保存并推送到 GitHub'
        except subprocess.TimeoutExpired:
            raise Exception('推送超时，请检查网络连接')
        except subprocess.CalledProcessError as e:
            raise Exception(f'推送失败: {e.stderr.strip() or e.stdout.strip() or "未知错误"}')
        except Exception as e:
            raise Exception(str(e))


def git_pull():
    try:
        subprocess.run(['git', 'pull'], cwd=BASE_DIR,
                       capture_output=True, text=True, timeout=30)
        return True, None
    except Exception as e:
        return False, str(e)


def main():
    print('正在同步远程数据...')
    ok, err = git_pull()
    if ok:
        print('✓ git pull 完成')
    else:
        print(f'! git pull 失败: {err}')

    api = Api()
    window = webview.create_window(
        'OI Record Editor',
        url='https://znpdco.github.io/record/#/edit',
        js_api=api,
        width=1280,
        height=800,
    )
    window.events.loaded += lambda: window.evaluate_js(INJECT_JS)
    webview.start()


if __name__ == '__main__':
    main()
