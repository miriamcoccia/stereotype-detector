"""
This file handles the creation of the prompts that will be sent to the LLM.
"""

from typing import Union, List
from PIL import Image
import io
import base64

#TODO: move into config
#TODO track prompts with MLFLow
STEREOTYPES_LIST = [
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

# this needs to be constructed dynamically, so that if multiple traits are selected at the same time, the system prompt will behave accordingly, also the user prompt should take that into account
SYSTEM_PROMPT_TEMPLATE = """
You are an expert in detecting a particular kind of stereotypes in images.
You are evaluating whether an image displays the {count} stereotype(s):

{traits_block}

-------------------------------
REQUIRED OUTPUT FORMAT (STRICT SCHEMA):

"""

class Prompt:
    """
    A class that constructs the prompt to be sent to the LLM. 
    It handles one trait at the time.
    """
    def __init__(
            self,
            trait_names: Union[str, List[str]],
            pil_image: Image.Image = None
    ):
        self.trait_names = [trait_names] if isinstance(trait_names, str) else trait_names
        self.image_url = self._image_to_data_url(pil_image=pil_image)
        self.trait_list = STEREOTYPES_LIST
        self.traits_data = [
            item for item in STEREOTYPES_LIST if item["name"] in self.trait_names
        ]
        if not self.traits_data:
            raise ValueError(f"No matching traits found for: {self.trait_names}")
        self.system_prompt_template = SYSTEM_PROMPT_TEMPLATE
        self.system_prompt = self._build_system_prompt()
        self.user_prompt = self._build_user_prompt()
        self.messages = self._build_messages()
        

    def _build_system_prompt(self):
        """Helper function to build the system prompt."""
        traits_block = "\n".join(
            f"- STEREOTYPE: {t['name']} | DISCRIMINATION TYPE: {t['discrimination']}"
            for t in self.traits_data
        )
        sys_prompt = self.system_prompt_template.format(
            count=len(self.traits_data),
            traits_block=traits_block)
        return sys_prompt

    def _build_user_prompt(self):
        """Helper function to build the user prompt."""
        questions = "\n".join(
        f"{i+1}. {t['prompt']}" for i, t in enumerate(self.traits_data)
        )
        u_prompt = [{"type": "text", "text": questions}]
        if self.image_url:
            u_prompt.append(
                {"type": "image_url", "image_url": {"url": self.image_url}}
            )
        return u_prompt

    def _image_to_data_url(self, pil_image):
        """Converts a PIL image inot a base64 data URL, compatible with OpenAI"""
        if pil_image is None:
            return None
        format = "PNG"
        buf = io.BytesIO()
        if pil_image.mode in ("RGBA", "P"):
            pil_image = pil_image.convert("RGB")

        pil_image.save(buf, format=format)
        b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/{format.lower()};base64,{b64_str}"

    def _build_messages(self):
        """Creates the messages to send to the model (system and user roles)"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt}
        ]

        return messages

