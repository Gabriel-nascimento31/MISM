import asyncio
from pathlib import Path
import pandas as pd
from pysus import PySUS

ANOS = [2021, 2022, 2023, 2024, 2025]
ESTADO = "SP"
COD_IBGE_RIO_CLARO = "354390"  # código de 6 dígitos usado pelo DATASUS
RAIZ_PROJETO = Path(__file__).resolve().parents[2]
PASTA_DESTINO = RAIZ_PROJETO / "dados" / "brutos"

# Codificação padrão do DATASUS para a coluna SEXO no SIH/SUS:
# 1 = Masculino, 3 = Feminino, 0/9 = Ignorado
VALORES_ESPERADOS_SEXO = {"1", "3", "0", "9"}
VALOR_FEMININO = "3"


def checar_valores_sexo(df, arquivo_nome):
    """Confere se os valores da coluna SEXO batem com o esperado.
    Se aparecer algo fora do padrão, avisa bem visivelmente."""
    valores_encontrados = set(df["SEXO"].astype(str).str.strip().unique())
    inesperados = valores_encontrados - VALORES_ESPERADOS_SEXO
    if inesperados:
        print("\n" + "!" * 60)
        print(f"ATENÇÃO: valores inesperados na coluna SEXO em {arquivo_nome}")
        print(f"Valores encontrados: {valores_encontrados}")
        print("Filtro de sexo pode estar incorreto. Revise antes de confiar no resultado.")
        print("!" * 60 + "\n")


async def main():
    PASTA_DESTINO.mkdir(parents=True, exist_ok=True)
    dados_consolidados = []
    primeiro_arquivo_checado = False

    async with PySUS() as pysus:
        for ano in ANOS:
            print("\n" + "=" * 60)
            print(f"CONSULTANDO SIH/SUS SP - ANO {ano}")
            print("=" * 60)

            try:
                arquivos = await pysus.query(
                    dataset="sih",
                    group="RD",  # AIH Reduzida = internações hospitalares
                    state=ESTADO,
                    year=ano,
                )
            except Exception as e:
                print(f"  ERRO ao consultar o ano {ano}: {e}")
                continue

            if not arquivos:
                print(f"Nenhum arquivo retornado para o ano {ano}.")
                continue

            print(f"Total de arquivos mensais encontrados: {len(arquivos)}")

            for arquivo in arquivos:
                print(f"Baixando: {arquivo.path}")
                try:
                    local = await pysus.download(arquivo)
                    df = pd.read_parquet(local.path)
                except Exception as e:
                    print(f"  -> Falhou ao baixar/ler este arquivo: {e}")
                    continue

                colunas_necessarias = {"DIAG_PRINC", "MUNIC_RES", "SEXO"}
                if not colunas_necessarias.issubset(df.columns):
                    faltando = colunas_necessarias - set(df.columns)
                    print(f"  -> Arquivo sem as colunas {faltando}, pulando.")
                    continue

                # Só confere os valores de SEXO uma vez, no primeiro arquivo,
                # pra não poluir o terminal
                if not primeiro_arquivo_checado:
                    checar_valores_sexo(df, arquivo.path)
                    primeiro_arquivo_checado = True

                # Filtro 1: Neoplasia Maligna da Mama (CID-10 C50) como diagnóstico principal
                mascara_cid = (
                    df["DIAG_PRINC"]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                    .str.startswith("C50")
                )

                # Filtro 2: Moradoras de Rio Claro (código IBGE 354390)
                mascara_rc = (
                    df["MUNIC_RES"]
                    .astype(str)
                    .str.strip()
                    .str.startswith(COD_IBGE_RIO_CLARO)
                )

                # Filtro 3: Sexo feminino
                mascara_sexo = (
                    df["SEXO"].astype(str).str.strip() == VALOR_FEMININO
                )

                df_mama_rc_mulheres = df[mascara_cid & mascara_rc & mascara_sexo].copy()

                if not df_mama_rc_mulheres.empty:
                    print(f"  -> {len(df_mama_rc_mulheres)} internações encontradas neste arquivo.")
                    dados_consolidados.append(df_mama_rc_mulheres)

    if dados_consolidados:
        df_final = pd.concat(dados_consolidados, ignore_index=True)
        caminho_csv = PASTA_DESTINO / "cancer_mama_mulheres_rio_claro_2021_2025.csv"

        df_final.to_csv(caminho_csv, index=False, sep=";", encoding="utf-8-sig")

        print("\n" + "=" * 60)
        print("DOWNLOAD E FILTRAGEM FINALIZADOS COM SUCESSO!")
        print(f"Total de internações de mulheres de Rio Claro coletadas: {len(df_final)}")
        print(f"Arquivo salvo em CSV: {caminho_csv}")
        print("=" * 60)
    else:
        print("\nNenhum registro correspondente foi localizado no período.")


if __name__ == "__main__":
    asyncio.run(main())