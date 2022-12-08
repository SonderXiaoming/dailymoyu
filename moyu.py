import io

import base64
import httpx

from hoshino import Service, aiorequests
from hoshino.typing import MessageSegment

sv_help = '''
每日摸鱼
启用后会在每天早上发送一份摸鱼日历
[@bot 摸鱼日历] （测试用）手动发送一份早报
'''.strip()

sv = Service(
    name='每日摸鱼',
    enable_on_default=True,
    visible=True,
    bundle="娱乐",
    help_=sv_help
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.6) ",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-cn"
}


async def get_calendar() -> str:
    async with httpx.AsyncClient(http2=True) as client:
        response = await client.get(
            url="https://api.j4u.ink/v1/store/other/proxy/remote/moyu.json",
            headers=headers
        )
    if response.is_error:
        raise ValueError(f"摸鱼日历获取失败，错误码：{response.status_code}")
    content = response.json()
    image_url = content["data"]["moyu_url"]
    try:
        image_bytes = await (await aiorequests.get(image_url, headers=headers)).content
        return f"base64://{base64.b64encode(io.BytesIO(image_bytes).getvalue()).decode()}"
    except Exception as e:
        sv.logger.critical(f"获取图片失败：{e}")
        return ""


@sv.scheduled_job('cron', hour='11', jitter=50)
async def automoyu():
    moyu_img = await get_calendar()
    if not moyu_img:
        sv.logger.warning("Error when getting moyu img")
        return
    message = MessageSegment.image(moyu_img)
    await sv.broadcast(message)


@sv.on_fullmatch('摸鱼日历', only_to_me=True)
async def handnews(bot, ev):
    moyu_img = await get_calendar()
    if not moyu_img:
        sv.logger.warning("Error when getting moyu img")
        return
    message = MessageSegment.image(moyu_img)
    await bot.send(ev, message)
