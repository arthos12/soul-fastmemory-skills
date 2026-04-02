# Polymarket 5分钟Up/Down市场查询

## 市场时间
- **只在美国白天生成**: ET 8am-8pm (北京时间 20:00-次日08:00)
- 美国凌晨(ET 0am-8am)没有5分钟市场

## 查询方式

### 1. 通过Event链接
格式: `https://polymarket.com/event/btc-updown-5m-{timestamp}`
- timestamp = Unix时间戳(UTC)
- 例如: `https://polymarket.com/event/btc-updown-5m-1774063500`

### 2. 通过Gamma API
- **不能用** `/markets` (不返回短期市场)
- **不能用** `/events/{id}` (需要特定ID)
- 需用时间戳生成公式获取

### 3. Python查询脚本
```python
import requests
from datetime import datetime, timedelta

def get_current_5m_timestamp():
    """获取当前5分钟窗口的时间戳(UTC)"""
    now_et = datetime.utcnow() + timedelta(hours=4)  # ET = UTC+4
    # 向下取整到5分钟
    minute = (now_et.minute // 5) * 5
    window = now_et.replace(minute=minute, second=0, microsecond=0)
    return int(window.timestamp())

def check_5m_markets():
    """检查当前可用的5分钟市场"""
    now_et = datetime.utcnow() + timedelta(hours=4)
    
    # 只在美国白天(8am-8pm ET)才有市场
    if now_et.hour < 8 or now_et.hour >= 20:
        return {"status": "closed", "reason": "美国凌晨，无5分钟市场"}
    
    # 生成接下来几小时的时间戳
    ts_list = []
    for i in range(1, 25):
        minute = ((now_et.minute // 5) + i) * 5
