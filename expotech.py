import mysql.connector
from mysql.connector import Error

def conectar_banco():
    """Estabelece a conexão com o banco de dados MySQL"""
    try:
        conexao = mysql.connector.connect(
            host="localhost",       
            user="root",            # Seu usuário do MySQL
            password="26081914",   # A senha do seu usuário do MySQL
            database="sistema_biblioteca"
        )
        return conexao
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None

# ==========================================
#           FUNÇÕES DE LIVROS
# ==========================================

def cadastrar_livro():
    print("\n--- CADASTRAR LIVRO ---")
    titulo = input("Digite o título do livro: ")
    autor = input("Digite o nome do autor: ")
    paginas = int(input("Digite a quantidade de páginas: "))
    ano = int(input("Digite o ano de publicação: "))
    status = "Disponivel"
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        comando = "INSERT INTO livros (titulo, autor, paginas, ano_publicacao, status) VALUES (%s, %s, %s, %s, %s)"
        valores = (titulo, autor, paginas, ano, status)
        
        try:
            cursor.execute(comando, valores)
            conexao.commit()
            print(f"✔️ Livro '{titulo}' cadastrado com sucesso!")
        except Error as e:
            print(f"❌ Erro ao inserir no banco: {e}")
        finally:
            cursor.close()
            conexao.close()

def listar_livros():
    print("\n--- LISTA DE LIVROS ---")
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        comando = "SELECT id, titulo, autor, status FROM livros"
        
        try:
            cursor.execute(comando)
            livros = cursor.fetchall()
            
            if not livros:
                print("Nenhum livro cadastrado ainda.")
                return False
            
            print(f"{'ID':<4} | {'TÍTULO':<30} | {'AUTOR':<20} | {'STATUS':<12}")
            print("-" * 75)
            for livro in livros:
                status = livro[3] if livro[3] is not None else "Disponivel"
                print(f"{livro[0]:<4} | {livro[1]:<30} | {livro[2]:<20} | {status:<12}")
            return True
                
        except Error as e:
            print(f"❌ Erro ao buscar livros: {e}")
            return False
        finally:
            cursor.close()
            conexao.close()

def editar_livro():
    print("\n--- EDITAR LIVRO  ---")
    if not listar_livros():
        return

    try:
        id_livro = int(input("\nDigite o ID do livro que deseja editar: "))
        
        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT titulo, autor, paginas, ano_publicacao FROM livros WHERE id = %s", (id_livro,))
            livro = cursor.fetchone()
            
            if livro:
                print(f"\nDados atuais -> Título: {livro[0]} | Autor: {livro[1]} | Páginas: {livro[2]} | Ano: {livro[3]}")
                novo_titulo = input("Digite o novo título (ou Enter para manter): ")
                novo_autor = input("Digite o novo autor (ou Enter para manter): ")
                nova_paginas = input("Digite a nova qtde de páginas (ou Enter para manter): ")
                novo_ano = input("Digite o novo ano de publicação (ou Enter para manter): ")
                
                # Validação para manter o dado antigo caso o usuário dê Enter
                titulo_final = novo_titulo if novo_titulo.strip() != "" else livro[0]
                autor_final = novo_autor if novo_autor.strip() != "" else livro[1]
                paginas_final = int(nova_paginas) if nova_paginas.strip() != "" else livro[2]
                ano_final = int(novo_ano) if novo_ano.strip() != "" else livro[3]
                
                comando = """UPDATE livros 
                             SET titulo = %s, autor = %s, paginas = %s, ano_publicacao = %s 
                             WHERE id = %s"""
                cursor.execute(comando, (titulo_final, autor_final, paginas_final, ano_final, id_livro))
                conexao.commit()
                print("✔️ Dados do livro atualizados com sucesso!")
            else:
                print("❌ Livro não encontrado.")
    except ValueError:
        print("❌ Entrada inválida. Certifique-se de digitar números para ID, páginas e ano.")
    except Error as e:
        print(f"❌ Erro ao editar livro: {e}")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

def emprestar_livro():
    print("\n--- EMPRESTAR LIVRO ---")
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        
        try:
            # Busca apenas livros disponíveis
            cursor.execute("SELECT id, titulo FROM livros WHERE status = 'Disponivel'")
            disponiveis = cursor.fetchall()
            
            if not disponiveis:
                print("Não há livros disponíveis para empréstimo no momento.")
                return
                
            print("Livros disponíveis:")
            for id_livro, titulo in disponiveis:
                print(f"[{id_livro}] {titulo}")
                
            id_escolhido = int(input("\nDigite o ID do livro que deseja emprestar: "))
            
            # Verifica o status atual do livro escolhido
            cursor.execute("SELECT status FROM livros WHERE id = %s", (id_escolhido,))
            resultado = cursor.fetchone()
            
            if resultado is None:
                print("❌ ID inválido. Livro não encontrado.")
                return

            # Lista os clientes para escolher quem vai pegar
            print("\n--- CLIENTES ---")
            cursor.execute("SELECT id, nome FROM clientes")
            clientes = cursor.fetchall()

            if not clientes:
                print("Nenhum cliente cadastrado. Cadastre um cliente antes de realizar empréstimos.")
                return

            for cliente in clientes:
                print(f"[{cliente[0]}] {cliente[1]}")

            cliente_id = int(input("\nDigite o ID do cliente: "))
            
            # Executa o empréstimo se estiver tudo ok
            comando_update = """UPDATE livros 
                                SET status = 'Emprestado', cliente_id = %s
                                WHERE id = %s"""
            cursor.execute(comando_update, (cliente_id, id_escolhido))
            conexao.commit()
            print("✔️ Empréstimo realizado com sucesso!")
                
        except ValueError:
            print("❌ Por favor, digite um número de ID válido.")
        except Error as e:
            print(f"❌ Erro durante o empréstimo: {e}")
        finally:
            cursor.close()
            conexao.close()

def excluir_livro():
    print("\n--- EXCLUIR LIVRO ---")
    if not listar_livros():
        return
    try:
        id_livro = int(input("\nDigite o ID do livro que deseja excluir: "))
        
        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()
            # Verifica se o livro existe
            cursor.execute("SELECT titulo FROM livros WHERE id = %s", (id_livro,))
            livro = cursor.fetchone()
            
            if livro:
                confirmar = input(f"Tem certeza que deseja excluir '{livro[0]}'? (S/N): ").upper()
                if confirmar == 'S':
                    cursor.execute("DELETE FROM livros WHERE id = %s", (id_livro,))
                    conexao.commit()
                    print("✔️ Livro excluído com sucesso!")
                else:
                    print("Operação cancelada.")
            else:
                print("❌ Livro não encontrado.")
    except ValueError:
        print("❌ ID inválido.")
    except Error as e:
        print(f"❌ Erro ao excluir livro: {e}")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

# ==========================================
#           FUNÇÕES DE CLIENTES
# ==========================================

def cadastrar_cliente():
    print("\n--- CADASTRAR CLIENTE ---")
    nome = input("Digite o nome do cliente: ")
    telefone = input("Digite o telefone do cliente: ")

    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        comando = "INSERT INTO clientes (nome, telefone) VALUES (%s, %s)"
        valores = (nome, telefone)
        
        try:
            cursor.execute(comando, valores)
            conexao.commit()
            print("✔️ Cliente cadastrado com sucesso!")
        except Error as e:
            print(f"❌ Erro ao cadastrar cliente: {e}")
        finally:
            cursor.close()
            conexao.close()

def listar_clientes():
    print("\n--- LISTA DE CLIENTES ---")
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT id, nome, telefone FROM clientes")
            clientes = cursor.fetchall()
            
            if not clientes:
                print("Nenhum cliente cadastrado ainda.")
                return False
            
            print(f"{'ID':<4} | {'NOME':<30} | {'TELEFONE':<15}")
            print("-" * 55)
            for c in clientes:
                id = f"{c[0]:<4}"
                nome =  f"{c[1]:<30}"
                telefone = ""
                if c[2]:
                    telefone =f"{c[2]:<15}"
                print(f"{id} | {nome} | {telefone}")
            return True
        except Error as e:
            print(f"❌ Erro ao listar clientes: {e}")
            return False
        finally:
            cursor.close()
            conexao.close()

def editar_cliente():
    print("\n--- EDITAR CLIENTE  ---")
    if not listar_clientes():
        return

    try:
        id_cliente = int(input("\nDigite o ID do cliente que deseja editar: "))
        
        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT nome, telefone FROM clientes WHERE id = %s", (id_cliente,))
            cliente = cursor.fetchone()
            
            if cliente:
                print(f"\nDados atuais -> Nome: {cliente[0]} | Telefone: {cliente[1]}")
                novo_nome = input("Digite o novo nome (ou pressione Enter para manter o atual): ")
                novo_tel = input("Digite o novo telefone (ou pressione Enter para manter o atual): ")
                
                # Se o usuário der Enter vazio, mantém o que já estava no banco
                nome_final = novo_nome if novo_nome.strip() != "" else cliente[0]
                tel_final = novo_tel if novo_tel.strip() != "" else cliente[1]
                
                comando = "UPDATE clientes SET nome = %s, telefone = %s WHERE id = %s"
                cursor.execute(comando, (nome_final, tel_final, id_cliente))
                conexao.commit()
                print("✔️ Dados do cliente updated com sucesso!")
            else:
                print("❌ Cliente não encontrado.")
    except ValueError:
        print("❌ ID inválido.")
    except Error as e:
        print(f"❌ Erro ao editar cliente: {e}")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

def excluir_cliente():
    print("\n--- EXCLUIR CLIENTE ---")
    if not listar_clientes():
        return

    try:
        id_cliente = int(input("\nDigite o ID do cliente que deseja excluir: "))
        
        conexao = conectar_banco()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT nome FROM clientes WHERE id = %s", (id_cliente,))
            cliente = cursor.fetchone()
            
            if cliente:
                confirmar = input(f"Tem certeza que deseja excluir o cliente '{cliente[0]}'? \n(Isso deixará os livros que ele pegou como 'Disponíveis') (S/N): ").upper()
                if confirmar == 'S':
                    # O banco vai atualizar automaticamente os livros do cliente para NULL por causa da CONSTRAINT ON DELETE SET NULL
                    cursor.execute("DELETE FROM clientes WHERE id = %s", (id_cliente,))
                    # Atualiza o status dos livros que estavam com esse cliente de volta para Disponível
                    cursor.execute("UPDATE livros SET status = 'Disponivel' WHERE cliente_id IS NULL AND status = 'Emprestado'")
                    conexao.commit()
                    print("✔️ Cliente excluído com sucesso!")
                else:
                    print("Operação cancelada.")
            else:
                print("❌ Cliente não encontrado.")
    except ValueError:
        print("❌ ID inválido.")
    except Error as e:
        print(f"❌ Erro ao excluir cliente: {e}")
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()


# --- MENU PRINCIPAL (LOOP) ---
while True:
    print("\n=========================")
    print("  SISTEMA DE BIBLIOTECA  ")
    print("=========================")
    print("1. Cadastrar livro")
    print("2. Ver livros")
    print("3. Editar livro ")
    print("4. Emprestar livro")
    print("5. Excluir livro")
    print("-------------------------")
    print("6. Cadastrar cliente")
    print("7. Ver clientes")
    print("8. Editar cliente ")
    print("9. Excluir cliente ")
    print("-------------------------")
    print("10. Sair")
    opcao = input("\nEscolha uma opção (1-10): ")
    
    if opcao == '1':
        cadastrar_livro()
    elif opcao == '2':
        listar_livros()
    elif opcao == '3':
        editar_livro()
    elif opcao == '4':
        emprestar_livro()
    elif opcao == '5':
        excluir_livro()
    elif opcao == '6':
        cadastrar_cliente()
    elif opcao == '7':
        listar_clientes()
    elif opcao == '8':
        editar_cliente()
    elif opcao == '9':
        excluir_cliente()
    elif opcao == '10':
        print("Saindo do sistema... Até logo!")
        break
    else:
        print(" Opção inválida! Tente novamente.")
