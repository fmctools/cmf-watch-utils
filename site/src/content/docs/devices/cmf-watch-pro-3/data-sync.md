---
title: Data sync frames
description: Watch 3 Pro 1.0.1.77 history push, activity, event-log and watch-initiated BLE frames.
---

These layouts come from static analysis of stock **1.0.1.77** `app.bin`
(base `0x10000000`), checked against one physical capture. Treat each field as
static evidence until a second capture or a decoder confirms it. The Watch Pro 2
protocol is described in [BLE protocol](/devices/cmf-watch-pro-2/protocol/ble/);
do not assume these layouts match it.

## History push

`0xFFFF/0x8005` (REQ_UPDATE_DATA) is acknowledged with `0xFFFF/0x0005`
payload `01`. The watch then pushes every history type that has pending data, in this order:
`0x0053` heart rate, `0x00DA` resting HR, `0x00E0` workout HR, `0x0056` activity, `0x0160`
workout summary, `0x0055` SpO2, `0x0058` sleep, `0xFFFF/0xA05A` GPS, `0x009D` stress, `0x0155`
PAI, `0xB004` step deltas, `0xFFFF/0xA0C1` AI-coach courses, `0xFFFF/0xA095` event log. It ends
with `0xFFFF/0x0005` payload `02`. `0x9057` is not needed to start the push on the Watch 3 Pro.

## `0x00DA` resting heart rate (5 bytes)

`u32` watch time at send, `u8` resting HR (bpm).
The push is skipped when the value is 0. The timestamp is not a measurement time.

## `0x0056` activity (32 bytes per record, up to 6 per frame)

| off | type | field |
|---|---|---|
| 0 | u32 | time (unix s) |
| 4 | u32 | steps, day total |
| 8 | u32 | distance, m |
| 12 | u16 | active kcal |
| 14 | u16 | active time (unit unconfirmed) |
| 16 | u8 | stand count |
| 17 | u16 | total kcal incl. resting |
| 19 | 13 B | reserved, zero |

Calories are a `u16`. Reading bytes 12–15 as one `u32` mixes in the active time.

## `0xFFFF/0xA095` event log (12 bytes per record, up to 16 per frame, 200 stored)

`u8 0xA5`, `u8 event`, `u8 info1`, `u8 info2`, `u32 info3`, `u32 time`. Known codes:
`3/1/1` BLE disconnect (info3 = HCI reason, e.g. 0x13), `3/1/2` classic BT disconnect
(reason), `3/1/3` HFP/A2DP disconnect, `3/3/2` SPP connect failed, `4/1/0` boot, `5/5/n`
battery changed to n %, `0x3E` reboot reason, `0x3F/1` bind, `0x3F/2` unbind; classes 6–9
cover sleep/algorithm, activity storage, file transfer and sensor events. The log reveals
connection and charging times, so raw dumps count as personal data.

## `0xFFFF/0xA0C1` AI-coach course upload

`u8` flag (1), 32-byte coach-plan block,
`u8 n`, then `n` × 7-byte entries `{u32, u8, u16}`. With no coach plan the frame is 34 bytes
of `01` followed by zeros. It is pushed on every sync.

## `0x005C` battery

`u8` percent, `u8` charge state (0 not charging, 1 charging, 3 full).
The watch pushes it on charge-state changes. It answers a request only when c2 is `0x0002`.

## `0xFFFF/0x907F` resolution

Answered with `0xA07F` only when the request payload is a
single `00` byte. The empty payload used by `specs` gets no reply. The reply is six `u16`
values: `466, 466, 466, 466, 360, 360`.

## Watch-initiated requests

`0xFFFF/0xA06B` asks the phone for weather (payload: 32-byte
language code, e.g. `en`; answer `0x906B`). `0xFFFF/0xA06A` with payload `5A` asks for an
assisted-GPS location (answer `0x906A`: time, longitude, latitude).

## Firmware references (1.0.1.77 `app.bin`)

| item | address |
|---|---|
| BLE dispatcher | `0x100C2491` (system c2 table at `0x100C2568`, ability table at `0x100C2B2C`) |
| REQ_UPDATE_DATA (`0x8005`) | `0x100C4D38` |
| sync state machine `updata_timer_func` | `0x100C4994` |
| history read/pack `GetRecordData` | `0x100C3AF0` |
| `pkg_step_data` (`0x0056`) | `0x100C3834` |
| activity record writer | `0x100E2700`–`0x100E28F8` |
| event-log writer (`EventID … Info3`) | `0x100EE268` |
| storage type table `{cap, rec_len}` | `0x1021F94C` |
| `up_ai_coach_course_up` (`0xA0C1`) | `0x100CD380` |
| `watch_resolution_rsq` (`0x907F`) | `0x100C6B88` |
| battery `0x005C` handler / push | `0x100C6538` / `0x101D15E6` |
| `weather_data_req` (`0xA06B`) | `0x100C7E3A` |
