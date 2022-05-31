import argparse
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow

from ServerForm import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ACCEPT_THREAD = None
        self.setupUi(self)
        self.SERVER = socket(AF_INET, SOCK_STREAM)
        self.pushButton.clicked.connect(self.startServe)
        self.pushButton_2.clicked.connect(self.clearText)

    def startServe(self):
        port = self.lineEdit.text()
        if len(port) == 0:
            QMessageBox.warning(self, "提示", "端口为空", QMessageBox.Yes)
            return
        self.SERVER.bind(("192.168.1.105", int(port)))
        self.SERVER.listen(5)
        self.plainTextEdit.appendPlainText("服务器开始运行")
        self.ACCEPT_THREAD = Thread(target=accept_incoming_connections)
        self.ACCEPT_THREAD.start()

    def clearText(self):
        self.plainTextEdit.clear()


def accept_incoming_connections():
    while True:
        client, client_address = win.SERVER.accept()
        win.plainTextEdit.appendPlainText("%s:%s 已连接" % client_address)
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # 接受客户端套接字作为参数
    name = ""
    prefix = ""

    while True:
        msg = client.recv(BUFSIZ)
        print(msg)
        if not msg is None:
            msg = msg.decode("utf-8")

        if msg == "":
            msg = "{QUIT}"

        # 防止信息出现早于登陆
        if msg.startswith("{ALL}") and name:
            new_msg = msg.replace("{ALL}", "{MSG}" + prefix)
            send_message(new_msg, broadcast=True)
            continue

        if msg.startswith("{REGISTER}"):
            name = msg.split("}")[1]
            welcome = '{MSG}欢迎 %s!' % name
            send_message(welcome, destination=client)
            msg = "{MSG}%s 已加入聊天室" % name
            send_message(msg, broadcast=True)
            clients[client] = name
            prefix = name + ": "
            send_clients()
            continue

        if msg == "{QUIT}":
            client.close()
            try:
                del clients[client]
            except KeyError:
                pass
            if name:
                send_message("{MSG}%s 已离开聊天室" % name, broadcast=True)
                send_clients()
            break

        # 防止信息出现早于登陆
        if not name:
            continue
        try:
            msg_params = msg.split("}")
            dest_name = msg_params[0][1:]
            # print(dest_name)
            dest_sock = find_client_socket(dest_name)
            # print(dest_sock)
            if dest_sock:
                send_message(msg_params[1], prefix=prefix, destination=dest_sock)
            else:
                print("无效地址 %s" % dest_name)
        except:
            print("信息解析失败: %s" % msg)


def send_clients():
    send_message("{CLIENTS}" + get_clients_names(), broadcast=True)


def get_clients_names(separator="|"):
    names = []
    for _, name in clients.items():
        print("用户 %s 连入服务器" % name)
        win.plainTextEdit.appendPlainText("用户 %s 连入服务器\n" % name)
        names.append(name)
    return separator.join(names)


def find_client_socket(name):
    for cli_sock, cli_name in clients.items():
        if cli_name == name:
            return cli_sock
    return None


def send_message(msg, prefix="", destination=None, broadcast=False):
    send_msg = bytes(prefix + msg, "utf-8")
    if broadcast:
        # 广播信息
        print(msg)
        win.plainTextEdit.appendPlainText(msg + "\n")
        for sock in clients:
            sock.send(send_msg)
    else:
        print("{private}" + msg)
        win.plainTextEdit.appendPlainText("{private}" + msg + "\n")
        if destination is not None:
            destination.send(send_msg)


clients = {}
addresses = {}

# parser = argparse.ArgumentParser(description="Chat Server")
# parser.add_argument(
#     '--host',
#     help='Host IP',
#     default="127.0.0.1"
# )
# parser.add_argument(
#     '--port',
#     help='Port Number',
#     default=9090
# )

# server_args = parser.parse_args()
#
# HOST = server_args.host
# PORT = int(server_args.port)
BUFSIZ = 2048
# ADDR = (HOST, PORT)

stop_server = False

# SERVER = socket(AF_INET, SOCK_STREAM)
# SERVER.bind(ADDR)

if __name__ == "__main__":
    # try:
    #     # SERVER.listen(5)
    #     # print("服务器地址 {}:{}".format(HOST, PORT))
    #     # print("等待连接...")
    #     # ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    #     # ACCEPT_THREAD.start()
    #     # ACCEPT_THREAD.join()
    #     # SERVER.close()
    # except KeyboardInterrupt:
    #     print("关闭连接...")
    #     ACCEPT_THREAD.interrupt()
    app = QApplication([])
    win = Window()
    win.show()
    app.exec_()
