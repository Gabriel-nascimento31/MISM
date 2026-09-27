import json
from pathlib import Path
import pandas as pd

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CSV_PATH = RAIZ_PROJETO / "dados" / "processados" / "saude_mulher_rio_claro_georreferenciado.csv"
BAIRROS_GEOJSON_FILENAME = "bairros_rio_claro_21_bairros.geojson"
MUNICIPIO_GEOJSON_PATH = RAIZ_PROJETO / "dados" / "referencia" / "municipio_rio_claro.geojson"
CLUSTERS_BAIRRO_PATH = RAIZ_PROJETO / "dados" / "processados" / "clusters_por_bairro.json"
HTML_OUTPUT_PATH = RAIZ_PROJETO / "saidas" / "mapa_rio_claro_saude_mulher.html"


def main():
    HTML_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Lendo dados de {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH, sep=";")

    df["LATITUDE"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
    df["IDADE_ANOS"] = pd.to_numeric(df["IDADE_ANOS"], errors="coerce").fillna(0).astype(int)
    df["ANO_INTERNACAO"] = df["ANO_INTERNACAO"].astype(str).str[:4]
    df["VAL_TOT_NUM"] = pd.to_numeric(df["VAL_TOT_NUM"], errors="coerce").fillna(0.0)
    df["DIAS_PERM"] = pd.to_numeric(df["DIAS_PERM"], errors="coerce").fillna(0).astype(int)
    df["MORTE"] = df["MORTE"].astype(str).str.strip() == "1"

    dicionario_cid = {
        # Câncer de Mama
        "C500": "Mamilo e aréola",
        "C501": "Porção central da mama",
        "C502": "Quadrante superior interno",
        "C503": "Quadrante inferior interno",
        "C504": "Quadrante superior externo",
        "C505": "Quadrante inferior externo",
        "C506": "Porção axilar da mama",
        "C508": "Lesão invasiva da mama",
        "C509": "Mama, não especificado",
        # Câncer do Colo do Útero
        "C530": "Endocérvix",
        "C531": "Ectocérvix",
        "C538": "Lesão invasiva do colo do útero",
        "C539": "Colo do útero, não especificado",
        # Câncer Colorretal
        "C180": "Ceco",
        "C181": "Apêndice",
        "C182": "Cólon ascendente",
        "C184": "Cólon transverso",
        "C185": "Flexura esplênica",
        "C187": "Cólon sigmóide",
        "C188": "Lesão invasiva do cólon",
        "C189": "Cólon, não especificado",
        "C19": "Junção retossigmóide",
        "C20": "Reto",
        # Câncer de Ovário
        "C56": "Ovário",
        # Câncer de Pele (Não Melanoma)
        "C440": "Pele dos lábios",
        "C441": "Pele da pálpebra",
        "C443": "Pele de outras partes do rosto",
        "C444": "Pele do couro cabeludo e pescoço",
        "C446": "Pele do membro superior",
        "C447": "Pele do membro inferior",
        "C448": "Lesão invasiva da pele",
        "C449": "Pele, não especificado",
        # Câncer de Pulmão
        "C340": "Brônquio principal",
        "C341": "Lóbulo superior (brônquio/pulmão)",
        "C342": "Lóbulo médio (brônquio/pulmão)",
        "C343": "Lóbulo inferior (brônquio/pulmão)",
        "C348": "Lesão invasiva dos brônquios e pulmão",
        "C349": "Brônquio ou pulmão, não especificado",
        # Câncer de Tireoide
        "C73": "Glândula tireóide",
    }

    records = []
    for _, row in df.iterrows():
        if pd.isna(row["LATITUDE"]) or pd.isna(row["LONGITUDE"]):
            continue

        diag = str(row.get("DIAG_PRINC", "")).strip()
        doenca = str(row.get("DOENCA", "Câncer de Mama")).strip()
        descricao_cid = dicionario_cid.get(diag, "Neoplasia maligna")

        records.append({
            "cep": str(row["CEP_NORMALIZADO"]),
            "bairro": str(row["BAIRRO"]).strip(),
            "logradouro": str(row["LOGRADOURO"]).strip() if pd.notna(row["LOGRADOURO"]) else "",
            "lat": round(float(row["LATITUDE"]), 6),
            "lng": round(float(row["LONGITUDE"]), 6),
            "idade": int(row["IDADE_ANOS"]),
            "ano": str(row["ANO_INTERNACAO"]),
            "valor": round(float(row["VAL_TOT_NUM"]), 2),
            "dias": int(row["DIAS_PERM"]),
            "morte": bool(row["MORTE"]),
            "cid": diag,
            "cid_desc": descricao_cid,
            "doenca": doenca,
        })

    total_internacoes = len(records)
    idade_media = round(sum(r["idade"] for r in records) / total_internacoes, 1) if total_internacoes else 0
    custo_total = round(sum(r["valor"] for r in records), 2)
    bairros_unicos = len(set(r["bairro"] for r in records if r["bairro"]))

    with open(MUNICIPIO_GEOJSON_PATH, "r", encoding="utf-8") as f:
        municipio_geojson = json.load(f)

    with open(CLUSTERS_BAIRRO_PATH, "r", encoding="utf-8") as f:
        clusters_bairro = json.load(f)

    json_records = json.dumps(records, ensure_ascii=False)
    json_municipio_geojson = json.dumps(municipio_geojson, ensure_ascii=False)
    json_clusters_bairro = json.dumps(clusters_bairro, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rio Claro (SP) - Saúde da Mulher - Mapa de Internações (2021-2025)</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    
    <!-- Phosphor Icons -->
    <script src="https://unpkg.com/@phosphor-icons/web"></script>

    <style>
        :root {{
            --bg-dark: #090d16;
            --surface-dark: rgba(15, 23, 42, 0.90);
            --surface-card: rgba(30, 41, 59, 0.78);
            --border-glass: rgba(255, 255, 255, 0.12);
            --border-accent: rgba(244, 63, 94, 0.45);
            
            --brand-pink: #f43f5e;
            --brand-pink-gradient: linear-gradient(135deg, #fb7185 0%, #e11d48 50%, #9f1239 100%);
            
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            --radius-lg: 18px;
            --radius-md: 12px;
            --radius-sm: 8px;
            --shadow-glass: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: var(--bg-dark);
            color: var(--text-primary);
        }}

        #map {{
            width: 100%;
            height: 100%;
            z-index: 1;
        }}

        .sidebar {{
            position: absolute;
            top: 16px;
            left: 16px;
            bottom: 16px;
            width: 450px;
            max-width: calc(100vw - 32px);
            background: var(--surface-dark);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-glass);
            z-index: 1000;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .sidebar.collapsed {{
            transform: translateX(-470px);
        }}

        .sidebar-header {{
            padding: 22px 24px;
            background: linear-gradient(180deg, rgba(244, 63, 94, 0.18) 0%, transparent 100%);
            border-bottom: 1px solid var(--border-glass);
            position: relative;
        }}

        .badge-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(244, 63, 94, 0.22);
            border: 1px solid rgba(244, 63, 94, 0.45);
            color: #fca5a5;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
        }}

        .badge-pill i {{
            font-size: 14px;
            color: #fb7185;
        }}

        .sidebar-header h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 22px;
            font-weight: 700;
            line-height: 1.25;
            color: #ffffff;
            margin-bottom: 4px;
        }}

        .sidebar-header p {{
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.4;
        }}

        .toggle-btn {{
            position: absolute;
            top: 20px;
            right: -48px;
            width: 44px;
            height: 44px;
            background: var(--surface-dark);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-glass);
            border-left: none;
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            cursor: pointer;
            box-shadow: 4px 0 16px rgba(0,0,0,0.35);
            z-index: 1001;
            transition: all 0.2s;
        }}

        .toggle-btn:hover {{
            background: var(--brand-pink);
            color: #fff;
        }}

        .sidebar-content {{
            flex: 1;
            padding: 18px 22px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .sidebar-content::-webkit-scrollbar {{
            width: 6px;
        }}

        .sidebar-content::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.18);
            border-radius: 3px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}

        .kpi-card {{
            background: var(--surface-card);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            gap: 3px;
            transition: transform 0.2s, border-color 0.2s;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--border-accent);
        }}

        .kpi-title {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .kpi-title i {{
            font-size: 15px;
            color: var(--brand-pink);
        }}

        .kpi-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 22px;
            font-weight: 800;
            color: #fff;
            letter-spacing: -0.02em;
        }}

        .kpi-subtext {{
            font-size: 11px;
            color: var(--text-muted);
        }}

        .filter-section {{
            background: var(--surface-card);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 15px;
        }}

        .section-header {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--text-primary);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .section-header i {{
            color: var(--brand-pink);
            font-size: 16px;
        }}

        .filter-label {{
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: var(--text-secondary);
            margin-bottom: 6px;
            display: block;
        }}

        .chip-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 12px;
        }}

        .chip {{
            padding: 5px 10px;
            font-size: 11px;
            font-weight: 600;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-glass);
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
            user-select: none;
        }}

        .chip:hover {{
            background: rgba(244, 63, 94, 0.18);
            color: #fff;
            border-color: rgba(244, 63, 94, 0.45);
        }}

        .chip.active {{
            background: var(--brand-pink-gradient);
            color: #fff;
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(244, 63, 94, 0.35);
        }}

        .layer-toggle-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}

        .layer-toggle-row:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}

        .layer-info {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            font-weight: 500;
        }}

        .layer-info i {{
            font-size: 17px;
            color: var(--brand-pink);
        }}

        .switch {{
            position: relative;
            display: inline-block;
            width: 38px;
            height: 20px;
        }}

        .switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}

        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(255, 255, 255, 0.18);
            transition: .25s;
            border-radius: 20px;
        }}

        .slider:before {{
            position: absolute;
            content: "";
            height: 14px;
            width: 14px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .25s;
            border-radius: 50%;
        }}

        input:checked + .slider {{
            background-color: var(--brand-pink);
        }}

        input:checked + .slider:before {{
            transform: translateX(18px);
        }}

        .search-box {{
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-sm);
            padding: 6px 10px;
            margin-bottom: 10px;
            gap: 8px;
        }}

        .search-box i {{
            color: var(--text-muted);
            font-size: 15px;
        }}

        .search-box input {{
            background: transparent;
            border: none;
            outline: none;
            color: #fff;
            font-size: 12px;
            width: 100%;
        }}

        .search-box input::placeholder {{
            color: var(--text-muted);
        }}

        .bairro-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 10px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: var(--radius-sm);
            margin-bottom: 5px;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
        }}

        .bairro-item:hover {{
            background: rgba(244, 63, 94, 0.16);
            border-color: rgba(244, 63, 94, 0.35);
            transform: translateX(4px);
        }}

        .bairro-name {{
            font-size: 12px;
            font-weight: 500;
            color: var(--text-primary);
            max-width: 240px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .bairro-count-badge {{
            background: rgba(244, 63, 94, 0.25);
            color: #fca5a5;
            font-weight: 700;
            font-size: 11px;
            padding: 2px 7px;
            border-radius: 999px;
        }}

        .basemap-selector {{
            position: absolute;
            top: 16px;
            right: 16px;
            background: var(--surface-dark);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 5px;
            z-index: 1000;
            display: flex;
            gap: 4px;
            box-shadow: var(--shadow-glass);
        }}

        .basemap-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 7px 12px;
            font-size: 12px;
            font-weight: 600;
            border-radius: var(--radius-sm);
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
        }}

        .basemap-btn:hover {{
            color: #fff;
            background: rgba(255, 255, 255, 0.08);
        }}

        .basemap-btn.active {{
            background: var(--brand-pink-gradient);
            color: #fff;
            box-shadow: 0 2px 8px rgba(244, 63, 94, 0.3);
        }}

        .leaflet-popup-content-wrapper {{
            background: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid rgba(244, 63, 94, 0.5) !important;
            border-radius: 14px !important;
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}

        .leaflet-popup-content {{
            margin: 0 !important;
            min-width: 280px;
        }}

        .popup-card {{
            padding: 16px 18px;
        }}

        .popup-header {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 8px;
            margin-bottom: 10px;
        }}

        .popup-tag {{
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            color: #fb7185;
            letter-spacing: 0.05em;
        }}

        .popup-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: #ffffff;
            margin-top: 2px;
        }}

        .popup-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 7px;
            font-size: 12px;
        }}

        .popup-label {{
            color: var(--text-secondary);
        }}

        .popup-value {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .leaflet-popup-tip {{
            background: #0f172a !important;
            border: 1px solid rgba(244, 63, 94, 0.5) !important;
        }}

        .bairro-tooltip {{
            background: rgba(15, 23, 42, 0.92) !important;
            border: 1px solid rgba(244, 63, 94, 0.6) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            padding: 6px 10px !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
        }}

        .bairro-tooltip:before {{
            border-top-color: rgba(15, 23, 42, 0.92) !important;
        }}

        .map-legend {{
            position: absolute;
            bottom: 24px;
            right: 16px;
            background: var(--surface-dark);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-glass);
            border-radius: var(--radius-md);
            padding: 14px 18px;
            z-index: 1000;
            font-size: 11px;
            box-shadow: var(--shadow-glass);
            display: flex;
            flex-direction: column;
            gap: 6px;
            min-width: 175px;
        }}

        .map-legend-title {{
            font-weight: 700;
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }}

        .legend-scale-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            color: var(--text-primary);
        }}

        .legend-color-box {{
            width: 16px;
            height: 12px;
            border-radius: 3px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
    </style>
</head>
<body>

    <div id="map"></div>

    <div class="basemap-selector">
        <button class="basemap-btn active" onclick="setBasemap('light', this)">
            <i class="ph ph-sun"></i> Claro
        </button>
        <button class="basemap-btn" onclick="setBasemap('dark', this)">
            <i class="ph ph-moon"></i> Escuro
        </button>
        <button class="basemap-btn" onclick="setBasemap('satellite', this)">
            <i class="ph ph-planet"></i> Satélite
        </button>
        <button class="basemap-btn" onclick="setBasemap('osm', this)">
            <i class="ph ph-map-trifold"></i> Ruas
        </button>
    </div>

    <div class="map-legend">
        <div class="map-legend-title">Casos por Bairro</div>
        <div class="legend-scale-item">
            <span class="legend-color-box" style="background: #881337;"></span>
            <span>15+ casos (Muito Alta)</span>
        </div>
        <div class="legend-scale-item">
            <span class="legend-color-box" style="background: #e11d48;"></span>
            <span>10 - 14 casos (Alta)</span>
        </div>
        <div class="legend-scale-item">
            <span class="legend-color-box" style="background: #f97316;"></span>
            <span>6 - 9 casos (Média-Alta)</span>
        </div>
        <div class="legend-scale-item">
            <span class="legend-color-box" style="background: #facc15;"></span>
            <span>3 - 5 casos (Média)</span>
        </div>
        <div class="legend-scale-item">
            <span class="legend-color-box" style="background: #4ade80;"></span>
            <span>1 - 2 casos (Baixa)</span>
        </div>
        <div class="legend-scale-item">
            <span class="legend-color-box" style="background: #334155; opacity:0.5;"></span>
            <span>0 casos (no filtro)</span>
        </div>
    </div>

    <div class="sidebar" id="sidebar">
        <button class="toggle-btn" onclick="toggleSidebar()" title="Ocultar/Expandir Painel">
            <i class="ph ph-sidebar-simple" id="toggleIcon"></i>
        </button>

        <div class="sidebar-header">
            <div class="badge-pill">
                <i class="ph ph-heartbeat"></i> DATASUS - SIH/SUS SP
            </div>
            <h1>Rio Claro (SP)</h1>
            <p>Saúde da Mulher: Internações Oncologicas Multidoenças (2021 a 2025).</p>
        </div>

        <div class="sidebar-content">
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <span class="kpi-title"><i class="ph ph-users-three"></i> Internações</span>
                    <span class="kpi-value" id="kpiTotal">{total_internacoes}</span>
                    <span class="kpi-subtext">Casos com AIH registrada</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title"><i class="ph ph-calendar"></i> Idade Média</span>
                    <span class="kpi-value" id="kpiIdade">{idade_media} <small style="font-size:13px; font-weight:500;">anos</small></span>
                    <span class="kpi-subtext">Todas as faixas etárias</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title"><i class="ph ph-map-pin"></i> Bairros</span>
                    <span class="kpi-value" id="kpiBairros">{bairros_unicos}</span>
                    <span class="kpi-subtext">Fronteiras mapeadas</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title"><i class="ph ph-currency-dollar"></i> Custo SUS</span>
                    <span class="kpi-value" id="kpiCusto">R$ {custo_total:,.0f}</span>
                    <span class="kpi-subtext">Total hospitalar pago</span>
                </div>
            </div>

            <div class="filter-section">
                <div class="section-header">
                    <span>Filtros Interativos</span>
                    <i class="ph ph-funnel"></i>
                </div>

                <span class="filter-label">Diagnóstico / Doença:</span>
                <div class="chip-group" id="filterDoenca">
                    <div class="chip active" onclick="filtrarDoenca('todas', this)">Todas (7)</div>
                    <div class="chip" onclick="filtrarDoenca('Câncer de Mama', this)">Mama</div>
                    <div class="chip" onclick="filtrarDoenca('Câncer do Colo do Útero', this)">Colo do Útero</div>
                    <div class="chip" onclick="filtrarDoenca('Câncer Colorretal', this)">Colorretal</div>
                    <div class="chip" onclick="filtrarDoenca('Câncer de Ovário', this)">Ovário</div>
                    <div class="chip" onclick="filtrarDoenca('Câncer de Pele (Não Melanoma)', this)">Pele (Não Mel.)</div>
                    <div class="chip" onclick="filtrarDoenca('Câncer de Pulmão', this)">Pulmão</div>
                    <div class="chip" onclick="filtrarDoenca('Câncer de Tireoide', this)">Tireoide</div>
                </div>

                <span class="filter-label">Ano da Internação:</span>
                <div class="chip-group" id="filterAno">
                    <div class="chip active" onclick="filtrarAno('todos', this)">Todos</div>
                    <div class="chip" onclick="filtrarAno('2021', this)">2021</div>
                    <div class="chip" onclick="filtrarAno('2022', this)">2022</div>
                    <div class="chip" onclick="filtrarAno('2023', this)">2023</div>
                    <div class="chip" onclick="filtrarAno('2024', this)">2024</div>
                    <div class="chip" onclick="filtrarAno('2025', this)">2025</div>
                </div>

                <span class="filter-label">Faixa Etária:</span>
                <div class="chip-group" id="filterIdade">
                    <div class="chip active" onclick="filtrarFaixa('todas', this)">Todas</div>
                    <div class="chip" onclick="filtrarFaixa('ate40', this)">&lt; 40</div>
                    <div class="chip" onclick="filtrarFaixa('40a49', this)">40 - 49</div>
                    <div class="chip" onclick="filtrarFaixa('50a59', this)">50 - 59</div>
                    <div class="chip" onclick="filtrarFaixa('60a69', this)">60 - 69</div>
                    <div class="chip" onclick="filtrarFaixa('70mais', this)">70+</div>
                </div>

                <span class="filter-label" style="margin-top: 10px;">Camadas no Mapa:</span>
                
                <div class="layer-toggle-row">
                    <div class="layer-info">
                        <i class="ph ph-polygon"></i>
                        <span>Fronteiras e Calor dos Bairros</span>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="toggleBairros" checked onchange="atualizarCamadas()">
                        <span class="slider"></span>
                    </label>
                </div>

                <div class="layer-toggle-row">
                    <div class="layer-info">
                        <i class="ph ph-circles-three"></i>
                        <span>Clusters por bairro</span>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="toggleClusters" checked onchange="atualizarCamadas()">
                        <span class="slider"></span>
                    </label>
                </div>

                <div class="layer-toggle-row">
                    <div class="layer-info">
                        <i class="ph ph-flame"></i>
                        <span>Mancha de Calor Contínua (Heatmap)</span>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="toggleHeatmap" onchange="atualizarCamadas()">
                        <span class="slider"></span>
                    </label>
                </div>

                <div class="layer-toggle-row">
                    <div class="layer-info">
                        <i class="ph ph-shield-check"></i>
                        <span>Limite Municipal de Rio Claro</span>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="toggleMunicipio" checked onchange="atualizarCamadas()">
                        <span class="slider"></span>
                    </label>
                </div>
            </div>

            <div class="filter-section">
                <div class="section-header">
                    <span>Ranking dos Bairros</span>
                    <i class="ph ph-buildings"></i>
                </div>

                <div class="search-box">
                    <i class="ph ph-magnifying-glass"></i>
                    <input type="text" id="bairroSearch" placeholder="Buscar bairro..." oninput="filtrarListaBairros(this.value)">
                </div>

                <div id="listaTopBairros" style="max-height: 220px; overflow-y: auto;">
                </div>
            </div>

        </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>

    <script>
        const rawData = {json_records};
        const municipioGeoJSON = {json_municipio_geojson};
        const clustersBairro = {json_clusters_bairro};

        let filtroDoencaAtivo = 'todas';
        let filtroAnoAtivo = 'todos';
        let filtroFaixaAtiva = 'todas';
        let buscaBairroTexto = '';
        let listaBairrosAtual = [];
        let bairrosGeoJSON = null;

        const centerRC = [-22.4149, -47.5614];
        
        const map = L.map('map', {{
            center: centerRC,
            zoom: 12.8,
            zoomControl: false,
            minZoom: 10,
            maxZoom: 18
        }});

        L.control.zoom({{ position: 'bottomright' }}).addTo(map);

        const basemaps = {{
            light: L.layerGroup([
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
                    maxZoom: 16
                }}),
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    maxZoom: 16
                }})
            ]),
            dark: L.layerGroup([
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
                    maxZoom: 16
                }}),
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    maxZoom: 16
                }})
            ]),
            satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS',
                maxZoom: 18
            }}),
            osm: L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 19
            }})
        }};

        let activeBasemap = basemaps.light;
        activeBasemap.addTo(map);

        function setBasemap(type, btnEl) {{
            if (activeBasemap) map.removeLayer(activeBasemap);
            activeBasemap = basemaps[type];
            activeBasemap.addTo(map);

            document.querySelectorAll('.basemap-btn').forEach(btn => btn.classList.remove('active'));
            if (btnEl) btnEl.classList.add('active');
        }}

        let bairrosLayer = null;
        let heatLayer = null;
        let clusterGroup = null;
        let municipioLayer = null;

        function normalizarBairro(nome) {{
            return String(nome || '')
                .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
                .toLowerCase().replace(/[^a-z0-9]/g, '');
        }}

        const coordenadasClusterPorBairro = new Map(
            clustersBairro
                .filter(item => item.latitude_cluster !== null && item.longitude_cluster !== null)
                .map(item => [normalizarBairro(item.bairro), item])
        );

        municipioLayer = L.geoJSON(municipioGeoJSON, {{
            style: {{
                color: '#f43f5e',
                weight: 2.5,
                dashArray: '6, 6',
                fillColor: 'transparent',
                fillOpacity: 0
            }}
        }}).addTo(map);

        function toggleSidebar() {{
            const sb = document.getElementById('sidebar');
            sb.classList.toggle('collapsed');
        }}

        function filtrarDoenca(doenca, el) {{
            filtroDoencaAtivo = doenca;
            document.querySelectorAll('#filterDoenca .chip').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            aplicarFiltros();
        }}

        function filtrarAno(ano, el) {{
            filtroAnoAtivo = ano;
            document.querySelectorAll('#filterAno .chip').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            aplicarFiltros();
        }}

        function filtrarFaixa(faixa, el) {{
            filtroFaixaAtiva = faixa;
            document.querySelectorAll('#filterIdade .chip').forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            aplicarFiltros();
        }}

        function filtrarListaBairros(texto) {{
            buscaBairroTexto = texto.toLowerCase().trim();
            renderizarListaBairros();
        }}

        function atendeFiltros(item) {{
            if (filtroDoencaAtivo !== 'todas' && item.doenca !== filtroDoencaAtivo) return false;
            if (filtroAnoAtivo !== 'todos' && item.ano !== filtroAnoAtivo) return false;
            
            if (filtroFaixaAtiva !== 'todas') {{
                const id = item.idade;
                if (filtroFaixaAtiva === 'ate40' && id >= 40) return false;
                if (filtroFaixaAtiva === '40a49' && (id < 40 || id > 49)) return false;
                if (filtroFaixaAtiva === '50a59' && (id < 50 || id > 59)) return false;
                if (filtroFaixaAtiva === '60a69' && (id < 60 || id > 69)) return false;
                if (filtroFaixaAtiva === '70mais' && id < 70) return false;
            }}
            return true;
        }}

        function getCorPorCasos(casos) {{
            if (casos >= 15) return '#881337';
            if (casos >= 10) return '#e11d48';
            if (casos >= 6)  return '#f97316';
            if (casos >= 3)  return '#facc15';
            if (casos >= 1)  return '#4ade80';
            return '#334155';
        }}

        function aplicarFiltros() {{
            if (!bairrosGeoJSON) return;

            const dadosFiltrados = rawData.filter(atendeFiltros);
            atualizarVisualizacao(dadosFiltrados);
            atualizarKPIs(dadosFiltrados);
        }}

        function renderizarListaBairros() {{
            const listEl = document.getElementById('listaTopBairros');
            listEl.innerHTML = '';

            const filtrados = listaBairrosAtual.filter(([bairro]) => 
                !buscaBairroTexto || bairro.toLowerCase().includes(buscaBairroTexto)
            );

            if (filtrados.length === 0) {{
                listEl.innerHTML = '<div style="color:var(--text-muted);font-size:12px;padding:8px;">Nenhum bairro encontrado.</div>';
                return;
            }}

            filtrados.forEach(([bairro, count]) => {{
                const item = document.createElement('div');
                item.className = 'bairro-item';
                item.innerHTML = `
                    <span class="bairro-name" title="${{bairro}}">${{bairro}}</span>
                    <span class="bairro-count-badge">${{count}} ${{count > 1 ? 'casos' : 'caso'}}</span>
                `;
                item.onclick = () => focarBairro(bairro);
                listEl.appendChild(item);
            }});
        }}

        function atualizarKPIs(dados) {{
            document.getElementById('kpiTotal').innerText = dados.length;
            
            if (dados.length > 0) {{
                const mediaIdade = (dados.reduce((acc, cur) => acc + cur.idade, 0) / dados.length).toFixed(1);
                document.getElementById('kpiIdade').innerHTML = `${{mediaIdade}} <small style="font-size:13px; font-weight:500;">anos</small>`;
                
                const custo = dados.reduce((acc, cur) => acc + cur.valor, 0);
                document.getElementById('kpiCusto').innerText = `R$ ${{custo.toLocaleString('pt-BR', {{ maximumFractionDigits: 0 }})}}`;

                const bairrosSet = new Set(dados.map(d => d.bairro).filter(Boolean));
                document.getElementById('kpiBairros').innerText = bairrosSet.size;

                const contagem = {{}};
                dados.forEach(d => {{
                    if (d.bairro) {{
                        contagem[d.bairro] = (contagem[d.bairro] || 0) + 1;
                    }}
                }});
                listaBairrosAtual = Object.entries(contagem).sort((a, b) => b[1] - a[1]);
                renderizarListaBairros();
            }} else {{
                document.getElementById('kpiIdade').innerText = '0';
                document.getElementById('kpiCusto').innerText = 'R$ 0';
                document.getElementById('kpiBairros').innerText = '0';
                listaBairrosAtual = [];
                renderizarListaBairros();
            }}
        }}

        function focarBairro(nomeBairro) {{
            let layerEncontrada = null;
            if (bairrosLayer) {{
                bairrosLayer.eachLayer(l => {{
                    if (l.feature && l.feature.properties && l.feature.properties.bairro === nomeBairro) {{
                        layerEncontrada = l;
                    }}
                }});
            }}

            if (layerEncontrada) {{
                map.flyToBounds(layerEncontrada.getBounds(), {{ duration: 1.2, maxZoom: 15 }});
                layerEncontrada.openPopup();
            }} else {{
                const pontos = rawData.filter(d => d.bairro === nomeBairro);
                if (pontos.length > 0) {{
                    const latAvg = pontos.reduce((acc, p) => acc + p.lat, 0) / pontos.length;
                    const lngAvg = pontos.reduce((acc, p) => acc + p.lng, 0) / pontos.length;
                    map.flyTo([latAvg, lngAvg], 15, {{ duration: 1.2 }});
                }}
            }}
        }}

        function atualizarVisualizacao(dados) {{
            if (bairrosLayer && map.hasLayer(bairrosLayer)) map.removeLayer(bairrosLayer);
            if (heatLayer && map.hasLayer(heatLayer)) map.removeLayer(heatLayer);
            if (clusterGroup && map.hasLayer(clusterGroup)) map.removeLayer(clusterGroup);

            const statsBairrosFiltrados = {{}};
            dados.forEach(d => {{
                if (!statsBairrosFiltrados[d.bairro]) {{
                    statsBairrosFiltrados[d.bairro] = {{
                        casos: 0,
                        idades: [],
                        custo: 0,
                        anos: new Set()
                    }};
                }}
                statsBairrosFiltrados[d.bairro].casos += 1;
                statsBairrosFiltrados[d.bairro].idades.push(d.idade);
                statsBairrosFiltrados[d.bairro].custo += d.valor;
                statsBairrosFiltrados[d.bairro].anos.add(d.ano);
            }});

            const totalFiltrado = dados.length || 1;

            bairrosLayer = L.geoJSON(bairrosGeoJSON, {{
                style: function(feature) {{
                    const nome = feature.properties.bairro;
                    const bStats = statsBairrosFiltrados[nome];
                    const numCasos = bStats ? bStats.casos : 0;
                    const temCasos = numCasos > 0;

                    return {{
                        color: temCasos ? '#ffffff' : '#64748b',
                        weight: temCasos ? 1.5 : 0.8,
                        opacity: temCasos ? 0.85 : 0.4,
                        fillColor: getCorPorCasos(numCasos),
                        fillOpacity: temCasos ? 0.65 : 0.15
                    }};
                }},
                onEachFeature: function(feature, layer) {{
                    const nome = feature.properties.bairro;
                    const bStats = statsBairrosFiltrados[nome];
                    const numCasos = bStats ? bStats.casos : 0;
                    const pct = ((numCasos / totalFiltrado) * 100).toFixed(1);
                    const idadeM = bStats && bStats.idades.length ? (bStats.idades.reduce((a,b)=>a+b,0)/numCasos).toFixed(1) : '-';
                    const custoLoc = bStats ? bStats.custo : 0;
                    const anosLista = bStats ? [...bStats.anos].sort().join(', ') : '-';

                    layer.bindTooltip(`
                        <div>
                            <strong>${{nome}}</strong><br>
                            <span style="color:#fb7185;">${{numCasos}} ${{numCasos === 1 ? 'caso' : 'casos'}}</span> (${{pct}}%)
                        </div>
                    `, {{ className: 'bairro-tooltip', sticky: true }});

                    const popupHtml = `
                        <div class="popup-card">
                            <div class="popup-header">
                                <span class="popup-tag">Bairro de Rio Claro</span>
                                <div class="popup-title">${{nome}}</div>
                            </div>
                            <div class="popup-row">
                                <span class="popup-label">Total de Internações:</span>
                                <span class="popup-value" style="color:#fb7185;font-weight:700;font-size:14px;">${{numCasos}} ${{numCasos === 1 ? 'caso' : 'casos'}}</span>
                            </div>
                            <div class="popup-row">
                                <span class="popup-label">Participação no Filtro:</span>
                                <span class="popup-value">${{pct}}% do total</span>
                            </div>
                            <div class="popup-row">
                                <span class="popup-label">Média de Idade:</span>
                                <span class="popup-value">${{idadeM}} anos</span>
                            </div>
                            <div class="popup-row">
                                <span class="popup-label">Anos Registrados:</span>
                                <span class="popup-value">${{anosLista}}</span>
                            </div>
                            <div class="popup-row" style="margin-bottom:0;">
                                <span class="popup-label">Valor SUS Total:</span>
                                <span class="popup-value">R$ ${{custoLoc.toLocaleString('pt-BR', {{ minimumFractionDigits: 2 }})}}</span>
                            </div>
                        </div>
                    `;
                    layer.bindPopup(popupHtml);

                    layer.on({{
                        mouseover: function(e) {{
                            const l = e.target;
                            l.setStyle({{ weight: 3, color: '#fb7185', fillOpacity: 0.85 }});
                        }},
                        mouseout: function(e) {{
                            bairrosLayer.resetStyle(e.target);
                        }}
                    }});
                }}
            }});

            const heatData = dados.map(d => [d.lat, d.lng, 0.85]);
            heatLayer = L.heatLayer(heatData, {{
                radius: 26, blur: 16, maxZoom: 16, max: 1.0,
                gradient: {{ 0.2: '#0055ff', 0.4: '#00ffee', 0.6: '#33ff33', 0.8: '#ffee00', 1.0: '#ff0044' }}
            }});

            clusterGroup = L.layerGroup();
            const bairrosComCasos = {{}};
            dados.forEach(d => {{
                const chave = normalizarBairro(d.bairro);
                if (!bairrosComCasos[chave]) {{
                    bairrosComCasos[chave] = {{ bairro: d.bairro, casos: [] }};
                }}
                bairrosComCasos[chave].casos.push(d);
            }});

            Object.values(bairrosComCasos).forEach(loc => {{
                const coordenada = coordenadasClusterPorBairro.get(normalizarBairro(loc.bairro));
                if (!coordenada) return;
                const count = loc.casos.length;
                const idades = loc.casos.map(c => c.idade);
                const idadeMedia = (idades.reduce((a, b) => a + b, 0) / count).toFixed(0);
                const idadeMinima = Math.min(...idades);
                const idadeMaxima = Math.max(...idades);
                const anos = [...new Set(loc.casos.map(c => c.ano))].sort().join(', ');
                const custoLoc = loc.casos.reduce((a, b) => a + b.valor, 0);

                const popupHtml = `
                    <div class="popup-card">
                        <div class="popup-header">
                            <span class="popup-tag">${{loc.bairro || 'Rio Claro'}}</span>
                            <div class="popup-title">Cluster do Bairro</div>
                        </div>
                        <div class="popup-row">
                            <span class="popup-label">Total de Internações:</span>
                            <span class="popup-value" style="color:#fb7185;font-weight:700;">${{count}} ${{count > 1 ? 'casos' : 'caso'}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-label">Idade Média:</span>
                            <span class="popup-value">${{idadeMedia}} anos</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-label">Faixa de Idade:</span>
                            <span class="popup-value">${{idadeMinima}} a ${{idadeMaxima}} anos</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-label">Anos Registrados:</span>
                            <span class="popup-value">${{anos}}</span>
                        </div>
                        <div class="popup-row" style="margin-bottom:0;">
                            <span class="popup-label">Valor SUS Total:</span>
                            <span class="popup-value">R$ ${{custoLoc.toLocaleString('pt-BR', {{ minimumFractionDigits: 2 }})}}</span>
                        </div>
                    </div>
                `;

                const marker = L.circleMarker([
                    coordenada.latitude_cluster,
                    coordenada.longitude_cluster
                ], {{
                    radius: Math.min(7 + count * 2.5, 18),
                    fillColor: '#f43f5e',
                    color: '#ffffff',
                    weight: 2,
                    opacity: 0.9,
                    fillOpacity: 0.85
                }}).bindPopup(popupHtml);

                clusterGroup.addLayer(marker);
            }});

            atualizarCamadas();
        }}

        function atualizarCamadas() {{
            const showBairros = document.getElementById('toggleBairros').checked;
            const showCluster = document.getElementById('toggleClusters').checked;
            const showHeat = document.getElementById('toggleHeatmap').checked;
            const showMunicipio = document.getElementById('toggleMunicipio').checked;

            if (showBairros) {{ if (bairrosLayer && !map.hasLayer(bairrosLayer)) map.addLayer(bairrosLayer); }}
            else {{ if (bairrosLayer && map.hasLayer(bairrosLayer)) map.removeLayer(bairrosLayer); }}

            if (showCluster) {{ if (clusterGroup && !map.hasLayer(clusterGroup)) map.addLayer(clusterGroup); }}
            else {{ if (clusterGroup && map.hasLayer(clusterGroup)) map.removeLayer(clusterGroup); }}

            if (showHeat) {{ if (heatLayer && !map.hasLayer(heatLayer)) map.addLayer(heatLayer); }}
            else {{ if (heatLayer && map.hasLayer(heatLayer)) map.removeLayer(heatLayer); }}

            if (showMunicipio) {{ if (municipioLayer && !map.hasLayer(municipioLayer)) map.addLayer(municipioLayer); }}
            else {{ if (municipioLayer && map.hasLayer(municipioLayer)) map.removeLayer(municipioLayer); }}
        }}

        fetch('{BAIRROS_GEOJSON_FILENAME}')
            .then(response => {{
                if (!response.ok) throw new Error(`Erro ao carregar bairros: ${{response.status}}`);
                return response.json();
            }})
            .then(geojson => {{
                bairrosGeoJSON = geojson;
                aplicarFiltros();
            }})
            .catch(error => console.error(error));
    </script>
</body>
</html>
"""

    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Mapa unificado gerado em: {HTML_OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()