from TikTokApi import TikTokApi
import asyncio
import os

ms_token = "OosMHDsuRy3tqoM5W18QBtLYIZwVL9aqVduIkA5vyxu7F8eHh6d-L8M_zeqlwnOxL0muV-ScTZ_cNQux_Qjks_7tEu8f-he_pUE92eu9hZrlMXqfqwrt-rwrNqIRHZvX8upblOeZcFfLfj2NBKdVqD6ffg=="

async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, browser=os.getenv("TIKTOK_BROWSER", "chromium"))
        async for video in api.trending.videos(count=30):
            print(video.as_dict.keys())

if __name__ == "__main__":
    asyncio.run(trending_videos())