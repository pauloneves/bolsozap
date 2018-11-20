#%% [markdown]
# # Análise de um grupo Bolsonarista no WhatsApp
#
# Após alguns surpreendentes resultados no primeiro turno da eleição de 2018, resolvi acompanhar um grupo de WhatsApp da campanha do candidato Jair Bolsonaro. Tinha curiosidade entender como funcionava tão importante engrenagem da campanha.
#
# A quantidade de mensagens é enorme. Não dá para ler tudo. Resolvi então fazer análise de dados para compreender padrões seu funcionamento.

#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
from dateutil.parser import parse as dtparse
get_ipython().run_line_magic('matplotlib', 'inline')
plt.rcParams['figure.figsize'] = [14, 7]
plt.rc('axes', titlesize=20)

from IPython.core.display import display, HTML
def printBig(s):
    display(HTML('<span style="font-size:2em;color:darkblue">{:s}</span>'.format(s)))


#%% [markdown]
# ## Reportagens sobre a campanha no WhatsApp
#
# Algumas reportagens sobre o esquema de divulgação:
# - [El País - A máquina de ‘fake news’ nos grupos a favor de Bolsonaro no WhatsApp](https://brasil.elpais.com/brasil/2018/09/26/politica/1537997311_859341.html)
# - [Folha - Estudo aponta para automação no envio de mensagens e orquestração entre grupos de WhatsApp pró-Bolsonaro](https://www1.folha.uol.com.br/poder/2018/10/estudo-aponta-para-automacao-no-envio-de-mensagens-e-orquestracao-entre-grupos-de-whatsapp-pro-bolsonaro.shtml)
# - [Folha - Grupos de WhatsApp simulam organização militar e compartilham apoio a Bolsonaro](https://www1.folha.uol.com.br/poder/2018/10/grupos-de-whatsapp-simulam-organizacao-militar-e-compartilham-apoio-a-bolsonaro.shtml)
# - [BBC - How WhatsApp is being abused in Brazil's elections](https://www.bbc.com/news/technology-45956557)
# - [New York Times - Disinformation Spreads on WhatsApp Ahead of Brazilian Election](https://www.nytimes.com/2018/10/19/technology/whatsapp-brazil-presidential-election.html)
#
# ## Mas as postagens são mentiras?
#
# **Sim.**
#
# Não vou abordar isto aqui, porque basta acompanhar um pouco os grupos para perceber que **não há a mínima preocupação com a verdade**. O El Pais publicou uma [boa coleção de mentiras](https://brasil.elpais.com/especiais/2018/eleicoes-brasil/conversacoes-whatsapp/) nos grupos Bolsonaristas.
#
# Você pode ter mais trabalho para chegar à mesma conclusão, como fez a [Agência](https://piaui.folha.uol.com.br/lupa/2018/10/17/whatsapp-lupa-usp-ufmg-imagens/) [Lupa](https://piaui.folha.uol.com.br/lupa/2018/10/18/imagens-falsas-whatsapp-presidenciaveis-lupa-ufmg-usp/) e os [pesquisadores da UFMG](https://www.eleicoes-sem-fake.dcc.ufmg.br/), para mim basta ver que boa parte das notícias são de imagens como estas:
#
# - Jogo do Bicho fazendo propaganda para Haddad.
# - Propaganda Haddad para presidários.
#
# <img alt="Jogo do Bicho fazendo propaganda para Haddad" src="jogo-do-bicho-haddad.jpg" width="29.465%" style="float:left;" align="top"><img alt="Propaganda para presidiários" src="panfleto-presidiarios.jpg" width="70%" style="float:right;" align="top">
#
#
#

#%%
#Parse de arquivo para dataframe
#whatsAppExported = 'https://drive.google.com/file/d/1tXBKAsAEy_wPI8h8xvsyXy-vJB0_J78c/view?usp=sharing'
whatsAppExported = "conversas/Conversa do WhatsApp com BOLSONARO, o Mito ! 😎👉👉.txt"

# exportar arquivo Abrindo grupo → configurações → mais → exportar conversa
# um parse ingênuo

import urllib.request
import re
import pandas as pd

inicioRE = re.compile(r'^(\d\d/\d\d/\d{4} \d\d:\d\d) - (.*)')
dadosRE = re.compile('^\u200e?\u202a(?P<fone>.*)\u202c'  + r'(?P<tipo>.) *(?P<texto>.*)')
foneRE = re.compile('[^0-9]+')
with open(whatsAppExported, encoding='utf8') as f:
    dados = []
    msg = []
    obs = {} # uma única observação
    txt = []
    for line in f:
        m = inicioRE.match(line)
        if m:
            if obs:
                obs['texto'] = '\n'.join(txt)
                dados.append(obs)
                obs = {}
                txt = []

            obs['data'] = pd.to_datetime(m.group(1), dayfirst=True) #brasil
            line = m.group(2)
            m = dadosRE.match(line)
            if m:
                grupos = m.groupdict()
                obs.update(grupos)

                obs['pais'], obs['uf'], obs['tel'] = foneRE.split(grupos['fone'][1:], #tirando o +
                                                                  maxsplit=2)
                txt = [obs['texto']]
            else:
                txt.append(line)
        else:
            txt.append(line)
        date = line[:16]

df = pd.DataFrame(dados)


#%%
# Categorizando as mensagens atribuindo um tipo para cada.
df.loc[(df.tipo==':') & (df.texto.str.contains('<Arquivo de mídia oculto>') ), 'tipo'] = 'midia'
df.loc[(df.tipo==':') & (df.texto.str.contains('Acesse este link para entrar no meu grupo do WhatsApp')), 'tipo'] = 'convite'
df.loc[(df.tipo==':') & (df.texto.str.contains('youtu.?be')), 'tipo'] = 'youtube'
df.loc[(df.tipo==':') & (df.texto.str.contains('https://www.facebook.com', case=False)), 'tipo'] = 'facebook'
df.loc[(df.tipo==':') & (df.texto.str.contains('https?://', case=False)), 'tipo'] = 'link'
df.loc[(df.tipo==':') & (df.texto.str.contains('Esta mensagem foi apagada')), 'tipo'] = 'apagada'
df.loc[(df.texto.str.contains('^removeu')), 'tipo'] = 'banimento'
df.loc[(df.texto.str.contains('^entrou usando o')), 'tipo'] = 'assinatura'
df.loc[(df.texto.str.contains('saiu$', case=False)), 'tipo'] = 'desistencia'
df.loc[(df.tipo==':'), 'tipo'] = 'texto'
df.loc[(df.tipo.str.strip().str.len()==0) & (df.texto.str.contains('alterado para')), 'tipo'] = 'muda-tel'
df.loc[(df.tipo.str.strip().str.len()==0), 'tipo']= np.NaN

tipos_msg = ['midia', 'youtube', 'facebook', 'link', 'texto']

#with pd.option_context("display.max_rows", 1000):
#    display(df[df.tipo == ':'])


#%%
#transformando em categoria
c = list(df.columns)
c.remove('texto')
c.remove('data')
df.loc[:, c] = df.loc[:, c].astype('category')

#%% [markdown]
# Múmero de mensagens de cada tipo

#%%
tipos = df.groupby('tipo').size()

display(tipos.sort_values(ascending=False))


#%%
df.head()


#%%
df.info()


#%%
# pegando alguns metadados do grupo
msg_criacao = df.loc[(df.tipo.isna()) & (df.texto.str.contains('criou o grupo '))]
data_criacao = msg_criacao.data

#isso daqui só lista os moderadores que estão participando ativamente do grupo
#TODO: pegar quem altera nome do grupo
msgs_moderacao = pd.concat([df.loc[df.tipo == 'banimento'], msg_criacao])
moderadores = msgs_moderacao.groupby('fone').size().reset_index(name ='nivel_atividade')
moderadores = moderadores[moderadores.nivel_atividade > 0]
print(f'O grupo tem {len(moderadores)} moderadores ativos')

#%% [markdown]
# ## Frequência de mensagens
#
# Analisando a frequência com que as mensagens são postadas.

#%%
#vamos tirar o dia de criação do grupo, e primeiro e último dia
#pois estes estão incompletos e bagunçarima as médias
import datetime
data_entrou = df.loc[(df.tipo.isna()) & (df.texto.str.contains('entrou')), ['data']]
primeiro_dia = data_entrou.data.dt.normalize() + datetime.timedelta(days=1)
primeiro_dia = primeiro_dia.iat[0]
ultimo_dia = df.loc[:, 'data'].max().normalize()
print(f'Primeiro dia completo: {primeiro_dia}\nùltimo dia: {ultimo_dia}')


#%%
#Para análise de frequência, tirar o dia em que entrou e o dia em que fez o backup
#e usar apenas as mensagens de conteúdo, excluindo moderações ou quem entrou e saiu
df['finde'] = df.data.dt.weekday.isin([5,6])
df_freq = df[(df.data >= primeiro_dia) & (df_freq.data < ultimo_dia) & (df.tipo.isin(tipos_msg))]

msg_media = df_freq.groupby(df_freq.data.dt.day).size().mean()
printBig('{:.0f} mensagens por dia (média)'.format(msg_media))


#%%
msg_media_dia_util = df_freq[~df_freq.finde].groupby(df_freq.data.dt.day).size().mean()
msg_media_finde = df_freq[df_freq.finde].groupby(df_freq.data.dt.day).size().mean()

printBig('{:.0f} nos dias úteis x {:.0f} nos findes'.format(msg_media_dia_util, msg_media_finde))
if msg_media_dia_util > msg_media_finde:
    print("Aumenta {:.1%} nos dias úteis".format(msg_media_dia_util/msg_media_finde - 1))
else:
    print("Aumenta {:.1%} nos fins de semana".format(msg_media_finde/msg_media_dia_util - 1))

#%% [markdown]
# Bem interessante. Será que as pessoas enviando mensagens folgam no fim de semana? Vamos ver quão maior é o número de mensagem em dias úteis em relação ao fim de semana.

#%%
import dateutil.parser
df_freq_por_dia =  df_freq.groupby(df_freq.data.dt.date).size()

ax = df_freq_por_dia.plot.line()
ax.set_xticks(df_freq.data.dt.date.unique())
ax.set_xticklabels(df_freq.data.dt.date.unique())

[label.set_color('blue') for label in ax.get_xticklabels() if dtparse(label.get_text()).weekday() in [5,6]]
ax.set_title("Postagens por dia (finde em azul)", loc='left')
ax.tick_params(axis='x', labelrotation=70)

#%% [markdown]
# Pelo visto não há relação entre o número de posts e o fim de semana. Parece haver alguma redução, mas nada significativo.

#%%
plt.hist(df_freq.data.dt.hour, bins=24);
plt.gca().set_title('Postagens por hora', loc='left');

#%% [markdown]
# O esperado é ter bem menos mensagens de madrugada. Caso contrário são robôs, gente paga, ou bolsonaristas com TOC e afetamina. Não acho que haja muita diferença entre as opções possíveis.

#%%
percentagem_midia = (tipos.loc[['midia', 'youtube']].sum() /
                     tipos.loc[['midia', 'youtube', 'texto']].sum())


printBig('{:.2%} são vídeo, áudio ou imagens'.format(percentagem_midia))

#%% [markdown]
# Percentual das mensagens que são vídeo ou imagens. Multimídia é caro de produzir. Isto é uma boa indicação que há uma infraestrutura por trás gerando conteúdo para estes fóruns.

#%%
printBig('{:d} pessoas diferentes postaram'.format(df.tel.unique().size))

#%% [markdown]
# Um grupo de WhatsApp  pode ter no máximo **256 pessoas**. Um número grande pessoas postando indica várias pessoas reais participando e que o grupo está cumprindo seu papel de divulgação. Note que nem todas as pessoas que postaram estavam presentes no grupo ao mesmo tempo. As pessoas vão entrando e saindo.

#%%
#tabela ddi editada na mão, códigos originais no outro arquivo
ddi = pd.read_table('ddi-paises-sem-duplicadas.tab', names=['ddi', 'pais_nome', 'continente'])

# efeito colateral: remove os participantes que estão nos contatos de quem gerou o arquivo
# vai remover pelo menos quem gerou o arquivo
df_pais = df.merge(ddi, left_on='pais', right_on='ddi')


df_pais.groupby('pais_nome').size().sort_values().plot.barh(color='lightslategray')
plt.ylabel("")
plt.gca().set_title("Postagens por país", loc='left')
plt.yticks(fontsize=18);

#%% [markdown]
# É estranho ter gente fora do Brasil. Mas brasileiro está espalhado no mundo todo. Algumas das reportagens afirmam que a campanha se vale de números no exterior para não ficarem ao alcance das leis brasileiras
#%% [markdown]
# ### Números que mais postam

#%%
iiq.values[0]


#%%
num_posts = df_freq.groupby('fone').size().sort_values(ascending=False)
iiq = num_posts.quantile([.25, .5, .75]).values
outliers_limit = iiq[2] + (iiq[2] - iiq[0]) * 1.5
num_bins=30
ax = num_posts.plot.hist(bins=num_bins)
ax.set_title('Distribuição de nº postagens', loc='left')
ax.axvline(outliers_limit, linestyle='--', label="Obssessivos", color='darkred');

#%% [markdown]
# Em uma distribuição normal, quem está à direita da linha tracejada, normalmente seria considerado um outlier, isto é, um _"ponto fora da curva"_ por postar demais. Vou considerar como obsessivo apenas quem postou ainda bem mais do que os outros.

#%%
hist, _ = np.histogram(num_posts.values, bins=num_bins)
apos_buraco = False;
for i, v in enumerate(hist):
    if not apos_buraco and v == 0:
        apos_buraco = True;
    elif apos_buraco and v > 0:
        break
obsessivos_fones = num_posts[num_posts >= (num_posts.max()/num_bins * i)].index


#%%
obsessivos_mask = num_posts.index.isin(obsessivos_fones)
obsessivos = num_posts[obsessivos_mask]
cores = np.where(obsessivos_mask, 'darkblue', 'lightslategrey')

ax = num_posts.plot.bar(color=cores, width=1, edgecolor='slategrey')
ax.tick_params(labelbottom=False)
ax.grid(False)
ax.set_facecolor('white')
percentual_msgs = obsessivos.sum()/num_posts.sum()
ax.set_title("{:.0%} das mensagens postadas por {:d} usuários".format(percentual_msgs, obsessivos.size),
             loc='left')
ax.legend(["{:.0%} das postagens".format(percentual_msgs)], prop={'size': 16}, loc="center");

#%% [markdown]
# Cada coluna é um número de telefone e a altura representa quantas postagens cada um fez.
#
# Há um usuário que postou muito mais do que os outros. Foi mais que o dobro do segundo colocado.
#
# Vamos ver se os sujeitos que mais postam costumam dormir.

#%%
df_freq[df_freq.fone.isin(obsessivos.index)].    groupby(["fone", df_freq.data.dt.hour]).size().    unstack(0)    .sort_values(df_freq.sum(), axis=1, ascending=False).drop("sum")
    #.plot.line(subplots=True);
#ax.set_title('Postagem por hora dos que mais postam', loc='left');


#%%
#Função auxiliar para plotar todos histogramas de uma categoria
#linhas verticais para realçar os outliers
def show_histograms(df, ax, sharey=False):
    df_hist = df[['intervalo', 'fone']].dropna().set_index('intervalo').resample('20min').count()
    ax = df_hist.plot.bar()
    subtitle = "obsessivo"
    ax.set_title(subtitle, loc="left")

    quartiles = df.intervalo.quantile([0, .25, .75, 1])
    iqr =  quartiles.loc[.75] - quartiles.loc[.25]
    out_lower = quartiles.loc[.25] - iqr * 1.5
    out_upper = quartiles.loc[.75] + iqr * 1.5
    if out_lower > df_hist.index[0] and out_lower >= quartiles.loc[0]:
        ax.axvline(out_lower, color="darkred", linestyle='--')
    if out_upper < df_hist.index[-1] and out_upper <= quartiles.loc[1]:
        ax.axvline(out_upper, color="darkred", linestyle='--')
show_histograms(obsessivo, ['intervalo'], None)
#obsessivo[['intervalo', 'fone']].dropna().set_index('intervalo').sort_index().resample('20min').count()


#%%

ax=None

fig, axis = plt.subplots(nrows=obsessivos.size, ncols=1, sharex=True, sharey=False)
fig.subplots_adjust(hspace=.6)


for i, (fone, obsessivo) in enumerate(df[df.fone.isin(obsessivos.index)].groupby('fone')):
    obsessivo.loc[:, 'intervalo'] = (obsessivo.data - obsessivo.data.shift(1)).copy()
    #display(obsessivo[obsessivo.intervalo > pd.to_timedelta(0)].quantile([.75, .9, .95, .99]))
    show_histograms(obsessivo, ['intervalo'], axis[i])#.groupby(obsessivo.data.dt.floor(freq='H')).size()
    #print(intervalo_postagem.quantile([.75, .9, .95, .99]))
ax.legend(metade.index)
#ax.grid(xdata=pd.date_range(start=data_criacao.iat[0], end=ultimo_dia, freq='D') )
ax.set_title('Postagem por hora dos que mais postam', loc='left');


#%%
obsessivo = df[df.fone=='+55 94 9147-8106'].copy()


#%%
obsessivo['intervalo'] = obsessivo.data - obsessivo.data.shift(1)


#%%
obsessivo.sort_values('intervalo', ascending=False)

#%% [markdown]
# ### Como os administrados postam?
#
# Alguns dos administradores não estão entre os que mais postaram. Esta é uma tática para manter o grupo caso as contas de muitas postagens sejam bloqueadas. Na primeira vez que medi nenhum dos administradores estavam entre os que mais postavam, na segunda, após a eleição e o bloqueio do grupo, um deles passou a postar bastante.

#%%
#Posta muito se 95% postarem menos do que ele
posts_admin =df.merge(moderadores, on='fone').fone.value_counts().reset_index(name='num_posts')
posts_admin['Posta muito'] = posts_admin.num_posts > df.fone.value_counts().quantile(.95)
posts_admin[['num_posts', 'Posta muito']]


#%%
#mais complicado do que deveria
num_dias_posts_admins =   len(df[df.data > data_criacao.iat[0]]      .merge(moderadores, on='fone')      .groupby(['fone', df[df.data > data_criacao.iat[0]].data.dt.date])      .size()      .reset_index()      .data      .unique())

printBig('{:d} dias com posts dos admins'.format(num_dias_posts_admins))

#%% [markdown]
# No dia 15 de outubro, que foi o dia em que entrei no grupo, neste dia os administradores postavam à beça, mas subtamente pararam. Por que?
#%% [markdown]
# ### Postagem por estado

#%%
df_ddd = pd.DataFrame(columns=["Prefixo", "Estado", "Principais cidades(capitais em negrito)"],
                      data=[
                        ["11", "São Paulo", "São Paulo/Guarulhos/São Bernardo do Campo/Santo André/Osasco/Jundiaí"],
                        ["12", "São Paulo", "São José dos Campos/Taubaté/Jacareí/Guaratinguetá"],
                        ["13", "São Paulo", "Santos/São Vicente/Praia Grande/Cubatão/Itanhaém/Peruíbe/Registro"],
                        ["14", "São Paulo", "Bauru/Jaú/Marília/Lençóis Paulista/Lins/Botucatu/Ourinhos/Avaré"],
                        ["15", "São Paulo", "Sorocaba/Itapetininga/Itapeva"],
                        ["16", "São Paulo", "Ribeirão Preto/Franca/Araraquara"],
                        ["17", "São Paulo", "São José do Rio Preto/Barretos/Fernandópolis"],
                        ["18", "São Paulo", "Presidente Prudente/Araçatuba/Birigui/Assis"],
                        ["19", "São Paulo", "Campinas/Piracicaba/Limeira/Americana/Sumaré"],
                        ["21", "Rio de Janeiro", "Rio de Janeiro/Niterói/São Gonçalo/Duque de Caxias/Nova Iguaçu"],
                        ["22", "Rio de Janeiro", "Campos dos Goytacazes/Macaé/Cabo Frio/Nova Friburgo"],
                        ["24", "Rio de Janeiro", "Volta Redonda/Barra Mansa/Petrópolis"],
                        ["27", "Espírito Santo", "Vitória/Serra/Vila Velha/Linhares"],
                        ["28", "Espírito Santo", "Cachoeiro de Itapemirim"],
                        ["31", "Minas Gerais", "Belo Horizonte/Contagem/Betim"],
                        ["32", "Minas Gerais", "Juiz de Fora/Barbacena"],
                        ["33", "Minas Gerais", "Governador Valadares/Teófilo Otoni/Caratinga/Manhuaçu"],
                        ["34", "Minas Gerais", "Uberlândia/Uberaba/Araguari/Araxá"],
                        ["35", "Minas Gerais", "Passos/Poços de Caldas/Pouso Alegre/Varginha/Itajubá"],
                        ["37", "Minas Gerais", "Divinópolis/Itaúna/Formiga/Capitólio"],
                        ["38", "Minas Gerais", "Montes Claros/Serro/Januária"],
                        ["41", "Paraná", "Curitiba/São José dos Pinhais/Paranaguá"],
                        ["42", "Paraná", "Ponta Grossa/Castro/União da Vitória"],
                        ["43", "Paraná", "Londrina/Arapongas/Assaí/Jacarezinho/Jandaia do Sul"],
                        ["44", "Paraná", "Maringá/Campo Mourão/Astorga"],
                        ["45", "Paraná", "Cascavel/Toledo/Medianeira"],
                        ["46", "Paraná", "Francisco Beltrão/Pato Branco/Palmas/Pinhão"],
                        ["47", "Santa Catarina", "Joinville/Blumenau/Balneário Camboriú"],
                        ["48", "Santa Catarina", "Florianópolis/São José/Criciúma"],
                        ["49", "Santa Catarina", "Chapecó/Lages/Concórdia"],
                        ["51", "Rio Grande do Sul", "Porto Alegre/Canoas/Esteio/Torres"],
                        ["53", "Rio Grande do Sul", "Pelotas/Rio Grande/Bagé/Aceguá/Chuí"],
                        ["54", "Rio Grande do Sul", "Caxias do Sul/Vacaria/Veranópolis"],
                        ["55", "Rio Grande do Sul", "Santa Maria/Uruguaiana/Santana do Livramento"],
                        ["61", "Distrito Federal", "Brasília"],
                        ["62", "Goiás", "Goiânia/Anápolis/Goiás/Pirenópolis"],
                        ["63", "Tocantins", "Palmas/Araguaína/Gurupi"],
                        ["64", "Goiás", "Rio Verde/Jataí/Caldas Novas/Catalão"],
                        ["65", "Mato Grosso", "Cuiabá/Várzea Grande/Cáceres"],
                        ["66", "Mato Grosso", "Rondonópolis/Sinop/Barra do Garças"],
                        ["67", "Mato Grosso do Sul", "Campo Grande/Dourados/Corumbá/Três Lagoas"],
                        ["68", "Acre", "Rio Branco/Cruzeiro do Sul"],
                        ["69", "Rondônia", "Porto Velho/Ji-Paraná/Ariquemes"],
                        ["71", "Bahia Bahia", "Salvador/Camaçari/Lauro de Freitas"],
                        ["73", "Bahia Bahia", "Itabuna/Ilhéus/Porto Seguro/Jequié"],
                        ["74", "Bahia Bahia", "Juazeiro/Xique-Xique"],
                        ["75", "Bahia Bahia", "Feira de Santana/Alagoinhas/Lençóis"],
                        ["77", "Bahia Bahia", "Vitória da Conquista/Barreiras/Correntina"],
                        ["79", "Sergipe", "Aracaju/Lagarto/Itabaiana"],
                        ["81", "Pernambuco", "Recife/Jaboatão dos Guararapes/Goiana/Gravatá/Paulista"],
                        ["82", "Alagoas", "Maceió/Arapiraca/Palmeira dos Índios/Penedo"],
                        ["83", "Paraíba", "João Pessoa/Campina Grande/Patos/Sousa/Cajazeiras"],
                        ["84", "Rio Grande do Norte", "Natal/Mossoró/Parnamirim/Caicó"],
                        ["85", "Ceará", "Fortaleza/Caucaia/Russas/Maracanaú"],
                        ["86", "Piauí", "Teresina/Parnaíba/Piripiri/Campo Maior/Barras"],
                        ["87", "Pernambuco", "Petrolina/Salgueiro/Arcoverde"],
                        ["88", "Ceará", "Juazeiro do Norte/Crato/Sobral/Itapipoca/Iguatu/Quixadá"],
                        ["89", "Piauí", "Picos/Floriano/Oeiras/São Raimundo Nonato/Corrente"],
                        ["91", "Pará", "Belém/Ananindeua/Castanhal/Abaetetuba/Bragança"],
                        ["92", "Amazonas", "Manaus/Iranduba/Parintins/Itacoatiara/Maués/Borba"],
                        ["93", "Pará", "Santarém/Altamira/Oriximiná/Itaituba/Jacareacanga"],
                        ["94", "Pará", "Marabá/Tucuruí/Parauapebas/Redenção/Santana do Araguaia"],
                        ["95", "Roraima", "Boa Vista/Rorainópolis/Caracaraí/Alto Alegre/Mucajaí"],
                        ["96", "Amapá", "Macapá/Santana/Laranjal do Jari/Oiapoque/Calçoene"],
                        ["97", "Amazonas", "Tefé/Coari/Tabatinga/Manicoré/Humaitá/Lábrea"],
                        ["98", "Maranhão", "São Luís/São José de Ribamar/Paço do Lumiar/Pinheiro/Santa Inês"],
                        ["99", "Maranhão", "Imperatriz/Caxias/Timon/Codó/Açailândia"]
                      ])


#%%
df['estado'] = df.merge(df_ddd, left_on='uf', right_on='Prefixo')['Estado']


#%%
uf = df.groupby(['estado']).size().sort_values(ascending=False).reset_index(name="Posts por estado")
printBig('{:d} dos 26 estados postaram'.format(uf.index.size))


#%%
uf.set_index('estado')

#%% [markdown]
# ### Quem divulga mais links para assinar outros grupos

#%%



#%%


#%% [markdown]
#
#
# ### Links indicados
#
#%% [markdown]
# ## Nuvem de palavras

