import sys
from PyQt5.QtWidgets import QWidget,QApplication,QPushButton,QCheckBox,QLineEdit,QListWidget,QListWidgetItem,QLabel
from PyQt5.QtWidgets import QHBoxLayout,QVBoxLayout
class Window(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle('网络配置')
        self.resize(200,250)

        self.name_label=QLabel('昵称：',self)
        self.name_edit=QLineEdit(self)
        self.name_edit.setText('玩家0')

        self.h1=QHBoxLayout()   #生成布局管理器
        self.h1.addWidget(self.name_label,3) #把空间加入管理器
        self.h1.addWidget(self.name_edit,7)

        self.player_label=QLabel('玩家列表',self)
        self.refresh_btn=QPushButton('刷新',self)

        self.h2=QHBoxLayout()   #生成布局管理器
        self.h2.addWidget(self.player_label,3) #把空间加入管理器
        self.h2.addWidget(self.refresh_btn,7)

        self.player_list=QListWidget(self) #列表控件
        item1=QListWidgetItem('条目1')
        item2=QListWidgetItem('条目2')
        item3=QListWidgetItem('条目3')
        self.player_list.addItem(item1)
        self.player_list.addItem(item2) 
        self.player_list.addItem(item3)
        self.player_list.itemDoubleClicked.connect(self.item_clicked)

        self.join_btn=QPushButton('加入房间',self)
        self.battle_btn=QPushButton('选择对战',self)
        self.battle_btn.setEnabled(False)

        self.h3=QHBoxLayout()   #生成布局管理器
        self.h3.addWidget(self.join_btn,3) #把空间加入管理器
        self.h3.addWidget(self.battle_btn,7)

        self.main_layout=QVBoxLayout()
        self.main_layout.addLayout(self.h1)
        self.main_layout.addLayout(self.h2)
        self.main_layout.addWidget(self.player_list)
        self.main_layout.addLayout(self.h3)
        self.setLayout(self.main_layout)  #让窗体应用布局

    def item_clicked(self,item):
        print(item.text())

class Window2(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.is_click=True
        self.resize(400,400)
        self.btn1=QPushButton('按钮1',self)
        self.btn1.move(100,100)
        self.btn2=QPushButton('按钮2',self)
        self.btn2.move(200,200)
        self.btn2.setEnabled(False)

        self.btn1.clicked.connect(self.func)#点击按钮，执行一个操作
        self.btn2.clicked.connect(self.func2)
    def func(self):
        print('香饽饽')
        if self.is_click:
            self.btn1.setText('1按钮')
            self.btn2.setEnabled(True)
        else:
            self.btn1.setText('按钮1')
            self.btn2.setEnabled(False)
        self.is_click= not self.is_click

    def func2(self):
        self.a=Window()
        self.a.show()
        self.close()

if __name__ == '__main__':
    app=QApplication(sys.argv)  #创建Qt应用对象
    w=Window2()                 #创建窗口
    # w.resize(400,400)
    # #w.setFixedSize(400,400)    #设置固定大小
    # w.setWindowTitle('酷炫五子棋')
    # w.move(50,50)
    # #按钮
    # btn=QPushButton(parent=w,text='按钮')
    # btn.move(60,100)
    # btn.setText('加入游戏')
    # btn.show()

    # #复选框
    # check1=QCheckBox(parent=w,text='111')
    # check2=QCheckBox(parent=w,text='222')
    # check3=QCheckBox(parent=w,text='333')
    # check1.move(150,100)
    # check2.move(200,100)
    # check3.move(250,100)

    # edit=QLineEdit(parent=w)
    # edit.move(100,200)
    # edit.resize(200,300)
    
    # list_widget=QListWidget(parent=w)
    # list_widget.move(100,250)
    # list_widget.resize(200,300)

    # item1=QListWidgetItem('条目1')
    # item2=QListWidgetItem('条目2')
    # item3=QListWidgetItem('条目3')
    # list_widget.addItem(item1)
    # list_widget.addItem(item2)
    # list_widget.addItem(item3)

    w.show()
    sys.exit(app.exec_())