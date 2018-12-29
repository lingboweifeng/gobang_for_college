from base import BasePlayer,Chess,is_win
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox,QLabel
from random import choice

class DoublePlayer(BasePlayer):
    def __init__(self,parent=None):
        super().__init__(parent)
        # 白黑棋随机先下
        self.is_black=choice([True,False])
        self.is_over=False
        # 建立一个为存储下棋顺序的列表
        self.order=[]
        self.chessboard = [[None for i in range(19)] for j in range(19)]
        # 点击开始按钮时
        self.restart_btn.clicked.connect(self.restart)
        # 点击认输按钮时
        self.lose_btn.clicked.connect(self.lose)
        # 点击悔棋按钮时
        self.hq_btn.clicked.connect(self.hq)
        self.win_label=None

    def hq(self):
        if not self.is_over:
            # 列表不为空时才可以悔棋
            if  self.order:
                pos = self.order.pop()
                # 通过元组记录的坐标销毁棋子
                self.chessboard[pos[0]][pos[1]].close()
                self.chessboard[pos[0]][pos[1]] = None
                # 转置棋子颜色
                self.is_black = not self.is_black

    def lose(self):
        if not self.is_over:
            self.lose_label = QLabel(self)
            if self.is_black:
                pic = QPixmap('source/白棋胜利.png')
            else:
                pic = QPixmap('source/黑棋胜利.png')
            self.lose_label.setPixmap(pic)
            self.lose_label.move(130, 75)
            self.lose_label.show()
            self.is_over = True

    def restart(self):
        # 重新开始游戏
        self.is_over=False
        if self.win_label is not None:
            # 清空胜利图片
            self.win_label.close()
        # 清空棋盘列表
        for i in range(0,19):
            for j in range(0,19):
                if self.chessboard[j][i] is not None:
                    self.chessboard[j][i].close()
                    self.chessboard[j][i]=None


    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        # 若游戏胜负已分，则鼠标点击失效
        if self.is_over:
            return

        #下一次鼠标点击是白棋还是黑棋有次决定
        if self.is_black:
            self.chess=Chess(color='b',parent=self)
        else:
            self.chess=Chess(color='w',parent=self)

        # 确定落子位置
        if 50<a0.x()<590 and 50<a0.y()<590:
            # cx=(a0.x()//30)*30+5
            # cy=(a0.y()//30)*30+5
            if (a0.x()-50)%30<=15:
                x=(a0.x()-50)//30*30+50
            else:
                x=((a0.x()-50)//30+1)*30+50
            if (a0.y()-50)%30<=15:
                y=(a0.y()-50)//30*30+50
            else:
                y=((a0.y()-50)//30+1)*30+50
            cx=(x-50)//30
            cy=(y-50)//30

            x=x-self.chess.width()/2
            y=y-self.chess.height()/2

            if self.chessboard[cx][cy] is None:
                self.chess.move(x,y)
                self.chess.show()
                self.is_black = not self.is_black
                self.chessboard[cx][cy] = self.chess      # 添加到棋盘中
                self.order.append((cx,cy))
            # is_win函数设计成如果有五子连珠，就返回对应颜色，反之返回False
            color=is_win(self.chessboard)
            if color:
                # QMessageBox.information(self,'消息','{0}棋胜利'.format(color)
                self.win_label=QLabel(self)
                if color=='b':
                    pic=QPixmap('source/黑棋胜利.png')
                else:
                    pic=QPixmap('source/白棋胜利.png')
                self.win_label.setPixmap(pic)
                self.win_label.move(130,75)
                self.win_label.show()
                self.is_over=True
            else:
                return