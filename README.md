# sistema-credito-clientes
Sistema básico de analise de créditos
# Análise de Crédito - PyQt5

Sistema desktop desenvolvido com Python e PyQt5 para cadastro, análise e gerenciamento de clientes e suas solicitações de crédito.

![screenshot](link_da_imagem_ou_gif_aqui)

## 🚀 Funcionalidades

- Cadastro de clientes com nome, CPF, idade, renda, observações e data de cadastro
- Análise automática de crédito baseada em idade e renda
- Cálculo de score e limite sugerido
- Validação de dados (CPF, nome, situação)
- Edição e exclusão de registros
- Interface gráfica moderna com PyQt5
- Relatório dos últimos cadastros
- Integração com banco de dados MySQL

## 📊 Lógica de análise de crédito

A lógica avalia a renda e idade do cliente para definir:
- Situação (aprovado, reprovado, limite reduzido ou especial)
- Score de 0 a 4
- Limite de crédito sugerido

## 🛠️ Tecnologias utilizadas

- Python 3.x
- PyQt5
- MySQL
- Qt Designer (.ui)

## 🧪 Como rodar o projeto

### Pré-requisitos

- Python 3.x
- PyQt5 (`pip install pyqt5`)
- MySQL instalado e rodando
- Crie o banco de dados com o nome `tectreinamentos_credito`

### Instalação

```bash
git clone https://github.com/SeuUsuario/analise-credito-pyqt5.git
cd analise-credito-pyqt5
python controle.py
CREATE DATABASE tectreinamentos_credito;

USE tectreinamentos_credito;

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    cpf VARCHAR(11),
    idade INT,
    renda DECIMAL(10,2),
    situacao VARCHAR(100),
    observacoes TEXT,
    data_cadastro DATETIME,
    data_atualizacao DATETIME
);
