import re
from geopy.geocoders import Nominatim

class LocationNormalizer:
    def __init__(self):
        # State abbreviations to full names
        self.state_mapping = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }
        
        # Major metro areas and their variations
        self.metro_areas = {
            'san francisco bay area': {'san francisco', 'oakland', 'san jose', 'silicon valley', 'fremont', 'palo alto', 'mountain view', 'redwood city', 'santa clara', 'sunnyvale', 'hayward', 'san leandro'},
            'greater boston': {'boston', 'cambridge', 'waltham', 'braintree', 'chelsea', 'billerica'},
            'greater seattle area': {'seattle', 'bellevue', 'redmond', 'bothell', 'renton', 'everett'},
            'greater chicago area': {'chicago', 'evanston', 'naperville', 'schaumburg'},
            'new york city metropolitan area': {'new york', 'brooklyn', 'jersey city', 'newark', 'manhattan'},
            'washington dc-baltimore area': {'washington dc', 'washington d.c.', 'baltimore', 'arlington', 'alexandria', 'mclean', 'fairfax', 'tysons'},
            'greater los angeles area': {'los angeles', 'long beach', 'anaheim', 'burbank', 'glendale', 'santa monica'},
            'greater houston': {'houston', 'spring', 'the woodlands', 'sugar land'},
            'dallas-fort worth metroplex': {'dallas', 'fort worth', 'irving', 'plano', 'arlington', 'richardson'},
            'greater atlanta': {'atlanta', 'alpharetta', 'duluth', 'smyrna'},
            'greater philadelphia': {'philadelphia', 'camden', 'wilmington', 'king of prussia'},
            'greater phoenix area': {'phoenix', 'scottsdale', 'tempe', 'chandler', 'mesa'},
            'greater pittsburgh region': {'pittsburgh', 'allegheny'},
            'greater sacramento': {'sacramento', 'roseville', 'folsom'},
            'greater minneapolis-st. paul area': {'minneapolis', 'st paul', 'saint paul', 'bloomington'},
        }

        # Reverse mapping for metro areas
        self.city_to_metro = {}
        self.geolocator = Nominatim(user_agent="job_search_app")
        for metro, cities in self.metro_areas.items():
            for city in cities:
                self.city_to_metro[city] = metro

    def normalize(self, location: str, enable_geolocator: bool = False) -> str:
        """
        Normalize location string to a standard format.
        Returns the most specific valid location identifier.
        """
        if not location or location.lower() == 'not specified':
            return 'united states'
            
        # Convert to lowercase for processing
        location = location.lower().strip()

        if enable_geolocator:
            if 'united states' not in location:
                location = location + ', united states'

            try:
                location = self.geolocator.geocode(location).raw['name'].lower().strip()
            except Exception as e:
                pass

        # Handle "United States" variations
        if location in {'united states', 'us', 'usa', 'u.s.', 'u.s.a.'}:
            return 'united states'
            
        # Remove common prefixes
        location = re.sub(r'^greater\s+|^the\s+', '', location)
        
        # Split location into components
        parts = [p.strip() for p in re.split(r'[,|-]', location)]
        parts = [p for p in parts if p and p not in {'united states', 'us', 'usa', 'area', 'region', 'metropolitan', 'metro', 'metroplex'}]
        
        if not parts:
            return 'united states'
            
        # Check for metro areas
        for part in parts:
            # Direct metro area match
            if part in self.metro_areas:
                return part
            # City in metro area match
            if part in self.city_to_metro:
                return self.city_to_metro[part]
        
        # Handle state abbreviations
        for part in parts:
            part = part.upper()
            if part in self.state_mapping:
                # If we have a city, return "city, state"
                if len(parts) > 1:
                    city = parts[0].strip()
                    return f"{city}, {self.state_mapping[part].lower()}"
                return self.state_mapping[part].lower()
        
        # Handle full state names
        for part in parts:
            for state_name in self.state_mapping.values():
                if part == state_name.lower():
                    return state_name.lower()
        
        # If we have multiple parts but couldn't match a state, assume first part is city
        if len(parts) > 1:
            return f"{parts[0]}, united states"
            
        # Default to the original location with United States
        return f"{parts[0]}, united states"

# Create singleton instance
_normalizer = LocationNormalizer()
normalize = _normalizer.normalize 