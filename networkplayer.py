from base import BasePlayer,TDPushButton,Chess,is_win
from PyQt5.QtWidgets import QLabel,QPushButton,QHBoxLayout,QVBoxLayout,QLineEdit,QWidget,QMessageBox
from threading import Thread
import socket
import json
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal
import pygame
'''
问题：接受数据出现问题，无论哪一端都无法接收数据  已解决

设定：
    服务端客户端设定：
        通过配置页面进入不同的模式
    接收数据的设定：
        接收对方发送过来的数据时,先经过外部函数的处理,通过专门的函数区分不同的数据做不同的操作
    开始设定：
        游戏双方连接成功后，游戏状态发生改变，此时游戏是结束状态，需要通过某一方主动点击，另一方
        回应确认，游戏任意一方才可以落子
    落子设定：
        每一方每个回合只能落一个子，再落无效，每次有棋子从棋盘落下都会有落子声
    标识设定：
        当棋盘上有棋子时，棋子标识会显示在最近棋子上，在棋盘上没有棋或者清空棋盘时，标识不会显示
    悔棋设定：
        己方回合时，悔棋按钮才有效，每次悔棋需要等对方确认，对方确认后，回到上一个回合，棋盘上上
        一回合的棋子消失，由悔棋方先下
    认输设定：
        己方回合时，认输按钮才有效，认输方显示对方胜，对方显示自己胜
    催促设定：
        对方回合时，催促按钮才有效，两方都会播放催促音效
    下线设定：
        如果在下棋过程中，有一方突然退出，游戏结束，被退出一方弹出消息框后，返回到游戏主界面，其
        它界面关闭
'''

# 接收完整的数据帧
def recv_sockdata(the_socket):
    total_data=""
    while True:
        print('recv_sockdata')
        data=the_socket.recv(1024).decode()
        print(data)
        if "END" in data:
            total_data+=data[:data.index("END")]
            print("数据接收完毕")
            break
        total_data+=data
    return total_data

# 网络设置窗口
class NetworkConfig(QWidget):
    def __init__(self,main_window = None,parent=None):
        super().__init__(parent)
        # 用一个变量保存主界面窗体
        self.main_window = main_window
        # 第一行：昵称：
        self.name_label = QLabel("昵称",self)
        self.name_edit = QLineEdit(self)
        self.name_edit.setText("玩家1")
        self.h1 = QHBoxLayout()
        self.h1.addWidget(self.name_label,3)
        self.h1.addWidget(self.name_edit,7)
        # 第二行：主机ip：
        self.ip_label = QLabel("主机IP",self)
        self.ip_edit = QLineEdit(self)
        self.ip_edit.setText("127.0.0.1")
        self.h2 = QHBoxLayout()
        self.h2.addWidget(self.ip_label,3)
        self.h2.addWidget(self.ip_edit,7)
        # 第三行 两个按钮
        self.con_btn = QPushButton("连接主机",self)
        self.ser_btn = QPushButton("我是主机",self)
        self.con_btn.clicked.connect(self.client_mode)
        self.ser_btn.clicked.connect(self.server_mode)
        self.h3 = QHBoxLayout()
        self.h3.addWidget(self.con_btn)
        self.h3.addWidget(self.ser_btn)
        # 垂直布局
        self.v = QVBoxLayout()
        self.v.addLayout(self.h1)
        self.v.addLayout(self.h2)
        self.v.addLayout(self.h3)
        self.setLayout(self.v)
        self.game_window = None


    def client_mode(self):
        # 启动客户端模式的程序
        self.game_window = NetworkClient(name=self.name_edit.text(),ip=self.ip_edit.text(),main_wind=self.main_window,conf_wind=self)
        self.game_window.show()
        self.game_window.backsignal.connect(self.main_window.back)
        self.close()

    def server_mode(self):
        # 启动服务器模式的程序
        self.game_window = NetworkServer(name=self.name_edit.text(),main_wind=self.main_window,conf_wind=self)
        self.game_window.show()
        self.game_window.backsignal.connect(self.main_window.back)
        self.close()


class NetworkPlayer(BasePlayer):
    # 用来标记传递数据，定义时后边括号有参数，信号里才可以发数据
    datasignal = pyqtSignal(dict)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.soonsetup_ui()
        # 给套接字预备的变量
        self.tcp_socket = None
        # 这里是棋盘
        self.chessboard = [[None for i in range(0, 19)] for j in range(0, 19)]
        # 生成一个历史数组，记录下棋的信息
        self.history = []
        # 生成像素列表
        self.pix_list=[]
        # 游戏是否的进行的标记
        self.is_over=True
        # 胜利标签
        self.win_label=None
        # 接收数据的信号，初始化完成后也能一直运行
        self.datasignal.connect(self.deal_data)
        # 决定下什么颜色棋的标记
        self.is_black=True
        # 区分是客户端还是服务器的标签
        self.is_color=None
        self.can_chess=True     # 通过这个变量控制各方每次只能下一棋
        # 标识两端是否连接
        self.is_connect=True
        # 主窗口接口
        self.main_wind=None
        # 配置页面接口
        self.conf_wind=None
        # 点开始按钮时
        self.restart_btn.clicked.connect(self.restart)
        # 点击认输按钮时
        self.lose_btn.clicked.connect(self.lose)
        # 点击悔棋按钮时
        self.hq_btn.clicked.connect(self.hq)

        # 初始化音乐
        pygame.mixer.init()
        # 当前棋子标识
        self.bs_label = QLabel(self)
        pic = QPixmap("source/标识.png")
        self.bs_label.setPixmap(pic)
        self.bs_label.close()
    # 点击悔棋按钮时
    def hq(self):
        if self.is_over:
            return
        if len(self.history)<=1:
            QMessageBox.information(self, "消息", "you must 要乖，现在还悔不了棋")
            return
        # 到己方下棋时才可以悔棋
        if self.can_chess:
            hq_data = {"msg":"hq"}
            self.tcp_socket.sendall((json.dumps(hq_data)+"END").encode())
    # 同意悔棋时执行
    def hq_func(self):
        if not self.is_over:
            # 列表不为空时才可以悔棋
            if self.history:
                # 悔棋时一次悔两个
                for i in range(2):
                    self.pix_list.pop()
                    pos = self.history.pop()
                    # 通过元组记录的坐标销毁棋子
                    self.chessboard[pos[0]][pos[1]].close()
                    self.chessboard[pos[0]][pos[1]] = None
                # 悔棋成功后还是我方下棋
                self.can_chess = True
                if not self.pix_list:
                    self.bs_label.close()
                else:
                    x,y=self.pix_list[-1]
                    self.bs_label.move(x,y)
                    self.bs_label.show()
    # 点认输按钮时
    def lose(self):
        if not self.history:
            QMessageBox.information(self, "消息", "还没开始就想放弃，太让我失望了，休想")
            return
        if not self.is_over:
            self.win_label = QLabel(self)
            if self.is_color==2:
                pic = QPixmap('source/白棋胜利.png')
            elif self.is_color==1:
                pic = QPixmap('source/黑棋胜利.png')
            self.win_label.setPixmap(pic)
            self.win_label.move(130, 75)
            self.win_label.show()
            self.is_over = True
            lose_data = {"msg":"lose","color":self.is_color}
            self.tcp_socket.sendall((json.dumps(lose_data)+"END").encode())
    # 点开始按钮时
    def restart(self):
        restart_data = {"msg":"restart"}
        self.tcp_socket.sendall((json.dumps(restart_data)+"END").encode())
    # 对方同意开始执行
    def restart_func(self):
        self.is_over=False
        # 重新开始游戏
        if self.win_label is not None:
            # 清空胜利图片
            self.win_label.close()
        self.bs_label.close()
        # 清空棋盘列表
        for i in range(0,19):
            for j in range(0,19):
                if self.chessboard[j][i] is not None:
                    self.chessboard[j][i].close()
                    self.chessboard[j][i]=None
    # 不与父类setup_ui函数同名了，否则父类里面的此方法将被重写，再调用父类的此方法时，就会相当于重复调用
    def soonsetup_ui(self):
        super().setup_ui()
        self.state_label = QLabel("游戏状态:",self)
        self.state_text = QLabel("等待连接",self)
        self.state_label.move(630,200)
        self.state_text.move(690,200)

        self.cuicu_btn = TDPushButton("source/催促按钮_normal.png","source/催促按钮_hover.png","source/催促按钮_press.png",self)
        self.cuicu_btn.clicked.connect(self.cuicu)
        self.cuicu_btn.show()
        self.cuicu_btn.move(640,450)

    def cuicu(self):
        if self.is_over:
            return
        if not self.can_chess:
            data1 = {"msg":"cuicu"}
            self.tcp_socket.sendall((json.dumps(data1)+"END").encode())
            music = pygame.mixer.Sound("source/cuicu.wav")
            music.play()

    def deal_data(self,data):
        print(data)
        # 游戏状态改变
        self.state_text.setText('我方回合')
        if data['msg']=="name":
            return

        # 点开始按钮时
        elif data["msg"]=="restart":
            reply1=QMessageBox.information(self,"消息","对方请求开始，是否开始？",QMessageBox.Yes | QMessageBox.No)
            if reply1==QMessageBox.Yes:
                self.restart_func()
                self.is_over=False
            reply1_data={"msg":"reply","data":reply1}
            self.tcp_socket.sendall((json.dumps(reply1_data)+"END").encode())

        # 接收对方的回复
        elif data["msg"]=="reply":
            if data["data"]==QMessageBox.Yes:
                self.restart_func()
                self.is_over=False
            elif data["data"]==QMessageBox.No:
                QMessageBox.information(self, "消息", "对方拒绝了你的请求")

        # 处理坐标信息
        elif data["msg"]=="pos":
            pos = data['data']
            xx = pos[0]
            yy = pos[1]
            if self.is_black:
                self.chess = Chess('w', self)
            else:
                self.chess = Chess('b', self)
            self.is_black = not self.is_black

            self.chessboard[xx][yy] = self.chess
            self.history.append((xx, yy))
            x = xx*30+50-15
            y = yy*30+50-15
            # 将像素点加入记录列表
            self.pix_list.append((x,y))

            self.chess.move(x, y)
            self.chess.show()
            # 落子声
            music = pygame.mixer.Sound("source/luozisheng.wav")
            music.play()

            # 移动标识
            self.bs_label.move(x,y)
            self.bs_label.raise_()
            self.bs_label.show()

            self.can_chess = True
            # 输赢判断
            color = is_win(self.chessboard)
            if color is False:
                return
            else:
                # QMessageBox.information(self,"消息","{}棋胜利".format(color))
                self.win_label = QLabel(self)
                if color == 'b':
                    pic = QPixmap("source/黑棋胜利.png")
                else:
                    pic = QPixmap("source/白棋胜利.png")
                self.win_label.setPixmap(pic)
                self.win_label.move(100, 100)
                self.win_label.show()
                self.is_over = True

        # 对方认输时
        elif data["msg"]=='lose':
            self.win_label = QLabel(self)
            if data["color"] == 2:
                pic = QPixmap('source/白棋胜利.png')
            elif data["color"] == 1:
                pic = QPixmap('source/黑棋胜利.png')
            self.win_label.setPixmap(pic)
            self.win_label.move(130, 75)
            self.win_label.show()
            self.is_over = True

        # 对方发出悔棋请求时
        elif data["msg"] == 'hq':
            reply3 = QMessageBox.question(self, "消息", "对方请求悔棋，是否准许？", QMessageBox.Yes | QMessageBox.No)
            if reply3==QMessageBox.Yes:
                for i in range(2):
                    self.pix_list.pop()
                    pos = self.history.pop()
                    # 通过元组记录的坐标销毁棋子
                    self.chessboard[pos[0]][pos[1]].close()
                    self.chessboard[pos[0]][pos[1]] = None
                if not self.pix_list:
                    self.bs_label.close()
                else:
                    x,y=self.pix_list[-1]
                    print(x,y)
                    self.bs_label.move(x,y)
                    # 把标识标签置在最顶层，保证不会被盖住
                    self.bs_label.raise_()
                    self.bs_label.show()

            reply3_data = {"msg": "reply4", "data": reply3}
            self.tcp_socket.sendall((json.dumps(reply3_data) + "END").encode())

        # 对方回应悔棋请求
        elif data["msg"] == "reply4":
            if data["data"] == QMessageBox.Yes:
                self.hq_func()
                self.can_chess = True
            elif data["data"] == QMessageBox.No:
                QMessageBox.information(self, "消息", "对方拒绝了你的悔棋请求")
        # 对方点击催促按钮时
        elif data["msg"]=="cuicu":
            music = pygame.mixer.Sound("source/cuicu.wav")
            music.play()

        # 有一方中断连接
        elif data['msg']=='error':
            QMessageBox.information(self,'消息','对方已断开连接')

        elif data["msg"]=="exit":
            QMessageBox.information(self, '消息', '对方已离开,返回主界面？')
            self.close()
            self.conf_wind.close()
            # 对方离开后返回主界面
            self.main_wind.show()


    def recv_data(self,sock):
        # 收到数据
        print("recv_data")
        while self.is_connect:
            # 处理因对方强制退出而发生的异常
            try:
                # 处理接收到的数据
                r_data = recv_sockdata(sock)
            except ConnectionResetError as e:
                print(e)
                # 游戏状态改变
                self.state_text.setText('对方已离开')
                data={'msg': 'error'}
                self.tcp_socket.sendall((json.dumps(data)+"END").encode())
                break
            except ConnectionAbortedError:
                pass
            data = json.loads(r_data)
            # 将数据通过信号发送出去
            self.datasignal.emit(data)

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        # 如果不是我方回合，不能下棋
        if not self.can_chess:
            return
        # 如果游戏已经结束，点击失效
        if self.is_over:
            return

        if a0.x() < 40 or a0.x() > 600:
            return
        if a0.y() < 40 or a0.y() > 600:
            return

        # 将棋子定位到准确的坐标点
        if (a0.x() - 50) % 30 <= 15:
            x = (a0.x() - 50) // 30 * 30 + 50
        else:
            x = ((a0.x() - 50) // 30 + 1) * 30 + 50

        if (a0.y() - 50) % 30 <= 15:
            y = (a0.y() - 50) // 30 * 30 + 50
        else:
            y = ((a0.y() - 50) // 30 + 1) * 30 + 50
        # 在棋盘数组中，保存棋子对象
        xx = (x - 50) // 30
        yy = (y - 50) // 30
        # 如果此处已经有棋子，点击失效
        if self.chessboard[xx][yy] is not None:
            return

        print("有效点击")
        # 通过标识，决定棋子的颜色
        if self.is_black:
            self.chess = Chess('w', self)
        else:
            self.chess = Chess('b', self)
        self.is_black = not self.is_black

        self.chessboard[xx][yy] = self.chess
        self.history.append((xx, yy))

        x = x - self.chess.width() / 2
        y = y - self.chess.height() / 2
        self.pix_list.append((x,y))

        self.chess.move(x, y)
        self.chess.show()
        # 落子声
        music = pygame.mixer.Sound("source/luozisheng.wav")
        music.play()
        # 当前棋子标识
        self.bs_label.move(x,y)
        self.bs_label.raise_()
        self.bs_label.show()

        # 游戏状态改变
        self.state_text.setText('对方回合')

        self.can_chess = False
        # 落子后， 发送棋子位置
        pos_data = {"msg":"pos","data":(xx,yy),"color":self.is_color}
        self.tcp_socket.sendall((json.dumps(pos_data)+"END").encode())

        # 翻转棋子颜色
        # self.is_black = not self.is_black

        color = is_win(self.chessboard)
        if color is False:
            return
        else:
            # QMessageBox.information(self,"消息","{}棋胜利".format(color))
            self.win_label = QLabel(self)
            if color == 'b':
                pic = QPixmap("source/黑棋胜利.png")
            else:
                pic = QPixmap("source/白棋胜利.png")
            self.win_label.setPixmap(pic)
            self.win_label.move(100, 100)
            self.win_label.show()
            self.is_over = True

    def closeEvent(self, a0: QtGui.QCloseEvent):
        self.is_connect=False
        super().closeEvent(a0)
        self.conf_wind.close()
        exit_data = {"msg": "exit"}
        self.tcp_socket.sendall((json.dumps(exit_data) + "END").encode())



class NetworkServer(NetworkPlayer):

    # 运行服务端游戏界面

    def __init__(self,name="玩家1",main_wind=None,conf_wind=None,parent=None):
        super().__init__(parent)

        self.name = name
        self.main_wind=main_wind
        self.conf_wind=conf_wind
        self.is_color=1
        self.ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.ser_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用
        try:
            self.ser_socket.bind(("127.0.0.1", 20096))
        except:
            QMessageBox.information(self,'消息','端口被占用,先重启试试')
            self.close()
            self.conf_wind.close()
            self.main_wind.show()    #返回主界面
            #发射信号，返回主界面
            #结束程序
            #停在主界面，等待连接
        self.ser_socket.listen(8)
        th = Thread(target=self.start_listen)
        th.start()

    def start_listen(self):
        print("start listening ")
        while True:
            sock, addr = self.ser_socket.accept()
            self.tcp_socket = sock
            # 客户端连接后，游戏状态改变
            self.state_text.setText('连接成功')
            # 发送了自己的昵称
            print(self.tcp_socket)
            self.tcp_socket.sendall((json.dumps({"msg":"name","data":self.name})+"END").encode())
            self.recv_data(self.tcp_socket)

class NetworkClient(NetworkPlayer):
    # 运行客户端游戏界面
    def __init__(self,name="玩家香",ip="127.0.0.1",main_wind=None,conf_wind=None,parent=None):
        super().__init__(parent)
        self.is_color = 2
        self.name = name
        self.main_wind=main_wind
        self.conf_wind=conf_wind
        self.tcp_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        addr = (ip,20096)
        self.tcp_socket.connect(addr)
        # 客户端连接后，游戏状态改变
        self.state_text.setText('连接成功')
        self.tcp_socket.sendall((json.dumps({"msg":"name","data":self.name})+"END").encode())
        th = Thread(target=self.recv_data,args=(self.tcp_socket,))
        # self.recv_data(self.tcp_socket)
        th.start()