from typing import Optional
import re

# You can adjust these lists to match your organization's policy or research protocol.
RACE_MAP = {
    # Malaysia-oriented canonical labels
    "malay": "Malay",
    "melayu": "Malay",
    "chinese": "Chinese",
    "cina": "Chinese",
    "indian": "Indian",
    "india": "Indian",  # Added variation
    "bumiputera": "Bumiputera (Sabah/Sarawak)",
    "bumiputera sabah": "Bumiputera (Sabah/Sarawak)",
    "bumiputera sarawak": "Bumiputera (Sabah/Sarawak)",
    "iban": "Bumiputera (Sabah/Sarawak)",
    "kadazan": "Bumiputera (Sabah/Sarawak)",
    "dusun": "Bumiputera (Sabah/Sarawak)",
    "murut": "Bumiputera (Sabah/Sarawak)",
    "orang ulu": "Bumiputera (Sabah/Sarawak)",
    "orang asli": "Orang Asli",
    "other": "Other",
    "others": "Other",
    "lain-lain": "Other",
}

GENDER_MAP = {
    "male": "Male",
    "m": "Male",
    "lelaki": "Male",
    "female": "Female",
    "f": "Female",
    "perempuan": "Female",
    "non-binary": "Non-binary",
    "nonbinary": "Non-binary",
    "nb": "Non-binary",
    "prefer not to say": "Prefer not to say",
    "na": "N/A",
    "n/a": "N/A",
}

ALLOWED_RACES = {
    "Malay", "Chinese", "Indian", "Bumiputera (Sabah/Sarawak)",
    "Orang Asli", "Other"
}
ALLOWED_GENDERS = {"Male", "Female", "Non-binary", "Prefer not to say", "N/A"}

def normalize_race(input_text: Optional[str]) -> str:
    """Normalize race/ethnicity input to standard categories"""
    if not input_text:
        return "N/A"
    key = input_text.strip().lower()
    canonical = RACE_MAP.get(key)
    if canonical:
        return canonical
    # If user typed a canonical label already
    if input_text.strip() in ALLOWED_RACES:
        return input_text.strip()
    return "Other"  # Unknown but user-entered => bucket as "Other"

def normalize_gender(input_text: Optional[str]) -> str:
    """Normalize gender input to standard categories"""
    if not input_text:
        return "N/A"
    key = input_text.strip().lower()
    canonical = GENDER_MAP.get(key)
    if canonical:
        return canonical
    if input_text.strip() in ALLOWED_GENDERS:
        return input_text.strip()
    return "Prefer not to say"  # fallback that avoids guessing

def detect_gender_from_name(name: str) -> str:
    """
    Detect gender from Malaysian naming conventions:
    - a/l (anak lelaki) - male
    - bin - male (son of)
    - a/p (anak perempuan) - female 
    - binti - female (daughter of)
    """
    if not name:
        return "N/A"
    
    name_lower = name.lower().strip()
    
    # Malaysian naming patterns
    male_patterns = [
        r'\ba/l\b',          # a/l (anak lelaki)
        r'\bal\b',           # al (short for a/l)
        r'\bbin\b',          # bin (son of)
        r'\bbinbin\b',       # sometimes written as binbin
    ]
    
    female_patterns = [
        r'\ba/p\b',          # a/p (anak perempuan)
        r'\bap\b',           # ap (short for a/p)
        r'\bbinti\b',        # binti (daughter of)
        r'\bbinte\b',        # alternative spelling
    ]
    
    # Check for male patterns
    for pattern in male_patterns:
        if re.search(pattern, name_lower):
            return "Male"
    
    # Check for female patterns
    for pattern in female_patterns:
        if re.search(pattern, name_lower):
            return "Female"
    
    # No pattern detected
    return "N/A"

def detect_race_from_name(name: str) -> str:
    """
    Detect race from name patterns (especially for Chinese surnames)
    Returns: 'Chinese', 'Indian', 'Malay', or 'N/A'
    """
    if not name:
        return "N/A"
    
    name_parts = name.strip().split()
    if not name_parts:
        return "N/A"
    
    # Get first part (usually surname for Chinese)
    first_part = name_parts[0].lower()
    
    # Common Chinese surnames in Malaysia
    chinese_surnames = {
        'tan', 'lim', 'lee', 'wong', 'ng', 'chan', 'ong', 'teo', 'goh', 'ho',
        'ang', 'yap', 'sia', 'loo', 'koh', 'chong', 'chin', 'yeoh', 'lai', 'low',
        'toh', 'heng', 'sim', 'goh', 'seah', 'tay', 'wee', 'yeo', 'foo', 'gan',
        'chia', 'khoo', 'liu', 'chen', 'chew', 'khor', 'thong', 'kor', 'lam', 'choo',
        'koay', 'neo', 'choong', 'chua', 'chim', 'saw', 'soo', 'yong', 'beh', 'teh',
        'lau', 'ooi', 'kam', 'kong', 'chang', 'chiang', 'khaw', 'siah', 'hoe', 'bay',
        'teoh', 'ting', 'hock', 'hon', 'loke', 'looi', 'mah', 'nah', 'pang', 'quek',
        'soh', 'tang', 'thoo', 'woon', 'yee', 'yuen'
    }
    
    # Check if first part is a Chinese surname
    if first_part in chinese_surnames:
        return "Chinese"
    
    # Check for Indian patterns
    name_lower = name.lower()
    if any(pattern in name_lower for pattern in ['singh', 'a/l', 'al ', 'a/p', 'ap ']):
        return "Indian"
    
    # Check for Malay patterns  
    if any(pattern in name_lower for pattern in ['bin', 'binti', 'bt ', 'bn ']):
        return "Malay"
    
    return "N/A"

def process_demographics(name: str = "", race: str = "", gender: str = "") -> dict:
    """
    Process and normalize demographic data with intelligent detection
    """
    # Normalize provided data
    normalized_race = normalize_race(race) if race else "N/A"
    normalized_gender = normalize_gender(gender) if gender else "N/A"
    
    # If race is not provided or unclear, try to detect from name
    if normalized_race == "N/A" or normalized_race == "Other":
        detected_race = detect_race_from_name(name)
        if detected_race != "N/A":
            normalized_race = detected_race
    
    # If gender is not provided or unclear, try to detect from name
    if normalized_gender == "N/A" or normalized_gender == "Prefer not to say":
        detected_gender = detect_gender_from_name(name)
        if detected_gender != "N/A":
            normalized_gender = detected_gender
    
    return {
        "race": normalized_race,
        "gender": normalized_gender,
        "detection_method": {
            "race_source": "provided" if race and normalize_race(race) not in ["N/A", "Other"] else ("name_detection" if detect_race_from_name(name) != "N/A" else "default"),
            "gender_source": "provided" if gender and normalize_gender(gender) != "N/A" else ("name_detection" if detect_gender_from_name(name) != "N/A" else "default")
        }
    }

# Map to choice codes for database storage
RACE_TO_CODE = {
    "Malay": "MAL",
    "Chinese": "CHN", 
    "Indian": "IND",
    "Bumiputera (Sabah/Sarawak)": "BUM",
    "Orang Asli": "OAS",
    "Other": "OTH",
    "N/A": "N/A"
}

GENDER_TO_CODE = {
    "Male": "M",
    "Female": "F", 
    "Non-binary": "NB",
    "Prefer not to say": "PNS",
    "N/A": "N/A"
}

def get_race_code(race: str) -> str:
    """Convert race to database code"""
    return RACE_TO_CODE.get(race, "OTH")

def get_gender_code(gender: str) -> str:
    """Convert gender to database code"""
    return GENDER_TO_CODE.get(gender, "N/A")

# Example usage
if __name__ == "__main__":
    print("=== Race Normalization ===")
    print(normalize_race("Melayu"))                 # -> Malay
    print(normalize_race("Kadazan"))                # -> Bumiputera (Sabah/Sarawak)
    print(normalize_race(None))                     # -> N/A
    
    print("\n=== Gender Normalization ===")
    print(normalize_gender("perempuan"))            # -> Female
    print(normalize_gender("nonbinary"))            # -> Non-binary
    print(normalize_gender(""))                     # -> N/A
    
    print("\n=== Name-based Gender Detection ===")
    print(detect_gender_from_name("Ahmad bin Rahman"))      # -> Male
    print(detect_gender_from_name("Siti binti Ahmad"))      # -> Female
    print(detect_gender_from_name("Raj a/l Kumar"))         # -> Male
    print(detect_gender_from_name("Priya a/p Devi"))        # -> Female
    print(detect_gender_from_name("John Smith"))            # -> N/A
    
    print("\n=== Complete Processing ===")
    result = process_demographics(
        name="Ahmad bin Rahman", 
        race="melayu", 
        gender=""
    )
    print(f"Name: Ahmad bin Rahman, Race: melayu, Gender: '' -> {result}")
    
    result = process_demographics(
        name="Siti binti Ahmad", 
        race="", 
        gender="perempuan"
    )
    print(f"Name: Siti binti Ahmad, Race: '', Gender: perempuan -> {result}")
