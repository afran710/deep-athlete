import pickle
import json
import csv
import streamlit as st

st.set_page_config(page_title="Deep Athlete", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600&display=swap');
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
    background:#030712 !important; color:#f1f5f9; font-family:'Inter',sans-serif;
}
[data-testid="stAppViewContainer"]::before {
    content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(0,200,80,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 110%, rgba(0,100,255,0.06) 0%, transparent 60%),
        repeating-linear-gradient(0deg, transparent, transparent 60px, rgba(255,255,255,0.013) 60px, rgba(255,255,255,0.013) 61px);
}
#MainMenu, footer, header, [data-testid="stToolbar"] { display:none !important; }
.block-container { padding:0 2rem 3rem !important; max-width:1400px !important; }
.hero { background:linear-gradient(135deg,#060d06,#08140f,#060a1a); border-bottom:1px solid rgba(0,255,80,0.12); padding:2.5rem 2rem 1.8rem; margin:0 -2rem 2rem; position:relative; }
.hero::after { content:''; position:absolute; bottom:0; left:0; right:0; height:1px; background:linear-gradient(90deg,transparent,#00ff50,#00ccff,transparent); }
.badge { display:inline-block; background:rgba(0,255,80,0.08); border:1px solid rgba(0,255,80,0.25); color:#00e567; font-size:0.68rem; letter-spacing:0.12em; text-transform:uppercase; padding:0.18rem 0.55rem; border-radius:2px; margin-right:0.4rem; }
.hero-title { font-family:'Bebas Neue',sans-serif; font-size:clamp(2.8rem,6vw,5rem); letter-spacing:0.04em; line-height:1; background:linear-gradient(90deg,#00ff50,#00ddff,#fff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin:0; }
.hero-sub { color:#4b5563; font-size:0.78rem; letter-spacing:0.18em; text-transform:uppercase; margin-top:0.35rem; }
.stat-row { display:grid; grid-template-columns:repeat(5,1fr); gap:0.9rem; margin-bottom:2rem; }
.sc { background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.07); border-radius:8px; padding:1.1rem 1rem; text-align:center; position:relative; overflow:hidden; }
.sc::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.sc.r::before{background:#ef4444;} .sc.y::before{background:#f59e0b;} .sc.g::before{background:#22c55e;} .sc.b::before{background:#3b82f6;} .sc.p::before{background:#a855f7;}
.sn { font-family:'Bebas Neue',sans-serif; font-size:2.8rem; line-height:1; }
.sl { font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase; color:#6b7280; margin-top:0.25rem; }
.sh { font-family:'Bebas Neue',sans-serif; font-size:1.5rem; letter-spacing:0.08em; color:#e2e8f0; border-left:3px solid #00ff50; padding-left:0.7rem; margin:1.6rem 0 0.9rem; }
.gender-card { border-radius:8px; padding:1rem 1.2rem; margin-bottom:1rem; border:1px solid rgba(255,255,255,0.08); }
.gender-card.male   { background:rgba(59,130,246,0.08); border-left:3px solid #3b82f6; }
.gender-card.female { background:rgba(236,72,153,0.08); border-left:3px solid #ec4899; }
.result-box { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:1.6rem; margin-top:1rem; }
.big-pct { font-family:'Bebas Neue',sans-serif; font-size:5.5rem; line-height:1; }
.zone-tag { display:inline-block; font-family:'Bebas Neue',sans-serif; font-size:1.3rem; letter-spacing:0.1em; padding:0.25rem 0.9rem; border-radius:3px; margin-top:0.4rem; }
.zone-tag.RED    { background:rgba(239,68,68,0.12);  color:#ef4444; border:1px solid rgba(239,68,68,0.35); }
.zone-tag.YELLOW { background:rgba(245,158,11,0.12); color:#f59e0b; border:1px solid rgba(245,158,11,0.35); }
.zone-tag.GREEN  { background:rgba(34,197,94,0.12);  color:#22c55e; border:1px solid rgba(34,197,94,0.35); }
.track { background:rgba(255,255,255,0.06); border-radius:6px; height:18px; overflow:hidden; margin:0.8rem 0; }
.fill  { height:100%; border-radius:6px; }
.tlabels { display:flex; justify-content:space-between; font-size:0.62rem; color:#4b5563; text-transform:uppercase; letter-spacing:0.07em; }
.advice-box { font-size:0.82rem; color:#94a3b8; background:rgba(255,255,255,0.03); border-radius:6px; padding:0.7rem 0.9rem; margin-top:0.8rem; }
.pills { display:flex; flex-wrap:wrap; gap:0.45rem; margin-top:0.8rem; }
.pill { font-size:0.7rem; padding:0.22rem 0.55rem; border-radius:3px; letter-spacing:0.05em; text-transform:uppercase; font-weight:600; }
.pill.hi { background:rgba(239,68,68,0.12);  color:#ef4444; border:1px solid rgba(239,68,68,0.28); }
.pill.md { background:rgba(245,158,11,0.12); color:#f59e0b; border:1px solid rgba(245,158,11,0.28); }
.pill.lo { background:rgba(34,197,94,0.12);  color:#22c55e; border:1px solid rgba(34,197,94,0.28); }
.model-tag { display:inline-block; font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase; padding:0.2rem 0.6rem; border-radius:3px; margin-bottom:0.5rem; }
.model-tag.male   { background:rgba(59,130,246,0.12); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
.model-tag.female { background:rgba(236,72,153,0.12); color:#f472b6; border:1px solid rgba(236,72,153,0.3); }
[data-testid="stTabs"] button { font-family:'Bebas Neue',sans-serif !important; font-size:0.95rem !important; letter-spacing:0.08em !important; color:#6b7280 !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#00ff50 !important; border-bottom-color:#00ff50 !important; }
[data-testid="stMetricValue"] { font-family:'Bebas Neue',sans-serif !important; font-size:1.9rem !important; }
[data-testid="stMetricLabel"] { font-size:0.68rem !important; letter-spacing:0.08em !important; text-transform:uppercase !important; color:#6b7280 !important; }
[data-testid="stButton"]>button { background:linear-gradient(135deg,#00ff50,#00c840) !important; color:#030712 !important; font-family:'Bebas Neue',sans-serif !important; font-size:1.1rem !important; letter-spacing:0.1em !important; border:none !important; border-radius:4px !important; }
</style>
""", unsafe_allow_html=True)

# ── Load models ──
@st.cache_resource
def load_models():
    with open("model.pkl","rb") as f:
        d = pickle.load(f)
    return d["male"], d["female"], d["feature_names"]

# ── Load summary CSV ──
@st.cache_data
def load_summary():
    rows = []
    with open("summary.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append((
                row["athlete_id"],
                row["name"],
                int(row["age"]) if row["age"] else 0,
                row["gender"],
                row["lifestyle"],
                float(row["vo2max"]) if row["vo2max"] else 0,
                float(row["recovery_rate"]) if row["recovery_rate"] else 0,
                float(row["acwr"]) if row["acwr"] else 0,
                row["risk_zone"],
                float(row["sleep_avg"]) if row["sleep_avg"] else 0,
                float(row["stress_avg"]) if row["stress_avg"] else 0,
                float(row["hrv_drop"]) if row["hrv_drop"] else 0,
                row["date"],
            ))
    return rows

male_model, female_model, feat_names = load_models()
data         = load_summary()
zc           = {"RED":"#ef4444","YELLOW":"#f59e0b","GREEN":"#22c55e","LOW":"#a855f7"}
male_count   = sum(1 for r in data if r[3] and r[3].lower()=="male")
female_count = sum(1 for r in data if r[3] and r[3].lower()=="female")

ZONE_LABEL = {"RED":"🔴 High Risk","YELLOW":"🟡 Monitor","GREEN":"🟢 Safe","LOW":"🟣 Undertrained"}
LABEL_ZONE = {v: k for k, v in ZONE_LABEL.items()}

st.markdown(f"""
<div class="hero">
  <div style="margin-bottom:0.6rem">
    <span class="badge">⚡ Live</span><span class="badge">Dual ML Models</span>
    <span class="badge">👨 {male_count} Male</span><span class="badge">👩 {female_count} Female</span>
    <span class="badge">77.5% Recall</span>
  </div>
  <div class="hero-title">Deep Athlete</div>
  <div class="hero-sub">Gender-Specific Injury Risk Intelligence · XGBoost · 366 Days Daily Data</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚡  TEAM DASHBOARD", "🔍  PREDICT A PLAYER"])

# ══════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════
with tab1:
    total=len(data); red=sum(1 for r in data if r[8]=="RED")
    yellow=sum(1 for r in data if r[8]=="YELLOW"); green=sum(1 for r in data if r[8]=="GREEN")
    low=sum(1 for r in data if r[8]=="LOW")

    st.markdown(f"""
    <div class="stat-row">
      <div class="sc b"><div class="sn">{total}</div><div class="sl">Total Athletes</div></div>
      <div class="sc r"><div class="sn">{red}</div><div class="sl">🔴 High Risk</div></div>
      <div class="sc y"><div class="sn">{yellow}</div><div class="sl">🟡 Monitor</div></div>
      <div class="sc g"><div class="sn">{green}</div><div class="sl">🟢 Safe</div></div>
      <div class="sc p"><div class="sn">{low}</div><div class="sl">🟣 Undertrained</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">Gender Model Overview</div>', unsafe_allow_html=True)
    gm1, gm2 = st.columns(2)
    with gm1:
        st.markdown(f"""<div class="gender-card male">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:#60a5fa;letter-spacing:0.08em">👨 Male Model</div>
          <div style="font-size:0.8rem;color:#94a3b8;margin-top:0.3rem">{male_count} athletes · 203,739 rows · 76.1% recall</div>
          <div style="font-size:0.75rem;color:#6b7280;margin-top:0.4rem">Top factors: Stress · Recovery Rate · HRV · Age</div>
        </div>""", unsafe_allow_html=True)
    with gm2:
        st.markdown(f"""<div class="gender-card female">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:#f472b6;letter-spacing:0.08em">👩 Female Model</div>
          <div style="font-size:0.8rem;color:#94a3b8;margin-top:0.3rem">{female_count} athletes · 135,261 rows · 77.5% recall</div>
          <div style="font-size:0.75rem;color:#6b7280;margin-top:0.4rem">Top factors: Stress · Recovery Rate · Body Battery · Age</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">Filter Athletes</div>', unsafe_allow_html=True)
    fa,fb,fc,fd = st.columns(4)
    with fa:
        zf_sel = st.multiselect("🎯 Risk Zone", list(ZONE_LABEL.values()), default=list(ZONE_LABEL.values()))
        zf = [LABEL_ZONE[z] for z in zf_sel] if zf_sel else list(ZONE_LABEL.keys())
    with fb:
        ls_opts = sorted(set(r[4] for r in data if r[4]))
        lf = st.multiselect("🏃 Lifestyle", ls_opts, default=ls_opts)
        lf = lf if lf else ls_opts
    with fc:
        gf = st.multiselect("⚧ Gender", ["male","female"], default=["male","female"])
        gf = gf if gf else ["male","female"]
    with fd:
        ma = st.slider("📊 Min ACWR", 0.0, 2.5, 0.0, step=0.05)

    fe,ff,fg,fh = st.columns(4)
    with fe: age_range = st.slider("🎂 Age Range", 16, 50, (16, 50))
    with ff: vo2_range = st.slider("💨 VO2 Max Range", 25.0, 80.0, (25.0, 80.0), step=0.5)
    with fg: sleep_range = st.slider("😴 Sleep Avg Range", 4.0, 10.0, (4.0, 10.0), step=0.1)
    with fh: stress_range = st.slider("😰 Stress Range", 0.0, 100.0, (0.0, 100.0), step=0.5)

    filtered = [r for r in data
                if r[8] in zf and r[4] in lf and r[3] in gf and r[7] >= ma
                and age_range[0] <= (r[2] or 0) <= age_range[1]
                and vo2_range[0] <= (r[5] or 0) <= vo2_range[1]
                and sleep_range[0] <= (r[9] or 0) <= sleep_range[1]
                and stress_range[0] <= (r[10] or 0) <= stress_range[1]]

    st.markdown('<div class="sh">Sort & Display</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        sort_by = st.selectbox("Sort By", [
            "ACWR (High to Low)","ACWR (Low to High)",
            "Age (High to Low)","Age (Low to High)",
            "Stress (High to Low)","Sleep (Low to High)",
            "VO2 Max (High to Low)","Recovery Rate (High to Low)",
            "Name (A to Z)","Name (Z to A)",
        ])
    with s2:
        show_top = st.selectbox("Show Top", [25, 50, 80, 100, "All"], index=1)

    sort_map = {
        "ACWR (High to Low)":          (lambda r: r[7],       True),
        "ACWR (Low to High)":          (lambda r: r[7],       False),
        "Age (High to Low)":           (lambda r: r[2] or 0,  True),
        "Age (Low to High)":           (lambda r: r[2] or 0,  False),
        "Stress (High to Low)":        (lambda r: r[10] or 0, True),
        "Sleep (Low to High)":         (lambda r: r[9] or 0,  False),
        "VO2 Max (High to Low)":       (lambda r: r[5] or 0,  True),
        "Recovery Rate (High to Low)": (lambda r: r[6] or 0,  True),
        "Name (A to Z)":               (lambda r: r[1] or "", False),
        "Name (Z to A)":               (lambda r: r[1] or "", True),
    }
    if sort_by not in sort_map: sort_by = "ACWR (High to Low)"
    key_fn, reverse = sort_map[sort_by]
    filtered = sorted(filtered, key=key_fn, reverse=reverse)
    limit = len(filtered) if show_top == "All" else int(show_top)
    st.caption(f"Showing **{min(limit,len(filtered))}** of **{len(filtered)}** athletes · sorted by **{sort_by}**")

    st.markdown('<div class="sh">Athlete Risk Table</div>', unsafe_allow_html=True)
    for row in filtered[:limit]:
        aid=row[0]; name=row[1]; age=row[2]; gender=row[3]
        vo2=row[5]; rec=row[6]; acwr=row[7]; zone=row[8]
        sleep=row[9]; stress=row[10]; date=row[12]
        bc=zc.get(zone,"#a855f7"); pct=min(int(acwr/2.5*100),100)
        ico=ZONE_LABEL.get(zone,"⚪").split()[0]
        gico="👨" if gender and gender.lower()=="male" else "👩"
        zlabel=ZONE_LABEL.get(zone,zone)
        with st.expander(f"{ico} {gico}  {name}  ·  ACWR {acwr:.3f}  ·  {zlabel}  ·  {date}"):
            c1,c2,c3,c4,c5,c6 = st.columns(6)
            c1.metric("Age",age); c2.metric("Gender",gender); c3.metric("VO2 Max",f"{vo2:.0f}")
            c4.metric("Sleep Avg",f"{sleep:.1f}h" if sleep else "—")
            c5.metric("Stress",f"{stress:.1f}" if stress else "—"); c6.metric("Recovery",f"{rec:.2f}")
            st.markdown(f"""
            <div style="margin-top:0.9rem">
              <div style="font-size:0.68rem;color:#6b7280;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:5px">ACWR — Sweet spot 0.8–1.3</div>
              <div style="display:flex;align-items:center;gap:1rem">
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2rem;color:{bc};min-width:55px">{acwr:.3f}</div>
                <div style="flex:1;background:rgba(255,255,255,0.06);border-radius:4px;height:8px;overflow:hidden">
                  <div style="width:{pct}%;height:100%;background:{bc};box-shadow:0 0 8px {bc}55;border-radius:4px"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sh">Breakdown by Lifestyle</div>', unsafe_allow_html=True)
    grps = {}
    for r in data:
        g=r[4]
        if g not in grps: grps[g]={"n":0,"red":0,"s":0}
        grps[g]["n"]+=1; grps[g]["s"]+=r[7]
        if r[8]=="RED": grps[g]["red"]+=1
    cols = st.columns(len(grps))
    for i,(g,s) in enumerate(sorted(grps.items())):
        with cols[i]:
            st.metric(g[:15], f"{s['s']/s['n']:.2f} ACWR")
            st.caption(f"🔴 {s['red']} / {s['n']} athletes")

# ══════════════════════════════════════════
# TAB 2 — Predict
# ══════════════════════════════════════════
with tab2:
    st.markdown('<div class="sh">Predict Injury Risk</div>', unsafe_allow_html=True)
    st.caption("Gender-specific model selected automatically")

    gender_sel     = st.radio("Athlete Gender", ["👨 Male","👩 Female"], horizontal=True)
    is_male        = gender_sel == "👨 Male"
    selected_model = male_model if is_male else female_model
    model_label    = "male" if is_male else "female"
    recall_pct     = "76.1%" if is_male else "77.5%"

    st.markdown(f"""<div class="model-tag {model_label}">
      {'👨 Male Model' if is_male else '👩 Female Model'} · Recall {recall_pct} ·
      {'203,739 training rows' if is_male else '135,261 training rows'}
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        name         = st.text_input("Player Name", placeholder="e.g. Rahul Sharma")
        age          = st.slider("Age", 16, 40, 22)
        acwr_i       = st.slider("ACWR", 0.0, 2.5, 1.0, step=0.01, help="Sweet spot: 0.8–1.3")
        acute_load   = st.slider("Acute Load (7-day TSS)", 0, 1000, 300)
        chronic_load = st.slider("Chronic Load (28-day avg×7)", 0, 1000, 300)
        hrv_drop     = st.slider("HRV Drop", -20.0, 20.0, 0.0, step=0.5)
        sleep_avg    = st.slider("Avg Sleep (7 days)", 4.0, 12.0, 7.5, step=0.1)
        stress_avg   = st.slider("Avg Stress (7 days)", 0.0, 100.0, 25.0, step=0.5)
    with c2:
        resting_hr   = st.slider("Resting Heart Rate", 35, 90, 55)
        hrv          = st.slider("Today's HRV", 20, 120, 65)
        body_bat_am  = st.slider("Body Battery Morning", 0, 100, 70,
                                  help="⭐ Most important for female athletes" if not is_male else "Body battery on waking")
        body_bat_pm  = st.slider("Body Battery Evening", 0, 100, 40)
        vo2max       = st.slider("VO2 Max", 25.0, 80.0, 50.0, step=0.5)
        recovery     = st.slider("Recovery Rate", 0.0, 1.0, 0.6, step=0.01,
                                  help="⚠️ Higher recovery rate may increase predicted risk — fast-recovering athletes tend to train more aggressively in the data.")
        hrv_baseline = st.slider("HRV Baseline", 20, 120, 65)
        weekly_hrs   = st.slider("Weekly Training Hours", 1.0, 30.0, 10.0, step=0.5)

    if not is_male:
        st.info("💡 **Female model insight:** Body Battery Morning is the strongest predictor for female athletes.")
    st.caption("⚠️ **Model note:** Higher Recovery Rate may slightly increase predicted risk — this reflects training behaviour correlation, not recovery quality alone.")

    st.write("")
    if st.button("⚡  PREDICT INJURY RISK", use_container_width=True):
        feats = [[float(acwr_i),float(acute_load),float(chronic_load),float(hrv_drop),
                  float(sleep_avg),float(stress_avg),float(resting_hr),float(hrv),
                  float(body_bat_am),float(body_bat_pm),float(age),float(vo2max),
                  float(recovery),float(hrv_baseline),float(weekly_hrs)]]

        prob     = float(selected_model.predict_proba(feats)[0][1])
        prob_pct = round(prob*100, 1)

        problems=[]; improvements=[]

        if stress_avg > 60:
            problems.append("🔴 Stress critically high")
            improvements.append("Introduce meditation, breathing exercises and reduce match intensity")
        elif stress_avg > 40:
            problems.append("🟡 Stress elevated")
            improvements.append("Schedule a rest day and reduce training volume by 20%")

        if sleep_avg < 6:
            problems.append("🔴 Severely sleep deprived")
            improvements.append("Target minimum 8hrs sleep — avoid screens 1hr before bed")
        elif sleep_avg < 7:
            problems.append("🟡 Sleep below optimal")
            improvements.append("Aim for 7.5–9hrs sleep — consider a sleep tracking routine")

        if acwr_i > 1.5:
            problems.append("🔴 ACWR in danger zone — workload spiked too fast")
            improvements.append("Cut training load by 30–40% this week and reintroduce gradually")
        elif acwr_i > 1.3:
            problems.append("🟡 ACWR above sweet spot")
            improvements.append("Hold current load — do not increase intensity this week")

        if hrv_drop > 8:
            problems.append("🔴 HRV dropped sharply — body under stress")
            improvements.append("Full rest day today — monitor HRV for 3 consecutive days")
        elif hrv_drop > 4:
            problems.append("🟡 HRV slightly low")
            improvements.append("Light recovery session only — no high intensity work")

        if body_bat_am < 30:
            problems.append("🔴 Body battery critically low — poor overnight recovery")
            improvements.append("No training today — prioritise sleep and nutrition")
        elif body_bat_am < 50:
            problems.append("🟡 Body battery below optimal")
            improvements.append("Reduce session intensity by 25% today")

        if resting_hr > 75:
            problems.append("🟡 Resting heart rate elevated — possible fatigue or illness")
            improvements.append("Monitor for 48hrs — if persistent consult medical staff")

        if recovery < 0.4:
            problems.append("🔴 Recovery rate critically low — athlete not recovering between sessions")
            improvements.append("Add 2 full rest days this week — no training at all")
        elif recovery < 0.6:
            problems.append("🟡 Recovery rate below optimal")
            improvements.append("Reduce training frequency — allow 48hrs between hard sessions")

        if not problems:
            risk_scores_f = {
                "Stress":       stress_avg/100,
                "Sleep":        max(0,(8-sleep_avg)/4),
                "ACWR":         max(0,(acwr_i-0.8)/0.7),
                "HRV Drop":     max(0,hrv_drop/20),
                "Body Battery": max(0,(100-body_bat_am)/100),
                "Resting HR":   max(0,(resting_hr-55)/35),
                "Acute Load":   max(0,(acute_load-200)/800),
            }
            improve_map = {
                "Stress":"Reduce mental and physical stress load this week",
                "Sleep":"Increase sleep by 30–60 mins — even small gains help recovery",
                "ACWR":"Avoid increasing training intensity for the next 5 days",
                "HRV Drop":"Prioritise recovery — light session or full rest today",
                "Body Battery":"Focus on sleep quality and reduce evening screen time",
                "Resting HR":"Monitor daily — elevated HR can signal early fatigue",
                "Acute Load":"Hold training load steady — do not add sessions this week",
            }
            top3 = sorted(risk_scores_f.items(), key=lambda x: x[1], reverse=True)[:3]
            for fname, fscore in top3:
                level = "critically low" if fname=="Sleep" and fscore>0.6 else "moderately elevated" if fscore>0.3 else "slightly above optimal"
                problems.append(f"🟡 {fname} is {level} — contributing to combined risk")
                improvements.append(improve_map.get(fname,"Monitor this metric closely"))

        if prob_pct >= 60:
            zone,label,bc = "RED","HIGH RISK","#ef4444"
            advice = "🚨 Rest this athlete immediately. Do not increase training load this week. Schedule physio review."
        elif prob_pct >= 40:
            zone,label,bc = "YELLOW","MONITOR CLOSELY","#f59e0b"
            advice = "⚠️ Reduce intensity. Monitor HRV and sleep daily. Avoid back-to-back hard sessions."
        else:
            zone,label,bc = "GREEN","SAFE TO TRAIN","#22c55e"
            advice = "✅ Athlete is well recovered. Safe to train at full intensity today."

        factors = {
            "Stress":stress_avg/100,"ACWR":max(0,(acwr_i-0.8)/0.7),
            "HRV Drop":max(0,hrv_drop/20),"Low Sleep":max(0,(8.0-sleep_avg)/4.0),
            "Low Battery":max(0,(100-body_bat_am)/100),
        }
        ranked = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        pills  = "".join(
            f'<span class="pill {"hi" if s>0.66 else "md" if s>0.33 else "lo"}">'
            f'{n}: {"▲ HIGH" if s>0.66 else "● MED" if s>0.33 else "▼ LOW"}</span>'
            for n,s in ranked
        )
        problems_html = "".join(
            f'<div style="font-size:0.8rem;color:#fca5a5;margin-bottom:0.5rem">{p}</div>'
            for p in problems
        ) if problems else '<div style="font-size:0.8rem;color:#6b7280">No critical issues detected</div>'

        improvements_html = "".join(
            f'<div style="font-size:0.8rem;color:#86efac;margin-bottom:0.5rem">→ {i}</div>'
            for i in improvements
        ) if improvements else '<div style="font-size:0.8rem;color:#6b7280">Keep current routine</div>'

        pname = name.strip() if name.strip() else "Athlete"
        gicon = "👨" if is_male else "👩"

        st.markdown(f"""
        <div class="result-box">
          <div style="margin-bottom:0.5rem">
            <span class="model-tag {model_label}">{gicon} {model_label.title()} Model · Recall {recall_pct}</span>
          </div>
          <div style="display:flex;align-items:flex-start;gap:2rem;flex-wrap:wrap">
            <div>
              <div style="font-size:0.68rem;color:#6b7280;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem">{pname} — Injury Probability</div>
              <div class="big-pct" style="color:{bc}">{prob_pct}%</div>
              <div class="zone-tag {zone}">{label}</div>
            </div>
            <div style="flex:1;min-width:220px">
              <div class="track"><div class="fill" style="width:{prob_pct}%;background:{bc}"></div></div>
              <div class="tlabels"><span>0% Safe</span><span>40%</span><span>60%</span><span>100%</span></div>
              <div class="advice-box" style="border-left:3px solid {bc}">{advice}</div>
            </div>
          </div>
          <div style="margin-top:1rem">
            <div style="font-size:0.65rem;color:#4b5563;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem">Key Risk Factors</div>
            <div class="pills">{pills}</div>
          </div>
          <div style="margin-top:1.2rem;display:grid;grid-template-columns:1fr 1fr;gap:1rem">
            <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);border-radius:8px;padding:1rem">
              <div style="font-size:0.68rem;color:#ef4444;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;font-weight:600">⚠ Problems Detected</div>
              {problems_html}
            </div>
            <div style="background:rgba(34,197,94,0.06);border:1px solid rgba(34,197,94,0.2);border-radius:8px;padding:1rem">
              <div style="font-size:0.68rem;color:#22c55e;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;font-weight:600">💡 Recommended Improvements</div>
              {improvements_html}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)