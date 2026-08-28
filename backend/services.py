# backend/services.py
import logging
import os
import re
from typing import Iterable, Optional

import requests

logger = logging.getLogger(__name__)


_STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "your", "you", "are", "what",
    "how", "why", "about", "event", "conference", "session", "working", "work", "want", "learn",
    "real", "world", "project", "projects", "professional", "technology", "technologies", "person",
    "interested", "interest", "networking", "goal", "meet", "meeting", "someone", "people",
    "using", "use", "can", "could", "would", "should", "from", "at", "in", "on", "to", "of",
}


def _clean_phrase(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip(" .,:;|\n\t")
    return text


def _dedupe_preserve(items: Iterable[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        value = _clean_phrase(item)
        key = value.lower()
        if value and key not in seen:
            seen.add(key)
            out.append(value)
    return out


class ThemeExtractor:
    """Extract useful themes while avoiding field-label artifacts such as USER/INTERESTS/EVENT."""

    DOMAIN_TERMS = {
        "ai", "artificial intelligence", "machine learning", "ml", "deep learning", "cybersecurity",
        "security", "cloud", "cloud computing", "devops", "docker", "kubernetes", "python", "java",
        "javascript", "react", "fastapi", "streamlit", "data science", "data engineering", "blockchain",
        "healthcare", "fintech", "robotics", "iot", "internet of things", "smart cities", "sustainability",
        "climate change", "urban planning", "responsible ai", "edge computing", "wifi", "networking",
        "wireless", "5g", "6g", "software engineering", "product development", "startups", "research",
    }

    def __init__(self):
        self.pipeline = None
        self.initialized = False

    def _init_pipeline(self):
        if self.initialized:
            return
        self.initialized = True
        try:
            from transformers import pipeline

            self.pipeline = pipeline(
                "ner",
                model="elastic/distilbert-base-uncased-finetuned-conll03-english",
                aggregation_strategy="simple",
            )
            logger.info("DistilBERT NER pipeline loaded.")
        except Exception as exc:
            logger.warning("DistilBERT unavailable; using deterministic theme extraction: %s", exc)
            self.pipeline = None

    def extract_themes(self, text: str, preferred_terms: Optional[Iterable[str]] = None) -> list[str]:
        preferred = [_clean_phrase(x) for x in (preferred_terms or []) if _clean_phrase(x)]
        themes = []

        # User-entered interests are already strong semantic themes. Prefer them first.
        themes.extend(preferred[:6])

        # Add known multi-word domain phrases found in the text.
        lowered = str(text or "").lower()
        for term in sorted(self.DOMAIN_TERMS, key=len, reverse=True):
            if term in lowered:
                themes.append(term)

        self._init_pipeline()
        if self.pipeline:
            try:
                entities = self.pipeline(str(text or ""))
                for entity in entities:
                    word = _clean_phrase(entity.get("word", ""))
                    label = str(entity.get("entity_group", "")).upper()
                    if word and label in {"ORG", "PERSON", "MISC"} and len(word) > 2:
                        themes.append(word)
            except Exception as exc:
                logger.warning("DistilBERT theme extraction failed: %s", exc)

        # Finally add meaningful user tokens while filtering UI field names.
        for token in re.findall(r"[A-Za-z][A-Za-z0-9+.#-]{2,}", lowered):
            if token not in _STOP_WORDS and token in self.DOMAIN_TERMS:
                themes.append(token)

        themes = _dedupe_preserve(themes)
        banned = {"user", "interests", "event", "description", "profile", "bio", "networking", "goal", "person"}
        return [t for t in themes if t.lower() not in banned][:8]


class StarterGenerator:
    """Generate event-focused spoken conversation openers with an optional GPT-2 layer and quality guardrails."""

    def __init__(self):
        self.gpt2 = None
        self.gpt2_initialized = False
        self.use_gpt2 = os.getenv("ENABLE_GPT2", "false").lower() in {"1", "true", "yes"}

    def _init_gpt2(self):
        if self.gpt2_initialized or not self.use_gpt2:
            return
        self.gpt2_initialized = True
        try:
            from transformers import pipeline

            self.gpt2 = pipeline("text-generation", model=os.getenv("GPT2_MODEL", "gpt2"))
            logger.info("GPT-2 text generation pipeline loaded.")
        except Exception as exc:
            logger.warning("GPT-2 unavailable; using quality-safe templates: %s", exc)
            self.gpt2 = None

    @staticmethod
    def _split_interests(interests: str) -> list[str]:
        return _dedupe_preserve(re.split(r"[,;\n]+", interests or ""))

    @staticmethod
    def _short(value: str, limit: int = 110) -> str:
        value = _clean_phrase(value)
        return value if len(value) <= limit else value[:limit].rsplit(" ", 1)[0] + "…"

    def _template_starters(
        self,
        interests: str,
        event: str,
        goal: str = "",
        person: str = "",
        tone: str = "professional",
    ) -> list[str]:
        interest_list = self._split_interests(interests)
        interest = self._short(interest_list[0] if interest_list else "technology")
        secondary = self._short(interest_list[1]) if len(interest_list) > 1 else interest
        event_short = self._short(event, 140)
        goal_clean = _clean_phrase(goal)
        person_clean = self._short(person, 140)
        tone = (tone or "professional").lower()

        if person_clean:
            opener = (
                f"I’m interested in {interest}. Given your work in {person_clean.lower()}, "
                f"what part of that work connects most with what’s being discussed at {event_short}?"
            )
        else:
            opener = (
                f"I’m interested in {interest}. What are you seeing at {event_short} that you think "
                f"will have the biggest impact in the next few years?"
            )

        second = (
            f"I’m exploring {interest} and {secondary}. Which area do you think is getting the most "
            f"interesting attention at {event_short}?"
        )

        if goal_clean:
            third = (
                f"I’m here to {goal_clean.lower().rstrip('.')}. From your experience, what would you "
                f"recommend someone interested in {interest} pay attention to at {event_short}?"
            )
        else:
            third = (
                f"What’s one challenge in {interest} that you think people at {event_short} should be "
                f"talking about more?"
            )

        if tone == "casual":
            opener = opener.replace("I’m interested in", "I’m really into").replace("what part of that work connects most", "what part of that work is most interesting")
            second = second.replace("Which area do you think", "What part do you think")
        elif tone == "warm":
            opener = opener.replace("What are you seeing", "What have you found most interesting").replace("I’m interested in", "I’ve been especially interested in")

        return _dedupe_preserve([opener, second, third])[:3]

    def _gpt2_starters(self, interests: str, event: str, goal: str, person: str, tone: str) -> list[str]:
        self._init_gpt2()
        if not self.gpt2:
            return []

        prompt = (
            "Write exactly three short spoken conversation starters for a professional technology event. "
            "They must be natural questions, not LinkedIn messages or emails. Use only the supplied facts. "
            "Do not invent names, companies, roles, or claims. Each starter must connect the event with "
            "at least one interest. Avoid greetings, labels, placeholders, and phrases such as 'I came across your profile'.\n"
            f"Interests: {interests}\nEvent: {event}\nGoal: {goal or 'make a meaningful professional connection'}\n"
            f"Person context: {person or 'none'}\nTone: {tone}\nStarters:"
        )
        try:
            generated = self.gpt2(prompt, max_new_tokens=120, num_return_sequences=1, do_sample=True, temperature=0.7)
            text = generated[0].get("generated_text", "")
            tail = text.split("Starters:", 1)[-1]
            candidates = re.split(r"\n+|(?<=\?)\s+", tail)
            return _dedupe_preserve([re.sub(r"^\s*(?:\d+\.|[-*•])\s*", "", c).strip() for c in candidates if c.strip()])
        except Exception as exc:
            logger.warning("GPT-2 generation failed: %s", exc)
            return []

    @staticmethod
    def _quality_ok(starter: str, interests: str, event: str) -> bool:
        text = _clean_phrase(starter)
        low = text.lower()
        if not (35 <= len(text) <= 260) or "?" not in text:
            return False
        banned = [
            "user interests", "event description", "event details", "profile bio", "profile, bio",
            "user, interests", "dear colleague", "dear professional", "i came across your profile",
            "hope you're having", "hope you are having", "connect on linkedin", "copy and paste",
        ]
        if any(x in low for x in banned):
            return False
        terms = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+.#-]{1,}", interests or "") if t.lower() not in _STOP_WORDS]
        event_terms = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9+.#-]{1,}", event or "") if t.lower() not in _STOP_WORDS]
        return any(t in low for t in terms) and any(t in low for t in event_terms)

    def generate_starters(
        self,
        context: str = "",
        themes: Optional[list] = None,
        relationship: str = "colleague",
        tone: str = "professional",
        interests: str = "",
        event: str = "",
        goal: str = "",
        person: str = "",
    ) -> list[str]:
        # Backwards compatibility for the old API: parse basic fields from context when structured values are absent.
        if not interests and context:
            match = re.search(r"USER INTERESTS:\s*(.*)", context, flags=re.I)
            interests = match.group(1).strip() if match else ""
        if not event and context:
            match = re.search(r"EVENT:\s*(.*)", context, flags=re.I)
            event = match.group(1).strip() if match else context
        if not goal and context:
            match = re.search(r"NETWORKING GOAL:\s*(.*)", context, flags=re.I)
            goal = match.group(1).strip() if match else ""
        if not person and context:
            match = re.search(r"PERSON CONTEXT:\s*(.*)", context, flags=re.I)
            person = match.group(1).strip() if match else ""

        # Optional GPT-2 output is accepted only after strict validation.
        candidates = self._gpt2_starters(interests, event, goal, person, tone)
        valid = [s for s in candidates if self._quality_ok(s, interests, event)]
        if len(valid) >= 2:
            return valid[:3]

        templates = self._template_starters(interests, event, goal, person, tone)
        return [s for s in templates if self._quality_ok(s, interests, event)][:3]


class FactChecker:
    """Wikipedia-backed topic lookup with exact-title and search fallback."""

    API_URL = "https://en.wikipedia.org/w/api.php"
    HEADERS = {"User-Agent": "PersonalizedNetworkingAssistant/2.1"}

    def verify_topic(self, query: str) -> dict:
        query = _clean_phrase(query)
        if not query:
            return {"verified": False, "message": "Enter a topic to search.", "title": None, "summary": None, "source_url": None}

        try:
            # First try an exact/redirected article title.
            params = {
                "action": "query", "format": "json", "prop": "extracts",
                "exintro": True, "explaintext": True, "titles": query,
                "redirects": 1, "formatversion": 2,
            }
            response = requests.get(self.API_URL, params=params, headers=self.HEADERS, timeout=8)
            response.raise_for_status()
            data = response.json()
            pages = data.get("query", {}).get("pages", [])
            if isinstance(pages, dict):
                pages = list(pages.values())
            for page in pages:
                if page.get("pageid") is not None and not page.get("missing"):
                    return self._result(page)

            # Fallback to Wikipedia search so natural phrases don't fail just
            # because they are not exact article titles (e.g. "blockchain in healthcare").
            search_params = {
                "action": "query", "format": "json", "list": "search",
                "srsearch": query, "srlimit": 5, "utf8": 1, "formatversion": 2,
            }
            search_response = requests.get(self.API_URL, params=search_params, headers=self.HEADERS, timeout=8)
            search_response.raise_for_status()
            search_data = search_response.json()
            matches = search_data.get("query", {}).get("search", [])

            if not matches:
                return {
                    "verified": False,
                    "message": f"No relevant Wikipedia article was found for '{query}'. Try a shorter or more specific topic.",
                    "title": None, "summary": None, "source_url": None,
                }

            title = matches[0].get("title", query)
            detail_params = {
                "action": "query", "format": "json", "prop": "extracts",
                "exintro": True, "explaintext": True, "titles": title,
                "redirects": 1, "formatversion": 2,
            }
            detail_response = requests.get(self.API_URL, params=detail_params, headers=self.HEADERS, timeout=8)
            detail_response.raise_for_status()
            detail_data = detail_response.json()
            detail_pages = detail_data.get("query", {}).get("pages", [])
            if isinstance(detail_pages, dict):
                detail_pages = list(detail_pages.values())
            for page in detail_pages:
                if page.get("pageid") is not None and not page.get("missing"):
                    result = self._result(page)
                    result["message"] = f"Wikipedia reference found for '{query}' via search: '{result['title']}'."
                    return result

            return {
                "verified": False, "message": f"A search result was found, but no article summary was available for '{query}'.",
                "title": title, "summary": None, "source_url": None,
            }
        except requests.RequestException as exc:
            logger.warning("Wikipedia request failed: %s", exc)
            return {
                "verified": False,
                "message": "Wikipedia could not be reached right now. Please try again.",
                "title": None, "summary": None, "source_url": None,
            }
        except Exception as exc:
            logger.exception("Unexpected fact-check error")
            return {
                "verified": False,
                "message": f"Fact-check lookup failed: {exc}",
                "title": None, "summary": None, "source_url": None,
            }

    @staticmethod
    def _result(page: dict) -> dict:
        title = page.get("title") or "Wikipedia article"
        source_url = "https://en.wikipedia.org/wiki/" + requests.utils.quote(title.replace(" ", "_"))
        summary = (page.get("extract") or "No introductory summary is available.").strip()
        return {
            "verified": True,
            "message": f"Wikipedia reference found: '{title}'.",
            "title": title,
            "summary": summary,
            "source_url": source_url,
        }
