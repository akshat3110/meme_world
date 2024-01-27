from config import *
from concurrent.futures import ThreadPoolExecutor
import os

def get_meme_videos(search, number_of_post,sort_opt, time):
    print(search, number_of_post,sort_opt, time)
    sorting_options =tuple(sort_opt)
    # search_relevence = reddit_object.subreddit('all').search(search,sort = sorting_options, time_filter=time, limit=1000)
    search_relevence = reddit_object.subreddit(f'{search}')
    result_url = []
    video_url = []
    audio_url = []
    posts = []
    for i in search_relevence.hot(limit=10):
        temp = dict()
        temp['is_video'] = i.is_video
        temp['i.media'] = True if i.media and 'reddit_video' in i.media else False
        temp['title'] = i.title
        temp['duration'] = i.media['reddit_video']['duration'] if i.is_video == True else 0
        temp['reddit_post_url'] = i.url
        temp['Number_of_likes'] = i.score
        temp['Number_of_comments'] = i.num_comments
        temp['video_url'] = i.media['reddit_video']['fallback_url'] if i.media and 'reddit_video' in i.media else "None"
        temp['audio_url'] = i.media['reddit_video']['fallback_url'].split("DASH_")[0] + "DASH_AUDIO_128.mp4" if i.media and 'reddit_video' in i.media else "None"
        posts.append(temp)
    data_revelence = pd.DataFrame(posts)

    # for i in search_top:
    #     temp = dict()
    #     # if len(set(result_title)) == number_of_post:
    #     #     break
    #     temp['is_video'] = i.is_video
    #     temp['i.media'] = True if i.media and 'reddit_video' in i.media else False
    #     temp['title'] = i.title
    #     temp['reddit_post_url'] = i.url
    #     temp['Number_of_likes'] = i.score
    #     temp['Number_of_comments'] = i.num_comments
    #     temp['video_url'] = i.media['reddit_video']['fallback_url'] if i.media and 'reddit_video' in i.media else "None"
    #     temp['audio_url'] = i.media['reddit_video']['fallback_url'].split("DASH_")[0] + "DASH_AUDIO_128.mp4" if i.media and 'reddit_video' in i.media else "None"
    #     posts.append(temp)
    # data_top = pd.DataFrame(posts)

    # data = pd.concat([data_revelence, data_top])
    data = data_revelence
    
    data['Number_of_likes'] = data['Number_of_likes'].astype(int)
    data['Number_of_comments'] = data['Number_of_comments'].astype(int)
    data = data[(data['video_url']!= 'None') & (data['audio_url'] != 'None')]
    data = data.drop_duplicates(subset = 'title').reset_index(drop=True)
    data = data.drop_duplicates(subset = 'video_url').reset_index(drop=True)
    data = data[(data['i.media']==True) & (data['duration'] < 60) & (data['Number_of_comments'] > 10)]
    data = data.sort_values(by = ['Number_of_likes','Number_of_comments'], ascending=False).reset_index(drop=True)
    
    data = data[:number_of_post]
    # print(data.head())
    # print(data['duration'].value_counts())
    print(data[['Number_of_comments','Number_of_likes' ]])
    
    folder_path = "final_videos"
    if os.path.exists(folder_path):
        # Delete the folder and its contents
        shutil.rmtree(folder_path)

    if data.shape[0]>0:
        text = f"Hello Guys,here are the top {search} Videos for you "

        tts = gTTS(text)
        tts.save(f"output.mp3")
        audio = AudioSegment.from_mp3("output.mp3")
        # play(audio)
        title = data['title'].unique().tolist()
        result_url = data['reddit_post_url'].unique().tolist()
        video_url = data['video_url'].unique().tolist()
        audio_url = data['audio_url'].unique().tolist()
        print("-"*10, "Reddit Posts", result_url)
        print("-"*10, "Titles Posts",title)
        print("-"*10, "Video Posts URLs",video_url)
        print("-"*10, "Audio Posts URLs",audio_url)


        def download_and_merge_video(video_url, audio_url, output_folder, i):
            # Download video content
            video_response = requests.get(video_url)
            video_filename = os.path.join(output_folder, f"video_{i}.mp4")

            if video_response.status_code == 200:
                with open(video_filename, 'wb') as video_file:
                    video_file.write(video_response.content)
                print(f"Video downloaded and saved as {video_filename}")
            else:
                print(f"Failed to download video from {video_url}. Status code: {video_response.status_code}")
                return None

            # Download audio content
            audio_response = requests.get(audio_url)
            audio_filename = os.path.join(output_folder, f"audio_{i}.mp3")

            if audio_response.status_code == 200:
                with open(audio_filename, 'wb') as audio_file:
                    audio_file.write(audio_response.content)
                print(f"Audio downloaded and saved as {audio_filename}")
            else:
                print(f"Failed to download audio from {audio_url}. Status code: {audio_response.status_code}")
                return None

            # Merge video and audio
            video_clip = VideoFileClip(video_filename)
            audio_clip = AudioFileClip(audio_filename)
            video_clip = video_clip.set_audio(audio_clip)

            # Write the final video file
            final_output_filename = os.path.join(output_folder, f"final_videos_{i}.mp4")
            try:
                video_clip.write_videofile(final_output_filename, codec='libx264', audio_codec='aac')
                print(f"Final video saved as {final_output_filename}")
            except Exception as e:
                print(f"Error writing final video file: {e}")

            # Optionally, you can delete the individual video and audio files if needed
            # os.remove(video_filename)
            # os.remove(audio_filename)

        def download_and_merge_videos_parallel(video_urls, audio_urls, output_folder):
            # Create the output folder if it doesn't exist
            os.makedirs(output_folder, exist_ok=True)

            with ThreadPoolExecutor(max_workers=10) as executor:
                # Use executor.map to download and merge videos in parallel
                results = executor.map(download_and_merge_video, video_urls, audio_urls, [output_folder] * len(video_urls), range(1, len(video_urls) + 1))

            # Check for any failures during the parallel processing
            if None in results:
                print("Some downloads or merges failed.")
                

        
        video_urls = video_url
        audio_urls = audio_url
        output_folder = "final_videos"
        download_and_merge_videos_parallel(video_urls, audio_urls, output_folder)

        def merge_audio_and_video(audio_path, video_path, output_path):
            # Load the audio and video clips
            audio_clip = AudioFileClip(audio_path)
            video_clip = VideoFileClip(video_path)

            # Set the audio of the video to the loaded audio clip
            video_clip = video_clip.subclip(0, audio_clip.duration)
            video_clip = video_clip.set_audio(audio_clip)
            # Write the merged video to the output file
            video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)

        audio_file_path = 'output.mp3'
        video_file_path = 'final_videos/video_1.mp4'
        output_file_path = 'final_videos/final_output_video.mp4'

        print("Call merge..............................................")
        merge_audio_and_video(audio_file_path, video_file_path, output_file_path)
    else:
        print("No Data Found")

    print("---------------------------done-----------------------------------------------------")