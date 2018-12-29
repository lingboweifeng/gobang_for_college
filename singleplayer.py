from base import BasePlayer,Chess,is_win
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox,QLabel
from random import choice,randint

class SinglePlayer(BasePlayer):
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
            if self.order:
                for i in range(2):
                    pos = self.order.pop()
                    # 通过元组记录的坐标销毁棋子
                    self.chessboard[pos[0]][pos[1]].close()
                    self.chessboard[pos[0]][pos[1]] = None


    def lose(self):
        if not self.is_over:
            self.win_label = QLabel(self)
            if self.is_black:
                pic = QPixmap('source/白棋胜利.png')
            else:
                pic = QPixmap('source/黑棋胜利.png')
            self.win_label.setPixmap(pic)
            self.win_label.move(130, 75)
            self.win_label.show()
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
            else:
                return
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
            if not self.is_over:
                self.auto_run()

    def auto_run(self):

        # 分别保存黑子，白子当前分数
        scores_c = [[0 for i in range(0, 19)] for j in range(0, 19)]
        scores_p = [[0 for i in range(0, 19)] for j in range(0, 19)]
        # 计算所有点的分数
        for i in range(0, 19):
            for j in range(0, 19):
                # 判断i,j 位置是否有棋
                if self.chessboard[i][j] is not None:
                    continue
                # 假设下黑棋的分数
                self.chessboard[i][j] = Chess('b', self)
                scores_c[i][j] += self.score(i, j, 'b')
                # 假设下白棋的分数
                self.chessboard[i][j] = Chess('w', self)
                scores_p[i][j] += self.score(i, j, 'w')

                self.chessboard[i][j] = None

        # 将棋盘二维数组转成一维
        r_scores_c=[]
        r_scores_p=[]
        for item in scores_c:
            r_scores_c+=item
        for item in scores_p:
            r_scores_p+=item

        #最终同一位置分数取最大值，然后合并成一个数组
        result=[max(a,b) for a,b in zip(r_scores_c,r_scores_p)]
        # 取去除最大值的下标
        chess_index=result.index(max(result))
        # 通过下标计算出落子位置
        xx=chess_index//19
        yy=chess_index%19

        if self.is_black:
            self.chess=Chess('b',self)
        else:
            self.chess=Chess('w',self)

        x = xx * 30 + 50 - 15
        y = yy * 30 + 50 - 15

        self.chess.move(x, y)
        self.chessboard[xx][yy] = self.chess
        self.chess.show()
        self.order.append((xx,yy))
        self.is_black = not self.is_black

        color = is_win(self.chessboard)
        if color:
            # QMessageBox.information(self,'消息','{0}棋胜利'.format(color)
            self.win_label = QLabel(self)
            if color == 'b':
                pic = QPixmap('source/黑棋胜利.png')
            else:
                pic = QPixmap('source/白棋胜利.png')
            self.win_label.setPixmap(pic)
            self.win_label.move(130, 75)
            self.win_label.show()
            self.is_over = True



    def score(self,x,y,color):
        # 计算如果在x，y这个点下棋会得多少分
        blank_score=[0,0,0,0]
        chess_score=[0,0,0,0] #横 纵 右下左上 左下右上
        # 右方
        for i in range(x,x+5):
            if i>=19:
                break
            if self.chessboard[i][y] is not None:
                if self.chessboard[i][y].color==color:
                    # 如果时相同颜色加一分
                    chess_score[0]+=1
                else:
                    break
            else:
                blank_score[0]+=1
                break
        # 左方
        for i in range(x-1,x-5,-1):
            if i<=0:
                break
            if self.chessboard[i][y] is not None:
                if self.chessboard[i][y].color==color:
                    # 如果时相同颜色加一分
                    chess_score[0]+=1
                else:
                    break
            else:
                blank_score[0]+=1
                break

        # 下方
        for j in range(y,y+5):
            if j>=19:
                break
            if self.chessboard[x][j] is not None:
                if self.chessboard[x][j].color==color:
                    # 如果时相同颜色加一分
                    chess_score[1]+=1
                else:
                    break
            else:
                blank_score[1]+=1
                break

        # 上方
        for j in range(y-1,y-5,-1):
            if j<=0:
                break
            if self.chessboard[x][j] is not None:
                if self.chessboard[x][j].color==color:
                    # 如果时相同颜色加一分
                    chess_score[1]+=1
                else:
                    break
            else:
                blank_score[1]+=1
                break
        # 右下方
        j=y
        for i in range(x,x+5):
            if i>=19 or j>=19:
                break
            if self.chessboard[i][j] is not None:
                if self.chessboard[i][j].color==color:
                    # 如果时相同颜色加一分
                    chess_score[2]+=1
                else:
                    break
            else:
                blank_score[2]+=1
                break
            j+=1

        # 左上方
        j=y-1
        for i in range(x-1,x-5,-1):
            if i<=0 or j<=0:
                break
            if self.chessboard[i][j] is not None:
                if self.chessboard[i][j].color==color:
                    # 如果时相同颜色加一分
                    chess_score[2]+=1
                else:
                    break
            else:
                blank_score[2]+=1
                break
            j-=1

        # 左下方
        j=y
        for i in range(x,x-5,-1):
            if i<=0 or j>=19:
                break
            if self.chessboard[i][j] is not None:
                if self.chessboard[i][j].color==color:
                    # 如果时相同颜色加一分
                    chess_score[3]+=1
                else:
                    break
            else:
                blank_score[3]+=1
                break
            j+=1

        # 右上方
        j=y-1
        for i in range(x+1,x+5):
            if i>=19 or j<=0:
                break
            if self.chessboard[i][j] is not None:
                if self.chessboard[i][j].color==color:
                    # 如果时相同颜色加一分
                    chess_score[3]+=1
                else:
                    break
            else:
                blank_score[3]+=1
                break
            j-=1

        # 计算总分
        for score in chess_score:
            if score>4:         #如果某个方向超过4，则此处权重最大
                return 100
        for i in range(0,len(blank_score)):
            if blank_score[i]==0:
                blank_score[i]-=20
        # 四个方向的分数，将两个列表相加
        result=[a+b for a,b in zip(chess_score,blank_score)]
        return max(result)