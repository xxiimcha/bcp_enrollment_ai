from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app, origins=["https://enrollment.bcp-sms1.com"])

COURSES_API_URL = "https://registrar.bcp-sms1.com/api/courses.php"

def tokenize(text):
    return re.findall(r'\b[a-z]+\b', text.lower())

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    interest_input = data.get('interest', '').strip()
    subject_input = data.get('subject', '').strip()
    level_filter = data.get('level', '').strip().lower()

    if not interest_input or not subject_input or not level_filter:
        return jsonify({"error": "Interest, subject, and level are required."}), 400

    interest_keywords = tokenize(interest_input)
    subject_keywords = tokenize(subject_input)

    try:
        response = requests.get(COURSES_API_URL)
        api_data = response.json()

        if not api_data.get('success'):
            return jsonify({"error": "Failed to fetch course data."}), 500

        best_match = None
        highest_score = 0

        for branch in api_data['branches']:
            branch_type = branch.get('branch_type', '').lower()
            if level_filter != branch_type:
                continue

            branch_name = branch.get('branch_name', 'Unknown Branch')

            for course in branch.get('courses_strands', []):
                course_name = (course.get('name') or '').lower()
                if not course_name:
                    continue

                course_tokens = tokenize(course_name)
                interest_score = sum(1 for word in interest_keywords if word in course_tokens)
                subject_score = sum(1 for word in subject_keywords if word in course_tokens)
                total_score = interest_score + subject_score

                if total_score > highest_score:
                    highest_score = total_score
                    best_match = {
                        "course": course.get('name'),
                        "branch": branch_name,
                        "branch_type": branch_type.title(),
                        "score": total_score
                    }

        if best_match:
            return jsonify({
                "recommendation": best_match["course"],
                "branch": best_match["branch"],
                "branch_type": best_match["branch_type"],
                "reason": f"This course matches your interest in '{interest_input}' and subject '{subject_input}'."
            })
        else:
            return jsonify({
                "recommendation": "General Studies",
                "branch": "Undetermined",
                "branch_type": level_filter.title(),
                "reason": "No strong match found, but this course provides flexibility for multiple interests."
            })

    except Exception as e:
        return jsonify({"error": "Something went wrong while processing.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
