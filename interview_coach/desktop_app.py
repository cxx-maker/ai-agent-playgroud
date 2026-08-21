"""桌面应用入口 - PyQt5 + WebEngine"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog, QMessageBox, QTextEdit, QHBoxLayout
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon

# 设置环境
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--no-sandbox'

class InterviewCoachApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("面试辅助系统 v1.0")
        self.setGeometry(100, 100, 1400, 900)

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 顶部说明
        title = QLabel("💼 面试辅助系统 - 多 Agent 架构")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # WebView - 嵌入 Gradio
        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl("http://localhost:7860"))
        layout.addWidget(self.webview)

        # 底部状态栏
        self.status_label = QLabel("状态: 正在连接...")
        self.status_label.setStyleSheet("padding: 5px; background: #f0f0f0;")
        layout.addWidget(self.status_label)

        # 定时检查连接状态
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self.check_loaded)
        self.load_timer.start(2000)

        # 加载完成回调
        self.webview.loadFinished.connect(self.on_load_finished)
        self.webview.page().loadStarted.connect(lambda: self.status_label.setText("状态: 加载中..."))

    def check_loaded(self):
        if self.webview.url().toString() != "about:blank":
            self.status_label.setText("状态: 已连接 ✅")
            self.load_timer.stop()

    def on_load_finished(self, ok):
        if ok:
            self.status_label.setText("状态: 加载成功 ✅")
        else:
            self.status_label.setText("状态: 加载失败 ❌ - 请确保 Gradio 服务已启动")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("面试辅助系统")

    # 创建并显示窗口
    window = InterviewCoachApp()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
