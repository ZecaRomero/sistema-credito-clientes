import sys
import os
import mysql.connector
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from datetime import datetime

class RelatorioWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        base = os.path.dirname(__file__)
        uic.loadUi(os.path.join(base, 'relatorio.ui'), self)
        self.setWindowTitle("Relatório de Clientes")
        self.setup_connections()
        self.load_data()

    def setup_connections(self):
        self.btnEditar.clicked.connect(self.editar_cliente)
        self.btnExcluir.clicked.connect(self.excluir_cliente)

    def get_connection(self):
        return mysql.connector.connect(
            host='127.0.0.1',
            user='dev',
            password='1234',
            database='tectreinamentos_credito'
        )

    def load_data(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, nome, cpf, idade, renda, situacao, 
                       DATE_FORMAT(data_cadastro, '%%d/%%m/%%Y %%H:%%i') as data_cadastro,
                       observacoes,
                       DATE_FORMAT(data_atualizacao, '%%d/%%m/%%Y %%H:%%i') as data_atualizacao
                FROM clientes
                ORDER BY data_cadastro DESC
            """)

            self.populate_table(cursor)

        except mysql.connector.Error as err:
            QtWidgets.QMessageBox.critical(
                self, "Erro",
                f"Falha ao carregar dados:\n{err}"
            )
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def editar_cliente(self):
        selected = self.tableClientes.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um cliente para editar")
            return

        row = selected[0].row()
        cliente_id = self.tableClientes.item(row, 0).text()

        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT *, DATE_FORMAT(data_cadastro, '%%Y-%%m-%%d %%H:%%i:%%s') as dt 
                FROM clientes WHERE id=%s
            """, (cliente_id,))

            cliente = cursor.fetchone()
            if cliente:
                main_window = self.parent()
                if main_window:
                    main_window.txtId.setText(str(cliente['id']))
                    main_window.txtNome.setText(cliente['nome'])

                    cpf = cliente['cpf']
                    cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
                    main_window.txtCpf.setText(cpf_formatado)

                    main_window.txtIdade.setValue(cliente['idade'])
                    main_window.txtRenda.setValue(float(cliente['renda']))
                    main_window.txtSituacao.setText(cliente['situacao'])
                    main_window.txtObs.setPlainText(cliente['observacoes'] or '')

                    data = QtCore.QDateTime.fromString(cliente['dt'], "yyyy-MM-dd HH:mm:ss")
                    main_window.txtDataCadastro.setDateTime(data)

                    main_window.update_statusbar(f"Editando: {cliente['nome']}")
                    self.close()

        except mysql.connector.Error as err:
            QtWidgets.QMessageBox.critical(
                self, "Erro",
                f"Falha ao carregar cliente:\n{err}"
            )
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def excluir_cliente(self):
        selected = self.tableClientes.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um cliente para excluir")
            return

        row = selected[0].row()
        cliente_id = self.tableClientes.item(row, 0).text()

        reply = QtWidgets.QMessageBox.question(
            self, 'Confirmar',
            f'Tem certeza que deseja excluir o cliente ID: {cliente_id}?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente_id,))
                conn.commit()
                self.load_data()
                QtWidgets.QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso")
            except mysql.connector.Error as err:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao excluir:\n{err}")
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

    def populate_table(self, cursor):
        self.tableClientes.setRowCount(0)

        for row_num, row_data in enumerate(cursor):
            self.tableClientes.insertRow(row_num)

            cpf = row_data['cpf']
            cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            renda_formatada = f"R$ {row_data['renda']:,.2f}"

            for col, value in enumerate([
                str(row_data['id']),
                row_data['nome'],
                cpf_formatado,
                str(row_data['idade']),
                renda_formatada,
                row_data['situacao'],
                row_data['data_cadastro'],
                row_data['observacoes'] or '',
                row_data['data_atualizacao'] or ''
            ]):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableClientes.setItem(row_num, col, item)

                if col == 5:
                    if "APROVADO" in value:
                        item.setBackground(QtGui.QColor('#E8F5E9'))
                    else:
                        item.setBackground(QtGui.QColor('#FFEBEE'))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        self.setup_table()
        self.load_report()

    def setup_ui(self):
        base = os.path.dirname(__file__)
        uic.loadUi(os.path.join(base, 'cadastro.ui'), self)
        self.txtDataCadastro.setDateTime(QtCore.QDateTime.currentDateTime())
        self.txtDataCadastro.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.txtSituacao.setText("NÃO ANALISADO")
        self.update_statusbar("Sistema pronto")

    def setup_connections(self):
        self.btnAnalisar.clicked.connect(self.analyze_credit)
        self.btnSalvar.clicked.connect(self.save_data)
        self.btnLimpar.clicked.connect(self.clear_fields)
        self.btnRelatorio.clicked.connect(self.abrir_relatorio)
        self.tabelaClientes.doubleClicked.connect(self.load_selected_row)

    def setup_table(self):
        header = self.tabelaClientes.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

    def get_connection(self):
        return mysql.connector.connect(
            host='127.0.0.1',
            user='dev',
            password='1234',
            database='tectreinamentos_credito'
        )

    def analyze_credit(self):
        idade = self.txtIdade.value()
        renda = self.txtRenda.value()

        if idade < 18:
            situacao = "REPROVADO (IDADE)"
            score = 0
        elif renda < 1000:
            situacao = "REPROVADO (RENDA BAIXA)"
            score = 1
        elif renda < 2000:
            situacao = "APROVADO COM LIMITE REDUZIDO"
            score = 2
        elif renda < 5000:
            situacao = "APROVADO"
            score = 3
        else:
            situacao = "APROVADO (LIMITE ESPECIAL)"
            score = 4

        limite = min(renda * 0.5, 10000) if score >= 2 else 0
        self.txtSituacao.setText(f"{situacao} - Limite: R$ {limite:,.2f}")
        self.update_statusbar(f"Análise concluída - Score: {score}/4")

    def save_data(self):
        if not self.validate_fields():
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            data = {
                'nome': self.txtNome.text().strip(),
                'cpf': self.txtCpf.text().strip().replace('.', '').replace('-', ''),
                'idade': self.txtIdade.value(),
                'renda': self.txtRenda.value(),
                'situacao': self.txtSituacao.text(),
                'data_cadastro': self.txtDataCadastro.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                'observacoes': self.txtObs.toPlainText()
            }

            if self.txtId.text():
                data['id'] = self.txtId.text()
                sql = """UPDATE clientes SET 
                         nome=%(nome)s, cpf=%(cpf)s, idade=%(idade)s, 
                         renda=%(renda)s, situacao=%(situacao)s,
                         observacoes=%(observacoes)s,
                         data_atualizacao=NOW()
                         WHERE id=%(id)s"""
            else:
                sql = """INSERT INTO clientes 
                         (nome, cpf, idade, renda, situacao, data_cadastro, observacoes)
                         VALUES (%(nome)s, %(cpf)s, %(idade)s, %(renda)s, 
                         %(situacao)s, %(data_cadastro)s, %(observacoes)s)"""

            cursor.execute(sql, data)
            conn.commit()

            QtWidgets.QMessageBox.information(self, "Sucesso", "Dados salvos com sucesso!")
            self.load_report()
            self.clear_fields()

        except mysql.connector.Error as err:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def validate_fields(self):
        errors = []

        if len(self.txtNome.text().strip()) < 5:
            errors.append("Nome deve ter pelo menos 5 caracteres")

        cpf = self.txtCpf.text().strip().replace('.', '').replace('-', '')
        if len(cpf) != 11 or not cpf.isdigit():
            errors.append("CPF inválido")

        if "NÃO ANALISADO" in self.txtSituacao.text():
            errors.append("Analise o crédito antes de salvar")

        if errors:
            QtWidgets.QMessageBox.warning(self, "Validação", "Erros:\n" + "\n".join(errors))
            return False
        return True

    def load_report(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id, nome, cpf, idade, renda, situacao, DATE_FORMAT(data_cadastro, '%%d/%%m/%%Y %%H:%%i') as data_formatada FROM clientes ORDER BY data_cadastro DESC LIMIT 100")
            self.populate_table(cursor)

        except mysql.connector.Error as err:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar dados:\n{err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def populate_table(self, cursor):
        self.tabelaClientes.setRowCount(0)
        for row in cursor:
            cpf_formatado = f"{row['cpf'][:3]}.{row['cpf'][3:6]}.{row['cpf'][6:9]}-{row['cpf'][9:]}"
            renda_formatada = f"R$ {row['renda']:,.2f}"
            row_pos = self.tabelaClientes.rowCount()
            self.tabelaClientes.insertRow(row_pos)
            self.tabelaClientes.setItem(row_pos, 0, self.create_table_item(row['nome']))
            self.tabelaClientes.setItem(row_pos, 1, self.create_table_item(cpf_formatado))
            self.tabelaClientes.setItem(row_pos, 2, self.create_table_item(str(row['idade'])))
            self.tabelaClientes.setItem(row_pos, 3, self.create_table_item(renda_formatada))
            situacao_item = self.create_table_item(row['situacao'])
            if "APROVADO" in row['situacao']:
                situacao_item.setBackground(QtGui.QColor('#E8F5E9'))
            else:
                situacao_item.setBackground(QtGui.QColor('#FFEBEE'))
            self.tabelaClientes.setItem(row_pos, 4, situacao_item)
            self.tabelaClientes.item(row_pos, 0).setData(QtCore.Qt.UserRole, row['id'])

    def create_table_item(self, text):
        item = QtWidgets.QTableWidgetItem(text)
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        return item

    def clear_fields(self):
        self.txtId.clear()
        self.txtNome.clear()
        self.txtCpf.clear()
        self.txtIdade.setValue(0)
        self.txtRenda.setValue(0.0)
        self.txtSituacao.setText("NÃO ANALISADO")
        self.txtObs.clear()
        self.txtDataCadastro.setDateTime(QtCore.QDateTime.currentDateTime())
        self.update_statusbar("Campos limpos")

    def update_statusbar(self, message):
        self.statusbar.showMessage(message)

    def abrir_relatorio(self):
        self.relatorio = RelatorioWindow(self)
        self.relatorio.show()

    def load_selected_row(self, index):
        row = index.row()
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            item_id = self.tabelaClientes.item(row, 0).data(QtCore.Qt.UserRole)
            cursor.execute("""
                SELECT *, DATE_FORMAT(data_cadastro, '%%Y-%%m-%%d %%H:%%i:%%s') as dt 
                FROM clientes WHERE id=%s
            """, (item_id,))
            cliente = cursor.fetchone()
            if cliente:
                self.txtId.setText(str(cliente['id']))
                self.txtNome.setText(cliente['nome'])
                self.txtCpf.setText(cliente['cpf'])
                self.txtIdade.setValue(cliente['idade'])
                self.txtRenda.setValue(float(cliente['renda']))
                self.txtSituacao.setText(cliente['situacao'])
                self.txtObs.setPlainText(cliente['observacoes'] or '')
                data = QtCore.QDateTime.fromString(cliente['dt'], "yyyy-MM-dd HH:mm:ss")
                self.txtDataCadastro.setDateTime(data)
                self.update_statusbar(f"Carregado: {cliente['nome']}")
        except mysql.connector.Error as err:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Erro ao carregar cliente:\n{err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
