# Monitoramento Inteligente da Saúde da Mulher - MISM

> Plataforma de visualização e análise de dados da Saúde da Mulher para apoio à tomada de decisões e à elaboração de políticas públicas.

## 📋 Sobre o Projeto

O **MISM** é uma solução tecnológica desenvolvida para apoiar a análise, organização e visualização de informações relacionadas à saúde das mulheres.

A plataforma tem como objetivo transformar dados em informações visuais e acessíveis, permitindo identificar regiões com maior vulnerabilidade e apoiar gestores e profissionais na tomada de decisões.

O projeto está relacionado à iniciativa da **Secretaria da Mulher / Observatório da Mulher** do município de Rio Claro (SP) e propõe a criação de uma plataforma capaz de integrar dados de saúde, realizar o tratamento e a anonimização das informações e apresentar indicadores por meio de mapas e dashboards interativos.

---

## 🎯 Objetivos

O projeto busca:

* Facilitar a análise dos dados relacionados à saúde das mulheres;
* Apoiar a criação de políticas públicas direcionadas;
* Identificar regiões e áreas com maior vulnerabilidade;
* Reduzir retrabalho na organização das informações;
* Melhorar o acompanhamento dos indicadores de saúde;
* Disponibilizar visualizações claras para gestores e profissionais;
* Garantir a privacidade e a proteção dos dados utilizados.

---

## 🗺️ Principais Funcionalidades

### 📊 Dashboard de Indicadores

A plataforma contará com um painel para visualização dos principais indicadores relacionados à saúde da mulher.

Entre os indicadores apresentados estão:

* Câncer de mama
* Comparação entre estados e regiões;
* Filtros por período;
* Indicadores regionais.

---

### 🌎 Mapa Interativo

O sistema contará com um mapa interativo para a visualização geográfica do município de Rio Claro (SP) com dados relacionados à saúde da mulher.

As funcionalidades incluem:

* Visualização por bairros do município de Rio Claro (SP)
* Mapa de calor (*choropleth*);
* Exibição de indicadores por localização;
* Tooltips com informações consolidadas;
* Seleção dinâmica de indicadores;
* Visualização detalhada dos dados do município

O objetivo é permitir a identificação de regiões com maiores índices de vulnerabilidade e auxiliar na análise da distribuição dos indicadores de saúde.

---

### 🧹 Tratamento e Higienização dos Dados

Antes de serem utilizados na plataforma, os dados passam por processos de tratamento e validação.

Entre as atividades previstas estão:

* Remoção ou tratamento de registros nulos;
* Identificação de valores inconsistentes;
* Padronização das informações;
* Validação dos dados;
* Organização dos datasets para análise;
* Otimização do armazenamento das informações.

---

### 🔒 Privacidade e LGPD

A proteção das informações é um dos principais pilares do projeto.

O sistema prevê mecanismos para garantir a privacidade dos dados, incluindo:

* Remoção de identificadores pessoais;
* Proteção contra exposição de informações sensíveis;
* Agregação geográfica dos dados;
* Prevenção de reidentificação;
* Validação da ausência de informações pessoais identificáveis;
* Conformidade com os princípios da LGPD.

---

## 🏗️ Arquitetura Geral

```text
                FONTES DE DADOS
                       │
                       ▼
        ┌──────────────────────────┐
        │  Ingestão dos Dados      │
        │  SIM / SINASC / etc.     │
        └──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │ Higienização e Validação │
        └──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │ Anonimização e LGPD      │
        └──────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │ Base de Dados Sanitizada │
        └──────────────────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
    ┌────────────────┐  ┌────────────────┐
    │ API / Back-End │  │ Análise de Dados│
    └────────────────┘  └────────────────┘
             │
             ▼
    ┌────────────────────────┐
    │ Dashboard e Mapa       │
    │ Interativo             │
    └────────────────────────┘
```

---

## 🛠️ Tecnologias Utilizadas

O projeto utiliza ou prevê a utilização de tecnologias voltadas ao processamento, análise e visualização de dados.

### Back-End e Dados

* Python;
* Pandas;
* Polars;
* APIs para disponibilização dos dados;
* Processamento de dados geoespaciais.

### Front-End e Visualização

* React;
* Plotly;
* Folium;
* Streamlit ou Dash;
* GeoJSON;
* SVG.

### Qualidade

* Testes unitários;
* Testes de usabilidade;
* Testes de responsividade;
* Revisão de código e Pull Requests.

---

## 📁 Estrutura do Projeto

```text
escudo-feminino/
│
├── src/
│   ├── app/
│   │   └── main.py
│   │
│   ├── components/
│   │   └── MapContainer.jsx
│   │
│   ├── data/
│   │   └── ingestao_saude_mulher.py
│   │
│   └── security/
│       └── anonymizer.py
│
├── tests/
│   ├── test_ingestao.py
│   └── ...
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│
├── README.md
└── requirements.txt
```

---

## 👥 Equipe

| Integrante                 | Função            |
| -------------------------- | ----------------- |
| **Kauê Lima**              | Product Owner     |
| **Thiago Plancke**         | Scrum Master      |
| **Gabriel do Nascimento**  | Back-End          |
| **Brendol Alves**          | Back-End          |
| **Vladimir Sejas**         | Analista de Dados |
| **Mateus Linardi Bianchi** | Testes            |

---

## 🔐 Privacidade e Segurança

Este projeto trabalha com informações relacionadas à saúde e, portanto, a proteção dos dados é fundamental.

Nenhuma informação pessoal identificável deve ser disponibilizada publicamente.

Os dados utilizados devem passar por processos de:

* Anonimização;
* Agregação;
* Validação;
* Controle de acesso;
* Proteção de informações sensíveis.

---

## 📈 Visão do Produto

O **MISM** busca transformar dados complexos em informações acessíveis e úteis para gestores, profissionais e instituições públicas.

Por meio de mapas, dashboards e indicadores, a plataforma pretende contribuir para uma melhor compreensão da realidade da saúde das mulheres e apoiar decisões baseadas em dados.

A proposta é oferecer uma ferramenta que facilite a identificação de padrões, desigualdades regionais e possíveis áreas de atenção, contribuindo para o desenvolvimento de políticas públicas mais direcionadas e eficazes.

---

## 📌 Status do Projeto

🚧 **Em desenvolvimento**

O projeto encontra-se em desenvolvimento, com foco na construção de uma plataforma capaz de integrar, tratar, proteger e visualizar dados relacionados à saúde da mulher.

---

## 🤝 Contribuição

As contribuições para o projeto devem seguir boas práticas de desenvolvimento:

1. Criar uma branch para a funcionalidade;
2. Desenvolver e testar a implementação;
3. Criar um Pull Request;
4. Solicitar revisão de outro integrante;
5. Realizar os ajustes necessários;
6. Integrar a funcionalidade após aprovação.

---

## 📄 Licença

Projeto acadêmico desenvolvido para fins educacionais e para a construção de soluções tecnológicas voltadas à análise e visualização de dados sobre a Saúde da Mulher.
