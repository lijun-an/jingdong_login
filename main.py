from pyppeteer import launch
import asyncio
from urllib import request
import cv2
import random


async def get_distance():
    img = cv2.imread('image.png', 0)  # 灰度读取
    template = cv2.imread('template.png', 0)  # 灰度读取
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)  # 使用cv2的平方差匹配法来取值，cv2.TM_CCOEFF_NORMED（相关系数匹配法）
    value = cv2.minMaxLoc(res)[2][0]  # minMaxLoc()在数组中找到全局最小和最大值
    distance = value * 278 / 360
    return distance


# 声明一个异步函数
async def main():
    # --window-size是外部窗口界面大小
    browser = await launch(headless=False, args=['--window-size=1366,768'])
    page = await browser.newPage()  # 创建一个新的空白窗口
    await page.setViewport({'width': 1366, 'height': 768})  # 设置内部窗口界面大小
    await page.goto('https://passport.jd.com/new/login.aspx')  # 访问京东登录页面
    await page.click('#content > div.login-wrap > div.w > div > div.login-tab.login-tab-r')  # 点击账户登录
    await page.waitFor(1000)  # 延时1000ms
    # 模拟输入账号密码
    await page.type('#loginname', '15616435916')
    await page.type('#nloginpwd', 'ljun123456')
    await page.waitFor(1000)  # 延时1000ms
    # 点击登录
    await page.click('#formlogin > div.item.item-fore5 > div')
    await page.waitFor(1000)  # 延时1000ms
    '''
    先获取图片，使用opencv模块的归一化平方差去识别对应的缺口，返回对应的位置
    '''
    img_src = await page.Jeval(
        '#JDJRV-wrap-loginsubmit > div > div > div > div.JDJRV-img-panel.JDJRV-click-bind-suspend > div.JDJRV-img-wrap > div.JDJRV-bigimg > img',
        'node=>node.src')  # 获取定位缺口图链接,Jeval()别名是querySelectorEval()对匹配的袁术执行js函数，第一个参数是定位选择器字符串，第二个参数是执行js函数的代码
    request.urlretrieve(img_src, 'image.png')  # 缺口图
    template_src = await page.Jeval(
        '#JDJRV-wrap-loginsubmit > div > div > div > div.JDJRV-img-panel.JDJRV-click-bind-suspend > div.JDJRV-img-wrap > div.JDJRV-smallimg > img',
        'node=>node.src')  # 滑块图
    request.urlretrieve(template_src, 'template.png')
    await page.waitFor(1000)
    distance = await get_distance()  # 对比图片的边缘距离差
    el = await page.J(
        '#JDJRV-wrap-loginsubmit > div > div > div > div.JDJRV-slide-bg > div.JDJRV-slide-inner.JDJRV-slide-btn')  # J()别名querySelector(),获取匹配元素的selector
    box = await el.boundingBox()
    await page.hover(
        '#JDJRV-wrap-loginsubmit > div > div > div > div.JDJRV-slide-bg > div.JDJRV-slide-inner.JDJRV-slide-btn')  # 模拟鼠标移动到选择元素上

    await page.mouse.down()  # 操作鼠标按下
    await page.mouse.move(box['x'] + distance + random.uniform(30, 33), box['y'], {'steps': 30})
    await page.waitFor(random.randint(300, 700))
    await page.mouse.move(box['x'] + distance + 27, box['y'], {'steps': 30})
    await page.mouse.up()
    await page.waitFor(500)


asyncio.get_event_loop().run_until_complete(main())  # 获取一个事件循环，直到main()运行结束
