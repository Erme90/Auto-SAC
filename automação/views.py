from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import pyautogui
from time import sleep


#Esta função renderiza (abre) a página para o usuário
def index (request):
    if request.method == 'GET':
        form = Formulario()
    print('abriu a pagina')
    return render(request, 'index.html', {'form': form})

#Esta classe, fará com que os campos do formulário seja preenchido de forma correta e não deixa dados de fora.
class Formulario(forms.Form):
    usuario_desejado = forms.CharField(max_length=100, required=True, error_messages={'required': 'Campo obrigatório.'})
    nome_completo = forms.CharField(max_length=100, required=True, error_messages={'required': 'Campo obrigatório.'})
    matricula = forms.CharField(max_length=10, required=True, error_messages={'required': 'Campo obrigatório.'})
    email = forms.EmailField(required=True, error_messages={'required': 'Campo obrigatório.'})
    vinculo = forms.ChoiceField(choices=[('', 'Selecione um vínculo'),('Funcamp', 'Funcamp'), ('Unicamp', 'Unicamp')], required=True, error_messages={'required': 'Selecione um vinculo.'})

#Esta função, será chamada pela função "gera_senha"
def liberacao_de_senha():  #identificará o usuário criado para enviar o e-mail com as orientações
    servico = Service(ChromeDriverManager().install()) #instala o driver mais recente do chrome para habilitar o acesso do selenium
    navegador = webdriver.Chrome(service = servico)  #variavel que armazena o drive e o navegador que será utilizado
    
    navegador.get('https://www.sistemas.unicamp.br/servlet/pckSsegLiberacaoSenha.LiberacaoSenha')   #site que será automatizado.
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[1]/tbody/tr[1]/td[2]/input').send_keys('ussonhc')
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[1]/tbody/tr[2]/td[2]/input').send_keys('C@mpinas0804')
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[2]/tbody/tr/td/table/tbody/tr/td[1]/input').click()
    sleep(2.5)
    pyautogui.moveTo(33,33, duration=1)
    
    

#Esta função faz a execução do selenium para criação da senha nova (primeira senha) do SISE.
def gera_senha(request):
    servico = Service(ChromeDriverManager().install()) #instala o driver mais recente do chrome para habilitar o acesso do selenium
    navegador = webdriver.Chrome(service = servico)  #variavel que armazena o drive e o navegador que será utilizado
    if request.method == 'POST':
        form = Formulario(request.POST)
        if form.is_valid():
            usuario_desejado = form.cleaned_data['usuario_desejado']   
            nome_completo = form.cleaned_data['nome_completo']  
            matricula = form.cleaned_data['matricula']
            email = form.cleaned_data['email']
            vinculo = form.cleaned_data['vinculo']
            print('O usuário desejado é:', usuario_desejado, nome_completo,matricula, email, vinculo)
       
            try:    
                '''op_do_chrome = Options() ,options= op_do_chrome
                op_do_chrome.add_argument('--headless') #faz com que a pagina web que será aberta, não apareça para o usuário.'''

                    
                navegador.get('https://www1.sistemas.unicamp.br/SiSeCorp/publico/solicitacao_username/formsolicitacaousername.do')   #site que será automatizado.
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[1]').send_keys(usuario_desejado)#preenche o campo de usuário desejado
                
                print("Enter para enserir o 'Vinculo' e 'Matricula'")
                input()


                #Esta condicional irá identificar se o usuário é Funcamp ou Unicamp, então clicar no vínculo apropriado e preeche o campo "matricula".
                if vinculo == 'Funcamp':#se Funcamp
                    navegador.find_element('xpath','//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[3]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_funcamp"]/input').send_keys(matricula)
                elif vinculo == 'Unicamp':#se Unicamp
                    navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[2]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_unicamp"]/input').send_keys(matricula)

                print("Enter para inserir o 'email' ")
                input()
                
                

                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[2]').send_keys(email)#preenche o campo 'email'
                
                print("Enter para clicar no botão de envio")
                input()

                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[3]/input[1]').click()#Clica no botão de envio do formulário
                
                print("Enter para clicar no botão 'confirmar' ")
                input()
                
                navegador.find_element('xpath', '//*[@id="ConfirmarSolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[3]/input[1]').click()#confirma a criação do usuário.
                
                print("Enter para clicar no 'OK' do pop-up")
                input()
                
                
                popup = Alert(navegador)
                popup.accept()
                input()
                print('terminou a tarefa')
                navegador.quit()

                print('Criou um usuário novo')
             
               
                #mensagem de sucesso, caso o usuário seja criado sem erros.             
                msg = {
                    'msg_sucesso' : f'Usuário criado com sucesso! Siga as instruções enviadas para o email: {email}',
                    
                }
                print('enviou mensagem de "Sucesso"')
                liberacao_de_senha()
                print('Ativou a função "liberação de senha"')
                return render(request, 'index.html', msg) #redireciona para a mesma página, porém com o aviso de "sucesso"
            
            
            #Caso haja algum erro no envio do formulário, o usuário será informado com uma mensagem de erro.
            except Exception:
                mensagem_erro = f'ERRO: Verifique os dados informados e tente novamente'
                print(mensagem_erro)
                form.add_error(None, mensagem_erro)
                return render(request, 'index.html', {'form': form, 'mensagem_erro': mensagem_erro})#redireciona para a mesma página, porém com o aviso de "Erro"
            finally:
                navegador.quit()
        else:
            form = Formulario() 
        return render(request, 'index.html', {'form': form})
    
    
    #Segunda parte da execução da senha inicial. Será onde o selenium irá procurar o usuário criado, para autorizar a criação:


    '''#EMAIL AUTOMATICO
        
        resultado_tarefa = "teste concluído com sucesso"
        detalhes = "A tarefa automatizada foi concluída sem problemas."


        #variaveis com os dados do email
        
        assunto= 'Teste do projeto SAC'
        texto_email = f'Resultado: {resultado_tarefa}\nDetalhes: {detalhes}'
        remetente = 'emersonnascimento.freire@gmail.com' #este email enviará o email para o teste
        destinatario = email #este email foi preenchido pelo usuário no form
        print('pegou os dados do email')
        
        #Configuração do servidor para envio do email:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend', print('EMAIL_BACKEND')
        EMAIL_HOST = 'smtp.gmail.com', print('EMAIL_HOST')
        EMAIL_PORT = 587, print('EMAIL_PORT')
        EMAIL_USE_TLS = True, print('EMAIL_USE_TLS')
        EMAIL_HOST_USER = 'emersonnascimento.freire@gmail.com', print('EMAIL_HOST_USER')
        EMAIL_HOST_PASSWORD = '[e]91046344', print('EMAIL_HOST_PASSWORD')

        #utilização da função 'send_mail'
        print('Vai chamar a função "send_mail"')

        send_mail(assunto, texto_email, remetente, [destinatario], fail_silently=False)
        print('email enviado')'''