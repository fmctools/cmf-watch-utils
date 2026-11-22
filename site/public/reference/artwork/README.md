# CMF watch artwork

Official Nothing X product artwork for Watch Pro, Watch Pro 2 and Watch 3 Pro.

- `index.html` displays 12 factory appearances and one shared grey catalog image.
- `inventory.json` records 26 SKU entries with their model, product ID, factory color code, catalog key, image field, source URL, file size and SHA-256.
- `assets/` contains 13 unique original PNG files, referenced by hash-based filenames.

`globalImageUrl` identifies the watch artwork. All watch SKU entries share the same `steerImageUrl` image; its exact use in Nothing X is not established. Duplicate URLs and files remain associated with their original catalog entries in the manifest.

Source: Nothing X 3.10.0 product catalog (`DeviceInfoTable`) and the public image URLs recorded in the manifest. The inventory contains no account records, individual device addresses, serial numbers, pairing secrets or location data.

Artwork remains the property of Nothing and the respective rights holders. The project license does not relicense these images.
