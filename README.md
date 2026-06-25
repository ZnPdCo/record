# OI 比赛档案

OI 赛后总结与复习工具，GitHub Pages 静态部署，支持 AES-256-GCM 加密。

## 文件说明

| 文件 | 用途 |
|------|------|
| `index.html` | 展示页 — 统计、年份筛选、可展开的比赛卡片 |
| `edit.html` | 编辑页 — 侧栏列表 + 完整表单（时间线、题目、标签、加密） |
| `data.json` | 数据文件 — 所有比赛的结构化 JSON |

## 快速开始

```bash
python -m http.server 8080
```

打开 `http://localhost:8080` 查看展示页，`http://localhost:8080/edit.html` 编辑数据。

> `file://` 协议下 `fetch()` 和 Web Crypto API 不可用，必须通过 HTTP 服务器访问。

## 加密机制

- 每场比赛可独立选择加密（勾选"加密此比赛"）
- 加密后仅比赛名称、日期、链接公开，其余字段（得分、题目、回顾等）用 AES-256-GCM 加密
- 密钥派生：PBKDF2-SHA256（60 万次迭代）+ 随机 16 字节盐
- 验证器存储在 `data.json` 中，密钥派生上下文与验证器不共用（防泄漏）
- 密码加密钥缓存在 `localStorage`，刷新不丢失，换浏览器需重新输入

## 数据格式

```json
{
  "verifier": "PBKDF2(password, salt) 的十六进制",
  "salt": "base64 随机盐",
  "contests": [
    {
      "date": "2025-06-25",
      "name": "比赛名称",
      "link": "https://...",
      "encrypted": "base64 密文",
      "iv": "base64 IV"
    }
  ]
}
```

未加密的比赛直接包含 `rank`、`totalScore`、`timeline`、`problems` 等字段。

## 标签预设

DP、图论、数据结构、贪心、数论、字符串、构造、思维、Ad-Hoc、模拟、博弈论

## 错误类型预设

看错题、算法不对、实现 bug、TLE、MLE、边界情况、long long

## 难度色标

| 难度 | 颜色 |
|------|------|
| 暂无评定 | `rgb(191, 191, 191)` |
| 入门 | `rgb(254, 76, 97)` |
| 普及− | `rgb(243, 156, 17)` |
| 普及/提高− | `rgb(255, 193, 22)` |
| 普及+/提高 | `rgb(82, 196, 26)` |
| 提高+/省选− | `rgb(52, 152, 219)` |
| 省选/NOI− | `rgb(157, 61, 207)` |
| NOI/NOI+/CTSC | `rgb(14, 29, 105)` |
