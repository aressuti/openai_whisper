import openai
from dotenv import load_dotenv
import os
import requests
from PIL import Image
from instabot import Bot
import shutil

def openai_whisper_transcrever(caminho_audio, nome_arquivo, modelo_whisper, openai):
    print("Estou transcrevendo com o whispers ...")

    audio = open(caminho_audio, "rb")

    resposta = openai.audio.transcriptions.create(
        model = modelo_whisper,
        file = audio
    )

    transcricao = resposta.text

    with open(f"texto_completo_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(transcricao)

    return transcricao

def openai_gpt_resumir_texto(transcricao_completa, nome_arquivo, openai):
    print("Resumindo com o gpt para um post do instagram ...")

    prompt_sistema = """
    Assuma que você é um digital influencer digital e que está construíndo conteúdos das áreas de tecnologia em uma plataforma de áudio (podcast).

    Os textos produzidos devem levar em consideração uma peresona que consumirá os conteúdos gerados. Leve em consideração:

    - Seus seguidores são pessoas super conectadas da área de tecnologia, que amam consumir conteúdos relacionados aos principais temas da área de computação.
    - Você deve utilizar o gênero neutro na construção do seu texto
    - Os textos serão utilizados para convidar pessoas do instagram para consumirem seu conteúdo de áudio
    - O texto deve ser escrito em português do Brasil.

    """
    prompt_usuario = ". \nReescreva a transcrição acima para que possa ser postado como uma legenda do Instagram. Ela deve resumir o texto para chamada na rede social. Inclua hashtags"

    resposta = openai.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
                {
                        "role": "system",
                        "content" : prompt_sistema
                },
                {
                        "role": "user",
                        "content": transcricao_completa + prompt_usuario
                }
        ],
        temperature = 0.6
    )

    resumo_instagram = resposta.choices[0].message.content

    with open(f"resumo_instagram_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(resumo_instagram)

    return resumo_instagram

def openai_gpt_criar_resumo_instagram(nome_arquivo, openai):
    print("Resumindo com o gpt para um post do instagram ...")

    prompt_sistema = """
    Assuma que você é um digital influencer e que está construíndo conteúdos das áreas de tecnologia voltado para data analytics.

    Os textos produzidos devem levar em consideração uma persona que consumirá os conteúdos gerados. Leve em consideração:

    - Seus seguidores são pessoas super conectadas da área de tecnologia, que amam consumir conteúdos relacionados aos principais temas da área de computação.
    - Você deve utilizar o gênero neutro na construção do seu texto
    - Os textos serão utilizados para convidar pessoas do instagram para consumirem seu conteúdo
    - O texto deve ser escrito em português do Brasil.

    """
    prompt_usuario = ". \nCrie um texto para que pequenos empresários entendam os benefícios do data analytics para os seus negócios e que possa ser postado como uma legenda do Instagram. Ela deve resumir o texto para chamada na rede social. Inclua hashtags"

    resposta = openai.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
                {
                        "role": "system",
                        "content" : prompt_sistema
                },
                {
                        "role": "user",
                        "content": prompt_usuario
                }
        ],
        temperature = 0.6
    )

    resumo_instagram = resposta.choices[0].message.content

    with open(f"resumo_instagram_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(resumo_instagram)

    return resumo_instagram

def ferramenta_ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, "rb") as arquivo:
            return arquivo.read()
    except IOError as e:
        print(f"Erro no carregamento de arquivo: {e}")

def openai_gpt_criar_hashtag(resumo_instagram, nome_arquivo, openai):
    print("Gerando as hashtags com a open ai ... ")

    prompt_sistema = """
    Assuma que você é um digital influencer digital e que está construíndo conteúdos das áreas de tecnologia em uma plataforma de áudio (podcast).

    Os textos produzidos devem levar em consideração uma peresona que consumirá os conteúdos gerados. Leve em consideração:

    - Seus seguidores são pessoas super conectadas da área de tecnologia, que amam consumir conteúdos relacionados aos principais temas da área de computação.
    - Você deve utilizar o gênero neutro na construção do seu texto
    - Os textos serão utilizados para convidar pessoas do instagram para consumirem seu conteúdo de áudio
    - O texto deve ser escrito em português do Brasil.
    - A saída deve conter 5 hashtags.

    """

    prompt_usuario =f'Aqui está um resumo de um texto "{resumo_instagram}". Por favor, gere 5 hashtags que sejam relevantes para este texto e que possam ser publicadas no Instagram.  Por favor, faça isso em português do Brasil '

    resposta = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content" : prompt_sistema
            },
            {
                "role": "user",
                "content": prompt_usuario
            }
        ],
        temperature = 0.6
    )
        
        
    hashtags = resposta.choices[0].message.content
        
    with open(f"hashtag_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
        arquivo_texto.write(hashtags)
    
    return hashtags

def openai_gpt_gerar_texto_imagem(resumo_instagram, nome_arquivo, openai):
    print("Gerando a saida de texto para criacao de imagens com o GPT ...")

    prompt_sistema = """

    - A saída deve ser uma única, do tamanho de um tweet, que seja capaz de descrever o conteúdo do texto para que possa ser transcrito como uma imagem.
    - Não inclua hashtags

    """

    prompt_usuario =  f'Reescreva o texto a seguir, em uma frase, para que descrever o texto abaixo em um tweet: {resumo_instagram}'

    resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {
                            "role": "system",
                            "content" : prompt_sistema
                    },
                    {
                            "role": "user",
                            "content": prompt_usuario
                    }
            ],
            temperature = 0.6
    )

    texto_para_imagem = resposta.choices[0].message.content

    with open(f"texto_para_geracao_imagem_{nome_arquivo}.txt", "w",encoding='utf-8') as arquivo_texto:
            arquivo_texto.write(texto_para_imagem)

    return texto_para_imagem

def openai_dalle_gerar_imagem(resolucao, resumo_para_imagem, nome_arquivo, openai, qtd_imagens = 1):
    print("Criando uma imagem utilizando a API do DALL-E ...")

    prompt_user = f"Uma imagem simples e lúdica, textless que retrate: {resumo_para_imagem}"
    prompt_user = "Uma imagem de logo em flat design para uma empresa de tecnologia da informação chamada salada de dados, que faz serviços de business intelligence, data analytics, engenharia de dados, desenvolvimento de software. Use símbolos que lembrem os serviços prestados"
    prompt_user = "imagem de avatar estilo Pixar de garota de 27 anos, cabelos castanho claro compridos e linda"
    prompt_user = f"Uma imagem atraente, sem texto, que retrate: {resumo_para_imagem}"

    resposta = openai.images.generate(
        prompt =prompt_user,
        n = qtd_imagens,
        size = resolucao
    )

    return resposta.data

def ferramenta_download_imagem(nome_arquivo, imagem_gerada,qtd_imagens = 1):
  lista_nome_imagens = []
  try:
    for contador_imagens in range(0,qtd_imagens):
        caminho = imagem_gerada[contador_imagens].url
        imagem = requests.get(caminho)

        with open(f"{nome_arquivo}_{contador_imagens}.png", "wb") as arquivo_imagem:
            arquivo_imagem.write(imagem.content)

        lista_nome_imagens.append(f"{nome_arquivo}_{contador_imagens}.png")
    return lista_nome_imagens
  except:
    print("Ocorreu um erro!")
    return  None

def selecionar_imagem (lista_nome_imagens):
    return lista_nome_imagens[int(input("Qual imagem você deseja selecionar, informe o numero do sufixo da imagem gerada?"))]

def selecionar_imagem (lista_nome_imagens):
    return lista_nome_imagens[int(input("Qual imagem você deseja selecionar? "))]

def ferramenta_converter_png_para_jpg(caminho_imagem_escolhida, nome_arquivo):
    img_png = Image.open(caminho_imagem_escolhida) 
    img_png.save(caminho_imagem_escolhida.split(".")[0]+".jpg") 

    return caminho_imagem_escolhida.split(".")[0] + ".jpg"

def postar_instagram(caminho_imagem, texto, user, password):
    # if os.path.exists("config"):
    #     shutil.rmtree("config")

    bot = Bot()
    bot.login(username=user, password=password, use_cookie=False)
    # user_id = bot.get_user_id_from_username("lego")
    # user_info = bot.get_user_info(user_id)
    # print(user_info['biography'])

    resposta = bot.upload_photo(caminho_imagem, caption=texto)

def confirmacao_postagem(caminho_imagem_convertida, legenda_imagem):
    print("f\nCaminho Imagem: (caminho_imagem_convertida}") 
    print(f"\Legenda: {legenda_imagem}") 
    
    print("\n\nDeseja postar os dados acima no seu instagram? Digite 's' para sim e 'n' para não.")
    return input()

def ferramenta_conversao_binario_para_string(texto):
    if isinstance(texto, bytes):
        return str(texto.decode())
    return texto

def main():
    load_dotenv()

    caminho_audio = "podcasts\Semente.mp3"
    nome_arquivo = "Semente.mp3"
    nome_arquivo = "post_instagram"
    url_podcast = "https://www.hipsters.tech/nvidia-ia-comunidade-e-dev-leaders-hipsters-ponto-tech-364/"
    resolucao = "1024x1024"
    qtd_imagens = 4
    usuario_instagram = os.getenv("USER_INSTAGRAM")
    password_instagram = os.getenv("PASSWORD_INSTAGRAM")

    print(usuario_instagram)
    print(password_instagram)

    api_openai = os.getenv("API_KEY_OPENAI")
    openai.api_key = api_openai

    modelo_whisper = "whisper-1"

    transcricao_completa = ferramenta_ler_arquivo("texto_completo_Semente.mp3.txt")
    # resumo_instagram = ferramenta_ler_arquivo("resumo_instagram_Semente.mp3.txt")
    # resumo_instagram = openai_gpt_criar_resumo_instagram(nome_arquivo, openai)
    resumo_instagram = ferramenta_ler_arquivo("resumo_instagram_post_instagram.txt")

    # hashtags = openai_gpt_criar_hashtag(resumo_instagram, nome_arquivo, openai)
    hashtags = ferramenta_ler_arquivo("hashtag_post_instagram.txt")

    # resumo_imagem_instagram = openai_gpt_gerar_texto_imagem(resumo_instagram, nome_arquivo, openai)
    # resumo_imagem_instagram = ferramenta_ler_arquivo("texto_para_geracao_imagem_post_instagram.txt")

    # imagem_gerada = openai_dalle_gerar_imagem(resolucao, resumo_imagem_instagram, nome_arquivo, openai, qtd_imagens)

    # lista_imagens_geradas = ferramenta_download_imagem(nome_arquivo, imagem_gerada, qtd_imagens)
    # caminho_imagem_escolhida = selecionar_imagem(lista_imagens_geradas)
    caminho_imagem_escolhida = "post_instagram_1.png"
    caminho_imagem_convertida = ferramenta_converter_png_para_jpg(caminho_imagem_escolhida, nome_arquivo)

    legenda_imagem = f"{ferramenta_conversao_binario_para_string(resumo_instagram)} \n {ferramenta_conversao_binario_para_string(hashtags)}"

    if confirmacao_postagem(caminho_imagem_convertida, legenda_imagem).lower() == "s":
        postar_instagram(caminho_imagem_convertida,
                        legenda_imagem, 
                        usuario_instagram, 
                        password_instagram)

if __name__ == "__main__":
    main()