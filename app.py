from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, origins=["https://enrollment.bcp-sms1.com"])

COURSES_API_URL = "https://registrar.bcp-sms1.com/api/courses.php"

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    interest = data.get('interest', '').lower()
    subject = data.get('subject', '').lower()

    try:
        response = requests.get(COURSES_API_URL)
        api_data = response.json()

        if not api_data.get('success'):
            return jsonify({"error": "Failed to fetch course data."}), 500

        best_match = None
        match_score = 0

        for branch in api_data['branches']:
            if branch['branch_type'].lower() != 'college':
                continue  # Only process college courses

            branch_name = branch.get('branch_name', 'Unknown Branch')
            for course in branch['courses_strands']:
                course_name = course.get('name', '').lower()

                if not course_name:
                    continue

                score = 0
                if any(keyword in course_name for keyword in interest.split()):
                    score += 1
                if any(keyword in course_name for keyword in subject.split()):
                    score += 1

                if score > match_score:
                    match_score = score
                    best_match = {
                        "course": course.get('name'),
                        "branch": branch_name
                    }

        if best_match:
            return jsonify({
                "recommendation": best_match["course"],
                "branch": best_match["branch"],
                "reason": f"This course matches your interest in '{interest}' and subject '{subject}'."
            })
        else:
            return jsonify({
                "recommendation": "General Studies",
                "branch": "Undetermined",
                "reason": "No strong match found, but this course provides flexibility for multiple interests."
            })

    except Exception as e:
        return jsonify({"error": "Something went wrong while processing.", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
