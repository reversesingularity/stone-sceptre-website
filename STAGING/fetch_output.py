"""Quick script to call Agent 13 and dump full output."""
import httpx, json, sys

r = httpx.post('http://localhost:8773/generate_content', json={
    'content_type': 'twitter_thread',
    'source_text': (
        "Brennan McNeeve trembled as the spectrographic overlay resolved. "
        "The acoustic signature of Adon's miracle cure was Cydonian. "
        "The same resonant frequency that powered the pyramids of Mars "
        "was embedded in every dose distributed to three billion human beings. "
        "'He is not curing them,' Brennan whispered. 'He is tuning them.'"
    ),
    'target_audience': 'Christian speculative fiction readers',
    'key_themes': ['acoustic reality', 'endurance commission', 'False Prophet', 'Cydonian technology'],
    'book_number': 3,
    'chapter_number': 2,
    'tone': 'urgent'
}, timeout=300)

data = r.json()
# Write full response to file
with open('STAGING/agent13_output.json', 'w') as f:
    json.dump(data, f, indent=2)

cv = data.get('content_variants', {})
print("=== STATUS:", r.status_code)
print()
print("=== SHORT ===")
print(cv.get('short', 'N/A'))
print()
print("=== MEDIUM ===")
print(cv.get('medium', 'N/A'))
print()
print("=== LONG ===")
print(cv.get('long', 'N/A'))
print()
print("=== HASHTAGS ===")
print(', '.join(data.get('hashtags', [])))
print()
print("=== SEO KEYWORDS ===")
print(', '.join(data.get('seo_keywords', [])))
print()
print("--- Full JSON saved to STAGING/agent13_output.json ---")
