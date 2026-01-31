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


# 2ª ETAPA . Processamento de Dados e Análises

**2.1 - Identificação e extração automática dos dados**
- O script foi projetado para localizar os arquivo, consolidados e filtrar apenas os registros onde a coluna "DESCRICAO"  é correspondente a **"Despesas com Eventos / Sinistros"**.

- O processamento adotado foi o incremental, uma vez que os dados podem atingir milhões de linhas por trimestre  e carregar tudo isso em memória poderia causar travamento e queda do pipeline. Além disso, os dados que já foram processados ficam registrados no arquivo (**p.file.txt**) o que evita o reprocessamento e colabora com a performance. 

**2.2 - Normalização de estruturas**

- Os arquivos podem apresentar variações de **formatos (CSV,XLSX,TXT), encoding e estrutura de colunas**.
- Por isso, foi implementado modo de leitura dinamico que identifica os formatos de arquivos e aplicam tratamento de encoding.

- As colunas foram normalizadas para Caixa Alta(**UPPER**) antes do processamento para evitar divergências de nomes.

- Algumas colunas de contexto foram inseridas, pois não existiam nos arquivos originais e eram necessárias em outras etapas, **exemplo:** A coluna Trimestre precisou ser criada e alimentadas conforme o nome do arquivo gerador do registro, ou seja, a coluna recebe valores **int** de **1-4** para sinalizar o trimestre a que se referece a informação.

- Também foram inseridas as colunas **ano** também derivada do nome do arquivo e a coluna **Arquivo_Origem** por questões de rastreabilidade em caso de problemas.

- As colunas foram que entram para consolidado passaram por mudança de tipagem para facilitar posteriormente.
 
**2.3 - Enriquecimento de dados**
- Os arquivos consolidados dos demostrativos contábeis passaram por um processo de enriquecimento, ou seja, realizando um merge entre consolidado e relatório_CADOP para inserimos as colunas **CNPJ,RazaoSocial**, ambas serão necessárias em processos futuros para validações, joins e auditorias.


**2.4 - Tratamento de inconsistências** 

**Caso 1- CNPJs duplicados e Razão Sociais diferentes**
**Tratativa:** Manutenção de ambos no dataset com marcação.
    - Como uma operadora pode alterar sua Razão Social mas manter o CNPJ, optei por manter o vínculo original do arquivo para preservar o histórico da base.

**Caso 2 - Valores Zerados ou Negativos**
**Tratativa:** Marcação como suspeito - Auditoria
    - Valores negativos em despesas sugerem estornos ou erros de lançamento, por isso, serão isolados no relatório de auditoria para conferência, mas mantidos no consolidado para não distorcer o saldo contábil total.

**Caso 3 - Datas Inconsistentes nos trimestres**
**Tratativa:** Normalização
    - Os nomes dos arquivos (ex: 1T2025) foram utilizados como fonte primária de verdade para extrair o Ano e Trimestre, garantindo que o dado de tempo seja padronizado independentemente do formato interno do arquivo.

**Caso 4 - Razão sociais x CNPJs e vice-versa**
**Tratativa:** Auditoria
    - Casos em que haja a mesma razaão social associdas a varios cnpjs ou "vice-versa" não foram excluidos, mas os casos encontrados enviados para auditoria para validação e possível higienização de base.

**Caso 5 - Validação de Dígitos Verificadores do CNPJ**
**Tratativa:** Sinalização e Auditoria
    - Decidi não descartar registros com CPNJ inválidos para não deturpar os valores de despesas totais e média trimestral. Em vez disso, o script gera colunas boleanas para dizer se o cnpj é valido ou nao e exporta as falhas para auditoria, o que permite rastreabilidade sem perder dados financeiros.

**2.5 - Análises**

 - Nesta fase foram realizadas algumas etapas importantes, como tratamentos de **NaN**, **join por CPNJ** entre (consolidado e relatorio CADOP), agregações e alguns cálculos estatísticos.

 - Os dados foram agrupados (groupby) por Razão Social e UF;
 - Calculado o total de despesas por operadora/UF.
 - Média da despesas por trimestre para cada operadora/UF
 - Desvio padrão dos trimestres. 
 - Dados ordernados do maior para o menor (orderby = Desc) para que a visualização rápida das operadoras de maior impacto. O ordenamento só foi realizado após todas as informações terem sido coletadas para não gerar disperdício computacional.
 - Ao fim é gerado o arquivo **despesas_agregadas.csv** e o mesmo é compactado em zip no arquivo "Teste_Lincoln_Silva.zip" esse arquivo se encontra no diretório principal.







