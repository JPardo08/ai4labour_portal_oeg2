
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

def build_title_lookup(dfs: Dict[str, pd.DataFrame]) -> Dict[str, str]:
    """Diccionario norm -> título original más representativo."""
    fil8, deg, dwa_top3 = dfs["fil8"], dfs["deg"], dfs["dwa_top3"]
    lut: Dict[str, str] = {}

    # Preferimos el original de deg (más completo), luego fil8 y luego vecinos.
    for _, r in deg[["dwa_norm", "dwa_title"]].drop_duplicates().iterrows():
        lut[r["dwa_norm"]] = r["dwa_title"]
    for _, r in fil8[["dwa_norm", "dwa_title"]].drop_duplicates().iterrows():
        lut.setdefault(r["dwa_norm"], r["dwa_title"])
    for _, r in dwa_top3.iterrows():
        lut.setdefault(r["dwa_original_norm"], r["dwa_original"])
        for col in ["dwa1", "dwa2", "dwa3"]:
            lut.setdefault(r[f"{col}_norm"], r[col])
    return lut

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
    routes: List[Tuple[str, str, str]] = []

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
                # si no fallback, se ignora esa DWA

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

def pretty_routes_df(routes: List[Tuple[str, str, str]], deg: pd.DataFrame, title_lut: Dict[str, str]) -> pd.DataFrame:
    """Convierte rutas en tabla legible con títulos y riesgos visibles."""
    risk_lookup = dict(zip(deg["dwa_norm"], deg["automation_quartile"]))
    df = pd.DataFrame(routes, columns=["dwa_origen_norm", "dwa_destino_norm", "ruta"])
    df["dwa_origen"] = df["dwa_origen_norm"].map(lambda x: title_lut.get(x, x))
    df["dwa_destino"] = df["dwa_destino_norm"].map(lambda x: title_lut.get(x, x))
    df["riesgo_destino"] = df["dwa_destino_norm"].map(lambda x: risk_lookup.get(x, "Alto"))
    return df[["ruta", "dwa_origen", "dwa_destino", "riesgo_destino"]].sort_values(["ruta","dwa_origen","dwa_destino"])

def neighbor_table_for(dwa_norm: str, neighbors_map: Dict[str, List[str]], deg: pd.DataFrame, title_lut: Dict[str, str]) -> pd.DataFrame:
    risk_lookup = dict(zip(deg["dwa_norm"], deg["automation_quartile"]))
    neighs = [n for n in neighbors_map.get(dwa_norm, []) if isinstance(n, str) and n]
    rows = []
    for n in neighs:
        rows.append({
            "vecina": title_lut.get(n, n),
            "riesgo_vecina": risk_lookup.get(n, "Alto"),
        })
    return pd.DataFrame(rows)

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
    title_lut = build_title_lookup(dfs)

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

# Bloques de ayuda / metodología
with st.expander("ℹ️ Cómo funciona (v2): pipeline y decisiones", expanded=False):
    st.markdown(
        """
**v2 sin puntuaciones de similitud**:

1. Conversión estática **Ocupación → DWAs** (`filtrado8_results.csv`).
2. Sacamos el **riesgo** de cada DWA desde dataset estático (`filtrado18_results_degree_cat.csv`): `Bajo` = **no en riesgo**, `Alto` = **en riesgo**.
3. Si una DWA está en riesgo, buscamos las **top-3 vecinas** en `dwa_top3.csv` y nos quedamos con las que sean **seguras (riesgo bajo)**.
4. Pasamos las **DWAs seguras** (directas o vecinas) a **skills** con `dwa_skill_top3.csv` (top-3 planas, sin puntuar).
5. Unimos **skills → cursos** con `courses_full.csv`. No hay *scoring* de similitud; sólo agregamos cuántas skills objetivo cubre cada curso (`n_skills`).
        

**Leyenda de rutas (Paso 3)**:
- `SAFE_DIRECT`: Si la DWA original ya era segura → se usa tal cual.
- `SAFE_VIA_NEIGHBOR`: Si la DWA original está en riesgo, pero tiene alguna vecina segura → se usa la(s) vecina.
- `FALLBACK_RISKY`: Si la DWA en riesgo no tiene vecinas seguras → se indica igualmente, marcado como fallback, para transparencia.
        """
    )

with st.expander("📏 Métricas — significado e interpretación", expanded=False):
    st.markdown(
        """
**DWAs (ocupación):** nº de DWAs únicas de la ocupación.

**DWAs seguras (tras ruta):** nº de DWAs de destino que usamos para mapear a skills \
(únicas), contando directas, via vecina y *fallback* (si está activado). Son las DWAs\
similares a aquellas que estan en riesgo, pero que suponen un riesgo bajo (Paso 3).  

**Rutas generadas:** nº de trazas (una por `SAFE_DIRECT`, una por `FALLBACK_RISKY` \
y **una por cada vecina segura** en `SAFE_VIA_NEIGHBOR`). Explicacion de que es cada\
en el primer desplegable. 

**Skills únicas:** nº de skills distintas recuperadas para las DWAs de destino (DWAs seguras).

**Cursos encontrados:** nº de cursos tras unir por skills (agregados por URL/nombre). \
La columna `n_skills` indica cuántas skills objetivo cubre cada curso (señal de cobertura, **no** puntuación).
        
**Lectura rápida**:
- Si recuperamos muchas DWAs `SAFE_VIA_NEIGHBOR` y pocas `FALLBACK_RISKY` ⇒ tenemos una buena reconversión.
- Si el nº de `DWAs seguras` ≫ `DWAs (ocupación)` ⇒ tenemos varias DWAs en riesgo que aportan vecinas seguras distintas.
- Si el nº de `Skills únicas` es alto pero `Cursos` bajo ⇒ poca cobertura en `courses_full` o filtros (p.ej. idioma) muy restrictivos.

**Nota:** Aunque haya un filtro para filtrar el curso por idioma, de momento solo contemplamos cursos en inglés. 
        """
    )

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

    # ===============================
    # 🔎 EXPLICABILIDAD PASO A PASO
    # ===============================
    with st.expander("🔎 Explicabilidad paso a paso", expanded=False):
        # st.subheader("🔎 Explicabilidad paso a paso")

        # 1) Profesión → DWAs con riesgo
        st.markdown("**1) DWAs de la ocupación y su riesgo**")
        risk_lookup = dict(zip(deg["dwa_norm"], deg["automation_quartile"]))
        dwas_table = pd.DataFrame({
            "DWA": [title_lut.get(d, d) for d in dwas_norm],
            "Riesgo": [risk_lookup.get(d, "Alto") for d in dwas_norm],
        }).sort_values(["Riesgo", "DWA"])
        st.dataframe(dwas_table, use_container_width=True)

        # 2) Para cada DWA en riesgo: mostrar vecinas y cuáles son seguras
        risky = [d for d in dwas_norm if risk_lookup.get(d, "Alto") == "Alto"]
        if risky:
            st.markdown("**2) Vecinas para DWAs en riesgo** (tomadas de `dwa_top3.csv`)")
            for d in risky:
                with st.expander(f"Vecinas de: {title_lut.get(d, d)} (riesgo: Alto)", expanded=False):
                    neigh_df = neighbor_table_for(d, neighbors_map, deg, title_lut)
                    if neigh_df.empty:
                        st.info("Sin vecinas registradas.")
                    else:
                        st.dataframe(neigh_df, use_container_width=True)
        else:
            st.caption("No hay DWAs en riesgo para esta ocupación.")

        # 3) Rutas efectivas (qué DWAs usamos finalmente) con etiqueta
        st.markdown("**3) Rutas usadas para continuar el flujo**")
        routes_df = pretty_routes_df(routes, deg, title_lut)
        st.dataframe(routes_df, use_container_width=True)

        # 4) DWAs de destino → skills (y nº cursos por skill)
        st.markdown("**4) Skills asociadas a las DWAs de destino y cobertura en cursos**")
        safe_titles = [title_lut.get(d, d) for d in safe_dwas]
        dest_to_skills = []
        # precomputo: nº de cursos por skill
        skill_course_counts = (
            courses[courses["skills_title"].isin(skills)]
            .groupby("skills_title")["url"]
            .nunique()
            .to_dict()
        )
        for d in safe_dwas:
            s_list = sorted(set(skills_map.get(d, [])))
            dest_to_skills.append({
                "DWA destino": title_lut.get(d, d),
                "Skills": s_list,
                "Nº skills": len(s_list),
                "Cursos/skill (resumen)": {s: skill_course_counts.get(s, 0) for s in s_list} if s_list else {},
            })
        if dest_to_skills:
            df_s = pd.DataFrame(dest_to_skills)
            st.dataframe(df_s, use_container_width=True)
        else:
            st.caption("Las DWAs de destino no tienen skills asociadas en `dwa_skill_top3.csv`.")

        # 5) Skills → cursos (muestra de ejemplo)
        st.markdown("**5) Muestra de cursos por skill (top 3 por skill)**")
        if skills:
            sample_rows = []
            for s in skills:
                sub = courses[courses["skills_title"] == s].head(3)[["name", "url", "language", "topics"]]
                if sub.empty:
                    sample_rows.append({"Skill": s, "Curso": "—", "URL": "—", "Idioma": "—", "Topics": "—"})
                else:
                    for _, r in sub.iterrows():
                        sample_rows.append({"Skill": s, "Curso": r["name"], "URL": r["url"], "Idioma": r["language"], "Topics": r["topics"]})
            st.dataframe(pd.DataFrame(sample_rows), use_container_width=True)
        else:
            st.caption("No se derivaron skills desde las DWAs de destino.")

