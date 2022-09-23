import httpx
from hoshino import Service
from hoshino.typing import MessageSegment

sv = Service('dailymoyu', enable_on_default=True, help_='''每日摸鱼
启用后会在每天早上发送一份摸鱼日历
[@bot 摸鱼日历] （测试用）手动发送一份早报''')

async def get_calendar() -> str:
    async with httpx.AsyncClient(http2=True) as client:
        #response = await client.get("https://api.j4u.ink/v1/store/other/proxy/remote/moyu.json")
        response = await client.get("https://api.vvhan.com/api/moyu?type=json")
    if response.is_error:
        raise ValueError(f"摸鱼日历获取失败，错误码：{response.status_code}")
    content = response.json()
    #return content["data"]["moyu_url"]
    return content["url"]

@sv.scheduled_job('cron', hour='10', minute='30', jitter=50)
async def automoyu():
    moyu_img = await get_calendar()
    message=MessageSegment.image(moyu_img)
    await sv.broadcast(message)

@sv.on_fullmatch('摸鱼日历', only_to_me=True)
async def handnews(bot, ev):
    moyu_img = await get_calendar()
    message=MessageSegment.image(moyu_img)
    await bot.send(ev,message)
