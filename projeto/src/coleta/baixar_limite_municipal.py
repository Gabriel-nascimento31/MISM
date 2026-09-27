"""Baixa o limite municipal de Rio Claro (SP) da API de Malhas do IBGE."""

from pathlib import Path

import requests


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
SAIDA = RAIZ_PROJETO / "dados" / "referencia" / "municipio_rio_claro.geojson"
URL_IBGE = "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3543907?formato=application/vnd.geo+json"


def main():
    print("Baixando limite municipal de Rio Claro (SP) pela API de Malhas do IBGE...")
    resposta = requests.get(URL_IBGE, timeout=30)
    resposta.raise_for_status()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(resposta.text, encoding="utf-8")
    print(f"Limite municipal salvo em: {SAIDA}")


if __name__ == "__main__":
    main()