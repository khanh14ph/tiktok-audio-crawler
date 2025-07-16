
from TikTokApi import TikTokApi
import asyncio
import os
from moviepy import VideoFileClip
ms_token = "P8nyrxjmfGXMx5ov8Iae8PaHVjPkZUe4jTC7QvJmQdi6uEZSS7RmvF2pNS-u6lUZPCZawi9GTb-r9HM564p0be0sSMEbN3oiNsQvKe1tV8U355mlPh_gI1LtcPlGGPpn17Xw94oJcupbHu6MazML"
from tqdm import tqdm
from glob import glob
lst=glob("resources/channel_video/*.txt")
result=[]
for i in lst:
    name=i.split("/")[-1][:-4]
    video_ids=open(i, "r").read().splitlines()
    for video_id in video_ids:
        result.append((name, video_id))
async def get_video_example(channel_name, video_id):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        video = api.video(
            url=f"https://www.tiktok.com/@{channel_name}/video/{video_id}"
        )



        video_info = await video.info()  # is HTML request, so avoid using this too much
        video_bytes = await video.bytes()
        os.makedirs(f"downloads/{channel_name}",exist_ok=True)
        video_path = f"downloads/{channel_name}/{video_id}.mp4"
        with open(video_path, "wb") as f:
            f.write(video_bytes)

        # Extract audio and save as FLAC
        video_clip = VideoFileClip(video_path)
        audio_path = f"downloads/{channel_name}/{video_id}.flac"
        video_clip.audio.write_audiofile(audio_path, codec='flac', fps=16000)

        # Clean up the video file if needed
        video_clip.close()
        os.remove(video_path)


if __name__ == "__main__":
    import time
    s=time.time()
    for i in tqdm(result[0:100]):
        asyncio.run(get_video_example(channel_name=i[0], video_id=i[1]))
    print(time.time()-s)