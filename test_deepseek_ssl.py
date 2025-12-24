"""
DeepSeek API SSL 连接诊断工具
"""

import requests
import ssl
import socket
from urllib.parse import urlparse

def test_deepseek_connection():
    """测试 DeepSeek API 连接"""

    print("=" * 60)
    print("DeepSeek API SSL 连接诊断")
    print("=" * 60)

    api_url = "https://api.deepseek.com"

    # 测试 1: DNS 解析
    print("\n[测试 1] DNS 解析...")
    try:
        parsed = urlparse(api_url)
        hostname = parsed.hostname
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS 解析成功: {hostname} -> {ip}")
    except Exception as e:
        print(f"❌ DNS 解析失败: {e}")
        return

    # 测试 2: TCP 连接
    print("\n[测试 2] TCP 连接 (端口 443)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, 443))
        sock.close()
        if result == 0:
            print(f"✅ TCP 连接成功")
        else:
            print(f"❌ TCP 连接失败: 错误代码 {result}")
            return
    except Exception as e:
        print(f"❌ TCP 连接失败: {e}")
        return

    # 测试 3: SSL 握手 (禁用证书验证)
    print("\n[测试 3] SSL 握手 (禁用证书验证)...")
    try:
        response = requests.get(api_url, verify=False, timeout=10)
        print(f"✅ SSL 握手成功 (禁用验证): HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ SSL 握手失败 (禁用验证): {e}")
        print("   原因: 即使禁用证书验证也失败,说明 SSL 层面有更底层的问题")

    # 测试 4: SSL 握手 (启用证书验证)
    print("\n[测试 4] SSL 握手 (启用证书验证)...")
    try:
        response = requests.get(api_url, verify=True, timeout=10)
        print(f"✅ SSL 握手成功 (启用验证): HTTP {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL 证书验证失败: {e}")
        print("   原因: 证书验证问题,可能是中间人干扰或证书过期")
    except Exception as e:
        print(f"❌ SSL 握手失败: {e}")

    # 测试 5: 实际 API 调用
    print("\n[测试 5] 实际 API 调用 (需要有效的 API Key)...")
    print("请手动输入您的 DeepSeek API Key (按 Enter 跳过):")
    api_key = input("API Key: ").strip()

    if api_key:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 10
            }
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                print(f"✅ API 调用成功: {response.status_code}")
            elif response.status_code == 401:
                print(f"⚠️ API Key 无效: {response.status_code}")
            else:
                print(f"❌ API 调用失败: HTTP {response.status_code}")
                print(f"   响应: {response.text[:200]}")
        except requests.exceptions.SSLError as e:
            print(f"❌ SSL 错误: {e}")
            print("   这就是问题所在!")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    else:
        print("跳过 API 调用测试")

    # 测试 6: SSL 上下文信息
    print("\n[测试 6] Python SSL 环境信息...")
    try:
        print(f"OpenSSL 版本: {ssl.OPENSSL_VERSION}")
        print(f"支持的 TLS 版本: {ssl.TLS_CLIENT_SUPPORTED_VERSIONS if hasattr(ssl, 'TLS_CLIENT_SUPPORTED_VERSIONS') else 'N/A'}")
    except Exception as e:
        print(f"无法获取 SSL 信息: {e}")

    print("\n" + "=" * 60)
    print("诊断完成!")
    print("=" * 60)

    # 建议
    print("\n💡 问题排查建议:")
    print("1. 如果测试 3 失败 -> 网络环境有问题,可能被防火墙/代理拦截")
    print("2. 如果测试 3 成功,测试 4 失败 -> 证书验证问题,可能有中间人")
    print("3. 如果测试 4 成功,测试 5 失败 -> DeepSeek API 层面的问题")
    print("4. 如果所有测试都失败 -> 网络完全无法访问 DeepSeek")
    print("\n解决方案:")
    print("- 暂时使用'跳过联系方式获取'功能")
    print("- 检查防病毒软件是否拦截了 HTTPS 连接")
    print("- 尝试关闭 VPN/代理")
    print("- 尝试使用手机热点测试")

if __name__ == "__main__":
    # 禁用 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    test_deepseek_connection()
