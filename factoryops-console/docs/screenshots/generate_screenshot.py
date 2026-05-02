#!/usr/bin/env python3
"""Generate a realistic SVG screenshot of the FactoryOps Console TUI."""

import datetime


def generate_main_screenshot():
    term_w = 960
    term_h = 600
    title_bar_h = 32
    pad = 12
    font = "monospace"
    fs = 13
    line_h = 18

    bg = "#0c0c0c"
    border_c = "#00aaaa"
    green_c = "#00ff00"
    yellow_c = "#ffff00"
    red_c = "#ff5555"
    blue_c = "#5555ff"
    cyan_c = "#00cccc"
    gray_c = "#888888"
    dark_gray_c = "#555555"
    white_c = "#cccccc"
    dim_c = "#444444"

    now = datetime.datetime.now().strftime("%H:%M:%S")

    cpu_vals = [
        32,
        35,
        38,
        42,
        45,
        43,
        40,
        38,
        36,
        34,
        37,
        41,
        48,
        52,
        55,
        58,
        62,
        65,
        68,
        72,
        70,
        67,
        63,
        59,
        55,
        51,
        48,
        45,
        42,
        39,
        36,
        34,
        37,
        40,
        44,
        48,
        53,
        57,
        60,
        63,
        66,
        64,
        61,
        58,
        54,
        50,
        47,
        43,
        40,
        38,
        41,
        45,
        50,
        55,
        59,
        63,
        67,
        70,
        68,
        65,
    ]

    mem_vals = [
        48,
        49,
        50,
        51,
        52,
        52,
        53,
        53,
        54,
        55,
        56,
        56,
        57,
        57,
        58,
        58,
        59,
        59,
        60,
        60,
        61,
        61,
        62,
        62,
        63,
        63,
        63,
        64,
        64,
        64,
        65,
        65,
        65,
        66,
        66,
        66,
        67,
        67,
        67,
        68,
        68,
        68,
        69,
        69,
        69,
        70,
        70,
        70,
        70,
        71,
        71,
        71,
        71,
        72,
        72,
        72,
        72,
        73,
        73,
        73,
    ]

    devices = [
        ("Line-1-Printer", "192.168.10.15", "Online", green_c),
        ("Pack-Station-A", "192.168.10.22", "Online", green_c),
        ("STAC6-Drive-01", "192.168.10.30", "Latency 245ms", yellow_c),
        ("Line-2-Printer", "192.168.10.16", "Online", green_c),
        ("Quality-Scanner", "192.168.10.45", "OFFLINE", red_c),
    ]

    logs = [
        (f"[{now}]", "[INFO]", " FactoryOps Console initialized", blue_c, white_c),
        (f"[{now}]", "[INFO]", " Monitoring 5 manufacturing devices", blue_c, white_c),
        (f"[{now}]", "[INFO]", " System heartbeat OK", blue_c, white_c),
        (f"[{now}]", "[INFO]", " ERP connection stable", blue_c, white_c),
        (
            f"[{now}]",
            "[WARN]",
            " High memory usage detected on Line-1-Printer",
            yellow_c,
            yellow_c,
        ),
        (f"[{now}]", "[INFO]", " System heartbeat OK", blue_c, white_c),
        (f"[{now}]", "[ERROR]", " Connection timeout to Quality-Scanner", red_c, red_c),
        (f"[{now}]", "[INFO]", " Backup completed successfully", blue_c, white_c),
        (
            f"[{now}]",
            "[WARN]",
            " Packet loss detected on Line-2-Printer",
            yellow_c,
            yellow_c,
        ),
        (
            f"[{now}]",
            "[INFO]",
            " Line-1-Printer (192.168.10.15) -> Online",
            blue_c,
            white_c,
        ),
        (
            f"[{now}]",
            "[INFO]",
            " Pack-Station-A (192.168.10.22) -> Online",
            blue_c,
            white_c,
        ),
        (
            f"[{now}]",
            "[WARN]",
            " STAC6-Drive-01 (192.168.10.30) -> High Latency (245ms)",
            yellow_c,
            yellow_c,
        ),
        (
            f"[{now}]",
            "[ERROR]",
            " Quality-Scanner (192.168.10.45) -> OFFLINE",
            red_c,
            red_c,
        ),
        (f"[{now}]", "[INFO]", " System heartbeat OK", blue_c, white_c),
        (
            f"[{now}]",
            "[WARN]",
            " Disk usage 85% on production server",
            yellow_c,
            yellow_c,
        ),
        (f"[{now}]", "[INFO]", " Backup completed successfully", blue_c, white_c),
        (f"[{now}]", "[INFO]", " System heartbeat OK", blue_c, white_c),
        (f"[{now}]", "[INFO]", " ERP connection stable", blue_c, white_c),
        (
            f"[{now}]",
            "[WARN]",
            " Packet loss detected on Line-2-Printer",
            yellow_c,
            yellow_c,
        ),
        (f"[{now}]", "[INFO]", " System heartbeat OK", blue_c, white_c),
        (f"[{now}]", "[INFO]", " Manual device refresh triggered", blue_c, white_c),
    ]

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{term_w}" height="{term_h}" viewBox="0 0 {term_w} {term_h}">
  <defs>
    <linearGradient id="titleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#0d0d1a;stop-opacity:1"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="1" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    text {{ font-family: {font}, 'Courier New', 'Liberation Mono', monospace; font-size: {fs}px; white-space: pre; }}
    .title-text {{ font-size: 13px; fill: {white_c}; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
  </style>
  <!-- Terminal window background -->
  <rect width="{term_w}" height="{term_h}" rx="8" fill="{bg}"/>
  <!-- Title bar -->
  <rect width="{term_w}" height="{title_bar_h}" rx="8" fill="url(#titleGrad)"/>
  <rect y="16" width="{term_w}" height="16" fill="url(#titleGrad)"/>
  <!-- Traffic lights -->
  <circle cx="20" cy="16" r="6" class="dot-red"/>
  <circle cx="40" cy="16" r="6" class="dot-yellow"/>
  <circle cx="60" cy="16" r="6" class="dot-green"/>
  <text x="{term_w // 2}" y="20" text-anchor="middle" class="title-text" fill="{gray_c}">factoryops-console -- 5 devices monitored</text>
''')

    content_y = title_bar_h + pad
    content_x = pad
    content_w = term_w - (pad * 2)
    content_h = term_h - title_bar_h - (pad * 2)

    left_w = int(content_w * 0.58)
    right_w = content_w - left_w - 4
    left_x = content_x
    right_x = content_x + left_w + 4

    infra_h = int(content_h * 0.38)
    device_h = content_h - infra_h - 4
    infra_y = content_y
    device_y = content_y + infra_h + 4
    log_y = content_y

    # Infrastructure Pulse border
    svg_parts.append(f'''  <!-- Infrastructure Pulse Panel -->
  <rect x="{left_x}" y="{infra_y}" width="{left_w}" height="{infra_h}" rx="2" fill="none" stroke="{border_c}" stroke-width="1"/>
  <rect x="{left_x + 1}" y="{infra_y - 1}" width="196" height="16" fill="{bg}"/>
  <text x="{left_x + 4}" y="{infra_y + 11}" fill="{cyan_c}" font-weight="bold"> Infrastructure Pulse </text>
''')

    half_w = (left_w - 12) // 2
    spark_y = infra_y + 22

    # CPU Sparkline
    cpu_bar_h_max = infra_h - 48
    svg_parts.append(f'''  <rect x="{left_x + 6}" y="{spark_y}" width="{half_w}" height="{infra_h - 28}" rx="1" fill="none" stroke="{dark_gray_c}" stroke-width="1"/>
  <rect x="{left_x + 7}" y="{spark_y - 1}" width="92" height="14" fill="{bg}"/>
  <text x="{left_x + 10}" y="{spark_y + 10}" fill="{gray_c}"> CPU 52% </text>
''')

    bar_count = min(len(cpu_vals), half_w // 4)
    bar_w_each = max(2, (half_w - 12) // bar_count)
    spark_base_y = spark_y + infra_h - 34
    for i in range(bar_count):
        val = cpu_vals[i]
        h = int((val / 100) * cpu_bar_h_max)
        y_pos = spark_base_y - h
        if val > 80:
            bc = red_c
        elif val > 60:
            bc = yellow_c
        else:
            bc = green_c
        x_pos = left_x + 10 + (i * bar_w_each)
        svg_parts.append(
            f'  <rect x="{x_pos}" y="{y_pos}" width="{bar_w_each - 1}" height="{h}" fill="{bc}" opacity="0.8"/>'
        )

    # Memory Sparkline
    mem_x = left_x + 6 + half_w + 6
    svg_parts.append(f'''  <rect x="{mem_x}" y="{spark_y}" width="{half_w}" height="{infra_h - 28}" rx="1" fill="none" stroke="{dark_gray_c}" stroke-width="1"/>
  <rect x="{mem_x + 1}" y="{spark_y - 1}" width="120" height="14" fill="{bg}"/>
  <text x="{mem_x + 4}" y="{spark_y + 10}" fill="{gray_c}"> Memory 73% </text>
''')

    for i in range(bar_count):
        val = mem_vals[i]
        h = int((val / 100) * cpu_bar_h_max)
        y_pos = spark_base_y - h
        if val > 85:
            bc = red_c
        elif val > 70:
            bc = yellow_c
        else:
            bc = blue_c
        x_pos = mem_x + 4 + (i * bar_w_each)
        svg_parts.append(
            f'  <rect x="{x_pos}" y="{y_pos}" width="{bar_w_each - 1}" height="{h}" fill="{bc}" opacity="0.8"/>'
        )

    # Device Grid
    svg_parts.append(f'''  <!-- Factory Floor - Device Grid -->
  <rect x="{left_x}" y="{device_y}" width="{left_w}" height="{device_h}" rx="2" fill="none" stroke="{border_c}" stroke-width="1"/>
  <rect x="{left_x + 1}" y="{device_y - 1}" width="240" height="16" fill="{bg}"/>
  <text x="{left_x + 4}" y="{device_y + 11}" fill="{cyan_c}" font-weight="bold" text-anchor="start"> Factory Floor - Device Grid </text>
''')

    table_y = device_y + 20
    headers = ["Device", "IP Address", "Status", "Last Check"]
    col_x = [left_x + 8, left_x + 160, left_x + 310, left_x + 470]

    svg_parts.append(
        f'  <text x="{col_x[0]}" y="{table_y}" fill="{white_c}" font-weight="bold">{headers[0]}</text>'
    )
    svg_parts.append(
        f'  <text x="{col_x[1]}" y="{table_y}" fill="{white_c}" font-weight="bold">{headers[1]}</text>'
    )
    svg_parts.append(
        f'  <text x="{col_x[2]}" y="{table_y}" fill="{white_c}" font-weight="bold">{headers[2]}</text>'
    )
    svg_parts.append(
        f'  <text x="{col_x[3]}" y="{table_y}" fill="{white_c}" font-weight="bold">{headers[3]}</text>'
    )

    svg_parts.append(
        f'  <line x1="{left_x + 4}" y1="{table_y + 6}" x2="{left_x + left_w - 4}" y2="{table_y + 6}" stroke="{dim_c}"/>'
    )

    for idx, (name, ip, status, color) in enumerate(devices):
        row_y = table_y + 20 + (idx * line_h)
        elapsed = ["1.2s", "0.8s", "3.5s", "0.9s", "12.4s"][idx]
        status_sym = (
            "\u25cf"
            if color == green_c
            else ("\u25d0" if color == yellow_c else "\u25cb")
        )
        svg_parts.append(
            f'  <text x="{col_x[0]}" y="{row_y}" fill="{white_c}">{name}</text>'
        )
        svg_parts.append(
            f'  <text x="{col_x[1]}" y="{row_y}" fill="{gray_c}">{ip}</text>'
        )
        svg_parts.append(
            f'  <text x="{col_x[2]}" y="{row_y}" fill="{color}">{status_sym} {status}</text>'
        )
        svg_parts.append(
            f'  <text x="{col_x[3]}" y="{row_y}" fill="{dark_gray_c}">{elapsed}</text>'
        )

    # System Logs Panel
    svg_parts.append(f'''  <!-- System Logs Panel -->
  <rect x="{right_x}" y="{log_y}" width="{right_w}" height="{content_h}" rx="2" fill="none" stroke="{border_c}" stroke-width="1"/>
  <rect x="{right_x + 1}" y="{log_y - 1}" width="260" height="16" fill="{bg}"/>
  <text x="{right_x + right_w // 2}" y="{log_y + 11}" fill="{cyan_c}" font-weight="bold" text-anchor="middle"> System Logs [{len(logs)}] [Auto] </text>
''')

    log_text_x = right_x + 6
    log_start_y = log_y + 22
    visible_logs = min(len(logs), int((content_h - 30) / line_h))

    for i in range(visible_logs):
        ly = log_start_y + (i * line_h)
        ts, level, msg, level_c, msg_c = logs[i]
        svg_parts.append(
            f'  <text x="{log_text_x}" y="{ly}" fill="{dark_gray_c}">{ts}</text>'
        )
        level_x = log_text_x + 80
        svg_parts.append(
            f'  <text x="{level_x}" y="{ly}" fill="{level_c}" font-weight="bold">{level}</text>'
        )
        msg_x = level_x + 60
        msg_text = msg[:42]
        svg_parts.append(
            f'  <text x="{msg_x}" y="{ly}" fill="{msg_c}">{msg_text}</text>'
        )

    svg_parts.append("</svg>")

    return "\n".join(svg_parts)


def generate_device_detail_screenshot():
    term_w = 640
    term_h = 420
    title_bar_h = 32
    pad = 10
    font = "monospace"
    fs = 12
    line_h = 17

    bg = "#0c0c0c"
    border_c = "#00aaaa"
    green_c = "#00ff00"
    yellow_c = "#ffff00"
    red_c = "#ff5555"
    blue_c = "#5555ff"
    cyan_c = "#00cccc"
    gray_c = "#888888"
    dark_gray_c = "#555555"
    white_c = "#cccccc"

    now = datetime.datetime.now().strftime("%H:%M:%S")

    network_data = [
        12,
        15,
        18,
        14,
        22,
        28,
        35,
        42,
        38,
        30,
        25,
        20,
        18,
        15,
        12,
        10,
        14,
        18,
        24,
        30,
        36,
        40,
        38,
        32,
        26,
        20,
        16,
        12,
        10,
        8,
    ]

    svg_parts = []
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{term_w}" height="{term_h}" viewBox="0 0 {term_w} {term_h}">
  <style>
    text {{ font-family: {font}, 'Courier New', monospace; font-size: {fs}px; white-space: pre; }}
  </style>
  <rect width="{term_w}" height="{term_h}" rx="8" fill="{bg}"/>
  <rect width="{term_w}" height="{title_bar_h}" rx="8" fill="#1a1a2e"/>
  <rect y="16" width="{term_w}" height="16" fill="#1a1a2e"/>
  <circle cx="20" cy="16" r="6" fill="#ff5f56"/>
  <circle cx="40" cy="16" r="6" fill="#ffbd2e"/>
  <circle cx="60" cy="16" r="6" fill="#27c93f"/>
  <text x="{term_w // 2}" y="20" text-anchor="middle" fill="{gray_c}" font-size="13">STAC6-Drive-01 -- Device Detail</text>
''')

    cx = pad
    cy = title_bar_h + pad

    svg_parts.append(f'''  <rect x="{cx}" y="{cy}" width="{term_w - 20}" height="60" rx="2" fill="none" stroke="{yellow_c}" stroke-width="1"/>
  <rect x="{cx + 1}" y="{cy - 1}" width="260" height="14" fill="{bg}"/>
  <text x="{cx + 4}" y="{cy + 11}" fill="{yellow_c}" font-weight="bold"> STAC6-Drive-01 (192.168.10.30) </text>
  <text x="{cx + 4}" y="{cy + 28}" fill="{yellow_c}">Status: \u25d0 High Latency (245ms)</text>
  <text x="{cx + 4}" y="{cy + 44}" fill="{gray_c}">Protocol: Modbus TCP | Uptime: 14h 32m</text>
''')

    bar_y = cy + 72
    svg_parts.append(f'''  <rect x="{cx}" y="{bar_y}" width="{term_w - 20}" height="140" rx="2" fill="none" stroke="{border_c}" stroke-width="1"/>
  <rect x="{cx + 1}" y="{bar_y - 1}" width="140" height="14" fill="{bg}"/>
  <text x="{cx + 4}" y="{bar_y + 11}" fill="{cyan_c}" font-weight="bold"> Network I/O </text>
''')

    bar_area_w = term_w - 44
    bar_h_max = 80
    bar_w_each = max(3, bar_area_w // len(network_data))
    bar_base = bar_y + 120
    for i, val in enumerate(network_data):
        h = int((val / 50) * bar_h_max)
        y_pos = bar_base - h
        x_pos = cx + 10 + (i * bar_w_each)
        color = green_c if val < 25 else (yellow_c if val < 40 else red_c)
        svg_parts.append(
            f'  <rect x="{x_pos}" y="{y_pos}" width="{bar_w_each - 1}" height="{h}" fill="{color}" opacity="0.7"/>'
        )

    stats_y = bar_y + 150
    svg_parts.append(f'''  <rect x="{cx}" y="{stats_y}" width="{(term_w - 24) // 3}" height="80" rx="2" fill="none" stroke="{border_c}" stroke-width="1"/>
  <text x="{cx + 6}" y="{stats_y + 16}" fill="{gray_c}">Avg Latency</text>
  <text x="{cx + 6}" y="{stats_y + 38}" fill="{yellow_c}" font-size="22" font-weight="bold">182ms</text>
  <text x="{cx + 6}" y="{stats_y + 56}" fill="{dark_gray_c}">p95: 312ms</text>
  <text x="{cx + 6}" y="{stats_y + 70}" fill="{dark_gray_c}">p99: 478ms</text>
''')

    stats2_x = cx + (term_w - 24) // 3 + 4
    svg_parts.append(f'''  <rect x="{stats2_x}" y="{stats_y}" width="{(term_w - 24) // 3}" height="80" rx="2" fill="none" stroke="{border_c}" stroke-width="1"/>
  <text x="{stats2_x + 6}" y="{stats_y + 16}" fill="{gray_c}">Packet Loss</text>
  <text x="{stats2_x + 6}" y="{stats_y + 38}" fill="{red_c}" font-size="22" font-weight="bold">2.4%</text>
  <text x="{stats2_x + 6}" y="{stats_y + 56}" fill="{dark_gray_c}">RX: 14.2 MB/s</text>
  <text x="{stats2_x + 6}" y="{stats_y + 70}" fill="{dark_gray_c}">TX: 8.7 MB/s</text>
''')

    stats3_x = stats2_x + (term_w - 24) // 3 + 4
    svg_parts.append(f'''  <rect x="{stats3_x}" y="{stats_y}" width="{(term_w - 24) // 3 - 2}" height="80" rx="2" fill="none" stroke="{border_c}" stroke-width="1"/>
  <text x="{stats3_x + 6}" y="{stats_y + 16}" fill="{gray_c}">Temperature</text>
  <text x="{stats3_x + 6}" y="{stats_y + 38}" fill="{green_c}" font-size="22" font-weight="bold">42.1C</text>
  <text x="{stats3_x + 6}" y="{stats_y + 56}" fill="{dark_gray_c}">Threshold: 60C</text>
  <text x="{stats3_x + 6}" y="{stats_y + 70}" fill="{dark_gray_c}">Cycles: 1,247,832</text>
''')

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


if __name__ == "__main__":
    main_svg = generate_main_screenshot()
    detail_svg = generate_device_detail_screenshot()

    with open("factoryops-main.svg", "w") as f:
        f.write(main_svg)
    print("Generated: factoryops-main.svg")

    with open("factoryops-device-detail.svg", "w") as f:
        f.write(detail_svg)
    print("Generated: factoryops-device-detail.svg")
