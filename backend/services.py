# backend/services.py
import logging
import requests

logger = logging.getLogger(__name__)

class ThemeExtractor:
    def __init__(self):
        self.pipeline = None
        self.initialized = False

    def _init_pipeline(self):
        if not self.initialized:
            try:
                from transformers import pipeline
                self.pipeline = pipeline("ner", model="elastic/distilbert-base-uncased-finetuned-conll03-english", aggregation_strategy="simple")
                self.initialized = True
            except Exception as e:
                logger.warning(f"Failed to load transformers NER pipeline: {e}. Falling back to rule-based theme extraction.")
                self.pipeline = None
                self.initialized = True

    def extract_themes(self, text: str) -> list:
        self._init_pipeline()
        if self.pipeline:
            try:
                entities = self.pipeline(text)
                themes = list(set([ent['word'].strip() for ent in entities if ent.get('word')]))
                themes = [t for t in themes if len(t) > 2]
                if themes:
                    return themes
            except Exception as e:
                logger.error(f"Error running NER pipeline: {e}")
        
        # Fallback: simple rule-based theme extractor
        words = text.split()
        candidate_themes = []
        for w in words:
            w_clean = "".join([c for c in w if c.isalnum() or c in ['-', '_']])
            if len(w_clean) > 2:
                if w_clean[0].isupper() or w_clean.lower() in ["kubernetes", "python", "rust", "docker", "react", "fastapi", "streamlit", "ai", "ml", "devops"]:
                    candidate_themes.append(w_clean)
        
        seen = set()
        themes = []
        for t in candidate_themes:
            t_lower = t.lower()
            if t_lower not in seen and t_lower not in ["the", "and", "for", "with", "this", "that"]:
                seen.add(t_lower)
                themes.append(t)
        return themes[:5]

class StarterGenerator:
    def generate_starters(self, context: str, themes: list, relationship: str, tone: str) -> list:
        """Generates high-quality conversational icebreakers tailored by relationship and tone."""
        theme_str = ", ".join(themes[:2]) if themes else "your recent work"
        relationship_lower = relationship.lower()
        tone_lower = tone.lower()
        
        if relationship_lower == "recruiter":
            if tone_lower == "casual":
                return [
                    f"Hey! Noticed you recruit in the {theme_str} space. I've been working on some cool projects here—would love to chat casually about what you're seeing in the market.",
                    f"Hi there, saw your posts about roles involving {theme_str}. I have a background in this area and wanted to connect to keep in touch for future opportunities!",
                    f"Hey, hope your week is going well. I'm active in {theme_str} and wanted to reach out. Are there any specific profiles or skills you're currently looking for?"
                ]
            elif tone_lower == "warm":
                return [
                    f"Hello! I hope you're having a wonderful week. I came across your profile and noticed your focus on recruiting for {theme_str}. I'd love to connect and learn more about the exciting teams you're building.",
                    f"Hi, it's great to connect with you. I'm really passionate about {theme_str} and saw you represent roles in this field. I'd love to share my journey and see if we might align on any upcoming opportunities.",
                    f"Hello! I wanted to reach out and say hello. I've been following your updates on {theme_str} talent, and I'd love to connect to discuss how my experience might fit into your pipeline."
                ]
            else: # professional
                return [
                    f"Dear Recruiter, I hope this message finds you well. I am reaching out as I noticed your specialization in recruiting for {theme_str}. I would appreciate the opportunity to connect and discuss potential alignment.",
                    f"Hello, I hope you're having a productive day. I came across your profile and wanted to connect. I have extensive experience with {theme_str} and would love to learn more about current open roles.",
                    f"Dear Colleague, I am writing to introduce myself. I specialize in {theme_str} and wanted to connect to see if my background aligns with any search mandates you are currently executing."
                ]
        elif relationship_lower == "mentor":
            if tone_lower == "casual":
                return [
                    f"Hey! I've been following your work in {theme_str} and really admire what you do. Would love to connect and grab a virtual coffee sometime to chat about your journey.",
                    f"Hi! Your background in {theme_str} is super inspiring. If you have a few minutes sometime, I'd love to get your quick take on how the industry is evolving.",
                    f"Hey there, love your insights on {theme_str}. I'm trying to grow in this area and would be incredibly grateful to connect and learn from your experience."
                ]
            elif tone_lower == "warm":
                return [
                    f"Hello! I hope you're doing well. I've been reading your posts about {theme_str} and find your perspective incredibly valuable. I'd be honored to connect and learn from your career journey.",
                    f"Hi, I hope your week is going beautifully. I'm currently working on building my skills in {theme_str} and would love to connect. Your advice and guidance would be highly appreciated.",
                    f"Hello! I wanted to reach out because your expertise in {theme_str} really stands out. I'd love to connect and occasionally seek your guidance as I navigate my path in this field."
                ]
            else: # professional
                return [
                    f"Dear Mentor, I hope this message finds you well. I have been following your professional contributions to the {theme_str} field. I would be grateful to connect and potentially seek your mentorship.",
                    f"Hello, I am reaching out to connect with senior leaders in the {theme_str} space. Your career trajectory is very impressive, and I would value the opportunity to learn from your insights.",
                    f"Dear Colleague, I hope you are well. Given your extensive expertise in {theme_str}, I wanted to request a brief connection to discuss industry best practices and professional development."
                ]
        elif relationship_lower == "client":
            if tone_lower == "casual":
                return [
                    f"Hey! Saw that you guys are focusing on {theme_str}. We've been helping folks solve some interesting challenges in this area—would love to connect and share some ideas.",
                    f"Hi! Hope you're having a great week. I noticed your team's work with {theme_str} and wanted to reach out. Let's connect and see if we can collaborate sometime.",
                    f"Hey there, saw your recent project involving {theme_str}. Looks awesome! Would love to connect and learn more about your goals for this quarter."
                ]
            elif tone_lower == "warm":
                return [
                    f"Hello! I hope you're doing well. I came across your business and was really impressed by your approach to {theme_str}. I'd love to connect and explore how we might add value to your initiatives.",
                    f"Hi, it's great to connect. I love what your team is building in the {theme_str} space. I'd love to stay in touch and see if there are opportunities to support your growth down the line.",
                    f"Hello! I wanted to reach out and congratulate you on your recent progress with {theme_str}. I'd love to connect to discuss how we can help optimize your workflows."
                ]
            else: # professional
                return [
                    f"Dear Client, I hope this message finds you well. I am reaching out to connect as I assist organizations in optimizing their operations with respect to {theme_str}. I would welcome a brief discussion.",
                    f"Hello, I hope you are having a successful week. I have been following your organization's work in {theme_str} and would love to connect to explore potential business collaboration.",
                    f"Dear Colleague, I am writing to connect with key stakeholders in the {theme_str} domain. I would appreciate the opportunity to introduce our services and discuss how we can support your objectives."
                ]
        else: # colleague / default
            if tone_lower == "casual":
                return [
                    f"Hey! Noticed we both work in the {theme_str} space. Would love to connect and exchange notes on what we're building!",
                    f"Hi there! Saw your posts about {theme_str}. I'm also working on this and wanted to reach out to say hello and connect.",
                    f"Hey, hope you're having a good week. Love to connect with fellow builders in the {theme_str} community!"
                ]
            elif tone_lower == "warm":
                return [
                    f"Hello! I hope you're having a great week. I came across your profile and noticed your focus on {theme_str}. I'd love to connect and share ideas about our shared interests.",
                    f"Hi, it's great to connect with you. I'm really passionate about {theme_str} and would love to add you to my professional network so we can support each other's work.",
                    f"Hello! I wanted to reach out and say hello. I've been following your updates on {theme_str} and would love to connect to stay in touch on industry trends."
                ]
            else: # professional
                return [
                    f"Dear Colleague, I hope this message finds you well. I am reaching out to connect as we share mutual professional interests in the field of {theme_str}.",
                    f"Hello, I hope you're having a productive day. I came across your profile and wanted to connect to expand my network of professionals working in {theme_str}.",
                    f"Dear Professional, I am writing to introduce myself. I work within the {theme_str} domain and wanted to connect to share insights and discuss industry developments."
                ]

class FactChecker:
    def verify_topic(self, query: str) -> dict:
        """Verifies a claim via Wikipedia API. Returns a dict compatible with FactCheckResponse."""
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": query,
            "redirects": 1
        }
        
        headers = {
            "User-Agent": "PersonalizedNetworkingAssistant/1.0 (student-project@apsche-vip.org)"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1":
                    title = page_data.get("title")
                    summary = page_data.get("extract", "No summary paragraph details found.")
                    safe_title = requests.utils.quote(title.replace(" ", "_"))
                    source_url = f"https://en.wikipedia.org/wiki/{safe_title}"
                    return {
                        "verified": True,
                        "message": f"Successfully verified against Wikipedia article: '{title}'",
                        "title": title,
                        "summary": summary,
                        "source_url": source_url
                    }
            return {
                "verified": False,
                "message": f"Could not find matching Wikipedia data for '{query}'.",
                "title": None,
                "summary": None,
                "source_url": None
            }
        except Exception as e:
            return {
                "verified": False,
                "message": f"Factcheck verification sync paused: {str(e)}",
                "title": None,
                "summary": None,
                "source_url": None
            }

def extract_themes_and_generate_starters(event_description: str, interests: str) -> list:
    themes = ThemeExtractor().extract_themes(event_description)
    return StarterGenerator().generate_starters(
        context=event_description,
        themes=themes,
        relationship="colleague",
        tone="professional"
    )