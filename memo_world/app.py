from flask import Flask, render_template, request, jsonify, send_from_directory
from main import get_meme_videos
import os

app = Flask(__name__)

# Define the folder to store the final videos
final_videos_folder = os.path.abspath(os.path.join(os.getcwd(), 'final_videos'))
if not os.path.exists(final_videos_folder):
    os.makedirs(final_videos_folder)

@app.route('/')
def index():
    return render_template('memo_world.html')

@app.route('/api/memes', methods=['GET'])
def fetch_memes():
    try:
        print("in")
        meme_name = request.args.get('memeName')
        num_posts = int(request.args.get('numPosts'))
        sorting = request.args.get('sorting').split(',')
        time = request.args.get('timeRange')
        
        # Call your existing backend function
        get_meme_videos(meme_name, num_posts, sorting, time)
        print("Extracted.....")
        # Save the videos to the final_videos folder
        saved_videos = os.listdir(final_videos_folder)

        return jsonify(saved_videos)

    except Exception as e:
        error_message = str(e)
        return jsonify({"error": error_message}), 500

@app.route('/final_videos/<filename>')
def download_file(filename):
    return send_from_directory(final_videos_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
