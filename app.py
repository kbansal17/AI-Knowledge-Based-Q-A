from flask import Flask, request, jsonify, render_template
import json
import string
from fuzzywuzzy import fuzz

app = Flask(__name__)

# Load knowledge base
with open('kb.json', 'r') as f:
    knowledge_base = json.load(f)

def clean_text(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).strip()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_question = clean_text(request.json.get('question', ''))

    # Exact match
    for entry in knowledge_base:
        if clean_text(entry['question']) == user_question:
            return jsonify({'answer': entry['answer'], 'status': 'success'})

    # Fuzzy matching (suggest closest match if similarity > threshold)
    threshold = 70
    best_match = None
    best_score = 0

    for entry in knowledge_base:
        score = fuzz.ratio(user_question, clean_text(entry['question']))
        if score > best_score and score >= threshold:
            best_score = score
            best_match = entry

    if best_match:
        return jsonify({
            'answer': f"🤔 Did you mean: \"{best_match['question']}\"?\n\nAnswer: {best_match['answer']}",
            'status': 'suggestion'
        })

    # No match
    return jsonify({
        'answer': "❗ Sorry, I don't know the answer to that question.",
        'status': 'error'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
