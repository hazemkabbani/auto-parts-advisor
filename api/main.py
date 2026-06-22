"""
Auto Parts Advisor API — FastAPI
"""
import sys, os, re, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/filters.db")

app = FastAPI(
    title="Auto Parts Advisor API",
    description="نظام توصية الفلاتر والزيوت للسيارات",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def smart_norm(s: str) -> str:
    """يحذف المسافات والرموز الخاصة للمقارنة الذكية"""
    return re.sub(r'[\s\-_/\.\(\)\+éèêëàâîïôûùç]', '', str(s)).upper()

def clean_text(s: str) -> str:
    """يزيل artifacts من PDF"""
    return re.sub(r'\(cid:\d+\)', '', str(s or '')).strip()


@app.get("/")
def root():
    return {"message": "Auto Parts Advisor API v2 ✅"}


# ══════════════════════════════════════════════════════════════
# 1. قائمة الشركات
# ══════════════════════════════════════════════════════════════
@app.get("/makes")
def makes():
    """كل الشركات من vehicle_filters"""
    db = get_db()
    rows = db.execute("""
        SELECT make, COUNT(*) as n FROM vehicle_filters
        WHERE make != '' AND (mann_oil!='' OR mann_air!='' OR mann_fuel!='')
        GROUP BY make ORDER BY n DESC
    """).fetchall()
    db.close()
    return {"makes": [r["make"] for r in rows]}


# ══════════════════════════════════════════════════════════════
# 2. موديلات شركة
# ══════════════════════════════════════════════════════════════
@app.get("/models")
def models(make: str = Query(...)):
    """موديلات شركة مع بحث ذكي في الاسم"""
    db = get_db()
    rows = db.execute("""
        SELECT DISTINCT model, COUNT(*) as n
        FROM vehicle_filters
        WHERE make = ?
          AND model != ''
          AND (mann_oil!='' OR mann_air!='' OR mann_fuel!='')
          AND model NOT LIKE '%Abgasnorm%'
          AND model NOT LIKE '%Anzahl%'
          AND model NOT LIKE '%Automatik%'
          AND model NOT LIKE '%Chassis%'
          AND model NOT LIKE '%EQUIPMENT%'
          AND model NOT LIKE '%CONSTRUCTION%'
          AND model NOT LIKE '%DITCHWITCH%'
          AND model NOT LIKE '%compressor%'
          AND model NOT LIKE '%Nebenstrom%'
          AND model NOT LIKE '%ChangeInterval%'
          AND model NOT LIKE '%fürOE%'
          AND model NOT LIKE '%useforOE%'
          AND model NOT LIKE '%BERNARD%'
          AND model NOT LIKE '%Getriebe%'
          AND model NOT LIKE '%Einbau%'
          AND model NOT LIKE '%teilweise%'
          AND model NOT LIKE '%Partikel%'
          AND model NOT LIKE '%Aktivkohle%'
          AND model NOT LIKE '%Biofunk%'
          AND model NOT LIKE '%Motorcode%'
          AND model NOT LIKE '%Alle Mod%'
          AND model NOT GLOB '[0-9]*'
          AND length(model) BETWEEN 2 AND 35
        GROUP BY model ORDER BY n DESC
    """, (make,)).fetchall()
    db.close()
    if not rows:
        raise HTTPException(404, detail="الشركة غير موجودة")
    return {"make": make, "models": [r["model"] for r in rows]}


# ══════════════════════════════════════════════════════════════
# 3. البحث الذكي الرئيسي
# ══════════════════════════════════════════════════════════════
@app.get("/search")
def smart_search(
    make:  str           = Query(..., description="الشركة"),
    model: Optional[str] = Query(None, description="الموديل"),
    year:  Optional[str] = Query(None, description="السنة"),
):
    """
    بحث ذكي — يتجاهل المسافات والأحرف الخاصة
    مثال: model=Corolla يجد CorollaX, CorollaIX, CorollaE210...
    """
    db = get_db()

    # ── بناء الاستعلام ──
    conditions = ["make = ?", "(mann_oil!='' OR mann_air!='' OR mann_fuel!='')"]
    params     = [make]

    if model:
        model_norm = smart_norm(model)
        conditions.append("""
            (REPLACE(REPLACE(REPLACE(REPLACE(UPPER(model),' ',''),'-',''),'/',''),'.','') LIKE ?
             OR REPLACE(REPLACE(REPLACE(REPLACE(UPPER(desc),' ',''),'-',''),'/',''),'.','') LIKE ?)
        """)
        params += [f"%{model_norm}%", f"%{model_norm}%"]

    if year:
        conditions.append("(year LIKE ? OR desc LIKE ?)")
        params += [f"%{year}%", f"%{year}%"]

    q = f"""
        SELECT make, model, year, desc,
               mann_air, mann_oil, mann_fuel, mann_cabin,
               wunder_air, wunder_oil, wunder_fuel, wunder_cabin,
               mc_air, mc_oil, mc_fuel, mc_cabin,
               source
        FROM vehicle_filters
        WHERE {' AND '.join(conditions)}
        ORDER BY
            CASE WHEN model LIKE ? THEN 0 ELSE 1 END,
            length(model)
        LIMIT 50
    """
    params.append(f"%{smart_norm(model or '')}%")

    rows = db.execute(q, params).fetchall()
    db.close()

    if not rows:
        raise HTTPException(404, detail=f"لم يتم العثور على {make} {model or ''}")

    def fmt(r):
        return {
            "make":   r["make"],
            "model":  r["model"],
            "year":   clean_text(r["year"]),
            "desc":   clean_text(r["desc"]),
            "filters": {
                "air":   {"mann": r["mann_air"],   "wunder": r["wunder_air"],  "mc": r["mc_air"]},
                "oil":   {"mann": r["mann_oil"],   "wunder": r["wunder_oil"],  "mc": r["mc_oil"]},
                "fuel":  {"mann": r["mann_fuel"],  "wunder": r["wunder_fuel"], "mc": r["mc_fuel"]},
                "cabin": {"mann": r["mann_cabin"], "wunder": r["wunder_cabin"],"mc": r["mc_cabin"]},
            },
            "source": r["source"],
        }

    return {"count": len(rows), "results": [fmt(r) for r in rows]}


# ══════════════════════════════════════════════════════════════
# 4. بحث برقم الفلتر (Cross-Reference)
# ══════════════════════════════════════════════════════════════
@app.get("/crossref")
def crossref(q: str = Query(..., description="أي رقم فلتر")):
    """ابحث بأي رقم → يطلع كل الأرقام المكافئة"""
    db = get_db()
    key = smart_norm(q)

    rows = db.execute("""
        SELECT DISTINCT cr.*
        FROM cross_ref cr
        JOIN cross_ref_index ci ON ci.ref_id = cr.id
        WHERE REPLACE(REPLACE(UPPER(ci.number_clean),' ',''),'-','') = ?
        LIMIT 20
    """, (key,)).fetchall()

    if not rows:
        # بحث جزئي
        rows = db.execute("""
            SELECT DISTINCT cr.*
            FROM cross_ref cr
            JOIN cross_ref_index ci ON ci.ref_id = cr.id
            WHERE REPLACE(REPLACE(UPPER(ci.number_clean),' ',''),'-','') LIKE ?
            LIMIT 20
        """, (f"%{key}%",)).fetchall()

    db.close()
    if not rows:
        raise HTTPException(404, detail=f"لم يتم العثور على '{q}'")

    type_ar = {"air":"هواء","oil":"زيت","fuel":"وقود","cabin":"كابين",
               "air_dryer":"جفف","water":"ماء","unknown":"","other":""}

    return {
        "query": q,
        "count": len(rows),
        "results": [{
            "wunder_no":   r["wunder_no"],
            "mc_no":       r["mc_no"],
            "mann_no":     r["mann_no"],
            "mahle_no":    r["mahle_no"],
            "hengst_no":   r["hengst_no"],
            "oem_no":      r["oem_no"],
            "filter_type": r["filter_type"],
            "filter_type_ar": type_ar.get(r["filter_type"], ""),
            "description": clean_text(r["description"]),
        } for r in rows]
    }


@app.get("/oil-grade")
def oil_grade(
    make:        str = Query(...),
    model:       str = Query(None),
    year:        int = Query(None),
    engine_type: str = Query(None),
):
    """درجة الزيت الموصى بها وموعد التغيير"""
    import sqlite3 as _sql, re as _re
    db = _sql.connect(os.path.join(os.path.dirname(__file__), "../data/filters.db"))
    db.row_factory = _sql.Row

    conditions = ["LOWER(make) = LOWER(?)"]
    params     = [make]

    if model:
        nm = _re.sub(r'[\s\-/\.]','',model).upper()
        conditions.append("REPLACE(REPLACE(UPPER(model),' ',''),'-','') LIKE ?")
        params.append(f"%{nm}%")

    if year:
        conditions.append("year_from <= ? AND year_to >= ?")
        params += [year, year]

    if engine_type:
        conditions.append("LOWER(engine_type) = LOWER(?)")
        params.append(engine_type)

    conditions.append("oil_grade != ''")
    oil_type_ar = {"Synthetic":"تركيبي","Semi-synthetic":"نصف تركيبي","Mineral":"معدني"}

    def raqqa_grade(official: str) -> dict:
        """توصية الرقة بناءً على الدرجة الرسمية"""
        g = official.upper().strip()
        if g in ("0W-20","0W-16","5W-20"):
            return {
                "grade":   "5W-30",
                "reason":  f"الكتاب يقول {official} — لكن للرقة (حرارة تصل 47°C) يُنصح بـ 5W-30 لحماية أفضل",
                "warning": True,
            }
        elif g == "5W-30":
            return {
                "grade":   "5W-30",
                "reason":  "مناسبة للرقة",
                "warning": False,
            }
        elif g in ("5W-40","5W-50"):
            return {
                "grade":   g,
                "reason":  "ممتازة للحرارة الشديدة",
                "warning": False,
            }
        elif g in ("10W-40","10W-30"):
            return {
                "grade":   g,
                "reason":  "مناسبة جداً للرقة وللسيارات الأكبر عمراً",
                "warning": False,
            }
        elif g in ("15W-40","15W-50","20W-50"):
            return {
                "grade":   g,
                "reason":  "للشاحنات والسيارات القديمة — مناسبة للحر",
                "warning": False,
            }
        return {"grade": g, "reason": "", "warning": False}

    rows = db.execute(
        f"SELECT DISTINCT year_from,year_to,engine_type,oil_grade,oil_type,change_interval_km,make,model FROM vehicles WHERE {' AND '.join(conditions)} ORDER BY year_from",
        params
    ).fetchall()
    db.close()

    if not rows:
        raise HTTPException(404, detail="لا توجد بيانات زيت لهذه السيارة")

    # إذا كل السنين نفس الدرجة — رجّع واحدة
    grades = list({r["oil_grade"] for r in rows})

    def fmt_row(r):
        rq = raqqa_grade(r["oil_grade"])
        return {
            "grade":    r["oil_grade"],
            "type":     r["oil_type"],
            "type_ar":  oil_type_ar.get(r["oil_type"], r["oil_type"]),
            "change_interval":         r["change_interval_km"],
            "change_interval_display": f"كل {r['change_interval_km']:,} كم",
            "raqqa": rq,
        }

    if len(grades) == 1 or year:
        r = rows[0]
        return {
            "make": r["make"], "model": r["model"],
            "year_from": r["year_from"], "year_to": r["year_to"],
            "needs_year": False,
            "oil": fmt_row(r),
        }

    # درجات مختلفة — لازم يحدد السنة
    return {
        "make": rows[0]["make"], "model": rows[0]["model"],
        "needs_year": True,
        "warning": f"⚠️ {rows[0]['make']} {rows[0]['model']} عندها {len(grades)} درجات زيت مختلفة حسب السنة — حدد سنة الصنع للحصول على الدرجة الصحيحة",
        "options": [
            {
                "years": f"{r['year_from']}–{r['year_to']}",
                "engine": r["engine_type"],
                **fmt_row(r),
            }
            for r in rows
        ]
    }


import urllib.request as _urlreq
import re as _re2

MANN_GQL = "https://www.mann-filter.com/api/graphql/catalog-prod"
MANN_HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json',
    'Referer': 'https://www.mann-filter.com/en/catalog.html',
    'Origin': 'https://www.mann-filter.com',
}

def _mann_gql(query: str, variables: dict = None):
    import json as _json
    body = _json.dumps({"query": query, "variables": variables or {}}).encode()
    req  = _urlreq.Request(MANN_GQL, body, MANN_HEADERS, method='POST')
    resp = _urlreq.urlopen(req, timeout=10)
    return _json.loads(resp.read())


@app.get("/vin/decode")
def decode_vin(
    vin: str = Query(..., description="رقم الشاصيه — 17 خانة"),
):
    """
    فك رقم الشاصيه وإرجاع معلومات السيارة + الفلاتر
    1. auto.dev  → make/model/year
    2. Mann GraphQL → make/model (fallback)
    3. vehicle_filters DB → أرقام الفلاتر
    4. vehicles DB → درجة الزيت
    """
    import urllib.request as ur
    import json as js

    vin = vin.strip().upper()
    if len(vin) != 17:
        raise HTTPException(400, detail="رقم الشاصيه يجب أن يكون 17 خانة")

    AUTO_DEV_KEY = "sk_ad_vRv2CCWwpr7sJp2Sv4HdqupM"
    make = model = year = engine = fuel_type = ""
    source = ""

    # ── الخطوة 1: auto.dev ──────────────────────────────────────────
    try:
        r = js.loads(ur.urlopen(
            ur.Request(f"https://auto.dev/api/vin/{vin}?apikey={AUTO_DEV_KEY}",
                       headers={'User-Agent':'Mozilla/5.0'}), timeout=8
        ).read())
        if r.get('make') and not r.get('status'):
            m  = r['make']
            mo = r.get('model', {})
            make  = (m.get('name') if isinstance(m,dict) else m or '').upper()
            model = mo.get('name') if isinstance(mo,dict) else mo or ''
            if r.get('year'): year = int(r['year'])
            eng = r.get('engine',{}) or {}
            if eng.get('size'): engine = f"{eng['size']}L"
            if eng.get('fuelType'): fuel_type = 'diesel' if 'diesel' in eng['fuelType'].lower() else 'gasoline'
            source = "auto.dev"
    except: pass

    # ── الخطوة 2: NHTSA fallback ────────────────────────────────────
    if not make or not model:
        try:
            r = js.loads(ur.urlopen(
                f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vin}?format=json",
                timeout=8
            ).read())['Results'][0]
            if not make  and r.get('Make'):     make  = r['Make'].upper()
            if not model and r.get('Model'):    model = r['Model']
            if not year  and r.get('ModelYear'): year = int(r['ModelYear'])
            if not fuel_type and r.get('FuelTypePrimary'):
                fuel_type = 'diesel' if 'diesel' in r['FuelTypePrimary'].lower() else 'gasoline'
            if make: source = source or "nhtsa"
        except: pass

    # ── الخطوة 3: Mann GraphQL fallback ─────────────────────────────
    mann_vehicles = []
    if not make or not model:
        try:
            r = _mann_gql("""
                query($v: String!) {
                  search_by_vin(vinNumber: $v) {
                    total_count
                    items {
                      vehicle_brand_name vehicle_name model_series_name
                      vehicle_manufactured_from vehicle_manufactured_to
                      fuel_type kw ccm engine_code model_series_id model_type_id
                    }
                  }
                }
            """, {"v": vin})
            items = (r.get('data') or {}).get('search_by_vin', {}).get('items') or []
            if items:
                best = items[0]
                if not make:  make  = best.get('vehicle_brand_name','').upper()
                if not model: model = best.get('model_series_name','')
                if not year and best.get('vehicle_manufactured_from'):
                    year = int(best['vehicle_manufactured_from'][:4])
                if not fuel_type:
                    fuel_type = 'diesel' if best.get('fuel_type','') == '08' else 'gasoline'
                mann_vehicles = items
                source = "mann_graphql"
        except: pass

    if not make:
        raise HTTPException(404, detail="تعذّر التعرف على السيارة من رقم الشاصيه")

    # ── الخطوة 4: البحث في قاعدة البيانات ──────────────────────────
    db = get_db()
    filters_result = None
    try:
        mn = _re2.sub(r'[\s\-/\.\(\)]','',model).upper()
        q = """
            SELECT make,model,year,desc,
                   mann_air,mann_oil,mann_fuel,mann_cabin,
                   wunder_air,wunder_oil,wunder_fuel,wunder_cabin,
                   mc_air,mc_oil,mc_fuel,mc_cabin
            FROM vehicle_filters
            WHERE make=?
              AND (REPLACE(REPLACE(UPPER(model),' ',''),'-','') LIKE ?
                   OR REPLACE(REPLACE(UPPER(desc),' ',''),'-','') LIKE ?)
              AND (mann_oil!='' OR mann_air!='' OR mann_fuel!='')
            ORDER BY CASE WHEN year LIKE ? THEN 0 ELSE 1 END
            LIMIT 5
        """
        yr_str = str(year) if year else ''
        rows = db.execute(q, (make, f"%{mn}%", f"%{mn}%", f"%{yr_str}%")).fetchall()

        if rows:
            def fmt(r):
                return {
                    "model":  r["model"],
                    "year":   r["year"],
                    "desc":   clean_text(r["desc"]),
                    "filters": {
                        "air":   {"mann":r["mann_air"],  "wunder":r["wunder_air"],  "mc":r["mc_air"]},
                        "oil":   {"mann":r["mann_oil"],  "wunder":r["wunder_oil"],  "mc":r["mc_oil"]},
                        "fuel":  {"mann":r["mann_fuel"], "wunder":r["wunder_fuel"], "mc":r["mc_fuel"]},
                        "cabin": {"mann":r["mann_cabin"],"wunder":r["wunder_cabin"],"mc":r["mc_cabin"]},
                    }
                }
            filters_result = [fmt(r) for r in rows]
    except: pass

    # ── الخطوة 5: درجة الزيت ────────────────────────────────────────
    oil_info = None
    try:
        mn2 = _re2.sub(r'[\s\-/\.]','',model).upper()
        conds = ["LOWER(make)=LOWER(?)", "oil_grade!=''"]
        params = [make]
        if model:
            conds.append("REPLACE(REPLACE(UPPER(model),' ',''),'-','') LIKE ?")
            params.append(f"%{mn2}%")
        if year:
            conds.append("year_from<=? AND year_to>=?")
            params += [year, year]

        row = db.execute(
            f"SELECT oil_grade,oil_type,change_interval_km FROM vehicles WHERE {' AND '.join(conds)} LIMIT 1",
            params
        ).fetchone()
        if row:
            oil_type_ar = {"Synthetic":"تركيبي","Semi-synthetic":"نصف تركيبي","Mineral":"معدني"}
            oil_info = {
                "grade": row["oil_grade"],
                "type_ar": oil_type_ar.get(row["oil_type"], row["oil_type"]),
                "change_interval_display": f"كل {row['change_interval_km']:,} كم",
            }
    except: pass
    db.close()

    return {
        "vin":    vin,
        "source": source,
        "vehicle": {
            "make":       make,
            "model":      model,
            "year":       year,
            "engine":     engine,
            "fuel_type":  fuel_type,
        },
        "mann_matches": mann_vehicles,
        "filters":  filters_result,
        "oil":      oil_info,
    }


# ── Static Files (Frontend) ──────────────────────────────────────
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os as _os2

_frontend_dir = _os2.path.join(_os2.path.dirname(__file__), "../frontend")
if _os2.path.exists(_frontend_dir):
    app.mount("/app", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

@app.get("/ui", include_in_schema=False)
def redirect_to_ui():
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/app/index.html")
