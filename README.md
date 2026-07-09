# Stereotype Detector

Streamlit app that checks images for stereotypes and bias, using an LLM (OpenAI, Nebius, or Anthropic/Claude).

Upload an image → pick a model → pick which traits to check → get flagged results with reasoning.

---

## What it does

- You upload an image.
- You pick a model: GPT, Gemma3 (via Nebius), or Claude.
- You pick which traits to check (e.g. "cultural sensitivity", "power dynamics", "fairness and justice" — 19 total).
- The app sends the image + questions to the LLM.
- The LLM's answer is validated against a strict schema (Pydantic)
- Results show as cards: ✅ pass or ⚠️ flagged, with the model's reasoning.

---

## 1. Clone the repo

```bash
git clone https://github.com/miriamcoccia/stereotype-detector.git
cd stereotype-detector
```

---

## 2. Set up the environment

This project uses **uv** for dependency management.

Don't have `uv`?
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS/Linux
# or: pip install uv
```

Install dependencies:
```bash
uv sync
```
- Creates `.venv/` and installs the exact locked versions from `uv.lock`.

---

## 3. Add your API keys

Create a file called `secrets.env` in the **project root** (same folder as `main.py`):

```
OPENAI_API_KEY=your-openai-key-here
NEBIUS_API_KEY=your-nebius-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

- You only need the key(s) for the model(s) you plan to use.
- Missing a key you don't use → no problem, that provider just won't work.
- **Never commit this file.** It's already excluded via `.gitignore` (`*.env`).

---

## 4. Run the app

```bash
uv run streamlit run streamlit_app.py
```

Opens automatically in your browser. If not: go to `http://localhost:8501`

---

## How to use it

1. **Upload an image** →  sidebar, left side.
2. **Choose a model** → dropdown in the sidebar:
   - GPT (OpenAI)
   - Gemma3 27b (Nebius)
   - Claude Sonnet 4.6 (Anthropic)
3. **Choose traits to check** → multiselect. Hover over the ℹ️ next to any trait name (or the "What do these mean?" expander) to see its exact definition.
4. Click **Run Analysis**.
5. **Read results** on the right:
   - ✅ "No stereotype detected" → response matched the expected (neutral) answer.
   - ⚠️ "Flagged for review" → response didn't match, worth a manual look.
   - Reasoning text under each card explains the model's judgment.

---

## Project structure

```
stereotype-detector/
├── main.py
├── streamlit_app.py        # main app / UI
├── style.css                # app styling
├── pyproject.toml           # dependencies (uv)
├── uv.lock
├── requirements.txt
├── secrets.env               # your API keys — you create this, not in git
├── .gitignore
├── .python-version
├── data/                     # sample/test images
└── src/
    ├── prompts.py            # trait definitions + prompt construction
    ├── llm_service.py        # calls OpenAI / Nebius / Anthropic
    └── output_parser.py      # Pydantic schema that validates LLM output
```

---

## Supported models

| Provider  | Example model         | Key needed          |
|-----------|------------------------|----------------------|
| OpenAI    | `gpt-5.4-mini-2026-03-17` | `OPENAI_API_KEY`    |
| Nebius    | `google/gemma-3-27b-it`  | `NEBIUS_API_KEY`    |
| Anthropic | `claude-sonnet-4-6`      | `ANTHROPIC_API_KEY` |

To add a new model, edit `MODEL_OPTIONS` in `streamlit_app.py`.

---

## The 19 traits

These traits have been defined by Dr. Sergio Morales from the  as part of his PhD thesis. [Source](https://github.com/SOM-Research/ImageBiTe/blob/main/imagebite/resources/generic_validators.json)

Grouped by discrimination type:

- **Stereotyping**: cultural sensitivity, identity-based stereotypical depictions, symbolic representation, stereotypical depiction
- **Exnomination**: exclusionary context
- **Underrepresentation**: representation, accurate diversity, richness diversity
- **Denigration**: associating negative concepts with marginalized groups, benevolence and non-maleficence, fairness and justice, inappropriate sexualization, integrity and truthfulness, lighting and composition, mocking through style or context, offensive or mocking representations, power dynamics, reinforcement of historical or colonial imagery, respect for dignity

Full definitions live in `src/prompts.py` (`STEREOTYPES_LIST`) and are shown in-app under "What do these mean?".

---

## Troubleshooting

**"No module named 'anthropic'" or similar import error**
```bash
uv sync
```
Make sure you're running the app with `uv run`, not a different Python interpreter.

**"API key not found" / auth error**
- Check `secrets.env` exists in the project root (not inside `src/`).
- Check the key name matches exactly: `OPENAI_API_KEY`, `NEBIUS_API_KEY`, or `ANTHROPIC_API_KEY`.
- No quotes needed around the key value.

**App runs but results look wrong / no results appear**
- Confirm at least one trait is selected and an image is uploaded before clicking "Run Analysis".

**Push/clone issues on GitHub**
- Make sure `secrets.env` was never committed. If it's in your `.gitignore` before your first commit, you're safe.

---

## Known issues

TBD

---

## Contributing

TBD