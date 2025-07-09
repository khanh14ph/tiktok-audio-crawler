from TikTokApi import TikTokApi
import asyncio
import os
from tqdm import tqdm
ms_token = "OosMHDsuRy3tqoM5W18QBtLYIZwVL9aqVduIkA5vyxu7F8eHh6d-L8M_zeqlwnOxL0muV-ScTZ_cNQux_Qjks_7tEu8f-he_pUE92eu9hZrlMXqfqwrt-rwrNqIRHZvX8upblOeZcFfLfj2NBKdVqD6ffg=="

async def user_example(name):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        user = api.user(name)
        print(user.videos)

        # Open a file to write Video IDs
        with open(f"resources/channel_video/{name}.txt", "w") as file:
            count=0
            async for video in user.videos(count=2000):
                print(f"\rProcessing video {count} for user {name}", end="")
                video_id = video.as_dict["video"]["id"]
                # Write the Video ID to the file
                file.write(f"{video_id}\n")
                count += 1

        # async for playlist in user.playlists():
        #     print(playlist)

if __name__ == "__main__":
    channel_lst= open("resources/channel.txt", "r").read().splitlines()
    for channel in channel_lst:
        print(f"Processing channel: {channel}")
        asyncio.run(user_example(channel))
        print(f"Finished processing channel: {channel}")