from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    interest = data.get('interest', '').lower()
    subject = data.get('subject', '').lower()

    if 'technology' in interest or 'math' in subject:
        course = "BS in Information Technology"
    elif 'business' in interest or 'accounting' in subject:
        course = "BS in Business Administration"
    elif 'science' in subject or 'health' in interest:
        course = "BS in Nursing"
    elif 'english' in subject or 'education' in interest:
        course = "Bachelor of Secondary Education"
    else:
        course = "General Studies"

    return jsonify({
        "recommendation": course,
        "reason": f"Based on your interest in {interest} and subject in {subject}."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
