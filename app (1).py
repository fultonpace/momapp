"""
ChromaLogic — Emotional Color Palette Generator
Generates color palettes from three orthogonal emotional dimensions.
"""

import streamlit as st
import colorsys
import hashlib
import math
import random

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChromaLogic",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Adjective taxonomy ─────────────────────────────────────────────────────────
# Dimension 1 — VALENCE (hedonic tone: pleasant ↔ unpleasant)
VALENCE = [
    "Euphoric",
    "Joyful",
    "Serene",
    "Wistful",
    "Melancholic",
    "Desolate",
    "Tender",
    "Bitter",
    "Content",
    "Anguished",
    "Hopeful",
    "Forlorn",
]

# Dimension 2 — AROUSAL (energy: activated ↔ deactivated)
AROUSAL = [
    "Frenzied",
    "Invigorated",
    "Restless",
    "Languid",
    "Dormant",
    "Electrified",
    "Hushed",
    "Turbulent",
    "Meditative",
    "Volatile",
    "Lethargic",
    "Pulsing",
]

# Dimension 3 — STANCE (relational posture: open ↔ closed)
STANCE = [
    "Expansive",
    "Surrendered",
    "Defiant",
    "Withdrawn",
    "Yielding",
    "Confrontational",
    "Embracing",
    "Guarded",
    "Dissolving",
    "Sovereign",
    "Receptive",
    "Armored",
]

# ── Color generation engine ────────────────────────────────────────────────────
# Maps each adjective to a triplet of HSL offsets (hue shift, sat mod, light mod)
# These are deterministic—same words always yield same palette.

ADJECTIVE_HSL_MAP = {
    # VALENCE
    "Euphoric":    (0.08,  0.30,  0.15),
    "Joyful":      (0.12,  0.25,  0.10),
    "Serene":      (0.55,  0.10,  0.05),
    "Wistful":     (0.62,  0.05, -0.05),
    "Melancholic": (0.66, -0.10, -0.10),
    "Desolate":    (0.58, -0.25, -0.20),
    "Tender":      (0.95,  0.15,  0.08),
    "Bitter":      (0.28, -0.15, -0.08),
    "Content":     (0.35,  0.08,  0.03),
    "Anguished":   (0.72, -0.20, -0.15),
    "Hopeful":     (0.18,  0.20,  0.12),
    "Forlorn":     (0.60, -0.18, -0.12),
    # AROUSAL
    "Frenzied":    (0.02,  0.35,  0.05),
    "Invigorated": (0.10,  0.28,  0.08),
    "Restless":    (0.45,  0.15, -0.03),
    "Languid":     (0.50, -0.12, -0.05),
    "Dormant":     (0.55, -0.22, -0.18),
    "Electrified": (0.15,  0.40,  0.10),
    "Hushed":      (0.48, -0.20, -0.08),
    "Turbulent":   (0.03,  0.30,  0.02),
    "Meditative":  (0.58,  0.05, -0.02),
    "Volatile":    (0.05,  0.38,  0.08),
    "Lethargic":   (0.52, -0.28, -0.15),
    "Pulsing":     (0.00,  0.32,  0.06),
    # STANCE
    "Expansive":   (0.20,  0.22,  0.12),
    "Surrendered": (0.72,  0.10, -0.05),
    "Defiant":     (0.02,  0.28,  0.05),
    "Withdrawn":   (0.62, -0.18, -0.12),
    "Yielding":    (0.80,  0.08, -0.02),
    "Confrontational": (0.00, 0.32, 0.08),
    "Embracing":   (0.92,  0.18,  0.06),
    "Guarded":     (0.45, -0.15, -0.10),
    "Dissolving":  (0.68,  0.05, -0.08),
    "Sovereign":   (0.12,  0.20,  0.03),
    "Receptive":   (0.30,  0.14,  0.08),
    "Armored":     (0.55, -0.25, -0.15),
}

def _seed_from_combo(v: str, a: str, s: str) -> int:
    key = f"{v}|{a}|{s}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**31)

def _clamp(val, lo=0.0, hi=1.0):
    return max(lo, min(hi, val))

def _hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

def _hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def _luminance(hex_str):
    r, g, b = [x/255.0 for x in _hex_to_rgb(hex_str)]
    def lin(c):
        return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
    return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)

def _contrast_color(hex_str):
    return "#0a0a0a" if _luminance(hex_str) > 0.35 else "#f5f5f0"

def generate_palette(valence: str, arousal: str, stance: str) -> list[dict]:
    """Generate a 7-swatch palette deterministically from three adjectives."""
    seed = _seed_from_combo(valence, arousal, stance)
    rng = random.Random(seed)

    dv = ADJECTIVE_HSL_MAP[valence]
    da = ADJECTIVE_HSL_MAP[arousal]
    ds = ADJECTIVE_HSL_MAP[stance]

    # Base hue is a blend of three adjective hue shifts
    base_h = (dv[0]*0.45 + da[0]*0.35 + ds[0]*0.20) % 1.0
    base_s = _clamp(0.55 + dv[1]*0.5 + da[1]*0.3 + ds[1]*0.2)
    base_l = _clamp(0.50 + dv[2]*0.5 + da[2]*0.3 + ds[2]*0.2)

    # Harmony angle: choose from common color harmonies seeded by combo
    harmonies = [
        [0, 0.5],                          # complementary
        [0, 1/3, 2/3],                     # triadic
        [0, 30/360, 60/360],               # analogous
        [0, 150/360, 210/360],             # split-complementary
        [0, 90/360, 180/360, 270/360],     # tetradic
    ]
    hue_offsets = rng.choice(harmonies)

    swatches = []
    n_target = 7
    swatch_count = 0

    for offset in hue_offsets:
        if swatch_count >= n_target:
            break
        hue = (base_h + offset) % 1.0
        # Lightness variation for each offset
        for l_shift in [0.12, -0.12, 0.0]:
            if swatch_count >= n_target:
                break
            l = _clamp(base_l + l_shift + rng.uniform(-0.05, 0.05))
            s = _clamp(base_s + rng.uniform(-0.08, 0.08))
            hex_c = _hsl_to_hex(hue, s, l)
            swatches.append({
                "hex": hex_c,
                "h": round(hue * 360, 1),
                "s": round(s * 100, 1),
                "l": round(l * 100, 1),
                "text": _contrast_color(hex_c),
            })
            swatch_count += 1

    return swatches[:n_target]

def palette_name(valence, arousal, stance):
    """Compose a poetic name from the three descriptors."""
    return f"{valence} · {arousal} · {stance}"

# ── CSS injection ──────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Mono:wght@300;400;500&display=swap');

    :root {
        --bg: #0d0d0f;
        --bg2: #15151a;
        --border: rgba(255,255,255,0.07);
        --muted: rgba(255,255,255,0.35);
        --accent: #c8a96e;
        --text: #e8e4dc;
    }

    html, body, .stApp {
        background-color: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Cormorant Garamond', Georgia, serif !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem 4rem !important; max-width: 1100px; }

    /* Title area */
    .chroma-title {
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 3.8rem;
        font-weight: 300;
        letter-spacing: 0.18em;
        color: var(--text);
        margin-bottom: 0.1em;
        line-height: 1;
    }
    .chroma-subtitle {
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.25em;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 2.5rem;
    }

    /* Dimension labels */
    .dim-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.3em;
        color: var(--accent);
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    /* Override Streamlit selectbox */
    .stSelectbox > div > div {
        background-color: var(--bg2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 2px !important;
        color: var(--text) !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.05rem !important;
    }
    .stSelectbox label {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.65rem !important;
        letter-spacing: 0.25em !important;
        color: var(--accent) !important;
        text-transform: uppercase !important;
    }

    /* Palette display */
    .palette-row {
        display: flex;
        width: 100%;
        border-radius: 4px;
        overflow: hidden;
        margin: 2rem 0 1.5rem;
        box-shadow: 0 8px 48px rgba(0,0,0,0.5);
    }
    .swatch {
        flex: 1;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 12px 10px;
        transition: flex 0.3s ease;
        position: relative;
        cursor: default;
    }
    .swatch:hover { flex: 1.6; }
    .swatch-hex {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        opacity: 0.85;
        margin-bottom: 3px;
        text-transform: uppercase;
    }
    .swatch-hsl {
        font-family: 'DM Mono', monospace;
        font-size: 0.52rem;
        letter-spacing: 0.05em;
        opacity: 0.55;
    }

    /* Palette name */
    .palette-name {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem;
        font-style: italic;
        font-weight: 300;
        color: var(--muted);
        letter-spacing: 0.06em;
        margin-bottom: 2rem;
    }

    /* Emotion map chip */
    .emotion-chips {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
    }
    .chip {
        font-family: 'DM Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        padding: 4px 10px;
        border: 1px solid var(--border);
        border-radius: 1px;
        color: var(--muted);
    }
    .chip.dim-v { border-color: rgba(200, 169, 110, 0.4); color: rgba(200, 169, 110, 0.8); }
    .chip.dim-a { border-color: rgba(110, 160, 200, 0.4); color: rgba(110, 160, 200, 0.8); }
    .chip.dim-s { border-color: rgba(160, 200, 110, 0.4); color: rgba(160, 200, 110, 0.8); }

    /* Copy grid */
    .hex-grid {
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    .hex-pill {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.12em;
        padding: 5px 10px;
        border-radius: 2px;
        border: 1px solid var(--border);
        color: var(--muted);
        text-transform: uppercase;
    }

    /* Divider */
    .thin-rule {
        border: none;
        border-top: 1px solid var(--border);
        margin: 2rem 0;
    }

    /* Shuffle button */
    .stButton > button {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.25em !important;
        text-transform: uppercase !important;
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--muted) !important;
        padding: 10px 28px !important;
        border-radius: 2px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* Section header */
    .section-head {
        font-family: 'DM Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.3em;
        color: var(--muted);
        text-transform: uppercase;
        margin: 1.5rem 0 0.8rem;
    }

    /* Footer */
    .chroma-footer {
        font-family: 'DM Mono', monospace;
        font-size: 0.58rem;
        letter-spacing: 0.2em;
        color: rgba(255,255,255,0.18);
        margin-top: 4rem;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)


# ── Emotional narrative engine ─────────────────────────────────────────────────
VALENCE_NOTES = {
    "Euphoric":    "The hedonic register peaks at ecstatic overflow — colors blaze at their most saturated pinnacle.",
    "Joyful":      "Warm positivity radiates outward; hues carry the warmth of full-body delight.",
    "Serene":      "Quiet pleasure settles into the mid-range; nothing agitates, nothing dims.",
    "Wistful":     "Bittersweet longing tints the palette with a faint blue undertow beneath amber warmth.",
    "Melancholic": "Hedonic valence dips into reflective sadness; chroma recedes toward cooler, softer tones.",
    "Desolate":    "The emotional floor — pleasure evacuated, colors drain toward grey and muted earth.",
    "Tender":      "Fragile, unguarded warmth — pastels hold an almost whispered quality of care.",
    "Bitter":      "Unpleasant sharpness undercuts warmth; acidic greens and dull ochres surface.",
    "Content":     "Stable, undramatic satisfaction — colors settle into comfortable mid-tones.",
    "Anguished":   "Pain at depth — deep purples and crushed magentas carry interior weight.",
    "Hopeful":     "Positive anticipation tilts warm and luminous, as if facing a clearing sky.",
    "Forlorn":     "Abandoned sweetness — faded roses and desaturated blues hold grief lightly.",
}
AROUSAL_NOTES = {
    "Frenzied":    "Maximum activation: colors vibrate at high frequencies, pulse with kinetic tension.",
    "Invigorated": "High-energy clarity — saturated, uplifting, alert without overwhelm.",
    "Restless":    "Mid-high arousal caught between action and release; colors shift and refuse to settle.",
    "Languid":     "Low activation, slow time — hues soften and spread like late-afternoon light.",
    "Dormant":     "Energy withdrawn to seed-state; palette approaches near-silence in muted cool tones.",
    "Electrified": "The body's current is live — sharp contrasts, electric blues, charged whites.",
    "Hushed":      "Arousal quieted to library-breath; tones whisper rather than speak.",
    "Turbulent":   "Chaotic activation — clashing warm-cool tensions held in uneasy suspension.",
    "Meditative":  "Deep stillness, not absence — awareness without agitation; neutral, balanced warmth.",
    "Volatile":    "Arousal swings unpredictably; palette carries sudden contrasts and unstable edges.",
    "Lethargic":   "Energy at ebb — grays and dull olives mark the body's reluctant presence.",
    "Pulsing":     "Rhythmic high arousal — the palette breathes in and out with steady intensity.",
}
STANCE_NOTES = {
    "Expansive":   "Relational posture wide open — colors reach outward, generous and unguarded.",
    "Surrendered": "Boundaries dissolved by choice — soft edges, no hard contrasts, yielding tonality.",
    "Defiant":     "Confrontational presence — palette holds its ground with hard-edged, assertive values.",
    "Withdrawn":   "Turned inward — colors compress into themselves, privacy over proclamation.",
    "Yielding":    "Pliable, responsive — colors give way gracefully, carrying no resistance.",
    "Confrontational": "Stance squared toward the other — high-contrast, directional, uncompromising.",
    "Embracing":   "Arms-open warmth — palette envelops with round, inclusive, soft-edged tones.",
    "Guarded":     "Protective closure — cool, measured hues that reveal nothing beyond the surface.",
    "Dissolving":  "Boundaries becoming permeable — edges blur, colors bleed into one another.",
    "Sovereign":   "Self-contained authority — deep tones assert without needing external validation.",
    "Receptive":   "Open to what arrives — pale, open forms that carry invitation.",
    "Armored":     "Maximum protective stance — metallic cool and compressed chroma, minimal openness.",
}


def emotional_profile(v, a, s):
    return f"{VALENCE_NOTES[v]} {AROUSAL_NOTES[a]} {STANCE_NOTES[s]}"


# ── Main app ───────────────────────────────────────────────────────────────────
def main():
    inject_css()

    # Title
    st.markdown('<div class="chroma-title">CHROMALOGIC</div>', unsafe_allow_html=True)
    st.markdown('<div class="chroma-subtitle">Emotional Spectrum → Color Palette Generator</div>', unsafe_allow_html=True)

    # ── Selectors ──────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([3, 3, 3, 1.2])

    with col1:
        st.markdown('<div class="dim-label">Ⅰ — Valence</div>', unsafe_allow_html=True)
        valence = st.selectbox(
            "Valence",
            VALENCE,
            index=0,
            label_visibility="collapsed",
            key="valence",
        )

    with col2:
        st.markdown('<div class="dim-label">Ⅱ — Arousal</div>', unsafe_allow_html=True)
        arousal = st.selectbox(
            "Arousal",
            AROUSAL,
            index=0,
            label_visibility="collapsed",
            key="arousal",
        )

    with col3:
        st.markdown('<div class="dim-label">Ⅲ — Stance</div>', unsafe_allow_html=True)
        stance = st.selectbox(
            "Stance",
            STANCE,
            index=0,
            label_visibility="collapsed",
            key="stance",
        )

    with col4:
        st.markdown('<div style="height:1.8rem"></div>', unsafe_allow_html=True)
        shuffle = st.button("⟳  Shuffle")

    if shuffle:
        rng = random.Random()
        st.session_state["valence"] = rng.choice(VALENCE)
        st.session_state["arousal"] = rng.choice(AROUSAL)
        st.session_state["stance"]  = rng.choice(STANCE)
        st.rerun()

    # ── Generate palette ───────────────────────────────────────────────────────
    swatches = generate_palette(valence, arousal, stance)

    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)

    # Emotional chips
    chips_html = f"""
    <div class="emotion-chips">
        <div class="chip dim-v">Valence · {valence}</div>
        <div class="chip dim-a">Arousal · {arousal}</div>
        <div class="chip dim-s">Stance · {stance}</div>
    </div>
    """
    st.markdown(chips_html, unsafe_allow_html=True)

    # Palette name
    st.markdown(f'<div class="palette-name">"{palette_name(valence, arousal, stance)}"</div>', unsafe_allow_html=True)

    # ── Swatch strip ───────────────────────────────────────────────────────────
    swatch_html_parts = []
    for sw in swatches:
        swatch_html_parts.append(f"""
        <div class="swatch" style="background:{sw['hex']}; color:{sw['text']};">
            <div class="swatch-hex">{sw['hex']}</div>
            <div class="swatch-hsl">H{sw['h']}° S{sw['s']}% L{sw['l']}%</div>
        </div>
        """)

    palette_html = f'<div class="palette-row">{"".join(swatch_html_parts)}</div>'
    st.markdown(palette_html, unsafe_allow_html=True)

    # ── Hex reference strip ────────────────────────────────────────────────────
    st.markdown('<div class="section-head">Hex Values</div>', unsafe_allow_html=True)
    hex_pills = "".join(
        f'<span class="hex-pill">{sw["hex"]}</span>' for sw in swatches
    )
    st.markdown(f'<div class="hex-grid">{hex_pills}</div>', unsafe_allow_html=True)

    # ── Emotional narrative ────────────────────────────────────────────────────
    st.markdown('<hr class="thin-rule">', unsafe_allow_html=True)
    st.markdown('<div class="section-head">Emotional Profile</div>', unsafe_allow_html=True)
    narrative = emotional_profile(valence, arousal, stance)
    st.markdown(f"""
    <p style="font-family:'Cormorant Garamond',serif; font-size:1.05rem;
              font-weight:300; line-height:1.75; color:rgba(232,228,220,0.65);
              max-width:720px; font-style:italic;">
        {narrative}
    </p>
    """, unsafe_allow_html=True)

    # ── Theory panel ──────────────────────────────────────────────────────────
    with st.expander("◈  Dimensional Theory"):
        st.markdown("""
        <div style="font-family:'Cormorant Garamond',serif; font-size:1rem;
                    line-height:1.8; color:rgba(232,228,220,0.6); font-weight:300;">
        <p>ChromaLogic maps emotional space to color space using three orthogonal
        axes derived from affective psychology's <em>circumplex model of affect</em>
        (Russell, 1980) extended with a relational dimension.</p>

        <p><strong style="color:#c8a96e; font-weight:400; letter-spacing:0.1em;">
        Ⅰ — VALENCE</strong> &nbsp;(hedonic tone) governs the hue temperature and
        overall saturation envelope. Positive valence pulls toward warm amber and
        golden yellows; negative valence shifts the dominant hue family toward
        cool blues, desaturated grays, and compressed chroma.</p>

        <p><strong style="color:#6ea0c8; font-weight:400; letter-spacing:0.1em;">
        Ⅱ — AROUSAL</strong> &nbsp;(activation energy) controls lightness contrast,
        saturation intensity, and color spread across the palette. High arousal
        produces sharp value contrasts and fully saturated anchors; low arousal
        compresses values toward mid-gray and softens saturation throughout.</p>

        <p><strong style="color:#a0c86e; font-weight:400; letter-spacing:0.1em;">
        Ⅲ — STANCE</strong> &nbsp;(relational posture) modulates harmony type and
        boundary behavior between swatches. Open stances favor analogous harmonies
        with soft edge transitions; closed or defensive stances favor complementary
        or split-complementary structures with higher inter-swatch contrast.</p>

        <p>Each combination of the three dimensions seeds a deterministic
        random function: the same trio of adjectives always yields the same palette,
        making ChromaLogic palettes reproducible and citable as named emotional states.</p>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown(
        '<div class="chroma-footer">CHROMALOGIC · Emotional Color Palette Generator · '
        'Based on Russell (1980) Circumplex Model of Affect</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
