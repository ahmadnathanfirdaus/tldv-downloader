import json
import os
import subprocess

import requests

# Create a 'downloads' directory if it doesn't exist
base_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(base_dir, 'downloads')

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Get the URL of the meeting from the user
url = input("Please paste the URL of the meeting you want to download: ")

# Extract the meeting ID from the URL
try:
    meeting_id = url.split("/meetings/")[1].strip('/')
    print(f"Found meeting ID: {meeting_id}")
except IndexError:
    print("Invalid URL format. Please ensure the URL is in the correct format.")
    exit()

# Make a request to the API to get the meeting information
api_url = f"https://gw.tldv.io/v1/meetings/{meeting_id}/watch-page?noTranscript=true"
print(f"Making request to: {api_url}")

# Initialize headers
headers = {}

# Make initial request
response = requests.get(api_url, headers=headers)

# Check if we get a 403 Forbidden error
if response.status_code == 403:
    print("Access forbidden (403). Authentication token required.")
    token = input("Please enter your authentication token: ")

    # Add token to headers (assuming Bearer token format)
    headers['Authorization'] = f'Bearer {token}'

    # Retry the request with the token
    print("Retrying request with authentication token...")
    response = requests.get(api_url, headers=headers)

# Check the final response status
if response.status_code == 200:
    data = response.json()
    print("Response JSON data:",
          json.dumps(data, indent=2))  # Imprime el contenido de la respuesta JSON para depuración

    if 'video' in data and 'source' in data['video']:
        video_url = data['video']['source']
        print(f"Video URL: {video_url}")

        # Name the downloaded file as the meeting ID with .mp4 extension
        mp4_file_path = os.path.join(download_dir, f"{meeting_id}.mp4")

        # Use ffmpeg to download the video
        command = [
            "ffmpeg", "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
            "-i", video_url, "-c", "copy", mp4_file_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        # Print the output of the ffmpeg command
        print(result.stdout)
        print(result.stderr)

        # Check if the video file was created successfully
        if os.path.exists(mp4_file_path):
            print(f"Video converted successfully as {mp4_file_path}")
        else:
            print("Failed to convert the video.")
    else:
        print("'video' key not found in the response JSON.")
elif response.status_code == 403:
    print("Access still forbidden after providing token. Please check if your token is valid.")
    print(f"Response content: {response.content}")
else:
    print(f"Failed to get the meeting information. Status code: {response.status_code}")
    print(f"Response content: {response.content}")
