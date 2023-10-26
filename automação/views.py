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
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv(override=True)

usuario = os.getenv('USER_ADM_SENHA')
senha = os.getenv('SENHA_ADM_SENHA')
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


#Esta função, será chamada pela função "cria_usuario", para iniciar o processo de liberação e envio da senha ao usuário.

'''def liberacao_de_senha(usuario_desejado, senha, usuario):  #identificará o usuário criado para enviar o e-mail com as orientações
    print('Chama a página')
    input()
    servico = Service(ChromeDriverManager().install()) #instala o driver mais recente do chrome para habilitar o acesso do selenium
    navegador = webdriver.Chrome(service = servico)  #variavel que armazena o drive e o navegador que será utilizado
    print('envia os dados de login do adm')
    input()
    print('usuario')
    navegador.get('https://www.sistemas.unicamp.br/servlet/pckSsegLiberacaoSenha.LiberacaoSenha')   #site que será automatizado.
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[1]/tbody/tr[1]/td[2]/input').send_keys('ussonhc') #senha
    print('senha')
    input()
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[1]/tbody/tr[2]/td[2]/input').send_keys('C@mpinas0804')#usuario
    print(senha)
    print(usuario)
    input()
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[2]/tbody/tr/td/table/tbody/tr/td[1]/input').click()#clica no botão "acessar"
    navegador.find_element('xpath', f"//tr/td/input[@value='{usuario_desejado}']").click()#clica no usuário que acabou de ser criado, para poder liberar a senha
    navegador.find_element('xpath', '/html/body/form/table[3]/tbody/tr/td/table/tbody/tr/td[1]/input').click()#clica no botão "avançar"
    sleep(1)
    input()
    navegador.find_element('xpath', '/html/body/form/table[2]/tbody/tr/td/table/tbody/tr/td[3]/input').click'''

    #email(email) #chama a função de envio de email.

#Esta função faz a execução do selenium para criação da senha nova (primeira senha) do SISE.
def cria_usuario(request):
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
                navegador.get('https://www1.sistemas.unicamp.br/SiSeCorp/publico/solicitacao_username/formsolicitacaousername.do')   #site que será automatizado.
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[1]').send_keys(usuario_desejado)#preenche o campo de usuário desejado
                #Esta condicional irá identificar se o usuário é Funcamp ou Unicamp, então clicar no vínculo apropriado e preeche o campo "matricula".
                if vinculo == 'Funcamp':#se Funcamp
                    navegador.find_element('xpath','//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[3]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_funcamp"]/input').send_keys(matricula)
                    
                elif vinculo == 'Unicamp':#se Unicamp
                    navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[2]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_unicamp"]/input').send_keys(matricula)
                sleep(1)
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[2]').send_keys(email)#preenche o campo 'email'
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[3]/input[1]').click()#Clica no botão de envio do formulário
                navegador.find_element('xpath', '//*[@id="ConfirmarSolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[3]/input[1]').click()#confirma a criação do usuário.
               
                #Este código identifica o popup de confirmação e clica no "ok"
                popup = Alert(navegador)
                popup.accept()
                sleep(1)
               
            #Caso haja algum erro no envio do formulário, o usuário será informado com uma mensagem de erro.
            except Exception:
                mensagem_erro = f'ERRO: Verifique os dados informados e tente novamente'
                form.add_error(None, mensagem_erro)
                print('Agora vai renderizar a página, com uma msg de erro!')
                return render(request, 'index.html', {'form': form, 'mensagem_erro': mensagem_erro})#redireciona para a mesma página, porém com o aviso de "Erro"
            finally:
                navegador.quit()
        else:
            form = Formulario() 
        mensagem_sucesso = f'Usuário criado com sucesso! Verifique o e-mail {email} para instruções.'
        msg = {
            'msg_sucesso': mensagem_sucesso
        }
        print('Agora vai renderizar a página novamente!!!')
        return render(request, 'index.html', msg)
    

#EMAIL AUTOMATICO
def email(email):
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
    print('email enviado')