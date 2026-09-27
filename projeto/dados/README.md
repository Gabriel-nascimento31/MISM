# Dados

- `brutos/`: base de internações recebida da etapa de coleta.
- `processados/`: base georreferenciada e camadas usadas diretamente pelo mapa.
- `referencia/`: limites geográficos de apoio.
- `cache/`: respostas de CEP reutilizadas no georreferenciamento.
- `fontes/`: material temporário baixado do IBGE, criado apenas quando for necessário reextrair a referência de bairros.

Não exponha a base bruta ou o cache publicamente: eles podem conter informação de localização associada a internações.

`processados/clusters_por_bairro_validacao.csv` é a tabela de auditoria das
posições dos clusters. Linhas sem latitude/longitude não são desenhadas no
mapa, para evitar que um bairro seja colocado em uma localização inventada.
