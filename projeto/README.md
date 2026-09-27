# Mapa de internações por câncer de mama — Rio Claro (SP)

Projeto para coletar, georreferenciar e visualizar internações de moradoras de Rio Claro entre 2021 e 2025.

## Como gerar o mapa

Com as dependências de `requirements.txt` instaladas, execute a partir da raiz do projeto:

```powershell
python src/processamento/georreferenciar_dados.py
python src/processamento/gerar_clusters_bairro.py
python src/visualizacao/gerar_mapa.py
```

O arquivo final é salvo em `saidas/mapa_rio_claro_cancer_mama.html` e carrega
externamente `saidas/bairros_rio_claro_21_bairros.geojson`, a malha oficial de
21 bairros usada pelo mapa.
Antes de gerar o mapa, confira `dados/processados/clusters_por_bairro_validacao.csv`.
Ela registra os casos e a coordenada usada por cada cluster, obtida do CEP e
de geocodificação OpenStreetMap, sem usar a posição dos polígonos do mapa.

## Estrutura

- `src/`: scripts organizados pelas etapas de coleta, processamento e visualização.
- `dados/`: entradas, resultados processados, referências geográficas e cache.
- `saidas/`: artefatos prontos para abrir ou compartilhar.

Consulte os READMEs de cada pasta para detalhes. Os marcadores do mapa são agregados por bairro para evitar a concentração artificial de CEPs no centro da cidade.
