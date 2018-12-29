import sys
from PyQt5.QtWidgets import  QApplication,QWidget,QPushButton,QLabel
from PyQt5.QtGui import QPalette,QPixmap,QIcon,QBrush
from singleplayer import SinglePlayer
from doubleplayer import DoublePlayer
from networkplayer import NetworkConfig
from base import TDPushButton
import cgitb
cgitb.enable(format='error')

"""
python 类中的某些实例对象为什么在使用前要把他的值设为None

实例化某一个类多次，并把他付给同一个对象多次，只是每次赋的值都不同，后面再来调用是靠什么来分这些事例的

doubleplayer中的初始化直接使用了 父类实例方法中的self.restart_btn.属性，子类的实例就是父类的实例吗，面对对象中只要是父子关系就可以这样用吗,那为什么返回按钮不这样设计呢
"""

class GameStart(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('source/icon.ico'))   #设图标
        self.setWindowTitle('五子棋--三级香')           #设标题
        self.setFixedSize(760,650)                     #设置窗体固定大小

        # 设置窗体的背景图片
        palette=QPalette()                 # palette调色板
        # setBrush(给谁设，设什么）
        palette.setBrush(self.backgroundRole(),QBrush(QPixmap('source/五子棋界面.png')))
        self.setPalette(palette)

        self.single_btn=TDPushButton('source/人机对战_normal.png','source/人机对战_hover.png','source/人机对战_press.png',self)
        self.double_btn=TDPushButton('source/双人对战_normal.png','source/双人对战_hover.png','source/双人对战_press.png',self)
        self.network_btn=TDPushButton('source/联机对战_normal.png','source/联机对战_hover.png','source/联机对战_press.png',self)
        self.single_btn.move(250,300)
        self.double_btn.move(250,400)
        self.network_btn.move(250,500)
        #给三个函数绑定处理函数，处理函数页面跳转

        self.single_btn.clicked.connect(self.single)
        self.double_btn.clicked.connect(self.double)
        self.network_btn.clicked.connect(self.network)

        self.game_window=None

    def single(self):
        self.game_window=SinglePlayer()
        # 点击返回按钮时
        self.game_window.backsignal.connect(self.back)
        self.game_window.show()
        self.close()

    def double(self):
        self.game_window=DoublePlayer()
        self.game_window.backsignal.connect(self.back)
        self.game_window.show()
        self.close()

    def network(self):
        self.game_window=NetworkConfig(main_window=self)
        #self.game_window.backsignal.connect(self.back)
        self.game_window.show()
        self.close()

    def back(self):       #捕获返回信号
        self.show()

if __name__=='__main__':
    app=QApplication(sys.argv)
    w=GameStart()
    w.show()
    sys.exit(app.exec_())