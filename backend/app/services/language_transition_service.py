from typing import Optional, Dict, Tuple
from loguru import logger
from app.services.llm_service import llm_service
from app.utils.language_codes import get_language_name


class LanguageTransitionService:
    """Manages the phased language learning pipeline for regional Indian language speakers."""

    PHASE_THRESHOLDS = {1: (0, 30), 2: (31, 50), 3: (51, 65), 4: (66, 80), 5: (81, 100)}

    def get_phase(self, overall_score: float) -> int:
        for phase, (low, high) in self.PHASE_THRESHOLDS.items():
            if low <= overall_score <= high:
                return phase
        return 1

    def get_phase_instruction(self, phase: int, native_language: str) -> str:
        lang_name = get_language_name(native_language)
        instructions = {
            1: f"Respond entirely in {lang_name}. Do NOT use English except for technical terms.",
            2: f"Respond mostly in {lang_name} (70%) with simple English phrases (30%).",
            3: f"Mix {lang_name} and English equally (50/50).",
            4: f"Respond mostly in English (70%) with {lang_name} support (30%).",
            5: "Respond entirely in professional English."
        }
        return instructions.get(phase, instructions[1])

    async def generate_phased_response(self, user_message: str, native_language: str, overall_score: float, context: str = "conversation") -> Tuple[str, int, str]:
        phase = self.get_phase(overall_score)
        phase_instruction = self.get_phase_instruction(phase, native_language)
        lang_name = get_language_name(native_language)
        system_prompt = f"You are Vani, an AI communication coach. The user's native language is {lang_name}. Current learning phase: {phase}/5. Language instruction: {phase_instruction}"
        prompt = f"Context: {context} practice session\nUser message: \"{user_message}\"\nRespond as a supportive communication coach."
        response = await llm_service.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.75)
        phase_descriptions = {1: "Comfortable in native language", 2: "Building English bridges", 3: "Balanced bilingual practice", 4: "Transitioning to English", 5: "Professional English fluency"}
        return response, phase, phase_descriptions.get(phase, "Learning journey")

    def get_transition_milestones(self, current_score: float, native_language: str) -> Dict:
        current_phase = self.get_phase(current_score)
        lang_name = get_language_name(native_language)
        if current_phase < 5:
            next_phase = current_phase + 1
            next_threshold = self.PHASE_THRESHOLDS[next_phase][0]
            progress_in_phase = ((current_score - self.PHASE_THRESHOLDS[current_phase][0]) / (self.PHASE_THRESHOLDS[current_phase][1] - self.PHASE_THRESHOLDS[current_phase][0]) * 100)
        else:
            next_threshold = 100
            progress_in_phase = 100.0
        return {
            "current_phase": current_phase,
            "current_score": current_score,
            "phase_description": self.get_phase_instruction(current_phase, native_language),
            "progress_in_phase": round(progress_in_phase, 1),
            "points_to_next_phase": max(0, next_threshold - current_score),
            "native_language": lang_name,
            "is_max_phase": current_phase == 5
        }


language_transition_service = LanguageTransitionService()