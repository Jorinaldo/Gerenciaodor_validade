import tkinter as tk
from datetime import datetime, timedelta
import json
from tkinter import messagebox

# Variável global para armazenar o índice do produto selecionado
indice_selecionado = None

def adicionar_produto():
    nome = entry_nome.get()
    marca = entry_marca.get()
    data_vencimento = entry_data.get()
    quantidade = int(entry_quantidade.get())
    data_adicao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    try:
        datetime.strptime(data_vencimento, '%d/%m/%Y')
    except ValueError:
        messagebox.showerror("Erro", "Formato de data inválido. Utilize o formato DD/MM/AAAA.")
        return

    resposta = messagebox.askokcancel("Confirmação", "Deseja realmente adicionar este produto?")
    
    if resposta:
        produtos.append({
            'nome': nome,
            'marca': marca,
            'data_vencimento': data_vencimento,
            'quantidade': quantidade,
            'data_adicao': data_adicao
        })

        # Limpar os campos de entrada
        entry_nome.delete(0, tk.END)
        entry_marca.delete(0, tk.END)
        entry_data.delete(0, tk.END)
        entry_quantidade.delete(0, tk.END)

        salvar_dados()
        atualizar_lista()

def desfazer_adicao():
    if produtos:
        ultimo_produto = produtos.pop()
        messagebox.showinfo("Desfazer Adição", f"Produto removido: {ultimo_produto['nome']}")
        salvar_dados()
        atualizar_lista()
    else:
        messagebox.showinfo("Desfazer Adição", "Nenhum produto para desfazer.")

def remover_produto(index):
    if messagebox.askyesno("Confirmar Exclusão", "Deseja realmente excluir este produto?"):
        del produtos[index]
        salvar_dados()
        atualizar_lista()

def selecionar_produto(index):
    global indice_selecionado
    indice_selecionado = index
    for i in range(len(produtos)):
        cor_destaque = 'lightgrey' if i == index else 'white'
        lista_produtos.tag_configure(f'linha{i}', background=cor_destaque)

    lista_produtos.tag_add('selecionado', f'{index + 1}.0', f'{index + 1}.end')

def calcular_dias_faltantes(data_vencimento):
    hoje = datetime.now()
    data_vencimento_obj = datetime.strptime(data_vencimento, '%d/%m/%Y')
    diferenca = data_vencimento_obj - hoje
    return diferenca.days

def filtrar_vencimentos():
    hoje = datetime.now()
    produtos_vencendo_em_7_dias = []

    for produto in produtos:
        data_vencimento = produto['data_vencimento']
        dias_faltantes = calcular_dias_faltantes(data_vencimento)

        if 0 <= dias_faltantes <= 7:
            produtos_vencendo_em_7_dias.append((produto, dias_faltantes))

    return produtos_vencendo_em_7_dias

def obter_10_proximos_vencimentos():
    produtos.sort(key=lambda x: datetime.strptime(x['data_vencimento'], '%d/%m/%Y'))
    return produtos[:10]

def exibir_alerta():
    proximos_vencimentos = obter_10_proximos_vencimentos()

    if proximos_vencimentos:
        alerta = tk.Toplevel(root)
        alerta.title("Alerta - Próximos Vencimentos")

        texto_alerta = tk.Label(alerta, text="Atenção! Os seguintes produtos estão próximos ao vencimento:")
        texto_alerta.pack()

        for produto in proximos_vencimentos:
            nome = produto['nome']
            marca = produto['marca']
            data_vencimento = produto['data_vencimento']
            quantidade = produto['quantidade']
            dias_faltantes = calcular_dias_faltantes(data_vencimento)

            cor_destaque = 'red' if dias_faltantes <= 7 else 'black'

            label_produto = tk.Label(alerta, text=f"Nome: {nome}, Marca: {marca}, Vencimento: {data_vencimento}, "
                                                  f"Quantidade: {quantidade}, Dias faltantes: {dias_faltantes} dias",
                                     fg=cor_destaque)
            label_produto.pack()
    else:
        messagebox.showinfo("Nenhum produto próximo ao vencimento", "Não há produtos próximos ao vencimento.")

def atualizar_lista():
    lista_produtos.delete(1.0, tk.END)

    produtos_vencendo_em_7_dias = filtrar_vencimentos()

    for i, (produto, dias_faltantes) in enumerate(produtos_vencendo_em_7_dias):
        nome = produto['nome']
        marca = produto['marca']
        data_vencimento = produto['data_vencimento']
        quantidade = produto['quantidade']
        data_adicao = produto['data_adicao']

        destaque_cor = 'red' if dias_faltantes <= 7 else 'black'

        lista_produtos.insert(tk.END, f"Nome: {nome}, Marca: {marca}, Vencimento: {data_vencimento}, "
                                        f"Quantidade: {quantidade}, Adicionado em: {data_adicao}, "
                                        f"Dias faltantes: {dias_faltantes} dias  ")

        # Verifica se o botão "Remover" já foi criado para este produto
        if not lista_produtos.tag_ranges(f'botao_remover_{i}'):
            botao_remover = tk.Button(root, text="Remover", command=lambda i=i: remover_produto(i))
            botao_remover.grid(row=i + 7, column=3)
            lista_produtos.window_create(f'{i + 7}.end', window=botao_remover)

        lista_produtos.tag_configure(f'linha{i}', background='white')

        # Adicionar a tag à linha atual
        lista_produtos.tag_add(f'linha{i}', f'{i + 7}.0', f'{i + 7}.end')

        # Associar a função de seleção ao clique na linha
        lista_produtos.tag_bind(f'linha{i}', '<Button-1>', lambda event, i=i: selecionar_produto(i))

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gerenciador de Produtos")

# Widgets
label_nome = tk.Label(root, text="Nome:")
label_marca = tk.Label(root, text="Marca:")
label_data = tk.Label(root, text="Data de Vencimento:")
label_quantidade = tk.Label(root, text="Quantidade:")

entry_nome = tk.Entry(root)
entry_marca = tk.Entry(root)
entry_data = tk.Entry(root)
entry_quantidade = tk.Entry(root)

botao_adicionar = tk.Button(root, text="Adicionar Produto", command=adicionar_produto)
botao_desfazer = tk.Button(root, text="Desfazer Adição", command=desfazer_adicao)
botao_alerta = tk.Button(root, text="Exibir Alerta", command=exibir_alerta)
lista_produtos = tk.Text(root, height=20, width=100)  # Ajuste de largura aqui

# Layout dos demais widgets
label_nome.grid(row=1, column=0, sticky=tk.W)
label_marca.grid(row=2, column=0, sticky=tk.W)
label_data.grid(row=3, column=0, sticky=tk.W)
label_quantidade.grid(row=4, column=0, sticky=tk.W)

entry_nome.grid(row=1, column=1)
entry_marca.grid(row=2, column=1)
entry_data.grid(row=3, column=1)
entry_quantidade.grid(row=4, column=1)

botao_adicionar.grid(row=5, column=0, columnspan=2)
botao_desfazer.grid(row=5, column=2, columnspan=2)
botao_alerta.grid(row=6, column=0, columnspan=2)
lista_produtos.grid(row=7, column=0, columnspan=4)  # Ajuste de coluna aqui

# Carregar ou criar dados ao iniciar o programa
try:
    with open('dados_produtos.json', 'r') as file:
        produtos = json.load(file)
except FileNotFoundError:
    produtos = []

# Atualizar a lista ao iniciar o programa
atualizar_lista()

# Exibir alerta ao iniciar o programa
exibir_alerta()

# Configurações da janela
largura_janela = 1000  # Ajuste de largura aqui
altura_janela = 600
largura_tela = root.winfo_screenwidth()
altura_tela = root.winfo_screenheight()
x_pos = largura_tela / 2 - largura_janela / 2
y_pos = altura_tela / 2 - altura_janela / 2
root.geometry(f'{largura_janela}x{altura_janela}+{int(x_pos)}+{int(y_pos)}')

root.mainloop()
