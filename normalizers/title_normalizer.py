import re
from typing import Set, List, Optional

class TitleNormalizer:
    def __init__(self):
        # Define the four seniority levels
        self.ENTRY_LEVEL = "entry-level"
        self.MID_LEVEL = "mid-level"
        self.SENIOR_LEVEL = "senior-level"
        self.LEAD_LEVEL = "lead-level"
        
        # Role aliases and abbreviations mapping
        self.role_aliases = {
            # Software Engineering roles
            'sde': 'software development engineer',
            'swe': 'software engineer',
            'dev': 'software developer',
            'developer': 'software developer',
            'programmer': 'software developer',
            'coder': 'software developer',
            'backend': 'backend developer',
            'frontend': 'frontend developer',
            'fullstack': 'full stack developer',
            'full-stack': 'full stack developer',
            'full stack': 'full stack developer',
            
            # Data Science roles
            'ds': 'data scientist',
            'mle': 'machine learning engineer',
            'ml engineer': 'machine learning engineer',
            'ai engineer': 'machine learning engineer',
            'data engineer': 'data engineer',
            'de': 'data engineer',
            'analytics engineer': 'data analyst',
            'data analytics': 'data analyst',
            
            # Business Intelligence roles
            'bie': 'business intelligence engineer',
            'bi engineer': 'business intelligence engineer',
            'bi developer': 'business intelligence developer',
            'bi analyst': 'business intelligence analyst',
            
            # DevOps and Infrastructure roles
            'sre': 'site reliability engineer',
            'devops': 'devops engineer',
            'platform engineer': 'devops engineer',
            'cloud engineer': 'cloud infrastructure engineer',
            'infra': 'infrastructure engineer',
            
            # Quality Assurance roles
            'qa': 'quality assurance engineer',
            'sdet': 'software development engineer in test',
            'test engineer': 'quality assurance engineer',
            'automation engineer': 'quality assurance automation engineer',
            
            # Product and Project roles
            'pm': 'product manager',
            'po': 'product owner',
            'tpm': 'technical program manager',
            'program manager': 'technical program manager',
            
            # Security roles
            'security engineer': 'information security engineer',
            'appsec': 'application security engineer',
            'infosec': 'information security engineer',
            
            # Mobile roles
            'ios': 'ios developer',
            'android': 'android developer',
            'mobile': 'mobile developer',
        }
        
        # Map various prefixes and suffixes to seniority levels
        self.seniority_mapping = {
            # Entry level indicators
            'junior': self.ENTRY_LEVEL,
            'jr': self.ENTRY_LEVEL,
            'entry level': self.ENTRY_LEVEL,
            'entry-level': self.ENTRY_LEVEL,
            'associate': self.ENTRY_LEVEL,
            'intern': self.ENTRY_LEVEL,
            'trainee': self.ENTRY_LEVEL,
            'graduate': self.ENTRY_LEVEL,
            'level 1': self.ENTRY_LEVEL,
            'level i': self.ENTRY_LEVEL,
            'i': self.ENTRY_LEVEL,
            'grade 1': self.ENTRY_LEVEL,
            
            # Mid level indicators
            'mid': self.MID_LEVEL,
            'mid level': self.MID_LEVEL,
            'mid-level': self.MID_LEVEL,
            'intermediate': self.MID_LEVEL,
            'level 2': self.MID_LEVEL,
            'level ii': self.MID_LEVEL,
            'ii': self.MID_LEVEL,
            'grade 2': self.MID_LEVEL,
            'level 3': self.MID_LEVEL,
            'level iii': self.MID_LEVEL,
            'iii': self.MID_LEVEL,
            'grade 3': self.MID_LEVEL,
            
            # Senior level indicators
            'senior': self.SENIOR_LEVEL,
            'sr': self.SENIOR_LEVEL,
            'staff': self.SENIOR_LEVEL,
            'principal': self.SENIOR_LEVEL,
            'distinguished': self.SENIOR_LEVEL,
            'level 4': self.SENIOR_LEVEL,
            'level iv': self.SENIOR_LEVEL,
            'iv': self.SENIOR_LEVEL,
            'grade 4': self.SENIOR_LEVEL,
            
            # Lead level indicators
            'lead': self.LEAD_LEVEL,
            'chief': self.LEAD_LEVEL,
            'head': self.LEAD_LEVEL,
            'director': self.LEAD_LEVEL,
            'manager': self.LEAD_LEVEL,
            'architect': self.LEAD_LEVEL,
            'level 5': self.LEAD_LEVEL,
            'level v': self.LEAD_LEVEL,
            'v': self.LEAD_LEVEL,
            'grade 5': self.LEAD_LEVEL,
        }

    def _normalize_role(self, title: str) -> str:
        """
        Normalize role aliases and abbreviations.
        """
        # Split the title into words
        words = title.lower().split()
        
        # Try to match multi-word aliases first
        for i in range(len(words), 0, -1):
            for j in range(len(words) - i + 1):
                phrase = ' '.join(words[j:j+i])
                if phrase in self.role_aliases:
                    # Replace the matched phrase with its normalized version
                    words[j:j+i] = self.role_aliases[phrase].split()
                    return ' '.join(words)
        
        # Try to match individual words
        for i, word in enumerate(words):
            if word in self.role_aliases:
                words[i] = self.role_aliases[word]
        
        return ' '.join(words)

    def _extract_seniority(self, title: str) -> tuple[Optional[str], str]:
        """
        Extract seniority level from title if it exists.
        Returns (seniority_level, remaining_title)
        """
        words = title.split()
        if not words:
            return None, ""
            
        # Check for exact matches in first word
        first_word = words[0].lower()
        if first_word in self.seniority_mapping:
            return self.seniority_mapping[first_word], ' '.join(words[1:])
            
        # Check for two-word prefixes
        if len(words) >= 2:
            first_two = ' '.join(words[:2]).lower()
            if first_two in self.seniority_mapping:
                return self.seniority_mapping[first_two], ' '.join(words[2:])
        
        # Check for suffixes
        last_word = words[-1].lower()
        if last_word in self.seniority_mapping:
            return self.seniority_mapping[last_word], ' '.join(words[:-1])
            
        # Check for two-word suffixes
        if len(words) >= 2:
            last_two = ' '.join(words[-2:]).lower()
            if last_two in self.seniority_mapping:
                return self.seniority_mapping[last_two], ' '.join(words[:-2])
        
        # Check if any word indicates seniority
        for word in words:
            word = word.lower()
            if word in self.seniority_mapping:
                remaining_words = [w for w in words if w.lower() != word]
                return self.seniority_mapping[word], ' '.join(remaining_words)
                
        # Default to mid-level if no seniority indicator is found
        return self.MID_LEVEL, ' '.join(words)

    def normalize(self, title: str) -> str:
        """
        Normalize job title to a standard format with one of four seniority levels:
        entry-level, mid-level, senior-level, or lead-level
        """
        if not title:
            return ""
            
        # Convert to lowercase and strip
        title = title.lower().strip()
        
        # Remove parenthetical content
        title = re.sub(r'\([^)]*\)', '', title)
        
        # First normalize the role aliases
        title = self._normalize_role(title)
        
        # Then extract seniority if present
        seniority, remaining_title = self._extract_seniority(title)
        
        # Clean remaining title
        title = remaining_title.strip()
        title = re.sub(r'[^\w\s-]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Combine seniority with cleaned title
        if seniority:
            title = f"{seniority} {title}"
            
        return title.strip()

# Create singleton instance
_normalizer = TitleNormalizer()
normalize = _normalizer.normalize 