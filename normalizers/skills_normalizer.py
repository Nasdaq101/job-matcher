import re
from typing import List, Set, Dict

class SkillsNormalizer:
    def __init__(self):
        # Common skill variations and their normalized forms
        self.skill_mapping = {
            'js': 'javascript',
            'py': 'python',
            'ts': 'typescript',
            'react.js': 'react',
            'reactjs': 'react',
            'node.js': 'node',
            'nodejs': 'node',
            'vue.js': 'vue',
            'vuejs': 'vue',
            'aws': 'amazon web services',
            'gcp': 'google cloud platform',
            'azure': 'microsoft azure',
            'k8s': 'kubernetes',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'nlp': 'natural language processing',
            'cv': 'computer vision',
            'oop': 'object oriented programming',
            'ci/cd': 'continuous integration and deployment',
            'cicd': 'continuous integration and deployment',
            'devops': 'development operations',
            'ui/ux': 'user interface design',
            'ui': 'user interface design',
            'ux': 'user experience design'
        }
        
        # Related skills groups
        self.related_skills = {
            'frontend': {'javascript', 'typescript', 'react', 'vue', 'angular', 'html', 'css'},
            'backend': {'python', 'java', 'node', 'c++', 'go', 'rust', 'ruby'},
            'cloud': {'amazon web services', 'google cloud platform', 'microsoft azure'},
            'data': {'sql', 'postgresql', 'mysql', 'mongodb', 'redis'},
            'ai': {'machine learning', 'artificial intelligence', 'natural language processing', 'computer vision'},
            'devops': {'kubernetes', 'docker', 'continuous integration and deployment', 'development operations'}
        }

    def normalize(self, skills: List[str]) -> List[str]:
        """
        Normalize a list of skills to standard formats.
        """
        if not skills:
            return []
            
        normalized = []
        for skill in skills:
            # Convert to lowercase and strip
            skill = skill.lower().strip()
            
            # Remove special characters except dots for things like node.js
            skill = re.sub(r'[^\w\s.-]', '', skill)
            
            # Check if we have a mapping for this skill
            if skill in self.skill_mapping:
                skill = self.skill_mapping[skill]
            
            if skill:
                normalized.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in normalized if not (x in seen or seen.add(x))]

    def get_related_skills(self, skill: str) -> Set[str]:
        """
        Get related skills for a given skill.
        """
        skill = skill.lower().strip()
        
        # Check if skill is in mapping
        if skill in self.skill_mapping:
            skill = self.skill_mapping[skill]
        
        # Find all skill groups this skill belongs to
        related = set()
        for group, skills in self.related_skills.items():
            if skill in skills:
                related.update(skills)
        
        # Remove the original skill from related set
        related.discard(skill)
        return related

# Create singleton instance
_normalizer = SkillsNormalizer()
normalize = _normalizer.normalize
get_related_skills = _normalizer.get_related_skills 