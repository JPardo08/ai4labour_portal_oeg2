
# streamlit_app.py
# Recomendador AI4Labour · v2 (sin puntuaciones de similitud)
# Requiere: streamlit>=1.28, pandas

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import streamlit as st

# ---------------------------
# Configuración de página
# ---------------------------
st.set_page_config(
    page_title="AI4Labour · Recomendador de cursos",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 Recomendador de cursos por ocupación (v2)")

# ---------------------------
# Utilidades
# ---------------------------
def norm(text: str) -> str:
    """Normaliza DWA/strings: trim, lowercase, sin punto final, colapsa espacios."""
    if not isinstance(text, str):
        return ""
    t = text.strip().lower()
    t = re.sub(r"[.\s]+$", "", t)  # quita punto final y espacios
    t = re.sub(r"\s+", " ", t)
    return t

@st.cache_data(show_spinner=False)
def load_data(data_dir: Path) -> Dict[str, pd.DataFrame]:
    # Carga CSV
    fil8 = pd.read_csv(data_dir / "filtrado8_results.csv")  # title, dwa_title
    deg = pd.read_csv(data_dir / "filtrado18_results_degree_cat.csv")  # dwa_title, automation_quartile
    dwa_top3 = pd.read_csv(data_dir / "dwa_top3.csv")  # dwa_original, dwa1, dwa2, dwa3
    dwa_skill = pd.read_csv(data_dir / "dwa_skill_top3.csv")  # dwa_original, skill1, skill2, skill3
    courses = pd.read_csv(data_dir / "courses_full.csv")  # skills_title, url, name, topics, ...

    # Limpieza básica
    for df in (fil8, deg, dwa_top3, dwa_skill, courses):
        for c in df.select_dtypes(include="object").columns:
            df[c] = df[c].astype(str).str.strip()

    # Normalizaciones clave
    fil8["dwa_norm"] = fil8["dwa_title"].apply(norm)
    deg["dwa_norm"] = deg["dwa_title"].apply(norm)
    dwa_top3["dwa_original_norm"] = dwa_top3["dwa_original"].apply(norm)
    for c in ["dwa1", "dwa2", "dwa3"]:
        dwa_top3[f"{c}_norm"] = dwa_top3[c].apply(norm)
    dwa_skill["dwa_original_norm"] = dwa_skill["dwa_original"].apply(norm)

    return {
        "fil8": fil8,
        "deg": deg,
        "dwa_top3": dwa_top3,
        "dwa_skill": dwa_skill,
        "courses": courses,
    }

def build_indexes(dfs: Dict[str, pd.DataFrame]):
    fil8, deg, dwa_top3, dwa_skill, courses = (
        dfs["fil8"],
        dfs["deg"],
        dfs["dwa_top3"],
        dfs["dwa_skill"],
        dfs["courses"],
    )

    # Mapa DWA->riesgo
    risk_map = dict(zip(deg["dwa_norm"], deg["automation_quartile"]))  # 'Bajo'/'Alto'

    # Ocupaciones disponibles
    occupations = sorted(fil8["title"].dropna().unique().tolist())

    # Mapa DWA->vecinos (normalizados)
    neighbors_map = {
        row["dwa_original_norm"]: [
            row.get("dwa1_norm", ""),
            row.get("dwa2_norm", ""),
            row.get("dwa3_norm", ""),
        ]
        for _, row in dwa_top3.iterrows()
    }

    # Mapa DWA->skills (texto tal cual en columnas skill1/2/3)
    skills_map = {
        row["dwa_original_norm"]: [
            s for s in [row.get("skill1", ""), row.get("skill2", ""), row.get("skill3", "")]
            if isinstance(s, str) and s
        ]
        for _, row in dwa_skill.iterrows()
    }

    # Idiomas y otros filtros
    langs = sorted(courses["language"].dropna().unique().tolist())

    return risk_map, occupations, neighbors_map, skills_map, langs

def dwas_for_occupation(fil8: pd.DataFrame, occupation: str) -> List[str]:
    """Devuelve DWAs normalizadas para una ocupación."""
    return fil8.loc[fil8["title"] == occupation, "dwa_norm"].dropna().unique().tolist()

def compute_safe_dwas(
    dwas: List[str],
    risk_map: Dict[str, str],
    neighbors_map: Dict[str, List[str]],
    use_fallback: bool = True,
) -> Tuple[List[str], List[Tuple[str, str, str]]]:
    """
    Devuelve:
      - lista de DWAs 'seguras' (normalizadas) que continuarán al mapeo a skills,
      - rutas [(origen_dwa, destino_dwa, TAG)] para explicabilidad.
    TAG ∈ {'SAFE_DIRECT', 'SAFE_VIA_NEIGHBOR', 'FALLBACK_RISKY'}
    """
    def is_safe(dwa_norm: str) -> bool:
        return risk_map.get(dwa_norm, "Alto") == "Bajo"

    safe_set = set()
    routes = []

    for d in dwas:
        if is_safe(d):
            safe_set.add(d)
            routes.append((d, d, "SAFE_DIRECT"))
        else:
            neighs = [n for n in neighbors_map.get(d, []) if isinstance(n, str) and n]
            safe_neighs = [n for n in neighs if is_safe(n)]
            if safe_neighs:
                for s in safe_neighs:
                    safe_set.add(s)
                    routes.append((d, s, "SAFE_VIA_NEIGHBOR"))
            else:
                if use_fallback:
                    safe_set.add(d)
                    routes.append((d, d, "FALLBACK_RISKY"))
                # si no fallback, simplemente se ignora esa DWA

    return sorted(safe_set), routes

def skills_for_dwas(safe_dwas: List[str], skills_map: Dict[str, List[str]]) -> List[str]:
    skills = []
    for d in safe_dwas:
        skills.extend(skills_map.get(d, []))
    # dedup y orden alfabético
    return sorted(set([s for s in skills if isinstance(s, str) and s]))

def courses_for_skills(courses_df: pd.DataFrame, skills: List[str]) -> pd.DataFrame:
    if not skills:
        return pd.DataFrame(columns=["url", "name", "language", "topics", "skills_matched", "n_skills"])
    sub = courses_df[courses_df["skills_title"].isin(skills)].copy()
    if sub.empty:
        return pd.DataFrame(columns=["url", "name", "language", "topics", "skills_matched", "n_skills"])
    agg = (
        sub.groupby(["url", "name", "language", "topics"], dropna=False)
           .agg(skills_matched=("skills_title", lambda s: sorted(set(s))),
                n_skills=("skills_title", "nunique"))
           .reset_index()
           .sort_values(["n_skills", "name"], ascending=[False, True])
    )
    return agg

def pretty_routes_df(routes: List[Tuple[str, str, str]], deg: pd.DataFrame) -> pd.DataFrame:
    """Convierte rutas en tabla legible con títulos originales y riesgos visibles."""
    # Para mostrar títulos bonitos, recuperamos las formas originales desde deg/fil8 si fuera necesario.
    # Aquí nos quedamos con normalizados y el riesgo de destino.
    risk_lookup = dict(zip(deg["dwa_norm"], deg["automation_quartile"]))
    df = pd.DataFrame(routes, columns=["dwa_origen_norm", "dwa_destino_norm", "ruta"])
    df["riesgo_destino"] = df["dwa_destino_norm"].map(lambda x: risk_lookup.get(x, "Alto"))
    return df

# ---------------------------
# Sidebar (parámetros)
# ---------------------------
st.sidebar.header("⚙️ Configuración")

data_dir_str = st.sidebar.text_input("Carpeta de datos", value="data")
DATA_DIR = Path(data_dir_str)

use_fallback = st.sidebar.checkbox("Permitir fallback si no hay DWAs seguras", value=True)
max_rows = st.sidebar.slider("Máx. cursos a mostrar", min_value=10, max_value=500, value=100, step=10)

# ---------------------------
# Carga de datos
# ---------------------------
with st.spinner("Cargando datos..."):
    dfs = load_data(DATA_DIR)
    risk_map, occupations, neighbors_map, skills_map, langs = build_indexes(dfs)

if not occupations:
    st.error("No se han encontrado ocupaciones en los datos. Revisa la ruta de la carpeta `data/`.")
    st.stop()

# ---------------------------
# UI principal
# ---------------------------
col1, col2 = st.columns([2, 1])
with col1:
    occupation = st.selectbox("Selecciona tu ocupación:", occupations, index=0)
with col2:
    lang_filter = st.multiselect("Filtrar por idioma del curso (opcional):", options=langs, default=[])

# Ejecutar flujo cuando hay ocupación
if occupation:
    fil8, deg, dwa_top3, dwa_skill, courses = (
        dfs["fil8"], dfs["deg"], dfs["dwa_top3"], dfs["dwa_skill"], dfs["courses"]
    )

    # 1) Ocupación → DWAs
    dwas_norm = dwas_for_occupation(fil8, occupation)

    # 2) DWAs → seguras (o fallback)
    safe_dwas, routes = compute_safe_dwas(dwas_norm, risk_map, neighbors_map, use_fallback=use_fallback)

    # 3) DWAs seguras → Skills
    skills = skills_for_dwas(safe_dwas, skills_map)

    # 4) Skills → Cursos (sin puntuaciones)
    results = courses_for_skills(courses, skills)

    # Filtros UI
    if lang_filter:
        results = results[results["language"].isin(lang_filter)]

    # Métricas rápidas
    n_dwas_total = len(dwas_norm)
    n_routes = len(routes)
    n_dwas_safe = len(safe_dwas)
    n_skills = len(skills)
    n_courses = len(results)

    st.subheader("📊 Métricas del resultado")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("DWAs (ocupación)", n_dwas_total)
    m2.metric("DWAs seguras (tras ruta)", n_dwas_safe)
    m3.metric("Rutas generadas", n_routes)
    m4.metric("Skills únicas", n_skills)
    m5.metric("Cursos encontrados", n_courses)

    # Tabla de cursos
    st.subheader("📚 Cursos recomendados")
    if results.empty:
        st.info("No se han encontrado cursos para las skills resultantes. Prueba otra ocupación o revisa los datos.")
    else:
        to_show = results.copy()
        # Reordenamos columnas y limitamos filas
        to_show = to_show[["name", "url", "language", "topics", "n_skills", "skills_matched"]].head(max_rows)
        st.dataframe(to_show, use_container_width=True)

        # Descarga
        st.download_button(
            label="⬇️ Descargar resultados (CSV)",
            data=to_show.to_csv(index=False).encode("utf-8"),
            file_name=f"cursos_{norm(occupation)}.csv",
            mime="text/csv",
        )

    # Explicabilidad
    with st.expander("🔎 Ver rutas de reconversión (explicabilidad)", expanded=False):
        routes_df = pretty_routes_df(routes, deg)
        st.dataframe(routes_df, use_container_width=True)

# Notas rápidas:
# - No se usa ninguna puntuación de similitud: dwa_top3 y dwa_skill_top3 se usan solo para navegar (top3 planos).
# - El riesgo se toma del dataset estático (Bajo = no riesgo, Alto = en riesgo).
# - Si una DWA está en riesgo y no tiene vecinas seguras, el fallback deja pasar esa DWA igualmente (para no vaciar resultados), pero la ruta queda marcada como FALLBACK_RISKY para transparencia.
# - Puse un filtro de idioma y exportación a CSV.
# - La app asume que los CSV están en ./data/. Si los tienes en otra ruta, cámbiala desde la sidebar.


# Métricas:
# 1. DWAs (ocupación)
#    Cuántas DWAs originales tiene la ocupación elegida según `filtrado8_results.csv`.
#    Fórmula: número de DWAs únicas asociadas a esa ocupación.

# 2. DWAs seguras (tras ruta)
#    Cuántas DWAs de destino usamos para mapear a skills después de aplicar la lógica de riesgo:
#       - SAFE\_DIRECT: la DWA original es Bajo (no riesgo) → usamos esa misma.
#       - SAFE\_VIA\_NEIGHBOR: la DWA original es Alto (riesgo), pero alguna vecina top-3 es Bajo → usamos la(s) vecina(s).
#       - FALLBACK\_RISKY (si el toggle está activo): la DWA es Alto y no hay vecinas seguras → aun así usamos la original (marcado como fallback).
# Es el tamaño del conjunto único de DWAs de destino; puede ser mayor que las DWAs originales si varias arrastran vecinas distintas.

# 3. Rutas generadas
#    El número de trazas creadas para explicabilidad.
#       - 1 ruta por SAFE\_DIRECT
#       - 1 por cada vecina segura en SAFE\_VIA\_NEIGHBOR (hasta 3)
#       - 1 por FALLBACK\_RISKY
# Suele ser ≥ que las DWAs originales porque una DWA en riesgo puede producir varias rutas (una por vecina segura).

# 4. Skills únicas
#    El total de skills distintas recuperadas desde `dwa_skill_top3.csv` para las DWAs de destino (las del punto 2).
# Si ves un número bajo, puede indicar DWAs de destino sin mapeo a skills o demasiados fallbacks hacia DWAs con pocas skills.

# 5. Cursos encontrados
#    El número de cursos tras unir `courses_full.csv` con las skills anteriores, agregados por `(url, name, language, topics)`.
#       - La tabla muestra también `n_skills`: cuántas de las skills objetivo cubre cada curso (sirve como señal de cobertura, no como puntuación de similitud).
#       - El conteo final respeta los filtros (p. ej., idioma).




# Interpretación de métricas:
# - Muchas `SAFE_VIA_NEIGHBOR` y pocas `FALLBACK_RISKY` → buena “reconversión” hacia tareas seguras.
# - `DWAs seguras` ≫ `DWAs (ocupación)` → varias DWAs en riesgo están aportando vecinas seguras distintas (más cobertura).
# - `Skills únicas` alto → mayor diversidad de puertas de entrada a cursos.
# - `Cursos encontrados` bajo con `Skills únicas` alto → quizá falta cobertura de esas skills en `courses_full` o filtros muy restrictivos (idioma).



# Explicabilidad: 
# - SAFE\_DIRECT
#   - Qué significa: La DWA original de la ocupación está “Bajo” (no en riesgo) en el dataset de riesgo.
#   - Qué hacemos: Usamos esa misma DWA para buscar sus 3 skills (`dwa_skill_top3`) y de ahí los cursos.
#   - Ejemplo: “prepare financial statements” → riesgo Bajo → vamos directo a sus skills.

# - SAFE\_VIA\_NEIGHBOR
#   - Qué significa: La DWA original está “Alto” (en riesgo), pero alguna de sus DWA vecinas (top-3) es segura (Bajo).
#   - Qué hacemos: En lugar de la DWA riesgosa, usamos la DWA vecina segura como “destino” para mapear a skills/cursos (ruta de reconversión).
#   - Ejemplo: “prepare procedural documents” → riesgo Alto; vecina “prepare proposal documents” → Bajo → mapeamos desde la vecina segura.

# - FALLBACK\_RISKY
#   - Qué significa: La DWA original está “Alto” y ninguna de sus vecinas top-3 es segura (o no hay vecinas).
#   - Qué hacemos: Aún así dejamos pasar esa DWA a sus skills/cursos (para no quedarnos sin resultados), pero marcamos la ruta como fallback para que el usuario sepa que procede de una DWA en riesgo.
#   - Cuándo usarlo: Útil para recuperar cobertura; en la UI puedes filtrarlo/avisar si prefieres evitar recomendaciones basadas en tareas en riesgo.

# En resumen: DIRECT = segura tal cual; VIA\_NEIGHBOR = segura por vecina; FALLBACK\_RISKY = no hay vecina segura y se continúa igualmente (con aviso).
