#存放相关的基础数据

from PyQt5.QtWidgets import QWidget,QPushButton,QLabel
from PyQt5.QtGui import QPalette,QBrush,QPixmap,QIcon
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import pyqtSignal

class BasePlayer(QWidget):

    backsignal=pyqtSignal()
    def __init__(self,parent=None):
        self.is_chess=True
        self.m_list=[]  #检查坐标是否重复

        super().__init__(parent)
        self.setWindowIcon(QIcon('source/icon.ico'))
        self.setWindowTitle('五子棋--三级狗')
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(760,650)
        palette=QPalette()
        palette.setBrush(self.backgroundRole() ,QBrush(QPixmap('source/游戏界面.png')))
        self.setPalette(palette)

        self.back_btn=TDPushButton('source/返回按钮_normal.png','source/返回按钮_hover.png','source/返回按钮_press.png',self)
        self.back_btn.clicked.connect(self.back)

        self.restart_btn=TDPushButton('source/开始按钮_normal.png','source/开始按钮_hover.png','source/开始按钮_press.png',self)
        self.lose_btn=TDPushButton('source/认输按钮_normal.png','source/认输按钮_hover.png','source/认输按钮_press.png',self)
        self.hq_btn=TDPushButton('source/悔棋按钮_normal.png','source/悔棋按钮_hover.png','source/悔棋按钮_press.png',self)

        self.back_btn.move(680,10)
        self.restart_btn.move(640,240)
        self.lose_btn.move(640,310)
        self.hq_btn.move(640,380)

    def back(self):
        #发射自定义的槽
        self.backsignal.emit()
        self.close()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        pich=QPixmap('source/黑子.png')
        picb=QPixmap('source/白子.png')
        self.chess=QLabel(self)
        if self.is_chess:
            self.chess.setPixmap(pich)
        else:
            self.chess.setPixmap(picb)
        self.is_chess=not self.is_chess

        if 50<a0.x()<590 and 50<a0.y()<590:
            cx=(a0.x()//30)*30+5
            cy=(a0.y()//30)*30+5
            if not [cx,cy] in self.m_list:
                self.chess.move(cx,cy)
                self.chess.show()
                self.m_list.append([cx,cy])
        #if                                            
        # self.mx,self.my=a0.x(),a0.y()
        # if 35<self.mx-15<575 and 35<self.my-15<575:
        #     if ((self.mx-50)//15)%2:
        #         self.cx=self.mx-(self.mx-50)%15
        #     else:
        #         self.cx=self.mx+15-(self.mx-50)%15
        #     if ((self.my-50)//15)%2:
        #         self.cy=self.my-(self.my-50)%15
        #     else:
        #         self.cy=self.my+15-(self.my-50)%15
        #
        #     self.chess.move(self.cx-15,self.cy-15)
        #     self.chess.show()


    def closeEvent(self, a0: QtGui.QCloseEvent):
        pass


class TDPushButton(QLabel):
    clicked=pyqtSignal()
    def __init__(self,str1,str2,str3,parent):
        super().__init__(parent)
        self.pic_normal=QPixmap(str1)
        self.pic_hover=QPixmap(str2)
        self.pic_press=QPixmap(str3)
        #重设大小，显示正常图片大小
        self.resize(self.pic_normal.size())
        self.setPixmap(self.pic_normal)

    def enterEvent(self, a0: QtCore.QEvent):
        self.setPixmap(self.pic_hover)

    def leaveEvent(self, a0: QtCore.QEvent):
        self.setPixmap(self.pic_normal)

    def mousePressEvent(self, ev: QtGui.QMouseEvent):
        self.setPixmap(self.pic_press)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent):
        self.clicked.emit()
        self.setPixmap(self.pic_hover)

class Chess(QLabel):
    def __init__(self,color='w',parent=None):
        super().__init__(parent)
        self.color=color
        if color=='w':
            pic=QPixmap('source/白子.png')
        elif color=='b':
            pic=QPixmap('source/黑子.png')
        self.resize(pic.size())
        self.setPixmap(pic)

def is_win(chessboard):
    '''
    判断棋盘上是否有玩家胜利
    :param chessboard: 19*19的二维数组
    :return: 没有返回False，有的话，返回胜利者的颜色
    '''
    for j in range(0,19): # 注意这里会出现数组越界的情况，我们在代码中直接pass掉
        for i in range(0,19):
            if chessboard[i][j] is not None:
                c = chessboard[i][j].color
                # 判断右、右下、下、左下四个方向是否构成五子连珠，如果构成了，就可以。
                # 右
                try:
                    if chessboard[i+1][j] is not None:
                        if chessboard[i+1][j].color == c:
                            if chessboard[i+2][j] is not None:
                                if chessboard[i+2][j].color == c:
                                    if chessboard[i+3][j] is not None:
                                        if chessboard[i+3][j].color == c:
                                            if chessboard[i+4][j] is not None:
                                                if chessboard[i+4][j].color == c:
                                                    return c
                except IndexError:
                    pass
                # 右下
                try:
                    if chessboard[i+1][j+1] is not None:
                        if chessboard[i+1][j+1].color == c:
                            if chessboard[i+2][j+2] is not None:
                                if chessboard[i+2][j+2].color == c:
                                    if chessboard[i+3][j+3] is not None:
                                        if chessboard[i+3][j+3].color == c:
                                            if chessboard[i+4][j+4] is not None:
                                                if chessboard[i+4][j+4].color == c:
                                                    return c
                except IndexError:
                    pass
                # 下
                try:
                    if chessboard[i][j+1] is not None:
                        if chessboard[i][j+1].color == c:
                            if chessboard[i][j+2] is not None:
                                if chessboard[i][j+2].color == c:
                                    if chessboard[i][j+3] is not None:
                                        if chessboard[i][j+3].color == c:
                                            if chessboard[i][j+4] is not None:
                                                if chessboard[i][j+4].color == c:
                                                    return c
                except IndexError:
                    pass
                # 左下
                try:
                    if chessboard[i-1][j+1] is not None:
                        if chessboard[i-1][j+1].color == c:
                            if chessboard[i-2][j+2] is not None:
                                if chessboard[i-2][j+2].color == c:
                                    if chessboard[i-3][j+3] is not None:
                                        if chessboard[i-3][j+3].color == c:
                                            if chessboard[i-4][j+4] is not None:
                                                if chessboard[i-4][j+4].color == c:
                                                    return c
                except IndexError:
                    pass

    # 所有的都不成立，返回False
    return False