import os
import subprocess
import sys
import ctypes
from PyQt6 import QtWidgets, QtGui, QtCore

class ResetFolderPermissionsApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ResetFolderPermissions")
        self.setFixedSize(400, 200)
        self.setWindowIcon(QtGui.QIcon('icon.png'))  # Opcional: Defina um ícone para o aplicativo

        self.init_ui()
        self.apply_styles()

        # Verificar se está rodando como administrador
        if not self.is_admin():
            self.run_as_admin()
            sys.exit()

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout()

        # Label
        lbl = QtWidgets.QLabel("Selecione o caminho da pasta ou drive:")
        lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

        # Input Field
        self.path_input = QtWidgets.QLineEdit()
        self.path_input.setPlaceholderText("Caminho da pasta ou drive")
        layout.addWidget(self.path_input)

        # Browse Button
        browse_btn = QtWidgets.QPushButton("Navegar")
        browse_btn.clicked.connect(self.select_directory)
        layout.addWidget(browse_btn)

        # Execute Button
        execute_btn = QtWidgets.QPushButton("Executar Comandos")
        execute_btn.clicked.connect(self.execute_commands)
        layout.addWidget(execute_btn)

        central_widget.setLayout(layout)

    def apply_styles(self):
        # QSS Stylesheet
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLabel {
            font-size: 14px;
            color: #333;
        }
        QLineEdit {
            padding: 5px;
            font-size: 14px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            font-size: 14px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3e8e41;
        }
        """
        self.setStyleSheet(style)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_as_admin(self):
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]),
            None, 1
        )

    def select_directory(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecione uma pasta ou drive")
        if folder_path:
            self.path_input.setText(folder_path)

    def execute_commands(self):
        pasta = self.path_input.text().strip()
        if not pasta:
            QtWidgets.QMessageBox.critical(self, "Erro", "Por favor, selecione um caminho da pasta.")
            return

        pasta = os.path.normpath(pasta)

        try:
            # Executa o comando takeown
            process = subprocess.Popen(
                f'takeown /F "{pasta}" /R /A',
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            process.communicate(input=b'S\n')

            # Executa o comando icacls para habilitar herança
            subprocess.run(f'icacls "{pasta}" /inheritance:e', shell=True, check=True)

            # Executa o comando icacls para resetar permissões
            subprocess.run(f'icacls "{pasta}" /RESET /T /Q', shell=True, check=True)

            QtWidgets.QMessageBox.information(self, "Êxito", "Operações realizadas com sucesso!")
        except subprocess.CalledProcessError as e:
            error_message = ""
            if e.stderr:
                try:
                    error_message = e.stderr.decode("cp850")
                except UnicodeDecodeError:
                    error_message = "Erro ao executar os comandos."
            else:
                error_message = "Erro desconhecido ao executar os comandos."
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao executar os comandos.\n\n{error_message}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ResetFolderPermissionsApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()