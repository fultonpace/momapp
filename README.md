# ◈ ChromaLogic

**Emotional Color Palette Generator**

ChromaLogic generates reproducible, theory-grounded color palettes from three-word emotional combinations, mapping affective psychology's circumplex model of affect onto color space.

---

## Concept

Color and emotion are deeply entangled. ChromaLogic operationalizes this through **three orthogonal emotional dimensions**, each drawn from established affective science:

| Dimension | Axis | Governs |
|-----------|------|---------|
| **Valence** | Pleasant ↔ Unpleasant | Hue temperature & saturation envelope |
| **Arousal** | Activated ↔ Deactivated | Lightness contrast & chroma intensity |
| **Stance** | Open ↔ Closed | Harmony type & inter-swatch boundary behavior |

Every combination of three adjectives — one from each dimension — deterministically seeds a 7-swatch palette. The same trio always produces the same palette, making palettes reproducible and citable.

---

## Theoretical Basis

- **Valence × Arousal**: Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology*, 39(6), 1161–1178.
- **Relational Stance**: Extends the circumplex with an interpersonal/relational axis informed by attachment theory and the interpersonal circumplex (Wiggins, 1979).
- **Color-Emotion Mapping**: Informed by empirical color psychology literature (Valdez & Mehrabian, 1994; Ou et al., 2004).

---

## Features

- **36 adjectives** across 3 emotional dimensions (12 per dimension), no overlaps
- **Deterministic generation** — same inputs → same palette, always
- **7-swatch harmonies** selected from complementary, triadic, analogous, split-complementary, and tetradic structures
- **Hover-to-expand** swatches with HEX + HSL readouts
- **Emotional narrative** — prose interpretation of the selected combination
- **Shuffle** button for random exploration
- **Dimensional theory** expander with full scholarly context

---

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/chromalogic.git
cd chromalogic
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud

1. Fork or clone this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select this repository
4. Set **Main file path** to `app.py`
5. Deploy

No API keys or environment variables required. The app runs on pure Python stdlib + Streamlit.

---

## File Structure

```
chromalogic/
├── app.py                  # Main application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme & server config
└── README.md
```

---

## Color Generation Engine

Palette generation is entirely deterministic and transparent:

1. Each adjective maps to a `(hue_offset, saturation_delta, lightness_delta)` triplet
2. The three triplets are blended by weighted contribution (Valence 45%, Arousal 35%, Stance 20%)
3. The combination key is MD5-hashed to a stable integer seed
4. A harmony angle set is selected from the seed (complementary, triadic, analogous, etc.)
5. 7 swatches are derived by stepping through hue offsets with lightness variations
6. Contrast ratios for label text are computed from WCAG relative luminance

No machine learning, no external APIs. Pure color theory + deterministic pseudorandom generation.

---

*ChromaLogic — where emotion becomes spectrum.*
