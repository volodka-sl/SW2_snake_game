import sys
import snake_game_ui
import socket
import threading
from PyQt6 import QtGui
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

player1_nick = ""
player2_nick = ""


class SnakeGame(QMainWindow, snake_game_ui.Ui_MainWindow):
    def __init__(self):
        super(SnakeGame, self).__init__()
        self.setFixedSize(QSize(870, 650))
        self.setupUi(self)
        self.setWindowTitle("Snake Online-Game 🐍")
        self.game_over_banner.setVisible(False)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', 8010))

        self.access_name_button.clicked.connect(self.name_button_was_clicked)

        self.game_table.clicked.connect(self.table_clicked)

        self.turn = 1

    def name_button_was_clicked(self):
        if self.name_line.text():
            self.client.send(("NICK" + self.name_line.text()).encode('ascii'))
            self.name_line.setEnabled(False)
            self.access_name_button.setEnabled(False)

            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()

    def receive(self):
        global player1_nick
        global player2_nick
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if "Player 2" in message:
                    self.logger.append(message)
                    self.client.send("HOWMANYNICKNAMES".encode('ascii'))
                    nicknames = self.client.recv(1024).decode('ascii')
                    player1_nick = nicknames.split(",")[0]
                    player2_nick = nicknames.split(",")[1]
                    self.player1_name_label.setText(player1_nick)
                    self.player2_name_label.setText(player2_nick)
                    self.logger.append(f"{player1_nick}! Your turn!")
                    if self.name_line.text() == player1_nick:
                        self.game_table.setEnabled(True)

                elif "," not in message:
                    self.logger.append(message)

                elif len(message) == 3:
                    new_cell = QTableWidgetItem()
                    row = int(message.split(",")[0])
                    column = int(message.split(",")[1])

                    if self.turn == 1:
                        self.logger.append(f"{player2_nick}! Your turn!")
                        new_cell.setBackground(QtGui.QColor(182, 215, 168))
                        self.turn = 2
                        if self.name_line.text() == player2_nick:
                            self.game_table.setEnabled(True)
                        else:
                            self.game_table.setDisabled(True)
                    elif self.turn == 2:
                        self.logger.append(f"{player1_nick}! Your turn!")
                        new_cell.setBackground(QtGui.QColor(234, 153, 153))
                        self.turn = 1
                        if self.name_line.text() == player1_nick:
                            self.game_table.setEnabled(True)
                        else:
                            self.game_table.setDisabled(True)
                    self.game_table.setItem(row, column, new_cell)
                elif "impossible" in message:
                    if self.turn == 1:
                        if self.name_line.text() == player1_nick:
                            self.game_table.setEnabled(True)
                        else:
                            self.game_table.setDisabled(True)
                    elif self.turn == 2:
                        if self.name_line.text() == player2_nick:
                            self.game_table.setEnabled(True)
                        else:
                            self.game_table.setDisabled(True)
                    self.logger.append(message)
                elif "GAME OVER" in message:
                    self.game_table.setVisible(False)
                    self.game_over_banner.setVisible(True)
                    if self.name_line.text() == message.split(",")[1]:
                        self.game_over_banner.setText("GAME OVER! YOU WON!")
                        self.game_over_banner.setStyleSheet("""
                                    background-color: rgb(182, 215, 168);
                                    font: 13pt "JetBrains Mono";
                                    padding: 5px;
                                    border: 2px solid black;
                                    font-size: 30px;
                                """)
                    else:
                        self.game_over_banner.setText("GAME OVER! YOU LOST!")
                        self.game_over_banner.setStyleSheet("""
                                    background-color: rgb(234, 153, 153);
                                    font: 13pt "JetBrains Mono";
                                    padding: 5px;
                                    border: 2px solid black;
                                    font-size: 30px;
                                """)
            except:
                self.client.close()
                break

    def table_clicked(self):
        self.game_table.setDisabled(True)
        row = self.game_table.currentRow()
        column = self.game_table.currentColumn()
        self.client.send(f"{row},{column}".encode('ascii'))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnakeGame()
    window.show()
    app.exec()
