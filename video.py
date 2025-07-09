
from TikTokApi import TikTokApi
import asyncio
import os

ms_token = "OosMHDsuRy3tqoM5W18QBtLYIZwVL9aqVduIkA5vyxu7F8eHh6d-L8M_zeqlwnOxL0muV-ScTZ_cNQux_Qjks_7tEu8f-he_pUE92eu9hZrlMXqfqwrt-rwrNqIRHZvX8upblOeZcFfLfj2NBKdVqD6ffg=="
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
        print(video_info)
        video_bytes = await video.bytes()
        os.makedirs(f"downloads/{channel_name}",exist_ok=True)
        with open(f"downloads/{channel_name}/{video_id}.mp4", "wb") as f:
            f.write(video_bytes)


if __name__ == "__main__":
    for i in tqdm(result):
        asyncio.run(get_video_example(channel_name=i[0], video_id=i[1]))