from django import forms
from django.shortcuts import render, redirect
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from time import sleep
from decouple import Config, Csv
from dotenv import load_dotenv
import smtplib
import email.message

def inicia_webdriver():
    options = Options()
    options.headless = True
    servico = Service(ChromeDriverManager().install()) 
    return webdriver.Chrome(service=servico, options=options)

#Configuração de variaveis de ambiente.
config = Config('.env')
load_dotenv(override=True)
usuario_adm = config('USER_ADM_SENHA')
senha_adm = config('SENHA_ADM_SENHA')
usuario_gmail = config('USER_GMAIL')
senha_gmail = config('SENHA_GMAIL')

#Esta função renderiza (abre) a página para o usuário
def index (request):
    if request.method == 'GET':
        form = Formulario()
    print('abriu a pagina')
    return render(request, 'index.html', {'form': form})

def sucesso (request):
    email_usuario = request.session.get('email_usuario')
    return render(request,'index_sucesso.html', {'email_usuario': email_usuario})

def valida_username(value):
    if not value.isalpha():
        raise forms.ValidationError('ERRO: O seu usuário deve conter somente letras.')

#Esta classe, fará com que os campos do formulário seja preenchido de forma correta e não deixa dados de fora.
class Formulario(forms.Form):
    usuario_desejado = forms.CharField(max_length=8, required=True, validators=[valida_username],error_messages={'required': 'Campo obrigatório.'})
    nome_completo = forms.CharField(max_length=100, required=True, error_messages={'required': 'Campo obrigatório.'})
    matricula = forms.CharField(max_length=10, required=True, error_messages={'required': 'Campo obrigatório.'})
    email_usuario = forms.EmailField(required=True, error_messages={'required': 'Campo obrigatório.'})
    vinculo = forms.ChoiceField(choices=[('', 'Selecione um vínculo'),('Funcamp', 'Funcamp'), ('Unicamp', 'Unicamp')], required=True, error_messages={'required': 'Selecione um vinculo.'})

def enviar_email(email_usuario, usuario_desejado, senha_provisoria, nome_completo):  
    corpo_email = f"""
    <p>Olá {nome_completo}</p>
    <p>O seu usuário <strong>{usuario_desejado}</strong> foi criado com sucesso e sua senha provisória é <strong>{senha_provisoria}</strong>. !</p>
    <br>    
    <P style="color: #f00;">LEIA ATENTAMENTE AS INSTRUÇÕES DESTA MENSAGEM, INCLUSIVE OS LINKS IMPORTANTES LOGO ABAIXO.</P>
    <br>
    <P># A senha contida neste e-mail, deverá ser trocada antes do primeiro acesso, para isso, clique no link relacionado abaixo e siga os passos da página.</P>
    <P># Este username criado, também é seu e-mail institucional ({usuario_desejado}@unicamp.br)</P> 
    <br>   
    <p>Links Importantes:</p>


    <p> Para efetuar a troca de senha: </p>

    <p> https://www1.sistemas.unicamp.br/TrocarSenha/trocarsenha.do </p>


    <p> Para acesso ao email institucional, após a troca da senha:</p>

    <p>https://webmail.unicamp.br</p>

    <p>Para recuperação de senha, em caso de esquecimentos ou problemas de acesso:</p>

    <p>https://www1.sistemas.unicamp.br/TrocarSenha/trocarsenhaesquecimento.do</p>


    <p>Para efetuar o acesso a rede wifi/vpn, após a troca da senha, SIGA à Risca  lendo o conteúdo completo dos procedimentos existentes no link abaixo:</p>

    <p>http://www.ccuec.unicamp.br/ccuec/catalogo/redes-vpn-e-redes-sem-fio-wi-fi </p>
    """

    msg = email.message.Message()
    msg['Subject'] = "Criação de usuário Sise"
    msg['From'] = usuario_gmail
    msg['To'] = email_usuario
    password = senha_gmail
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )
    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Credenciais para login no email.
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))

#Esta função faz a execução do selenium para criação da senha nova (primeira senha) do SISE.
def cria_usuario(request):
    navegador = inicia_webdriver()
    if request.method == 'POST':
        form = Formulario(request.POST)
        if form.is_valid():
            usuario_desejado = form.cleaned_data['usuario_desejado']   
            nome_completo = form.cleaned_data['nome_completo']  
            matricula = form.cleaned_data['matricula']
            email_usuario = form.cleaned_data['email_usuario']
            vinculo = form.cleaned_data['vinculo']
       
            try:    
                print('entrou no "try"')            
                navegador.get('https://www1.sistemas.unicamp.br/SiSeCorp/publico/solicitacao_username/formsolicitacaousername.do')   #site que será automatizado.
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[1]').send_keys(usuario_desejado)#preenche o campo de usuário desejado
                #Esta condicional irá identificar se o usuário é Funcamp ou Unicamp, então clicar no vínculo apropriado e preeche o campo "matricula".
                if vinculo == 'Funcamp':#se Funcamp
                    navegador.find_element('xpath','//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[3]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_funcamp"]/input').send_keys(matricula)
                    
                elif vinculo == 'Unicamp':#se Unicamp
                    navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/div[1]/select/option[2]').click()
                    navegador.find_element('xpath', '//*[@id="div_matricula_unicamp"]/input').send_keys(matricula)
           
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[2]/input[2]').send_keys(email_usuario)#preenche o campo 'email_usuario'
                navegador.find_element('xpath', '//*[@id="SolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[3]/input[1]').click()#Clica no botão de envio do formulário
                navegador.find_element('xpath', '//*[@id="ConfirmarSolicitacaoUsernameActionForm"]/div/div[1]/div/div/div[3]/input[1]').click()#confirma a criação do usuário.
                request.session['email_usuario'] = email_usuario

                #Este código identifica o popup de confirmação e clica no "ok"
                popup = Alert(navegador)
                popup.accept()
                sleep(0.5)                                
               
            #Caso haja algum erro no envio do formulário, o usuário será informado com uma mensagem de erro.
            
            except NoSuchElementException as e:
                print('entrou no "except"')
                mensagem_erro = f'ERRO: por favor tente novamente'
                form.add_error(None, mensagem_erro)
                navegador.quit()
                return render(request, 'index.html', {'form': form})

            finally:  
                print('Entrou no "finally"')
                navegador.quit()
                if form.errors:
                    return render(request, 'index.html', {'form': form}) 
        else:
            print('entrou no "else"')
            form.add_error = (None, 'ERRO: Username não está dentro dos padrões, tente novamente')    
            return render (request, 'index.html', {'form': form})     
        
        liberacao_de_senha(usuario_desejado, email_usuario, nome_completo)
       
        return redirect ('sucesso')


#Esta função, será chamada pela função "cria_usuario", para iniciar o processo de liberação e envio da senha ao usuário e também chamará a função
# de envio do email com instruções.

def liberacao_de_senha(usuario_desejado, email_usuario, nome_completo):
    print('entrou no "liberação de senha"')  
    navegador = inicia_webdriver()
    navegador.get('https://www.sistemas.unicamp.br/servlet/pckSsegLiberacaoSenha.LiberacaoSenha')   #site que será automatizado.
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[1]/tbody/tr[1]/td[2]/input').send_keys('ussonhc')
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[1]/tbody/tr[2]/td[2]/input').send_keys('C@mpinas0804')
    navegador.find_element('xpath', '/html/body/form/div/div/div/div/table[2]/tbody/tr/td/table/tbody/tr/td[1]/input').click()
    navegador.find_element('xpath', f"//tr/td/input[@value='{usuario_desejado}']").click()
    navegador.find_element(By.NAME, 'cmdAvancar').click()
    navegador.find_element(By.NAME, 'cmdAvancar').click()
    #armazena a senha provisória capturada na página
    senha_provisoria = navegador.find_element('xpath', '/html/body/form/b[3]').text
    #navegador.find_element(By.NAME, 'cmdConfirmar').click()
    enviar_email(email_usuario, usuario_desejado, senha_provisoria, nome_completo)