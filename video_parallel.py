from TikTokApi import TikTokApi
import asyncio
import os
from glob import glob

ms_token = "OosMHDsuRy3tqoM5W18QBtLYIZwVL9aqVduIkA5vyxu7F8eHh6d-L8M_zeqlwnOxL0muV-ScTZ_cNQux_Qjks_7tEu8f-he_pUE92eu9hZrlMXqfqwrt-rwrNqIRHZvX8upblOeZcFfLfj2NBKdVqD6ffg=="

# Đọc danh sách video IDs
lst = glob("resources/channel_video/*.txt")
result = []
for i in lst:
    name = i.split("/")[-1][:-4]
    video_ids = open(i, "r").read().splitlines()
    for video_id in video_ids:
        result.append((name, video_id))
result=result[0:10]
async def download_video(api, channel_name, video_id):
    """Tải xuống một video"""
    video_url = f"https://www.tiktok.com/@{channel_name}/video/{video_id}"
    video = api.video(url=video_url)
    
    print(f"Đang tải: {channel_name}/{video_id}")
    video_info = await video.info()
    video_bytes = await video.bytes()
    
    # Tạo thư mục nếu chưa có
    os.makedirs(f"downloads/{channel_name}", exist_ok=True)
    
    # Lưu file
    filename = f"downloads/{channel_name}/{video_id}.mp4"
    with open(filename, "wb") as f:
        f.write(video_bytes)
    
    print(f"Đã lưu: {filename}")

async def download_videos_in_batches():
    """Tải xuống video theo batch size 10"""
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token], 
            num_sessions=5, 
            sleep_after=3, 
            browser=os.getenv("TIKTOK_BROWSER", "chromium")
        )
        
        batch_size = 5
        total_videos = len(result)
        
        for i in range(0, total_videos, batch_size):
            batch = result[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            print(f"\nBatch {batch_num}: Tải {len(batch)} video ({i+1}-{min(i+batch_size, total_videos)}/{total_videos})")
            
            # Tạo tasks cho batch hiện tại
            tasks = []
            for channel_name, video_id in batch:
                task = download_video(api, channel_name, video_id)
                tasks.append(task)
            
            # Chạy batch hiện tại
            await asyncio.gather(*tasks)
            
            print(f"Hoàn thành batch {batch_num}")

if __name__ == "__main__":
    asyncio.run(download_videos_in_batches())
