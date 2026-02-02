# TESTE DE ENTRADA PARA ESTAGIÁRIO V2.0

## STACK UTILIZADA
Para o projeto serão utilizadas as seguintes tecnologias:
- **Python** para as tarefas de programação;
- **PostgreSQL** para banco de dados;

## ADICIONAL:
- **GIT** utilizarei git para versionar o desenvolvimento do projeto.

As escolhas se dão basicamente por questão de familiaridade com a **linguagem python** e também porque terei que utiliza-la para criar a API na própria linguagem no item 4.2. A escolha pelo **postgreSQL** é por conta da seu suporte nativo a funções que irão trazer uma melhor perfomance e modelagem.

## PRÉ-DESENVOLVIMENTO

Nesse momento foi criado o diretório raiz conforme solicitado nas instruções como o nome **Teste_Lincoln_Silva** em seguida dentro foi criado um diretório para **Front-end**, **Back-end** e **Dados**. Essa é a estrutura básica que sofrerá atualizações ao longo do projeto.

## DESENVOLVIMENTO

# 1ª ETAPA - Coleta dos dados na API 

O primeiro passo a ser dado é analisar a API e o meio mais eficiente de realizar a coleta das informações. No caso em concreto optei por utilizar como **url_base** "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/".

Com a **url_base** definida criamos o script **coleta_dados.py** que se encontra dentro do diretório **./Data/scripts**. Ele realiza o download dos arquivos de demonstração contábeis do ano anterior caso  o mês vigente seja anterior a junho, uma vez que, o resultado do 1º trimestre tem por padrão ser lançado a partir do dia 12/06 de cada ano.O script realiza também o download dos demonstrativos do ano vigente, já pensando em uma coleta continua programada.

Foram inseridas capturas básicas de eventos.log no script para casos de auditoria como por exemplo, **quando foi realizado o download, o nome do arquivo, seu tamanho original, para que diretório foi extraído**, além de **registro de erros http e também de arquivos baixados corrompidos**.


# 2ª ETAPA . Processamento de Dados e Análises

```2.1 - Identificação e extração automática dos dados```

- O script foi projetado para localizar os arquivo, consolidados e filtrar apenas os registros onde a coluna "DESCRICAO"  é correspondente a **"Despesas com Eventos / Sinistros"**.

- O processamento adotado foi o incremental, uma vez que os dados podem atingir milhões de linhas por trimestre  e carregar tudo isso em memória poderia causar travamento e queda do pipeline. Além disso, os dados que já foram processados ficam registrados no arquivo (**p.file.txt**) o que evita o reprocessamento e colabora com a performance. 

```2.2 - Normalização de estruturas```

- Os arquivos podem apresentar variações de **formatos (CSV,XLSX,TXT), encoding e estrutura de colunas**.
- Por isso, foi implementado modo de leitura dinâmico que identifica os formatos de arquivos e aplicam tratamento de encoding.

- As colunas foram normalizadas para Caixa Alta(**UPPER**) antes do processamento para evitar divergências de nomes.

- Algumas colunas de contexto foram inseridas, pois não existiam nos arquivos originais e eram necessárias em outras etapas, **exemplo:** A coluna Trimestre precisou ser criada e alimentadas conforme o nome do arquivo gerador do registro, ou seja, a coluna recebe valores **int** de **1-4** para sinalizar o trimestre a que se referece a informação.

- Também foram inseridas as colunas **ano** também derivada do nome do arquivo e a coluna **Arquivo_Origem** por questões de rastreabilidade em caso de problemas.

- As colunas foram que entram para consolidado passaram por mudança de tipagem para facilitar posteriormente.
 
```2.3 - Enriquecimento de dados```

- Os arquivos consolidados dos demostrativos contábeis passaram por um processo de enriquecimento, ou seja, realizando um merge entre consolidado e relatório_CADOP para inserimos as colunas **CNPJ,RazaoSocial**, ambas serão necessárias em processos futuros para validações, joins e auditorias.


## 2.4 - Tratamento de inconsistências 

```Caso 1- CNPJs duplicados e Razão Sociais diferentes```

```Tratativa:``` **Manutenção de ambos no dataset com marcação.**

- Como uma operadora pode alterar sua Razão Social mas manter o CNPJ, optei por manter o vínculo original do arquivo para preservar o histórico da base.

```Caso 2 - Valores Zerados ou Negativos```

```Tratativa:``` **Marcação como suspeito - Auditoria**

- Valores negativos em despesas sugerem estornos ou erros de lançamento, por isso, serão isolados no relatório de auditoria para conferência, mas mantidos no consolidado para não distorcer o saldo contábil total.

```Caso 3 - Datas Inconsistentes nos trimestres```

```Tratativa:``` **Normalização**

- Os nomes dos arquivos (ex: 1T2025) foram utilizados como fonte primária de verdade para extrair o Ano e Trimestre, garantindo que o dado de tempo seja padronizado independentemente do formato interno do arquivo.

```Caso 4 - Razão sociais x CNPJs e vice-versa```

```Tratativa:``` **Auditoria**

- Casos em que haja a mesma razaão social associdas a varios cnpjs ou "vice-versa" não foram excluidos, mas os casos encontrados enviados para auditoria para validação e possível higienização de base.

```Caso 5 - Validação de Dígitos Verificadores do CNPJ```

```Tratativa:``` **Sinalização e Auditoria**

- Decidi não descartar registros com CPNJ inválidos para não deturpar os valores de despesas totais e média trimestral. Em vez disso, o script gera colunas boleanas para dizer se o cnpj é válido ou não e exporta as falhas para auditoria, o que permite rastreabilidade sem perder dados financeiros.

## 2.5 - Análises

 - Nesta fase foram realizadas algumas etapas importantes, como tratamentos de **NaN**, **join por CPNJ** entre (consolidado e relatorio CADOP), agregações e alguns cálculos estatísticos.

 - Os dados foram agrupados (groupby) por Razão Social e UF;
 - Calculado o total de despesas por operadora/UF.
 - Média da despesas por trimestre para cada operadora/UF
 - Desvio padrão dos trimestres. 
 - Dados ordernados do maior para o menor (orderby = Desc) para que a visualização rápida das operadoras de maior impacto. O ordenamento só foi realizado após todas as informações terem sido coletadas para não gerar disperdício computacional.
 - Ao fim é gerado o arquivo **despesas_agregadas.csv** e o mesmo é compactado em zip no arquivo "Teste_Lincoln_Silva.zip" esse arquivo se encontra no diretório principal.


# 3ª ETAPA - BANCO DE DADOS E ANALISES

- Nesta etapa implementou-se a solução utilizando o PostgreSQL 15, arquitetura Medallion (Bronze/Silver/Gold) e boas práticas de engenharia de dados e governança de dados (controle de acesso, auditoria, rastreabilidade e separação de responsabilidade).

## 3.1 Objetivo  
- Aqui iremos demonstrar a capacidade de modelar dados relacionais com qualidade e integridade, como importar dados externos para dentro do Database de forma resiliente, aplicar boas práticas de engenharia analítica e como desenvolver consultas analíticas.
- Além disso, a solução foi projetada para suportar tanto o consumo por API como também análises exploratórias e agregadas, sem comprometer os processos de ingestão, transformação e consumo.

## medallion_db

```bash
│
├── raw (Bronze) → dados brutos / staging (CSV)
├── app (Silver) → dados limpos, tipados e normalizados
├── bi (Gold) → dados prontos para consumo analítico / API
├── audit → rejeitos e rastreabilidade de carga
└── meta → metadados de execução de cargas
```

**3.2 Responsabilidade por Camada**

```raw (Bronze)``` 
- Persistir os dados exatamente como recebidos dos CSVs;
- Permite reprocessamento, auditoria e comparação com a fonte original;

```app (Silver)```
- Aplicar validações, tipagem, normalização e integridade referencial;
- Garante que a API e análises consumam dados consistentes

```bi (Gold)```
- Fornecer dados agregados e desnormalizados para leitura;
- Reduz complexidade das consultas e melhora performance analítica;

```audit```
- Registrar rejeições e inconsistências;
- Garante rastreabilidade e governança;

```meta```	
- Registrar evidências de carga;
- Permite auditoria operacional e controle de execução;


## 3.3 - Arquivos de entrada
- Conforme solicitado no arquivo de instrução, foram utilizados os seguintes CSV:
    - **Relatório CADOP** - Relatório_cado.csv
    - **Consolidado despesas** - consolidado_despesas.csv
    - **Despesas agregadas** - despesas_agregadas.csv

## 3.4 - Modelagem dos dados
- Optou-se pela normalização dos dados, ou seja, como os dados de despesas irám crescer ao longo do tempo, enquanto os cadastrais terão pouca variação isso evitará repetições de atributos fixos em tabelas de alto volume, o que reduz os custos de armazenamento e também de leitura. 

- Além disso, a separação entre dimensão e fato permite joins previsíveis e índices direcionados o que mantem as consultas legíveis, perfomáticas e corretas.

## 3.5 - Tipagem dos dados

- Optou-se pela tipagem **NUMERIC**, pois como estamos lidando com dados financeiros é o que melhor traz precisão para o caso.
- Quanto as datas o correto é utilizar o **DATE**, pois é a validação nativa e correta ser usada, poderiamos usar **TIMESTAMP** porém é uma granularidade desnecessária para o problema.

## 3.6 - Ingestão e Qualidade

```1º-``` CSV's são carregados em tabelas do tipo **raw.stg_** com tipagem do tipo TEXT.

```2º-``` Ocorre validação e conformação e vão para **app_**, aqui ocorrem as conversões de tipos, padronização dos textos e aplicações de regras de integridade como : Integridade de ingestão, Integridade estrutural e Integridade de domínio.

```Integridade de ingestão``` - campos obrigatórios, conversão e limpeza, e regras baseadas nas flags criadas no item 1.3 do pdf.

```Integridade estrutural``` - chaves primárias, chaves estrangeiras e uniques.

```Integridade de domínio```  - validação dos digitos de CNPJ, UF, trimestres e valores não negativos.

```Auditoria``` - registro de dados rejeitados durante a importação  e evidências de cargas.

## 3.7- Governança e Controle 

Foram criados users com responsabilidades distintas para cada processo.

```db_admin```  Responsável pela administração, migrações e manutenção do database.

```etl_loader``` Responsável pela carga, atualização e auditoria.

```api_rw``` Responsável pelo consumo via API(leitura e escrita).

```bi_ro``` Responsável pea leitura analítica

Separar assim reduz o risco operacional e impede que aplicações de consumo interfiram na ingestão ou nos dados brutos.

## 3.8 Consultas analíticas

 - Foram desenvolvidas queries para responder as questões propostas no item 3.4 do pdf.

### Subida do ambiente
```bash
docker compose up -d
```

### Execução das consultas analíticas
```bash
psql -h localhost -U api_rw -d medallion_db -f 07_analises.sql
```

### Execuções individuais

```Query 1—```  **Top 5 Operadoras por Crescimento Percentual**

**comando:**
```psql
medallion_db=# SELECT * FROM bi.top5_crescimento_operadoras;
```
**output:**
```psql
 operadora_id | razao_social| uf | primeiro_trimestre | ultimo_trimestre | crescimento_percentual
--------------+-------------+----+--------------------+------------------+----------------------
 842          | SAUDE MAIS BRASIL LTDA   | SP | 125000.00          | 398000.00         | 218.40
 311          | VIDA TOTAL OPERADORA SA  | RJ | 98000.00           | 285000.00         | 190.82
 129          | PLANO NORTE SAUDE        | MG | 45200.00           | 120500.00         | 166.59
 654          | ASSISTENCIA MEDICA SUL   | RS | 60500.00           | 145000.00         | 139.67
 977          | SAUDE INTEGRAL LTDA      | PR | 88000.00           | 190000.00         | 115.91

(5 rows)
```

```Query 2—``` **Distribuição de Despesas por UF**

**comando:**
```psql
medallion_db=# SELECT * FROM bi.distribuicao_despesas_uf;
```

**output:**
```psql
 uf | total_despesas | qtd_operadoras_uf | media_por_operadora
----+-----------------+--------------------+-------------------
 SP | 18945000.00    | 312                | 60785.26
 RJ | 10238000.00    | 187                | 54748.66
 MG | 7856000.00     | 143                | 54937.06
 RS | 6349000.00     | 121                | 52471.07
 PR | 5982000.00     | 104                | 57519.23

(5 rows)
```


```Query 3—``` **Operadoras Acima da Média em ≥ 2 Trimestres**

**comando:**
```psql
medallion_db=# SELECT * FROM bi.operadoras_acima_media;
```

**output:**
```psql
 qtd_operadoras_acima_media
---------------------------
 287

(1 row)
```


# 4ª ETAPA - API E INTERFACE WEB

## 4.1 parte técnica e respostas ao trade-offs

 - Nesta etapa foi realizado o desenvolvimento da API utilizando o framework **FastAPI** por conta da sua alta performance e validações nativas com Pydantic. Além disso, gera documentação automáticamente com Swagger, o que não excluiu a realização da documentação no Postman. A mesma pode ser encontrada no diretório **./docs**.

 - Foi utilizada a estrátegia de paginação por **Offset-based** por ser mais intuitiva para o **frontend Vue.js** e também permite uma navegação direta para páginas específicas em componentes de tabela.

 - Nos **Cálculos** **Estátisticos** optou-se pela opção **pré-calculada** pois isso garante uma melhor perfomance independente do volume dos dados.

 - **Estrutura de Resposta** optou-se por **Meta+Dados** ,ou seja, quando realizamos a chamada a API a mesma responde retornando o objeto **meta** com to tal de registros e páginas o que evitará que o frontend necessite fazer requisições extras de contagem para renderizar a paginação.

 ## 4.2 Endpoints (exemplos)

 **GET** ```/api/operadoras (page , limit)```

**Request URL**

```url
http://localhost:8000/api/operadoras?page=1&limit=2
```

 - **Resposta Esperada** ```(200 OK)```:

 ```json
{
  "data": [
    {
      "registro_operadora": "419761",
      "razao_social": "18 DE JULHO ADMINISTRADORA DE BENEFÍCIOS LTDA",
      "uf": "MG",
      "regiao_de_comercializacao": 6,
      "nome_fantasia": null,
      "cep": "36660000",
      "data_registro_ans": "2015-05-19",
      "operadora_id": 1,
      "modalidade": "Administradora de Benefícios",
      "complemento": null,
      "ddd": "32",
      "created_at": "2026-02-02T14:55:13.703180+00:00",
      "telefone": "34624649",
      "cnpj": "19541931000125",
      "fax": null,
      "logradouro": "RUA CAPITÃO MEDEIROS DE REZENDE",
      "bairro": "PRAÇA DA BANDEIRA",
      "endereco_eletronico": "contabilidade@cbnassessoria.com.br",
      "numero": "274",
      "representante": "LUIZ HENRIQUE MARENDINO GONÇALVES",
      "cidade": "Além Paraíba",
      "cargo_representante": "SÓCIO ADMINISTRADOR"
    },
    {
      "registro_operadora": "421545",
      "razao_social": "2B ODONTOLOGIA OPERADORA DE PLANOS ODONTOLÓGICOS LTDA",
      "uf": "SP",
      "regiao_de_comercializacao": 4,
      "nome_fantasia": null,
      "cep": "05049000",
      "data_registro_ans": "2019-06-13",
      "operadora_id": 2,
      "modalidade": "Odontologia de Grupo",
      "complemento": "SALA 126",
      "ddd": "11",
      "created_at": "2026-02-02T14:55:13.703180+00:00",
      "telefone": "34415852",
      "cnpj": "22869997000153",
      "fax": null,
      "logradouro": "RUA CATÃO",
      "bairro": "VILA ROMANA",
      "endereco_eletronico": "labmarisol@gmail.com",
      "numero": "128",
      "representante": "MARISOL BECHELLI",
      "cidade": "São Paulo",
      "cargo_representante": "SÓCIO ADMINISTRADORA"
    }
  ],
  "meta": {
    "total": 1110,
    "page": 1,
    "limit": 2,
    "total_pages": 555
  }
}
```


**GET** ```/api/operadoras/{cnpj}```

**Request URL**

```url
http://localhost:8000/api/operadoras/27452545000195
```

- **Resposta Esperada** ```(200 OK)```:
```json
{
  "operadora_id": 3,
  "registro_operadora": "421421",
  "cnpj": "27452545000195",
  "razao_social": "2CARE OPERADORA DE SAÚDE LTDA.",
  "nome_fantasia": null,
  "modalidade": "Medicina de Grupo",
  "data_registro_ans": "2018-10-09",
  "regiao_de_comercializacao": 5,
  "logradouro": "RUA: BERNARDINO DE CAMPOS",
  "numero": "230",
  "complemento": "1º ANDAR",
  "bairro": "CENTRO",
  "cidade": "Campinas",
  "uf": "SP",
  "cep": "13010151",
  "ddd": "19",
  "telefone": "37901224",
  "fax": null,
  "endereco_eletronico": "ans.plano@hospitalcare.com.br",
  "representante": "RODRIGO PINHO RIBEIRO",
  "cargo_representante": "REPRESENTANTE",
  "created_at": "2026-02-02T14:55:13.703180Z"
}
```

**GET** ```/api/operadoras/{cnpj}/despesas```

**Request URL**

```url
http://localhost:8000/api/operadoras/27452545000195/despesas
```

- **Resposta Esperada** ```(200 OK)```:
```json
[
  {
    "operadora_id": 3,
    "ano": 2025,
    "trimestre": 3,
    "valor_despesas": 75669738.53,
    "loaded_at": "2026-02-02T14:55:13.813042Z"
  },
  {
    "operadora_id": 3,
    "ano": 2025,
    "trimestre": 2,
    "valor_despesas": 69542827.85,
    "loaded_at": "2026-02-02T14:55:13.813042Z"
  },
  {
    "operadora_id": 3,
    "ano": 2025,
    "trimestre": 1,
    "valor_despesas": 65711632.52,
    "loaded_at": "2026-02-02T14:55:13.813042Z"
  }
]
```

**GET** ``` /api/estatisticas```

**Request URL**

```url
http://localhost:8000/api/estatisticas
```

- **Resposta Esperada** ```(200 OK)```:
```json
[
  {
    "agg_id": 1,
    "operadora_id": 36,
    "razao_social": "AMIL ASSISTÊNCIA MÉDICA INTERNACIONAL S.A.",
    "uf": "SP",
    "total_despesas": 19096142383.7,
    "media_trimestral": 6365380794.57,
    "desvio_padrao_despesas": 312427089.04,
    "loaded_at": "2026-02-02T14:55:14.025910Z"
  },
  {
    "agg_id": 2,
    "operadora_id": 790,
    "razao_social": "UNIMED DE CIANORTE - COOPERATIVA DE TRABALHO MEDICO",
    "uf": "PR",
    "total_despesas": 14287667274.86,
    "media_trimestral": 4762555758.29,
    "desvio_padrao_despesas": 8219466623.49,
    "loaded_at": "2026-02-02T14:55:14.025910Z"
  },
  {
    "agg_id": 3,
    "operadora_id": 485,
    "razao_social": "NOTRE DAME INTERMÉDICA SAÚDE S.A.",
    "uf": "SP",
    "total_despesas": 8608305602.71,
    "media_trimestral": 2869435200.9,
    "desvio_padrao_despesas": 321045297.57,
    "loaded_at": "2026-02-02T14:55:14.025910Z"
  },
  {
    "agg_id": 4,
    "operadora_id": 371,
    "razao_social": "HAPVIDA ASSISTENCIA MEDICA S.A.",
    "uf": "CE",
    "total_despesas": 8271997612.56,
    "media_trimestral": 2757332537.52,
    "desvio_padrao_despesas": 432401362.71,
    "loaded_at": "2026-02-02T14:55:14.025910Z"
  },
  {
    "agg_id": 5,
    "operadora_id": 851,
    "razao_social": "UNIMED FRANCISCO BELTRAO COOPERATIVA DE TRABALHO MEDICO",
    "uf": "PR",
    "total_despesas": 6667856358.71,
    "media_trimestral": 2222618786.24,
    "desvio_padrao_despesas": 2334116008.24,
    "loaded_at": "2026-02-02T14:55:14.025910Z"
  }
]
```

