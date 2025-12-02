import re

def process_command(text):
    """
    Process voice command text to extract search query.
    Example: "Search for funny cats" -> "funny cats"
    """
    if not text:
        return ""
    
    # simple regex to remove "search for" or "show me"
    # case insensitive
    text = text.strip()
    
    patterns = [
        r'^search for\s+(.*)',
        r'^show me\s+(.*)',
        r'^find\s+(.*)',
        r'^look for\s+(.*)'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
            
    return text
