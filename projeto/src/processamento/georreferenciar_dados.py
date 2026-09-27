import asyncio
import json
from pathlib import Path
import httpx
import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parents[2]

ARQUIVOS_CSV_ENTRADA = [
    (RAIZ_PROJETO / "dados" / "brutos" / "cancer_mama_mulheres_rio_claro_2021_2025.csv", "Câncer de Mama"),
    (RAIZ_PROJETO / "dados" / "brutos" / "cancer_colo_utero_mulheres_rio_claro_2021_2025.csv", "Câncer do Colo do Útero"),
    (RAIZ_PROJETO / "dados" / "brutos" / "cancer_colorretal_mulheres_rio_claro_2021_2025.csv", "Câncer Colorretal"),
    (RAIZ_PROJETO / "dados" / "brutos" / "cancer_ovario_mulheres_rio_claro_2021_2025.csv", "Câncer de Ovário"),
    (RAIZ_PROJETO / "dados" / "brutos" / "cancer_pele_nao_melanoma_mulheres_rio_claro_2021_2025.csv", "Câncer de Pele (Não Melanoma)"),
    (RAIZ_PROJETO / "dados" / "brutos" / "cancer_pulmao_mulheres_rio_claro_2021_2025.csv", "Câncer de Pulmão"),
    (RAIZ_PROJETO / "dados" / "brutos" / "cancer_tireoide_mulheres_rio_claro_2021_2025.csv", "Câncer de Tireoide"),
]

ARQUIVO_CSV_SAIDA = RAIZ_PROJETO / "dados" / "processados" / "saude_mulher_rio_claro_georreferenciado.csv"
CACHE_FILE = RAIZ_PROJETO / "dados" / "cache" / "ceps_rio_claro.json"

LAT_RIO_CLARO = -22.4149
LON_RIO_CLARO = -47.5614

LAT_MIN, LAT_MAX = -22.60, -22.20
LON_MIN, LON_MAX = -47.80, -47.35


def carregar_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def coordenada_valida(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX
    except (ValueError, TypeError):
        return False


async def buscar_cep(client, cep_str, cache, sem):
    if cep_str in cache and cache[cep_str].get("lat") is not None:
        return cache[cep_str]

    resultado = {
        "cep": cep_str,
        "logradouro": "",
        "bairro": "",
        "lat": None,
        "lon": None,
        "fonte": None,
    }

    async with sem:
        # 1. BrasilAPI
        try:
            r = await client.get(f"https://brasilapi.com.br/api/cep/v2/{cep_str}", timeout=7.0)
            if r.status_code == 200:
                data = r.json()
                resultado["logradouro"] = data.get("street") or ""
                resultado["bairro"] = data.get("neighborhood") or ""
                coords = data.get("location", {}).get("coordinates", {})
                lat, lon = coords.get("latitude"), coords.get("longitude")
                if lat and lon and coordenada_valida(lat, lon):
                    resultado["lat"] = float(lat)
                    resultado["lon"] = float(lon)
                    resultado["fonte"] = "BrasilAPI"
        except Exception:
            pass

        # 2. AwesomeAPI
        if resultado["lat"] is None:
            try:
                r = await client.get(f"https://cep.awesomeapi.com.br/json/{cep_str}", timeout=7.0)
                if r.status_code == 200:
                    data = r.json()
                    if not resultado["bairro"]:
                        resultado["bairro"] = data.get("district") or ""
                    if not resultado["logradouro"]:
                        resultado["logradouro"] = data.get("address") or ""
                    lat, lon = data.get("lat"), data.get("lng")
                    if lat and lon and coordenada_valida(lat, lon):
                        resultado["lat"] = float(lat)
                        resultado["lon"] = float(lon)
                        resultado["fonte"] = "AwesomeAPI"
            except Exception:
                pass

        # 3. ViaCEP
        if not resultado["bairro"]:
            try:
                r = await client.get(f"https://viacep.com.br/ws/{cep_str}/json/", timeout=6.0)
                if r.status_code == 200:
                    data = r.json()
                    resultado["bairro"] = data.get("bairro") or ""
                    resultado["logradouro"] = resultado["logradouro"] or data.get("logradouro") or ""
            except Exception:
                pass

        # 4. OSM / Nominatim
        if resultado["lat"] is None and resultado["bairro"]:
            try:
                bairro_clean = resultado["bairro"].split("-")[0].strip()
                query = f"{bairro_clean}, Rio Claro, SP, Brasil"
                r = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": query, "format": "json", "limit": 1},
                    headers={"User-Agent": "RioClaroHealthAnalysisApp/1.0"},
                    timeout=6.0,
                )
                if r.status_code == 200 and r.json():
                    item = r.json()[0]
                    lat, lon = item["lat"], item["lon"]
                    if coordenada_valida(lat, lon):
                        resultado["lat"] = float(lat)
                        resultado["lon"] = float(lon)
                        resultado["fonte"] = "OSM_Bairro"
            except Exception:
                pass

        # 5. Fallback Centro de Rio Claro
        if resultado["lat"] is None:
            h = hash(cep_str) % 1000
            jitter_lat = ((h % 50) - 25) * 0.0003
            jitter_lon = (((h // 50) % 50) - 25) * 0.0003
            resultado["lat"] = round(LAT_RIO_CLARO + jitter_lat, 6)
            resultado["lon"] = round(LON_RIO_CLARO + jitter_lon, 6)
            resultado["fonte"] = "Centro_RioClaro"
            if not resultado["bairro"]:
                resultado["bairro"] = "Rio Claro (Geral)"

        cache[cep_str] = resultado
        return resultado


async def main():
    print("Iniciando georreferenciamento de todas as bases de Saúde da Mulher...")
    dfs = []
    for caminho, doenca in ARQUIVOS_CSV_ENTRADA:
        if caminho.exists():
            df_temp = pd.read_csv(caminho, sep=";", dtype={"CEP": str})
            df_temp["DOENCA"] = doenca
            dfs.append(df_temp)
            print(f"- Lidos {len(df_temp)} registros de {doenca}")
        else:
            print(f"- Aviso: Arquivo não encontrado em {caminho}")

    if not dfs:
        print("Nenhum arquivo CSV encontrado!")
        return

    df = pd.concat(dfs, ignore_index=True)
    df["CEP_NORMALIZADO"] = (
        df["CEP"]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
        .str.zfill(8)
    )

    ceps_unicos = df["CEP_NORMALIZADO"].unique()
    print(f"\nTotal de registros combinados: {len(df)}")
    print(f"Total de CEPs únicos: {len(ceps_unicos)}")

    ARQUIVO_CSV_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    cache = carregar_cache()

    sem = asyncio.Semaphore(6)
    async with httpx.AsyncClient(headers={"User-Agent": "RioClaroGeoApp/1.0"}) as client:
        tasks = [
            buscar_cep(client, cep, cache, sem)
            for cep in ceps_unicos
            if cep not in cache or cache[cep].get("lat") is None
        ]

        if tasks:
            print(f"Consultando {len(tasks)} novos CEPs no geocodificador...")
            for i in range(0, len(tasks), 30):
                chunk_tasks = tasks[i : i + 30]
                await asyncio.gather(*chunk_tasks)
                salvar_cache(cache)
                await asyncio.sleep(1.0)

    salvar_cache(cache)

    df["LATITUDE"] = df["CEP_NORMALIZADO"].map(lambda c: cache.get(c, {}).get("lat"))
    df["LONGITUDE"] = df["CEP_NORMALIZADO"].map(lambda c: cache.get(c, {}).get("lon"))
    df["BAIRRO"] = df["CEP_NORMALIZADO"].map(
        lambda c: cache.get(c, {}).get("bairro", "") or "Não informado"
    )
    df["LOGRADOURO"] = df["CEP_NORMALIZADO"].map(
        lambda c: cache.get(c, {}).get("logradouro", "")
    )
    df["FONTE_GEO"] = df["CEP_NORMALIZADO"].map(
        lambda c: cache.get(c, {}).get("fonte", "")
    )

    df["IDADE_ANOS"] = pd.to_numeric(df["IDADE"], errors="coerce")
    df["ANO_INTERNACAO"] = df["DT_INTER"].astype(str).str[:4]
    df["VAL_TOT_NUM"] = pd.to_numeric(
        df["VAL_TOT"].astype(str).str.replace(",", "."), errors="coerce"
    )

    df.to_csv(ARQUIVO_CSV_SAIDA, sep=";", index=False, encoding="utf-8-sig")
    print(f"\nArquivo final unificado salvo em: {ARQUIVO_CSV_SAIDA}")


if __name__ == "__main__":
    asyncio.run(main())