import praw
import json
# from prawcore.exceptions import ResponseException
from pydub import AudioSegment
from pydub.playback import play
from gtts import gTTS
import numpy as np
import pandas as pd
import os
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import shutil

# reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
reddit_object = praw.Reddit(
    client_id="HDdI1LLvE7uDANi3oQ2teQ",
    client_secret="oDoTRKQhuCRVHmqgb5RyjyFsyQAYqw",
    user_agent="testing by u'/JuggernautBorn5378 "
    # username="JuggernautBorn5378",
    # password="kanakshat"
)
