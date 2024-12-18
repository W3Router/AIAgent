from flask import Flask, request, jsonify, render_template_string
import os
from content_assistant import ContentAssistant
from dotenv import load_dotenv

app = Flask(__name__)
content_assistant = ContentAssistant()

# Store pending content with unique IDs
pending_content = {}

# HTML template for the edit page
EDIT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Edit Content</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .content-box {
            border: 1px solid #ddd;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        textarea {
            width: 100%;
            min-height: 150px;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .button-group {
            margin-top: 20px;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 5px;
            text-decoration: none;
            color: white;
            font-weight: bold;
            cursor: pointer;
            border: none;
        }
        .approve { background-color: #28a745; }
        .reject { background-color: #dc3545; }
        .regenerate { background-color: #007bff; }
        .feedback {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            display: none;
        }
    </style>
</head>
<body>
    <h2>Review and Edit Content</h2>
    <div class="content-box">
        <form id="editForm" method="POST">
            <label for="content">Content:</label><br>
            <textarea id="content" name="content">{{content}}</textarea><br>
            <label for="feedback">Feedback for AI (optional):</label><br>
            <textarea id="feedback" name="feedback" placeholder="Enter your feedback for AI to improve the content..."></textarea>
            <div class="button-group">
                <button type="button" class="button approve" onclick="submitAction('approve')">Approve & Post</button>
                <button type="button" class="button reject" onclick="submitAction('reject')">Reject</button>
                <button type="button" class="button regenerate" onclick="submitAction('regenerate')">Regenerate with AI</button>
            </div>
        </form>
    </div>

    <script>
        function submitAction(action) {
            const form = document.getElementById('editForm');
            const content = document.getElementById('content').value;
            const feedback = document.getElementById('feedback').value;
            
            fetch(`/review/${action}/{{content_id}}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    feedback: feedback
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (action === 'regenerate') {
                        document.getElementById('content').value = data.new_content;
                    } else {
                        window.location.href = data.redirect || '/success';
                    }
                } else {
                    alert(data.message || 'An error occurred');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/review/<action>/<content_id>', methods=['GET', 'POST'])
def review_content(action, content_id):
    if content_id not in pending_content:
        return jsonify({"success": False, "message": "Content not found"}), 404
    
    content = pending_content[content_id]
    
    if request.method == 'GET':
        # Show edit page
        return render_template_string(
            EDIT_TEMPLATE,
            content=content['text'],
            content_id=content_id
        )
    
    # Handle POST requests
    data = request.get_json()
    updated_content = data.get('content', content['text'])
    feedback = data.get('feedback', '')
    
    if action == 'approve':
        # Post to Twitter
        tweet_id = content_assistant.post_to_twitter(updated_content)
        if tweet_id:
            del pending_content[content_id]
            return jsonify({
                "success": True,
                "message": "Content approved and posted to Twitter!"
            })
        return jsonify({
            "success": False,
            "message": "Error posting to Twitter"
        })
    
    elif action == 'reject':
        del pending_content[content_id]
        return jsonify({
            "success": True,
            "message": "Content rejected"
        })
    
    elif action == 'regenerate':
        # Use feedback to improve content
        prompt = f"Please improve this content based on the following feedback:\n\nOriginal content:\n{updated_content}\n\nFeedback:\n{feedback}\n\nGenerate improved version:"
        new_content = content_assistant.generate_content(prompt)
        if new_content:
            return jsonify({
                "success": True,
                "new_content": new_content
            })
        return jsonify({
            "success": False,
            "message": "Error generating new content"
        })
    
    return jsonify({"success": False, "message": "Invalid action"}), 400

@app.route('/success')
def success():
    return "Action completed successfully!"

if __name__ == '__main__':
    load_dotenv()
    app.run(host='0.0.0.0', port=5001)
