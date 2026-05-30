import requests
import time
import os

# ========== 配置区 ==========
# 优先从环境变量获取（用于 GitHub Actions），如果不存在则使用默认值（本地测试用）
SEND_KEY = os.environ.get('SEND_KEY', '')   # 修正：第一个参数应该是 'SEND_KEY'
BARK_KEY = os.environ.get('BARK_KEY', 'fRtmHT3fprXvXzfuZJDLYB')

# ========== 获取热搜（返回标题列表）==========
def get_hot_titles():
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    hot_list = data['data'][:10]
    titles = [item['Title'] for item in hot_list]
    return titles

# ========== 推送函数 ==========
def send_to_wechat(content):
    if not SEND_KEY:
        return
    url = f"https://sctapi.ftqq.com/{SEND_KEY}.send"
    try:
        requests.post(url, data={"title": "热点新增", "desp": content}, timeout=10)
        print("✅ 微信推送成功")
    except Exception as e:
        print(f"❌ 微信推送异常: {e}")

def send_to_bark(content):
    if not BARK_KEY:
        return
    title = "热点新增"
    full_url = f"https://api.day.app/{BARK_KEY}/{title}/{content[:200]}"
    try:
        requests.get(full_url, timeout=10)
        print("✅ Bark推送成功")
    except Exception as e:
        print(f"❌ Bark推送异常: {e}")

# ========== 核心：对比新旧列表，推送新增 ==========
def check_and_push_new(new_titles, old_titles):
    new_ones = [t for t in new_titles if t not in old_titles]
    if not new_ones:
        print("没有新热点，跳过推送")
        return old_titles
    msg = "🔥 发现新热点：\n" + "\n".join(f"• {t}" for t in new_ones)
    print(msg)
    send_to_wechat(msg)
    send_to_bark(msg)
    return new_titles

# ========== 主程序 ==========
if __name__ == "__main__":
    print("首次获取热搜列表...")
    old_list = get_hot_titles()
    print("当前热搜：", old_list)
    print("程序将监控新热点，按 Ctrl+C 退出。")
    # 可选：首次运行是否推送？如果需要，取消下面注释
    # send_to_bark("监控已启动，当前热搜：" + " ".join(old_list[:5]))
    while True:
        time.sleep(10)  # 测试用10秒，正式改为300秒
        print("\n检查新热点...")
        new_list = get_hot_titles()
        old_list = check_and_push_new(new_list, old_list)
