# -*- coding: utf-8 -*-

import os
import re
import time
import requests
import datetime
from bs4 import BeautifulSoup


headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit'
                      '/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safar'
                      'i/537.36',
    }


def numtozh(num):
    num_dict = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七',
                8: '八', 9: '九', 0: '零'}
    num = int(num)
    if 100 <= num < 1000:
        b_num = num // 100
        s_num = (num-b_num*100) // 10
        g_num = (num-b_num*100) % 10
        if g_num == 0 and s_num == 0:
            num = '%s百' % (num_dict[b_num])
        elif s_num == 0:
            num = '%s百%s%s' % (num_dict[b_num], num_dict.get(s_num, ''), num_dict.get(g_num, ''))
        elif g_num == 0:
            num = '%s百%s十' % (num_dict[b_num], num_dict.get(s_num, ''))
        else:
            num = '%s百%s十%s' % (num_dict[b_num], num_dict.get(s_num, ''), num_dict.get(g_num, ''))
    elif 10 <= num < 100:
        s_num = num // 10
        g_num = (num-s_num*10) % 10
        if g_num == 0:
            g_num = ''
        num = '%s十%s' % (num_dict[s_num], num_dict.get(g_num, ''))
    elif 0 <= num < 10:
        g_num = num
        num = '%s' % (num_dict[g_num])
    elif -10 < num < 0:
        g_num = -num
        num = '零下%s' % (num_dict[g_num])
    elif -100 < num <= -10:
        num = -num
        s_num = num // 10
        g_num = (num-s_num*10) % 10
        if g_num == 0:
            g_num = ''
        num = '零下%s十%s' % (num_dict[s_num], num_dict.get(g_num, ''))
    return num


def get_seconds(h='23', m='41', s='55'):
    """获取当前时间与程序启动时间间隔秒数"""

    # 设置程序启动的时分秒
    time_pre = '%s:%s:%s' % (h, m, s)
    # 获取当前时间
    time1 = datetime.datetime.now()
    # 获取程序今天启动的时间的字符串格式
    time2 = time1.date().strftime('%Y-%m-%d') + ' ' + time_pre
    # 转换为datetime格式
    time2 = datetime.datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
    # 判断当前时间是否晚于程序今天启动时间，若晚于则程序启动时间增加一天
    if time1 > time2:
        time2 = time2 + datetime.timedelta(days=1)

    return time.mktime(time2.timetuple()) - time.mktime(time1.timetuple())


def get_weather():
    # 下载墨迹天气主页源码
    res = requests.get('http://tianqi.moji.com/', headers=headers)
    # 用BeautifulSoup获取所需信息
    soup = BeautifulSoup(res.text, "html.parser")
    temp = soup.find('div', attrs={'class': 'wea_weather clearfix'}).em.getText()
    temp = numtozh(int(temp))
    weather = soup.find('div', attrs={'class': 'wea_weather clearfix'}).b.getText()
    sd = soup.find('div', attrs={'class': 'wea_about clearfix'}).span.getText()
    sd_num = re.search(r'\d+', sd).group()
    sd_num_zh = numtozh(int(sd_num))
    sd = sd.replace(sd_num, sd_num_zh)
    wind = soup.find('div', attrs={'class': 'wea_about clearfix'}).em.getText()
    aqi = soup.find('div', attrs={'class': 'wea_alert clearfix'}).em.getText()
    aqi_num = re.search(r'\d+', aqi).group()
    aqi_num_zh = numtozh(int(aqi_num))
    aqi = aqi.replace(aqi_num, aqi_num_zh).replace(' ', ',空气质量')
    info = soup.find('div', attrs={'class': 'wea_tips clearfix'}).em.getText()
    sd = sd.replace(' ', '百分之').replace('%', '')
    aqi = '空气质量指数' + aqi
    info = info.replace('，', ',')
    # 获取今天的日期
    # today = datetime.datetime.now().date().strftime('%Y年%m月%d日')
    today = datetime.datetime.now().strftime('%Y.%m.%d')
    # 将获取的信息拼接成一句话
    end = '谢谢，再见，哈哈哈哈!'
    text = '大家好！我是任强。今天是%s,天气%s,温度%s摄氏度,%s,%s,%s,%s,%s' % \
           (today, weather, temp, sd, wind, aqi, info, end)
    return text


def text2voice(text):
    url = 'http://tts.baidu.com/text2audio?idx=1&tex={0}&cuid=baidu_speech_' \
          'demo&cod=2&lan=zh&ctp=1&pdt=1&spd=4&per=4&vol=5&pit=5'.format(text)
    # 下载转换后的mp3格式语音
    res = requests.get(url, headers=headers)
    # 将MP3存入本地
    with open(datetime.datetime.now().strftime('%Y.%m.%d')+'天气.mp3', 'wb') as f:
        f.write(res.content)


def main():
    while True:
        s = get_seconds()
		
        print(s)
        time.sleep(s)
        # 获取需要转换语音的文字
        text = get_weather()
        print(text)
        # 将文字转换为语音并存入程序所在文件夹
        text2voice(text)
        # 获取音乐文件绝对地址
        mp3path2 = os.path.join(os.path.dirname(__file__), 'clockrq.mp3')
        # 先播放一首音乐做闹钟
        # os.system('mplayer %s' % mp3path2)
        os.system('%s' % mp3path2)
        # 播报语音天气
        mp3path1 = os.path.join(os.path.dirname(__file__), datetime.datetime.now().strftime('%Y.%m.%d')+'天气.mp3')
        # os.system('mplayer %s' % mp3path1)
        os.system('%s' % mp3path1)
        # os.remove(mp3path1)

if __name__ == '__main__':
    main()
