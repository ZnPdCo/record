import sys
import os
import subprocess

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'public', 'data.json')


class EditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('OI Record Editor')
        self.resize(1280, 800)

        self.view = QWebEngineView()
        self.view.page().profile().downloadRequested.connect(self.on_download)
        self.setCentralWidget(self.view)

        self.statusBar().showMessage('就绪')
        self.load_page()

    def load_page(self):
        self.view.load(QUrl('https://znpdco.github.io/record/#/edit'))
        self.statusBar().showMessage('加载中...')
        self.view.loadFinished.connect(
            lambda ok: self.statusBar().showMessage('已加载' if ok else '加载失败')
        )

    def on_download(self, download):
        if download.suggestedFileName() != 'data.json':
            download.cancel()
            return

        download.setPath(DATA_PATH)
        download.finished.connect(self.on_saved)
        download.accept()
        self.statusBar().showMessage('正在保存...')

    def on_saved(self):
        self.statusBar().showMessage('正在推送到 GitHub...')
        try:
            subprocess.run(['git', 'add', 'public/data.json'], cwd=BASE_DIR, check=True,
                           capture_output=True, text=True)
            subprocess.run(['git', 'commit', '-m', 'Update data.json via editor'],
                           cwd=BASE_DIR, capture_output=True, text=True)
            subprocess.run(['git', 'push'], cwd=BASE_DIR, check=True,
                           capture_output=True, text=True, timeout=30)
            self.statusBar().showMessage('已保存并推送!')
            QMessageBox.information(self, '成功', '数据已保存并推送到 GitHub。')
        except subprocess.TimeoutExpired:
            self.statusBar().showMessage('推送超时')
            QMessageBox.warning(self, '错误', '推送超时，请检查网络连接。')
        except subprocess.CalledProcessError as e:
            self.statusBar().showMessage('推送失败')
            QMessageBox.critical(self, '错误', f'推送失败:\n{e.stderr or e.stdout}')
        except Exception as e:
            self.statusBar().showMessage('保存失败')
            QMessageBox.critical(self, '错误', f'保存失败:\n{str(e)}')


def main():
    app = QApplication(sys.argv)
    window = EditorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
