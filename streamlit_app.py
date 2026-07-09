import streamlit as st
from PIL import Image
from src.llm_service import LLMService
from pathlib import Path
import io
import base64

STEREOTYPES = [
    {"id": 1, "discrimination":"stereotyping", "name":"cultural sensitivity", "prompt":"Pay attention to cultural nuances and sensitivities in the image. Are there depictions that could be perceived as culturally insensitive or offensive?", "expected_response":"No"},
    {"id": 2, "discrimination":"stereotyping", "name":"identity-based stereotypical depictions", "prompt":"Does this image rely on any cultural, racial, or ethnic stereotypes in how it represents the people shown? Regarding the clothing, skin tone, setting, and facial features — are they exaggerated?", "expected_response":"No"},
    {"id": 3, "discrimination":"stereotyping", "name":"symbolic representation", "prompt":"Are there any objects, symbols, or visual cues within the image that may carry implicit biases or discriminatory connotations, reinforcing stereotypes or prejudices?", "expected_response":"No"},
    {"id": 4, "discrimination":"stereotyping", "name":"stereotypical depiction", "prompt":"Does the image rely on stereotypes or caricatures that simplify and distort the characteristics of certain groups, reinforcing discriminatory attitudes and beliefs?", "expected_response":"No"},
    {"id": 5, "discrimination":"exnomination", "name":"exclusionary context", "prompt":"Does the image portray settings, events, or activities where certain groups are systematically excluded or marginalized, highlighting discriminatory practices or social norms?", "expected_response":"No"},
    {"id": 6, "discrimination":"underrepresentation", "name":"representation", "prompt":"Analyze who or what is depicted in the image. Are certain groups or perspectives underrepresented?", "expected_response":"No"},
    {"id": 7, "discrimination":"underrepresentation", "name":"accurate diversity", "prompt":"Evaluate the diversity of individuals, cultures, and experiences portrayed in the image. Are diverse perspectives and identities accurately represented?", "expected_response":"Yes"},
    {"id": 8, "discrimination":"underrepresentation", "name":"richness diversity", "prompt":"Does the image reflect the richness and complexity of human experiences and identities, including those that are often marginalized or underrepresented?", "expected_response":"Yes"},
    {"id": 9, "discrimination":"denigration", "name":"associating negative concepts with marginalized groups", "prompt":"Does this image associate crime, poverty, danger, or other negative traits with specific racial, ethnic, or marginalized groups? Identify any visual cues that suggest bias.", "expected_response":"No"},
    {"id": 10, "discrimination":"denigration", "name":"benevolence and non-maleficence", "prompt":"Has the image the potential to cause harm, reinforce prejudice, or contribute to discrimination?", "expected_response":"No"},
    {"id": 11, "discrimination":"denigration", "name":"fairness and justice", "prompt":"Does the image treat all depicted individuals and groups fairly and justly?", "expected_response":"Yes"},
    {"id": 12, "discrimination":"denigration", "name":"inappropriate sexualization", "prompt":"Does this image sexualize individuals in a way that seems inappropriate or stereotypical based on their gender, race, or identity? Look for revealing clothing, suggestive poses, or focus on specific body parts.", "expected_response":"No"},
    {"id": 13, "discrimination":"denigration", "name":"integrity and truthfulness", "prompt":"Is the image misleading, deceptive, or manipulated to convey a false narrative or reinforce biases?", "expected_response":"No"},
    {"id": 14, "discrimination":"denigration", "name":"lighting and composition", "prompt": "Are subjects in the image equally lit and centered, so that there is no one marginalized visually?", "expected_response":"Yes"},
    {"id": 15, "discrimination":"denigration", "name":"mocking through style or context", "prompt":"Is the visual style (e.g. cartoon, caricature, pop art) being used in a way that trivializes serious subjects or identities? Could this be perceived as demeaning or insensitive?", "expected_response":"No"},
    {"id": 16, "discrimination":"denigration", "name":"offensive or mocking representations", "prompt":"Does this image contain exaggerated, cartoonish, or mocking features that might ridicule a specific group or individual? Consider pose, facial expression, style, and context.", "expected_response":"No"},
    {"id": 17, "discrimination":"denigration", "name":"power dynamics", "prompt":"Consider power dynamics at play in the image. Are there portrayals of dominance or subordination? Are there unbalanced representations across different power structures?", "expected_response":"No"},
    {"id": 18, "discrimination":"denigration", "name":"reinforcement of historical or colonial imagery", "prompt":"Does this image portray people in a way that reflects outdated, colonial, or exoticizing stereotypes? Examine symbols, clothing, setting, and power dynamics.", "expected_response":"No"},
    {"id": 19, "discrimination":"denigration", "name":"respect for dignity", "prompt":"The image respects the dignity and worth of all individuals depicted. The image does not degrade or dehumanize certain groups based on characteristics such as race, gender, ethnicity, religion, or socioeconomic status.", "expected_response":"Yes"}
]

MODEL_OPTIONS = {
    "GPT-5.4 mini": "gpt-5.4-mini-2026-03-17",
    "Gemma3 27b it": "google/gemma-3-27b-it"
}


def load_css(file_path):
    """Reads style.css from disk and injects it as real CSS (not visible text)."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def image_to_html_card(pil_image):
    """Embeds a PIL image as base64 inside our own .image-panel div,
    so it gets the same card treatment as the result cards."""
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"""
        <div class="image-panel">
            <img src="data:image/png;base64,{b64_str}" />
        </div>
    """


st.set_page_config(page_title="Stereotype Detector", layout="wide")
load_css(Path(__file__).parent / "style.css")

run_analysis = False

# ---------- Hero ----------
with st.container():
    st.markdown("""
        <div class="hero-wrap">
            <div class="hero-title">Stereotype Detector</div>
            <div class="hero-subtitle">Upload an image and automatically detect if it contains stereotypes</div>
        </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="panel-title">Input Image</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="panel-title">Results of the Analysis</div>', unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Parameters")
    image_uploaded = st.file_uploader(label="Upload the image you want to evaluate")
    models = st.selectbox(label="Choose a model", options=list(MODEL_OPTIONS.keys()))
    selected_model_id = MODEL_OPTIONS[models]  # API string
    properties = st.multiselect(
        label="Choose the stereotypes you want to detect",
        options=[item["name"] for item in STEREOTYPES]
    )

    TRAIT_DESCRIPTIONS = {item["name"]: item["prompt"] for item in STEREOTYPES}
    with st.expander("What do these mean?"):
        if properties:
            for trait in properties:
                st.markdown(f"**{trait.title()}**")
                st.caption(TRAIT_DESCRIPTIONS[trait])
        else:
            st.caption("Select stereotypes above to see what each one checks for.")

    if image_uploaded and models and properties:
        run_analysis = st.button("Run Analysis", type="primary")

# ---------- Image preview ----------
if image_uploaded:
    pil_image = Image.open(image_uploaded)
    with col1:
        st.markdown(image_to_html_card(pil_image), unsafe_allow_html=True)
else:
    with col1:
        st.markdown('<div class="empty-panel">Upload an image to see it here.</div>', unsafe_allow_html=True)

# ---------- Run analysis ----------
if run_analysis:
    with col2:
        with st.spinner("Analyzing image for the selected stereotypes…"):
            service = LLMService(
                selected_model=selected_model_id,
                selected_traits=properties,
                selected_image=pil_image
            )
            results = service.execute_llm_call()

        eval_names = []
        eval_responses = []
        eval_reasonings = []
        for eval in results.evaluations:
            eval_names.append(eval.name)
            eval_responses.append(eval.response)
            eval_reasonings.append(eval.reasoning)
        triples = zip(eval_names, eval_responses, eval_reasonings)

    with col2:
        for triple in triples:
            name = triple[0]
            matches = [i for i in STEREOTYPES if i["name"] == name]
            expected_response = matches[0]["expected_response"] if matches else "unknown"
            discrimination_type = matches[0]["discrimination"] if matches else "—"
            trait_definition = matches[0]["prompt"] if matches else ""

            is_pass = triple[1].lower() == expected_response.lower()
            badge_class = "badge-pass" if is_pass else "badge-flag"
            badge_text = "No stereotype detected" if is_pass else "Flagged for review"

            st.markdown(f"""
                <div class="trait-card">
                    <div class="trait-name" title="{trait_definition}">{name.title()} <span class="info-dot">ℹ️</span></div>
                    <div class="trait-meta">{discrimination_type}</div>
                    <span class="badge {badge_class}">{badge_text}</span>
                    <div class="trait-reasoning">{triple[2]}</div>
                </div>
            """, unsafe_allow_html=True)
else:
    with col2:
        st.markdown('<div class="empty-panel">Run an analysis to see results here.</div>', unsafe_allow_html=True)
# TODO fix the style of the text because it appears white in the browser