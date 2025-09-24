from typing import Dict, Any, List
import re
import logging

class ClinicalNotePromptTemplates:
    """
    Provides a library of prompt templates for LLM-driven synthetic clinical note generation from FHIR-structured data. Supports prompt parameterization for diversity, style, and privacy compliance.
    """
    def __init__(self) -> None:
        self.base_templates = [
            (
                "You are a clinical documentation specialist. Given this patient's FHIR data: {fhir_json}, generate a single, realistic, fully anonymized SOAP-format clinical note in fluent English. Do NOT reveal any actual names, addresses, or hospital/doctor identifiers."
            ),
            (
                "Use the following FHIR-formatted patient and encounter information: {fhir_json}. Compose a detailed clinical progress note (in narrative form). Incorporate relevant medical facts, plausible clinical reasoning, and anonymize all personal details. Structure the note logically and use terminology consistent with modern electronic health records."
            ),
            (
                "Given the FHIR fields: {fhir_json}, synthesize a fictional clinical note for a patient. Note tone: {note_tone}. The note should emulate a typical {document_type} as found in US hospital EHRs. Ensure that no explicit PHI data (names, addresses, dates of birth, MRNs) is present."
            ),
            (
                "As an AI healthcare assistant, generate a plausible clinical note for the presented FHIR data: {fhir_json}. Use medical jargon appropriate for {userType} writing a {section_formatting} (e.g., discharge summary, progress note, chief complaint). Randomize patient age/gender (do not match original), use generic placeholders for sensitive fields, and emphasize both real and rare symptoms for research realism."
            )
        ]
        # Configure logger for prompt template issues
        self.logger = logging.getLogger(__name__)

    def get_templates(self) -> List[str]:
        return self.base_templates

    def render_prompt(self, template: str, data: Dict[str, Any], extra_params: Dict[str, str]) -> str:
        """
        Renders a prompt template with provided parameters. Warns if any placeholders remain unresolved in the template.
        Fix: Now checks for unresolved placeholders and logs a warning if any exist.
        """
        prompt = template
        merged_params = {**data, **extra_params}
        # Replace all provided parameters
        for k, v in merged_params.items():
            prompt = prompt.replace(f"{{{k}}}", str(v))
        # Check for unresolved placeholders (e.g., {field})
        unresolved = re.findall(r'\{(\w+)\}', prompt)
        if unresolved:
            self.logger.warning(
                f"Prompt rendering: Unresolved placeholders in template '{template}': {unresolved}"
            )
        return prompt

    def parameterize_prompt(self, fhir_json: str, document_type: str = 'encounter note', note_tone: str = 'formal', userType: str = 'clinician', section_formatting: str = 'SOAP') -> List[str]:
        rendered = []
        for prompt in self.base_templates:
            params = {
                'fhir_json': fhir_json,
                'document_type': document_type,
                'note_tone': note_tone,
                'userType': userType,
                'section_formatting': section_formatting
            }
            rendered.append(self.render_prompt(prompt, {}, params))
        return rendered


def clinical_text_generation_prompt_examples() -> List[str]:
    """
    Returns several real prompt examples instantiated with FHIR-like data.
    """
    fhir_data1 = '{"resourceType": "Patient", "gender": "female", "age": 67, "visit": {"chiefComplaint": "shortness of breath", "vitals": {"temp": 99.3, "bp": "140/86", "pulse": 98}, "diagnosis": "CHF exacerbation"}}'
    fhir_data2 = '{"resourceType": "Encounter", "date": "2023-01-12", "reason": "abdominal pain", "labs": [{"test": "CBC", "result": "WNL"}]}'
    pt = ClinicalNotePromptTemplates()
    # Repair: generate prompt examples for both example FHIR resources
    examples = pt.parameterize_prompt(
        fhir_json=fhir_data1,
        document_type="history & physical",
        note_tone="professional",
        userType="physician",
        section_formatting="SOAP"
    )
    examples += pt.parameterize_prompt(
        fhir_json=fhir_data2,
        document_type="ER note",
        note_tone="concise",
        userType="resident",
        section_formatting="narrative"
    )
    return examples
