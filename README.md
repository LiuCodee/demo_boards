# My_boards ESP Board Manager Board Pack

[中文](README_CN.md)

This component provides ESP Board Manager YAML definitions for My_boards
development boards. Applications can install it from the
[ESP Component Registry](https://components.espressif.com) and select a board.

> Template note: Replace `My_boards` and update the following table with
> the supported boards before publishing.

## Supported Boards

Run `python scripts/update_supported_boards_table.py` to update the board and
chip columns. Maintainers fill in the device capability columns.

<!-- BEGIN SUPPORTED_BOARDS -->
| Board | Chip | Audio | SD Card | LCD | LCD Touch | Camera | Buttons | LED Strip | Knob |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `example_board` | ESP32-S3 | | | | | | | | |
| `example_board2` | ESP32-S31 | | | | | | | | |
| `example_board1` | ESP32 | | | | | | | | |
<!-- END SUPPORTED_BOARDS -->

## Use This Pack in an Application

Install the helper once in the active ESP-IDF Python environment:

```bash
python -m pip install --upgrade esp-bmgr-assist
```

Add the released component, then select a board:

```bash
idf.py add-dependency "LiuCodee/demo_boards"
idf.py bmgr -l
idf.py bmgr -b <board_name>
idf.py build
```

The board pack already declares `espressif/esp_board_manager`; applications do
not need to add it again unless they need a tighter version constraint.

## Vendor Maintenance Guide

For creating a repository from this template, migrating an existing BSP,
configuring CI, and publishing the component, see
[VENDOR_GUIDE.md](VENDOR_GUIDE.md).

## License

This component uses Apache-2.0. Preserve and comply with existing copyright
notices and licenses when migrating a BSP or adding third-party content.
