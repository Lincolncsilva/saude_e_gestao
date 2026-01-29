# TESTE DE ENTRADA PARA ESTAGIÁRIO V2.0

## STACK UTILIZADA
Para o projeto serão utilizadas as seguintes tecnologias:
- **Python** para as tarefas de programação;
- **PostgreSQL** para banco de dados;

## ADICIONAL:
- **GIT** utilizarei git para versionar o desenvolvimento do projeto.

As escolhas se dão basicamente por questão de familiaridade com a **linguagem python** e também porque terei que utiliza-la para criar a API na própria linguagem no item 4.2. A escolha pelo **postgreSQL** é por conta da seu suporte nativo para funções a analíticas como  window functions e materialized views o que irá trazer uma melhor perfomance e modelagem.

## PRÉ-DESENVOLVIMENTO

Nesse momento foi criado o diretório raiz conforme solicitado nas instruções como o nome **Teste_Lincoln_Silva** em seguida dentro foi criado um diretório para **Front-end**, **Back-end** e **Dados**. Essa é a estrutura básica que sofrerá atualizações ao longo do projeto.

## DESENVOLVIMENTO

# 1ª ETAPA - Coleta dos dados na API 

O primeiro passo a ser dado é analisar a API e o meio mais eficiente de realizar a coleta das informações. No caso em concreto optei por utilizar como **url_base** "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/".

Com a **url_base** definida criamos o script **coleta_dados.py** que se encontra dentro do diretório **./Data/scripts**. Ele realiza o download dos arquivos de demonstração contábeis do ano anterior caso  o mês vigente seja anterior a junho, uma vez que, o resultado do 1º trimestre tem por padrão ser lançado a partir do dia 12/06 de cada ano.O script realiza também o download dos demonstrativos do ano vigente, já pensando em uma coleta continua programada.

Foram inseridas capturas básicas de eventos.log no script para casos de auditoria como por exemplo, **quando foi realizado o download, o nome do arquivo, seu tamanho original, para que diretório foi extraído**, além de **registro de erros http e também de arquivos baixados corrompidos**.



