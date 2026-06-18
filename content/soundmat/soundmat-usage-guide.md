---
title: "SoundMat 使用说明"
docLang: zh
translationKey: soundmat-usage-guide
alternates:
  zh: /soundmat/soundmat-usage-guide/
  en: /soundmat/en/soundmat-usage-guide/
aliases:
  - /soundmat/soundmat-usage-guide/
---

## 检查单

- [ ] 音箱已开，电量 ≥ 40%（建议 ≥ 60%）
- [ ] 音频线接音箱，POWER 线接 PD 20V 电源
- [ ] 等 1～2 分钟，四向红色定位 LED 已呼吸
- [ ] 连 `SoundMat` 热点，浏览器能打开控制台（可选）

## 1  接线

两根线：一根接音箱，一根接电源。电源线上贴有 **POWER** 标签。音箱通过 type-c 转接头转到 3.5mm 接口接到音箱上。

## 2  音箱

先打开音箱，会中文播报电量。需 **≥ 40%**（建议 **≥ 60%**），否则音量很小；不够就用 Micro-USB 充电。

音箱有两个 Micro-USB：**充电口**和**音频口**，不要插错。充上电后红色指示灯亮起。

建议先开音箱、确认电量，再接装置电源。

## 3  开机

POWER 线接支持 **PD 20V** 的 Type-C 充电器或充电宝，装置自动启动，约 **1～2 分钟**。

LED 先常亮，再变为呼吸；出现四向红色定位灯时，音乐引擎就绪，装置可用。

## 4  控制台

装置会开 **`SoundMat`** 热点（密码 `soundmat2026`）。手机/电脑连上后，浏览器打开：

- 手机：`http://10.42.0.1:8000`
- 电脑：`http://soundmat-pi.local:8000`（或 `http://10.42.0.1:8000`）

目前控制台不支持调整模式。

## 5  远程开发

手机开热点：

| SSID | 密码 |
| --- | --- |
| `soundmat` | `soundmat2026` |

手机连 WiFi 或开数据，插拔 POWER 重启，等约一分钟。装置连上该热点后即可上网，可进行全球远程开发。
