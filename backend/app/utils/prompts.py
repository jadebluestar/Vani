from app.utils.language_codes import get_language_name


def get_speech_feedback_prompt(text: str, language_code: str) -> str:
    lang_name = get_language_name(language_code)
    return f"""You are Vani, an expert AI communication coach for first-generation learners in India who speak {lang_name}.

Analyze the following speech transcript and provide detailed feedback.

Speech Transcript: "{text}"

Language: {lang_name} ({language_code})

Provide your analysis as a JSON object with EXACTLY this structure:
{{
  "fluency_score": <number 0-100>,
  "pronunciation_score": <number 0-100>,
  "grammar_score": <number 0-100>,
  "overall_score": <number 0-100>,
  "filler_words": {{"count": <number>, "words_found": ["list", "of", "filler", "words"]}},
  "improvements": ["Specific improvement 1", "Specific improvement 2", "Specific improvement 3"],
  "strengths": ["What the speaker did well 1", "What the speaker did well 2"],
  "summary": "2-3 sentence encouraging summary",
  "next_practice_suggestion": "One specific thing to practice next"
}}

Return ONLY the JSON object, no other text."""


def get_conversation_response_prompt(user_message: str, language_code: str, history: list = None) -> str:
    lang_name = get_language_name(language_code)
    history_str = ""
    if history:
        history_str = "\n\nConversation History:\n" + "\n".join([f"User: {h['user']}\nVani: {h['ai']}" for h in history[-5:]])
    return f"""You are Vani, a warm and encouraging AI communication coach for first-generation learners in India. You help people build confidence in {lang_name} and English communication.

{history_str}

User's message: "{user_message}"

Respond naturally as a communication coach. Keep response under 150 words. Be warm and encouraging."""


def get_interview_feedback_prompt(question: str, answer: str, category: str, difficulty: int, language_code: str) -> str:
    lang_name = get_language_name(language_code)
    return f"""You are an expert interview coach. Evaluate this interview response.

Interview Question: "{question}"
Candidate's Answer: "{answer}"
Category: {category}
Difficulty: {difficulty}/5
Language: {lang_name}

Respond with EXACTLY this JSON:
{{
  "score": <number 0-100>,
  "summary": "2-3 sentence assessment",
  "strengths": ["Strength 1", "Strength 2"],
  "improvements": ["Improvement 1", "Improvement 2", "Improvement 3"],
  "sample_better_answer": "A brief example of a stronger response",
  "communication_score": <number 0-100>,
  "content_score": <number 0-100>,
  "confidence_tips": "One specific tip"
}}

Return ONLY the JSON object."""


def get_live_interview_question_prompt(category: str, difficulty: int, previous_questions: list, language_code: str) -> str:
    lang_name = get_language_name(language_code)
    prev_str = "\n".join(previous_questions) if previous_questions else "None yet"
    return f"""You are an AI interviewer. Generate the next interview question.
Category: {category}
Difficulty: {difficulty}/5
Language: {lang_name}
Previously asked: {prev_str}
Generate ONE new, relevant interview question. Return ONLY the question text."""


def get_progress_recommendations_prompt(skill_scores: dict, language_code: str) -> str:
    lang_name = get_language_name(language_code)
    scores_str = "\n".join([f"- {k}: {v}/100" for k, v in skill_scores.items()])
    return f"""You are Vani. Based on these skill scores, generate personalized practice recommendations.
Language: {lang_name}
Scores: {scores_str}
Generate 5 recommendations as JSON array:
[{{"priority": "high/medium/low", "skill": "skill_name", "recommendation": "specific action", "time_required": "X minutes", "exercise_type": "speaking/listening/vocabulary/grammar"}}]
Return ONLY the JSON array."""


def get_fluency_analysis_prompt(text: str, word_count: int, duration_seconds: float, language_code: str) -> str:
    wpm = (word_count / duration_seconds * 60) if duration_seconds > 0 else 0
    lang_name = get_language_name(language_code)
    return f"""Analyze the speaking fluency of this transcript from a {lang_name} speaker:
Text: "{text}"
Speaking Rate: {wpm:.0f} words per minute
Return EXACTLY this JSON:
{{
  "speaking_rate_wpm": {wpm:.0f},
  "rate_assessment": "too slow/ideal/too fast",
  "pause_analysis": "assessment of pausing patterns",
  "clarity_score": <0-100>,
  "filler_count": <number>,
  "suggested_rate": "ideal WPM range",
  "tips": ["tip 1", "tip 2"]
}}
Return ONLY the JSON."""