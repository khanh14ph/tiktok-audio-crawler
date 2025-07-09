from TikTokApi import TikTokApi
import asyncio
import os
from glob import glob
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ms_token = "OosMHDsuRy3tqoM5W18QBtLYIZwVL9aqVduIkA5vyxu7F8eHh6d-L8M_zeqlwnOxL0muV-ScTZ_cNQux_Qjks_7tEu8f-he_pUE92eu9hZrlMXqfqwrt-rwrNqIRHZvX8upblOeZcFfLfj2NBKdVqD6ffg=="

# Đọc danh sách video IDs
lst = glob("resources/channel_video/*.txt")
result = []
for i in lst:
    name = i.split("/")[-1][:-4]
    video_ids = open(i, "r").read().splitlines()
    for video_id in video_ids:
        result.append((name, video_id))
result = result[0:10]

async def download_video_with_retry(api, channel_name, video_id, max_retries=3):
    """Tải xuống một video với retry mechanism"""
    for attempt in range(max_retries):
        try:
            video_url = f"https://www.tiktok.com/@{channel_name}/video/{video_id}"
            video = api.video(url=video_url)
            
            logger.info(f"Attempt {attempt + 1}: Đang tải {channel_name}/{video_id}")
            
            # Thêm timeout cho info()
            video_info = await asyncio.wait_for(video.info(), timeout=30)
            
            # Kiểm tra xem video có tồn tại không
            if not video_info or 'video' not in video_info:
                logger.error(f"Video không tồn tại hoặc bị private: {video_id}")
                return False
                
            # Thêm timeout cho bytes()
            video_bytes = await asyncio.wait_for(video.bytes(), timeout=60)
            
            # Tạo thư mục nếu chưa có
            os.makedirs(f"downloads/{channel_name}", exist_ok=True)
            
            # Lưu file
            filename = f"downloads/{channel_name}/{video_id}.mp4"
            with open(filename, "wb") as f:
                f.write(video_bytes)
            
            logger.info(f"✅ Đã lưu thành công: {filename}")
            return True
            
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Timeout khi tải {video_id} (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                await asyncio.sleep(5 * (attempt + 1))  # Exponential backoff
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi tải {video_id} (attempt {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                # Tăng thời gian chờ theo rate limiting guidelines
                await asyncio.sleep(10 * (attempt + 1))
            
    logger.error(f"❌ Thất bại hoàn toàn: {channel_name}/{video_id}")
    return False

async def download_videos_sequential():
    """Tải xuống video tuần tự để tránh rate limiting"""
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token], 
            num_sessions=2,  # Giảm số sessions
            sleep_after=5,   # Tăng thời gian chờ
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=True
        )
        
        success_count = 0
        fail_count = 0
        
        for i, (channel_name, video_id) in enumerate(result):
            logger.info(f"\n📹 Video {i+1}/{len(result)}: {channel_name}/{video_id}")
            
            # Kiểm tra file đã tồn tại chưa
            filename = f"downloads/{channel_name}/{video_id}.mp4"
            if os.path.exists(filename):
                logger.info(f"⏭️  File đã tồn tại, bỏ qua: {filename}")
                continue
            
            success = await download_video_with_retry(api, channel_name, video_id)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
            
            # Rate limiting: chờ giữa các requests
            if i < len(result) - 1:  # Không chờ ở video cuối
                wait_time = 3  # Chờ 3 giây giữa các video
                logger.info(f"⏳ Chờ {wait_time}s trước video tiếp theo...")
                await asyncio.sleep(wait_time)
        
        logger.info(f"\n📊 Kết quả: ✅ {success_count} thành công, ❌ {fail_count} thất bại")

async def download_videos_batch_improved():
    """Phiên bản batch cải tiến với rate limiting"""
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token], 
            num_sessions=3,
            sleep_after=5,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=True
        )
        
        batch_size = 3  # Giảm batch size
        total_videos = len(result)
        success_count = 0
        fail_count = 0
        
        for i in range(0, total_videos, batch_size):
            batch = result[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"\n🔄 Batch {batch_num}: Tải {len(batch)} video ({i+1}-{min(i+batch_size, total_videos)}/{total_videos})")
            
            # Tạo semaphore để giới hạn concurrent requests
            semaphore = asyncio.Semaphore(2)  # Chỉ 2 requests đồng thời
            
            async def download_with_semaphore(channel_name, video_id):
                async with semaphore:
                    return await download_video_with_retry(api, channel_name, video_id)
            
            # Chạy batch với semaphore
            tasks = [download_with_semaphore(channel_name, video_id) 
                    for channel_name, video_id in batch]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Đếm kết quả
            for result in results:
                if result is True:
                    success_count += 1
                else:
                    fail_count += 1
            
            logger.info(f"✅ Hoàn thành batch {batch_num}")
            
            # Chờ giữa các batch để tránh rate limiting
            if i + batch_size < total_videos:
                wait_time = 15  # Chờ 15 giây giữa các batch
                logger.info(f"⏳ Chờ {wait_time}s trước batch tiếp theo...")
                await asyncio.sleep(wait_time)
        
        logger.info(f"\n📊 Tổng kết: ✅ {success_count} thành công, ❌ {fail_count} thất bại")

if __name__ == "__main__":
    # Chọn một trong hai phương pháp:
    
    # Phương pháp 1: Tải tuần tự (an toàn hơn)
    asyncio.run(download_videos_sequential())
    
    # Phương pháp 2: Tải batch cải tiến (nhanh hơn nhưng riskier)
    # asyncio.run(download_videos_batch_improved())
