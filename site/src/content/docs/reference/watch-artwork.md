---
title: Watch artwork
description: Official Nothing X artwork, factory color codes, source URLs and downloadable files for CMF watches.
---

The Nothing X catalog contains artwork for Watch Pro, Watch Pro 2 and Watch 3 Pro.
This reference groups identical images and records the product and factory color codes
used to select them. It is shared reference material; inclusion does not imply that
firmware or installation tools support every listed watch.

[Browse the artwork gallery](/reference/artwork/index.html) ·
[Download the complete inventory (ZIP)](/reference/artwork/watch-artwork.zip) ·
[Download the machine-readable manifest (JSON)](/reference/artwork/inventory.json)

## Inventory

The saved Nothing X 3.10.0 catalog has **26 watch SKU entries**, **31 image URLs**
and **13 distinct image files**. Twelve images show watch appearances; the remaining
image is a shared grey catalog image (`case.png`). Multiple SKU codes point to the same artwork,
so the gallery shows each appearance once. The meaning of each SKU alias is not established.

| Watch | Product ID | Appearance | Color codes (hex) |
| --- | --- | --- | --- |
| Watch 3 Pro | `335BBD62` | dark grey | `01`, `19`, `20` |
| Watch 3 Pro | `335BBD62` | green | `25`, `26` |
| Watch 3 Pro | `335BBD62` | light grey | `21`, `22` |
| Watch 3 Pro | `335BBD62` | orange | `23`, `24` |
| Watch Pro | `82D5BB72` | dark grey | `01`, `03` |
| Watch Pro | `82D5BB72` | dark grey, ash-grey strap | `07`, `08` |
| Watch Pro | `82D5BB72` | orange | `05`, `06` |
| Watch Pro | `82D5BB72` | silver | `02`, `04` |
| Watch Pro 2 | `34F72851` | blue | `15`, `16` |
| Watch Pro 2 | `34F72851` | dark grey | `01`, `09`, `10` |
| Watch Pro 2 | `34F72851` | light grey | `11`, `12` |
| Watch Pro 2 | `34F72851` | orange | `13`, `14` |

## Image fields

`globalImageUrl` contains the model/color watch artwork used in the gallery.
Every watch SKU entry uses the same `steerImageUrl`, pointing to a grey `case.png`.
It is a shared catalog asset rather than another watch appearance. Its exact use
in the Nothing X interface has not been established. The gallery lists this asset
once below the watch images, and the manifest preserves the original field names.

## Manifest and verification

Each record contains the catalog model name, product ID (`modelId`), factory color
code (`colorId`), catalog SKU key (`fastPairId`) and named image views. Each view has
its source URL, local file path, byte length and SHA-256 digest. Files are stored once
by hash and referenced by the catalog records that use them. All 13 local files were
checked against their recorded size and SHA-256 before publication.

These images describe factory appearances. Replacement straps or bezels can make a
physical watch look different from its reported factory color. See
[model and color identification](/reference/watch-identity/) for the advertisement
layouts and the distinction between detected identity and a manual preview choice.

## Source and attribution

The catalog metadata comes from the Nothing X 3.10.0 `DeviceInfoTable` product catalog;
the source URLs are recorded for each image. Account records, device addresses,
serial numbers, pairing secrets and location data are not part of this inventory.

The artwork belongs to Nothing and its respective rights holders. The project license
does not grant rights to third-party artwork. The included manifest preserves source
attribution; see [legal and attribution](/about/legal/) for project licensing.
