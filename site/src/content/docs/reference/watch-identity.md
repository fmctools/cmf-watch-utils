---
title: Watch model and color identification
description: Nothing X advertisement layouts, product identifiers, factory color codes and browser integration.
---

The local FMC integration reads optional factory identity to choose preview artwork. Its Watch Frame controls are independent of installation compatibility. They do not change the advertised name, firmware board checks, package validation, watch settings or flash. Reconnecting restores automatic appearance selection. Selection is session-only.

## Evidence and format

The saved Nothing X 3.10.0 Android package contains `NothingWatchParser` in `com.nothing.link.bluetooth.sdk.scan.parser`. Its output is consumed by `NtBlePlugin` (`PRODUCT_ID`, `COLOR_ID`) and Flutter's `BluetoothHelper.getDeviceInfoByBluetoothDevice`, which resolves the pair against its device SKU catalog. This is distinct from the earbud parser.

After manufacturer-ID bytes have been removed, manufacturer 0x0CCB carries the complete payload; the older supported manufacturer forms prepend bytes 2C BE before parsing. Two layouts appear in the parser:

| Normalized bytes | Legacy layout | Compact layout |
|---|---|---|
| 0–5 | Embedded Bluetooth address (not retained by FMC) | Same |
| 6 onward | `JX-IWD` (6 bytes) | `JX` (2 bytes) |
| Product ID | Bytes 12–15 | Bytes 8–11 |
| Factory color | Byte 16 | Byte 12 |
| Pairing state | Byte 17 | Byte 13 |

The product ID is rendered as eight hexadecimal digits, preserving byte order. The color byte is two hexadecimal digits. The SKU key is the concatenation. The QR onboarding path also uses product `P` and color `C`; QR color is decimal and must be converted to the hexadecimal catalog representation.

| Product ID | Model |
|---|---|
| 82D5BB72 | Watch Pro |
| 34F72851 | Watch Pro 2 |
| 335BBD62 | Watch 3 Pro |

The saved public DeviceInfoTable catalog supplies the color-to-artwork mapping, including multiple SKU codes for the same appearance. Unknown IDs remain unknown. Factory colors cannot describe later strap or bezel replacements. WP1 identity is recognized, but that does not add WP1 installation or preview support.

## Browser integration

This describes the local FMC implementation under development, rather than a guarantee about the currently deployed FMC site.

`watchAdvertisements()` is optional and browser-dependent. FMC requests only the known manufacturer IDs, observes only the selected device, stops after one parsed identity or 1.2 seconds, and aborts/cleans up its listener. Missing permission, unsupported APIs or absent advertisements do not fail the connection. Advertising may stop when GATT connects, so this does not promise automatic color detection on every browser.

After normal authentication, FMC optionally sends `AT GETPID` through an available shell service. Both saved WP2 and WP3 firmware images contain `APP_PID`, `GETPID` and `GETPID:%s,OK`. The WP3 firmware research confirms the public product ID is read from APP_PID and used in its stock QR. The shell reply provides a product ID only: it does not establish a color. The response collector accepts fragmented replies and has a bounded timeout. Recovery mode never performs this extra query. A conflicting shell PID discards the advertisement color.

When neither route reports a model, the existing advertised-name fallback selects preview artwork. Missing color uses the default preview color without claiming that the default is the factory color. A manual preview choice is never treated as detected metadata.

## Verification

Parser tests use synthetic non-personal advertisements for WP1/WP2/WP3, both layouts, unknown companies, truncated data and unknown SKUs. Shell tests verify fragmented replies and that only AT GETPID is sent. Browser tests verify automatic appearance, manual override, unchanged reported identity and reset on reconnect. Existing BLE/recovery tests also pass.

This establishes the static Nothing X format and the local integration. It does not establish fresh on-device validation of automatic color detection on every watch/browser combination. A fresh Windows scan did not find the physical watch. No GATT connection was established during that check; hardware validation of the new integration remains pending.

Official artwork remains vendor-owned. The [artwork inventory](/reference/watch-artwork/) includes all 26 watch SKU rows and 31 image URLs (13 distinct image files after deduplication) from the saved catalog; it contains no account, pairing, serial or location data. Only WP2/WP3 preview assets are bundled in FMC.

Browser API reference: https://bluetooth.spec.whatwg.org/ and https://developer.mozilla.org/en-US/docs/Web/API/BluetoothDevice
