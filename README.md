# PROJETO SAUDE E GESTAO

## 🛠️ Stack Tecnológica

### Backend

* **Python 3.11**
* **FastAPI**
* **SQLAlchemy**
* **PostgreSQL 15**

### Frontend

* **Vue 3 (Composition API)**
* **Vite**
* **Pinia**
* **ECharts / vue-echarts**
* **Axios**

### Infra

* **Docker**
* **Docker Compose**

### Versionamento

* **GIT/GITHUB**

## 📁 Estrutura do Projeto

```
.
├── backend
│   ├── API
│   └── SQL
├── Data
│   ├── logs
│   ├── processed
│   ├── raw
│   ├── references
│   └── scripts
├── docker-compose.yml
├── Dockerfile
├── docs
│   └── Saude_e_Gestao.postman_collection.json
├── frontend
│   ├── Dockerfile
│   ├── index.html
│   ├── nginx.conf
│   ├── node_modules
│   ├── package.json
│   ├── package-lock.json
│   ├── public
│   ├── README.md
│   ├── src
│   └── vite.config.js
├── main.py
├── README.md
└── requirements.txt
```

# DESENVOLVIMENTO - ENGENHARIA DE DADOS

## 1ª ETAPA - Coleta dos dados na API 

O primeiro passo a ser dado é analisar a API e o meio mais eficiente de realizar a coleta das informações. No caso em concreto optei por utilizar como **url_base** "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/".

Com a **url_base** definida criamos o script **coleta_dados.py** que se encontra dentro do diretório **./Data/scripts**. Ele realiza o download dos arquivos de demonstração contábeis do ano anterior caso  o mês vigente seja anterior a junho, uma vez que, o resultado do 1º trimestre tem por padrão ser lançado a partir do dia 12/06 de cada ano.O script realiza também o download dos demonstrativos do ano vigente, já pensando em uma coleta continua programada.

Foram inseridas capturas básicas de eventos.log no script para casos de auditoria como por exemplo, **quando foi realizado o download, o nome do arquivo, seu tamanho original, para que diretório foi extraído**, além de **registro de erros http e também de arquivos baixados corrompidos**.


## 2ª ETAPA . Processamento de Dados e Análises

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


## 3ª ETAPA - BANCO DE DADOS E ANALISES

- Nesta etapa implementou-se a solução utilizando o PostgreSQL 15, arquitetura Medallion (Bronze/Silver/Gold) e boas práticas de engenharia de dados e governança de dados (controle de acesso, auditoria, rastreabilidade e separação de responsabilidade).

## 3.1 Objetivo  
- Aqui iremos demonstrar a capacidade de modelar dados relacionais com qualidade e integridade, como importar dados externos para dentro do Database de forma resiliente, aplicar boas práticas de engenharia analítica e como desenvolver consultas analíticas.
- Além disso, a solução foi projetada para suportar tanto o consumo por API como também análises exploratórias e agregadas, sem comprometer os processos de ingestão, transformação e consumo.

## 📌 Visão Geral da Arquitetura

```
[CSV / Dados Brutos]
        ↓
   Pipeline (Python)
        ↓
   PostgreSQL (RAW)
        ↓
   PostgreSQL (SILVER / APP)
        ↓
   API (FastAPI)
        ↓
   Frontend (Vue + Vite)
```

### Camadas:

* **RAW** → Dados brutos importados
* **SILVER / APP** → Dados tratados e normalizados
* **GOLD / BI** → Dados prontos para serem consumidos por BI (Opicional)
* **API** → Exposição dos dados via endpoints REST
* **Frontend** → Visualização interativa (tabela, mapas, rankings e gráficos)

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


### Execução das consultas analíticas
```bash
psql -h localhost -U api_rw -d medallion_db -f 07_analises.sql
```

### Execuções individuais

```Query 1—```  **Top 5 Operadoras por Crescimento Percentual**

**Desafio:**
``` 
R: Para as operadoras que não possuem dados em pelomenos 2 trimestres foram retiradas e serão contempladas quando possuirem mais informação.
```  

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

**Desafio:**
``` 
R: Foi utilizada CTEs com FILTER e COUNT condicional, combinando:

1 - CTE media_tri: Calcula a média de despesas por trimestre

2 - CTE acima_media: Para cada operadora, conta quantos trimestres estão acima da média

3 - Consulta final: Conta operadoras com ≥ 2 trimestres acima da média

```  

**comando:**
```psql
medallion_db=# SELECT * FROM bi.operadoras_acima_media;
```
```sql
media_tri AS (
  SELECT
    ano,
    trimestre,
    AVG(valor_operadora) AS media_trimestre
  FROM operadora_tri
  GROUP BY ano, trimestre
),
acima_media AS (
  SELECT
    o.operadora_id,
    COUNT(*) FILTER (
      WHERE o.valor_operadora > m.media_trimestre
    ) AS qtd_trimestres_acima
  FROM operadora_tri o
  JOIN media_tri m
    ON m.ano = o.ano
   AND m.trimestre = o.trimestre
  GROUP BY o.operadora_id
)
SELECT
  COUNT(*) AS operadoras_acima_em_pelo_menos_2_trimestres
FROM acima_media
WHERE qtd_trimestres_acima >= 2;
```

**output:**
```psql
 qtd_operadoras_acima_media
---------------------------
 287

(1 row)
```


# 4ª ETAPA - API E INTERFACE WEB - FULLSTACK

## 🧩 Funcionalidades

### Backend / API

* Listagem paginada de operadoras
* Busca global por **Razão Social** ou **CNPJ**
* Filtro: apenas operadoras com despesas
* Histórico trimestral por operadora
* Estatísticas nacionais por UF
* Ranking Top 5 nacional
* Ranking Top 5 por estado (UF)

## 4.1 parte técnica e respostas ao trade-offs

 - Nesta etapa foi realizado o desenvolvimento da API utilizando o framework **FastAPI** por conta da sua alta performance e validações nativas com Pydantic. Além disso, gera documentação automáticamente com Swagger, o que não excluiu a realização da documentação no Postman. A mesma pode ser encontrada no diretório **./docs**.

 - Foi utilizada a estrátegia de paginação por **Offset-based** por ser mais intuitiva para o **frontend Vue.js** e também permite uma navegação direta para páginas específicas em componentes de tabela.

 - Nos **Cálculos Estátisticos** optou-se pela opção **pré-calculada** pois isso garante uma melhor perfomance independente do volume dos dados.

 - **Estrutura de Resposta** optou-se por **Meta+Dados** ,ou seja, quando realizamos a chamada a API a mesma responde retornando o objeto **meta** com to tal de registros e páginas o que evitará que o frontend necessite fazer requisições extras de contagem para renderizar a paginação.

 ## 4.2 Endpoints (exemplos)

### Lista de Operadoras

```http
GET /api/operadoras?page=1&limit=10&q=amil&has_despesas=true
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


### Detalhe da Operadora

```http
GET /api/operadoras/{cnpj}
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

### Histórico de despesas por operadora

```http
GET /api/operadoras/{cnpj}/despesas
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

### Estatísticas Nacionais - TOP 5 maiores despesas do país

```http
GET /api/estatisticas
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
### Mapa interativo - despesas/UF

```http
GET /api/estatisticas/uf
```

- **Resposta Esperada** ```(200 OK)```:
```json
[
  {
    "uf": "SC",
    "total": 5313651681.77
  },
  {
    "uf": "RS",
    "total": 6353323934.91
  },
  {
    "uf": "DF",
    "total": 14974288439.09
  },
  {
    "uf": "MG",
    "total": 11075543815.71
  },
  {
    "uf": "RN",
    "total": 436679006.11
  },
  {
    "uf": "SP",
    "total": 80367805381.5
  }
]
``` 

### Top 5 por Estado

```http
GET /api/estatisticas/uf/{UF}
```

- **Resposta Esperada** ```(200 OK)```:
```json
{
  "uf": "SC",
  "total_uf": 5313651681.77,
  "top5": [
    {
      "operadora_id": 856,
      "razao_social": "UNIMED GRANDE FLORIANÓPOLIS-COOPERATIVA DE TRABALHO MEDICO",
      "cnpj": "77858611000108",
      "total": 973797633.6
    },
    {
      "operadora_id": 840,
      "razao_social": "UNIMED DO ESTADO DE SANTA CATARINA FED. EST. DAS COOP. MÉD.",
      "cnpj": "76590884000143",
      "total": 645875455.25
    },
    {
      "operadora_id": 873,
      "razao_social": "UNIMED LITORAL COOPERATIVA DE TRABALHO MÉDICO LTDA",
      "cnpj": "85377174000120",
      "total": 638027144.91
    },
    {
      "operadora_id": 801,
      "razao_social": "UNIMED DE JOINVILLE COOPERATIVA DE TRABALHO MÉDICO",
      "cnpj": "82602327000106",
      "total": 560041417.88
    },
    {
      "operadora_id": 746,
      "razao_social": "UNIMED BLUMENAU - COOPERATIVA DE TRABALHO MEDICO",
      "cnpj": "82624776000147",
      "total": 527965290.3
    }
  ]
}
``` 

## 4.3 Interface Web

### Trade-offs técnicos

**Estratégia de Busca/Filtro**

```Opção A``` - Busca no servidor - O volume alto de informação por conta de todas as operadoras iria aumentar o tempo de carregamento e uso de memória e não é escalável.

**Gerenciamento de Estado**

```Opção B``` - Vuex/Pinia - A aplicação tem estado compartilhado entre múltiplos componentes e páginas: lista paginada, meta de paginação, busca atual, toggle “somente com dados”, seleção de operadora, despesas, etc. O pinia irá fornecer ações assincronas, fluxos previsível e estado centralizado, isso vem acoplado a dependências e alguma estrutura extra mas reduz a complexidade conforme a aplicação cresce.

**Performance da Tabela**

- A estratégia adota foi a de paginação no lado do servidor e renderização limitada por páginas para evitar renderizar milhares de linhas ao mesmo tempo, deste modo a tabela fica mais rápida e estável, request menores. O usuário navega por página ao invés de scroll.


**Tratamento de Erros e Loading**

```Erros de rede/API``` - Centralizado no http.js, padronização do erro em um shape simplista **status**,**mensagem**, **raw** o que evita duplicar lógia de erro em cada componente e garante maior consistência.

```Estados de Loading```- O store expõe a flag **loadingList**, **loadingStats**, etc. A UI utiliza componentes de estado (UIState) com orvelay o que melhora a experiência do usuário.

```Dados Vazios``` - Quando a busca nao retorna resultados a tabela mostra o  contéudo vazio com mensagem específica **Nenhum resultado encontrado** em caso de falta de contexto mensagem genéricas como **"falha Inesperada"**, isso melhora a taxa de resolução do lado do cliente sem necessidade de logs.


## 🧩 Funcionalidades

### Frontend

* Tabela paginada com:

  * Busca server-side
  * Seleção visual da linha
  * Filtro "Somente com dados"
* Mapa de calor do Brasil por despesas (UF)
* Painel interativo por estado (Top 5 do estado)
* Gráfico trimestral por operadora
* Indicador de status da API (online/offline)

## 4.4 Como Utilizar!

## ⚙️ Pré-requisitos

* Docker
* Docker Compose
* Node.js 18+ (apenas para desenvolvimento local do frontend)

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Usuários
POSTGRES_USER=sg
API_USER=sg
ETL_USER=sg
BI_USER=sg

#Passwords
POSTGRES_PASSWORD=sg
API_PASSWORD=sg
ETL_PASSWORD=sg
BI_PASSWORD=sg

#Informações DB
POSTGRES_DB=sg_db
HOST=db
PORTA=5432
```


## 🐳 Subindo o Ambiente (Docker)

Na raiz do projeto, execute:

```bash
docker compose up -d --build
```

Fluxo automático:

1. Banco PostgreSQL sobe
2. Pipeline executa
3. Importação RAW
4. Processamento SILVER / APP
5. API sobe

A API estará disponível em:

```
http://localhost:8000
```

---

## 🌐 Rodando o Frontend

### Modo Desenvolvimento

```bash
cd frontend
npm install
npm run dev
```

Acesse:

```
http://localhost:5173
```

### Modo Produção (Docker + Nginx)

> (Opcional), caso deseje empacotar o frontend no container

O frontend usa:

```env
VITE_API_BASE_URL=/api
```

E o Nginx faz proxy para o container da API.


## 📊 Funcionalidades Visuais

* 🗺️ **Mapa de Calor por UF**

  * Mostra despesas totais por estado
  * Clique em um estado para abrir painel lateral com Top 5 operadoras

* 📈 **Histórico Trimestral**

  * Exibido ao selecionar uma operadora na tabela

* 🏆 **Ranking Nacional**

  * Top 5 operadoras por despesas no Brasil

---

## ⚡ Performance

Índices importantes no banco:

```sql
CREATE INDEX operadoras_uf_idx ON app.operadoras (uf);
CREATE INDEX operadoras_razao_idx ON app.operadoras USING btree (razao_social);
CREATE INDEX despesas_operadora_idx ON app.despesa_consolidada (operadora_id);
```

---

## 🧪 Debug & Logs

### Ver logs da API

```bash
docker compose logs api
```

### Ver logs do banco

```bash
docker compose logs db
```



## 👤 Autor

Projeto desenvolvido por **Lincoln Silva**


