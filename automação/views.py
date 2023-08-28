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
from selenium.common.exceptions import NoSuchElementException

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

#Esta função faz a execução do selenium para criação da senha nova (primeira senha) do SISE.
def gera_senha(request):
    print('clicou no botão')
    print('A função foi ativada')
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
                op_do_chrome = Options()
                op_do_chrome.add_argument('--headless') #faz com que a pagina web que será aberta, não apareça para o usuário.

                servico = Service(ChromeDriverManager().install()) #instala o driver mais recente do chrome para habilitar o acesso do selenium
                navegador = webdriver.Chrome(service = servico, options= op_do_chrome)  #variavel que armazena o drive e o navegador que será utilizado    
                navegador.get('https://www1.sistemas.unicamp.br/SiSeCorp/publico/solicitacao_username/formsolicitacaousername.do')   #site que será automatizado.
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[1]').send_keys(usuario_desejado)

                if vinculo == 'Funcamp':
                    navegador.find_element('xpath','//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[3]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_funcamp"]/input').send_keys(matricula)
                elif vinculo == 'Unicamp':
                    navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[2]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_unicamp"]/input').send_keys(matricula)

                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[2]').send_keys(email)
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[3]/input[1]').click()
                
                #EMAIL AUTOMATICO
                
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
                
                print('TERMINOU O CÓDIGO AGORA VAI REDIRECIONAR')
                return redirect('index')
            
            
            except NoSuchElementException as e:
                mensagem_erro = f'Erro: {str(e)}'
                print(mensagem_erro)
                form.add_error(None, mensagem_erro)
        else:
            print('deu erro no formulario')
            form = Formulario()
        return render(request, 'index.html', {'form': form})