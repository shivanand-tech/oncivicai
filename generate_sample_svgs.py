"""
Generates high-definition futuristic SVG graphics for complaint previews & before/after comparisons.
"""

import os

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images", "samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

svgs = {
    "manhole_open_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <radialGradient id="hole" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="70%" stop-color="#090d16"/>
      <stop offset="100%" stop-color="#334155"/>
    </radialGradient>
    <linearGradient id="laser" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="rgba(239,68,68,0)"/>
      <stop offset="50%" stop-color="rgba(239,68,68,0.8)"/>
      <stop offset="100%" stop-color="rgba(239,68,68,0)"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#bg)"/>
  <!-- Street paving grid -->
  <line x1="0" y1="280" x2="600" y2="280" stroke="#334155" stroke-width="2"/>
  <line x1="0" y1="360" x2="600" y2="360" stroke="#334155" stroke-width="2"/>
  <ellipse cx="300" cy="240" rx="140" ry="70" fill="url(#hole)" stroke="#ef4444" stroke-width="3" stroke-dasharray="8,4"/>
  <ellipse cx="300" cy="240" rx="100" ry="50" fill="#000000"/>
  <!-- Warning tape -->
  <path d="M 120 180 L 480 300" stroke="#f59e0b" stroke-width="8" stroke-dasharray="20,15" opacity="0.6"/>
  <!-- HUD elements -->
  <rect x="20" y="20" width="190" height="36" rx="6" fill="rgba(15,23,42,0.85)" stroke="#ef4444" stroke-width="1.5"/>
  <text x="32" y="44" fill="#ef4444" font-family="monospace" font-size="14" font-weight="bold">● CRITICAL HAZARD</text>
  <rect x="200" y="210" width="200" height="60" rx="4" fill="none" stroke="#00d9ff" stroke-width="1.5" stroke-dasharray="4,4"/>
  <text x="210" y="200" fill="#00d9ff" font-family="monospace" font-size="12">CHAMBER DEPTH: 2.1m</text>
  <line x1="160" y1="240" x2="440" y2="240" stroke="url(#laser)" stroke-width="2"/>
  <text x="300" y="375" fill="#94a3b8" font-family="sans-serif" font-size="13" text-anchor="middle">Open Manhole Cavity — Residency Road Zone</text>
</svg>""",

    "pothole_crater_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="asphalt" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <radialGradient id="potholeDepth" cx="45%" cy="45%" r="60%">
      <stop offset="0%" stop-color="#090d16"/>
      <stop offset="60%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#475569"/>
    </radialGradient>
  </defs>
  <rect width="600" height="400" fill="url(#asphalt)"/>
  <!-- Road markings -->
  <line x1="0" y1="200" x2="160" y2="200" stroke="#f59e0b" stroke-width="8" stroke-dasharray="25,20"/>
  <line x1="440" y1="200" x2="600" y2="200" stroke="#f59e0b" stroke-width="8" stroke-dasharray="25,20"/>
  <!-- Crater shape -->
  <path d="M 180 180 Q 240 130 330 150 Q 420 170 440 230 Q 430 290 340 310 Q 230 320 180 260 Z" fill="url(#potholeDepth)" stroke="#f59e0b" stroke-width="2.5"/>
  <path d="M 220 200 Q 280 180 340 190 Q 380 230 350 260 Q 270 280 220 230 Z" fill="#020617"/>
  <!-- HUD Detection box -->
  <rect x="160" y="120" width="300" height="210" rx="4" fill="none" stroke="#00d9ff" stroke-width="1.5" stroke-dasharray="6,4"/>
  <rect x="160" y="96" width="160" height="24" rx="4" fill="rgba(15,23,42,0.85)" stroke="#00d9ff" stroke-width="1"/>
  <text x="170" y="113" fill="#00d9ff" font-family="monospace" font-size="11">WIDTH: 1.4m | DEPTH: 16cm</text>
  <rect x="20" y="20" width="160" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="30" y="42" fill="#f59e0b" font-family="monospace" font-size="13" font-weight="bold">▲ HIGH PRIORITY</text>
  <text x="300" y="375" fill="#94a3b8" font-family="sans-serif" font-size="13" text-anchor="middle">Asphalt Crater Fracture — Indiranagar 100ft Road</text>
</svg>""",

    "pothole_resolved_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="freshAsphalt" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <linearGradient id="patchGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#334155"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#freshAsphalt)"/>
  <!-- Road markings restored -->
  <line x1="0" y1="200" x2="600" y2="200" stroke="#f59e0b" stroke-width="8" stroke-dasharray="25,20"/>
  <!-- Freshly compacted asphalt patch -->
  <path d="M 170 170 Q 240 130 340 145 Q 430 165 445 235 Q 430 300 335 315 Q 220 325 170 255 Z" fill="url(#patchGrad)" stroke="#10b981" stroke-width="2"/>
  <!-- Smooth roller compaction texture -->
  <line x1="190" y1="180" x2="420" y2="180" stroke="#475569" stroke-width="1" stroke-dasharray="4,8"/>
  <line x1="185" y1="220" x2="435" y2="220" stroke="#475569" stroke-width="1" stroke-dasharray="4,8"/>
  <line x1="190" y1="260" x2="415" y2="260" stroke="#475569" stroke-width="1" stroke-dasharray="4,8"/>
  <!-- Verified Badge -->
  <rect x="20" y="20" width="200" height="36" rx="6" fill="rgba(15,23,42,0.9)" stroke="#10b981" stroke-width="1.5"/>
  <text x="32" y="44" fill="#10b981" font-family="monospace" font-size="13" font-weight="bold">✓ RESOLUTION VERIFIED</text>
  <rect x="390" y="20" width="190" height="36" rx="6" fill="rgba(15,23,42,0.9)" stroke="#00d9ff" stroke-width="1"/>
  <text x="402" y="44" fill="#00d9ff" font-family="monospace" font-size="12">PWD RAPID CREW #14</text>
  <text x="300" y="375" fill="#10b981" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">Hot-Mix Steam Compacted &amp; Slope Restored</text>
</svg>""",

    "waterlogging_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="sky" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="floodWater" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(6,182,212,0.4)"/>
      <stop offset="50%" stop-color="rgba(14,116,144,0.7)"/>
      <stop offset="100%" stop-color="rgba(21,94,117,0.85)"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#sky)"/>
  <!-- Submerged road and reflections -->
  <path d="M 0 210 Q 150 200 300 205 Q 450 210 600 200 L 600 400 L 0 400 Z" fill="url(#floodWater)"/>
  <!-- Water ripples -->
  <ellipse cx="220" cy="280" rx="90" ry="18" fill="none" stroke="#38bdf8" stroke-width="1.5" opacity="0.6"/>
  <ellipse cx="400" cy="320" rx="130" ry="24" fill="none" stroke="#38bdf8" stroke-width="1.5" opacity="0.5"/>
  <ellipse cx="180" cy="340" rx="100" ry="20" fill="none" stroke="#38bdf8" stroke-width="1.5" opacity="0.4"/>
  <!-- Submerged traffic divider -->
  <rect x="280" y="220" width="40" height="50" fill="#f59e0b" stroke="#ffffff" stroke-width="2"/>
  <rect x="20" y="20" width="180" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#ef4444" stroke-width="1.5"/>
  <text x="32" y="42" fill="#ef4444" font-family="monospace" font-size="13" font-weight="bold">● SEVERE FLOODING</text>
  <text x="300" y="375" fill="#e2e8f0" font-family="sans-serif" font-size="13" text-anchor="middle">Water Depth > 30cm — Koramangala 80ft Road</text>
</svg>""",

    "waterlogging_2.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="drainBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#drainBg)"/>
  <!-- Grating choked -->
  <rect x="150" y="160" width="300" height="160" rx="8" fill="#334155" stroke="#64748b" stroke-width="2"/>
  <line x1="180" y1="160" x2="180" y2="320" stroke="#0f172a" stroke-width="8"/>
  <line x1="220" y1="160" x2="220" y2="320" stroke="#0f172a" stroke-width="8"/>
  <line x1="260" y1="160" x2="260" y2="320" stroke="#0f172a" stroke-width="8"/>
  <line x1="300" y1="160" x2="300" y2="320" stroke="#0f172a" stroke-width="8"/>
  <line x1="340" y1="160" x2="340" y2="320" stroke="#0f172a" stroke-width="8"/>
  <line x1="380" y1="160" x2="380" y2="320" stroke="#0f172a" stroke-width="8"/>
  <line x1="420" y1="160" x2="420" y2="320" stroke="#0f172a" stroke-width="8"/>
  <!-- Silt overlay -->
  <path d="M 170 240 Q 300 210 430 250 L 440 330 L 160 330 Z" fill="#78350f" opacity="0.85"/>
  <text x="300" y="280" fill="#fef3c7" font-family="monospace" font-size="12" text-anchor="middle">CHOKED WITH SILT &amp; SOLID WASTE</text>
  <rect x="20" y="20" width="180" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="32" y="42" fill="#f59e0b" font-family="monospace" font-size="13" font-weight="bold">▲ DRAIN INLET CHOKE</text>
  <text x="300" y="375" fill="#94a3b8" font-family="sans-serif" font-size="13" text-anchor="middle">Stormwater Grating Silt Blockage — Koramangala 6th Block</text>
</svg>""",

    "electrical_wire_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="nightBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#nightBg)"/>
  <!-- Utility pole -->
  <rect x="100" y="40" width="24" height="360" fill="#475569"/>
  <rect x="60" y="80" width="104" height="12" fill="#64748b"/>
  <!-- Snapped cable with spark -->
  <path d="M 112 86 Q 220 180 320 280 Q 330 295 345 285" fill="none" stroke="#38bdf8" stroke-width="4"/>
  <!-- Spark effect -->
  <circle cx="345" cy="285" r="14" fill="#fef08a" opacity="0.9"/>
  <line x1="335" y1="275" x2="315" y2="260" stroke="#f59e0b" stroke-width="2"/>
  <line x1="355" y1="275" x2="375" y2="255" stroke="#facc15" stroke-width="2"/>
  <line x1="345" y1="295" x2="350" y2="315" stroke="#f59e0b" stroke-width="2"/>
  <!-- Warning badge -->
  <rect x="20" y="20" width="190" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#ef4444" stroke-width="1.5"/>
  <text x="32" y="42" fill="#ef4444" font-family="monospace" font-size="13" font-weight="bold">⚡ 440V LIVE CABLE</text>
  <text x="300" y="375" fill="#f87171" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">Danglng High Tension Cable — Hebbal Flyover Corridor</text>
</svg>""",

    "electrical_resolved_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="nightSky" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#090d16"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#nightSky)"/>
  <!-- Utility pole rewired -->
  <rect x="100" y="40" width="24" height="360" fill="#475569"/>
  <rect x="60" y="80" width="104" height="12" fill="#64748b"/>
  <!-- Taut insulated cable -->
  <line x1="112" y1="86" x2="550" y2="110" stroke="#10b981" stroke-width="4"/>
  <!-- New LED street light beam -->
  <polygon points="112,120 0,400 350,400" fill="rgba(250,204,21,0.18)"/>
  <!-- Verified Badge -->
  <rect x="20" y="20" width="210" height="36" rx="6" fill="rgba(15,23,42,0.9)" stroke="#10b981" stroke-width="1.5"/>
  <text x="32" y="44" fill="#10b981" font-family="monospace" font-size="13" font-weight="bold">✓ BESCOM SQUAD RESTORED</text>
  <text x="300" y="375" fill="#10b981" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">Cable Anchored &amp; Lockable Galvanized Box Sealed</text>
</svg>""",

    "streetlight_dark_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="darkAvenue" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="100%" stop-color="#0b0f19"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#darkAvenue)"/>
  <!-- Silhouette poles dark -->
  <rect x="120" y="80" width="8" height="320" fill="#1e293b"/>
  <path d="M 120 80 Q 150 60 170 80" stroke="#1e293b" stroke-width="6" fill="none"/>
  <rect x="280" y="110" width="7" height="290" fill="#1e293b"/>
  <rect x="420" y="140" width="6" height="260" fill="#1e293b"/>
  <!-- Road strip dark -->
  <line x1="0" y1="360" x2="600" y2="360" stroke="#1e293b" stroke-width="2"/>
  <rect x="20" y="20" width="180" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="32" y="42" fill="#f59e0b" font-family="monospace" font-size="13" font-weight="bold">▲ ZERO LUX BLACKOUT</text>
  <text x="300" y="375" fill="#64748b" font-family="sans-serif" font-size="13" text-anchor="middle">800m Luminaire Outage — Outer Ring Road</text>
</svg>""",

    "garbage_pile_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="alley" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#alley)"/>
  <!-- Green municipal bin toppled -->
  <rect x="360" y="220" width="110" height="90" rx="8" fill="#15803d" stroke="#22c55e" stroke-width="2" transform="rotate(18 360 220)"/>
  <!-- Waste mound -->
  <path d="M 140 340 Q 220 200 320 220 Q 420 240 500 340 Z" fill="#64748b"/>
  <circle cx="240" cy="280" r="14" fill="#3b82f6" opacity="0.8"/>
  <rect x="270" y="290" width="35" height="25" fill="#f59e0b" opacity="0.8"/>
  <rect x="320" y="270" width="40" height="30" fill="#ef4444" opacity="0.8"/>
  <!-- Odor / vector waves -->
  <path d="M 260 210 Q 270 180 260 160" stroke="#84cc16" stroke-width="2" fill="none" opacity="0.6"/>
  <path d="M 310 200 Q 320 170 310 150" stroke="#84cc16" stroke-width="2" fill="none" opacity="0.6"/>
  <rect x="20" y="20" width="180" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#00d9ff" stroke-width="1.5"/>
  <text x="32" y="42" fill="#00d9ff" font-family="monospace" font-size="13" font-weight="bold">◈ SOLID WASTE DUMP</text>
  <text x="300" y="375" fill="#94a3b8" font-family="sans-serif" font-size="13" text-anchor="middle">Overflowing Municipal Bin — HSR Sector 2</text>
</svg>""",

    "garbage_pile_2.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="lakeBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#lakeBg)"/>
  <!-- Lake bank -->
  <path d="M 0 260 Q 300 240 600 270 L 600 400 L 0 400 Z" fill="#334155"/>
  <!-- Concrete debris mound -->
  <polygon points="180,330 260,220 380,240 450,330" fill="#94a3b8" stroke="#cbd5e1" stroke-width="1.5"/>
  <polygon points="220,330 290,260 340,330" fill="#64748b"/>
  <rect x="20" y="20" width="190" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="32" y="42" fill="#f59e0b" font-family="monospace" font-size="13" font-weight="bold">▲ DEBRIS FLY-TIPPING</text>
  <text x="300" y="375" fill="#94a3b8" font-family="sans-serif" font-size="13" text-anchor="middle">Illegal Construction Rubble — Agara Lake Bund</text>
</svg>""",

    "garbage_resolved_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="cleanAlley" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#cleanAlley)"/>
  <!-- Spotless pavement -->
  <line x1="0" y1="280" x2="600" y2="280" stroke="#334155" stroke-width="2"/>
  <!-- 2 New smart sensor bins -->
  <rect x="220" y="200" width="60" height="100" rx="6" fill="#15803d" stroke="#22c55e" stroke-width="2"/>
  <rect x="310" y="200" width="60" height="100" rx="6" fill="#1d4ed8" stroke="#3b82f6" stroke-width="2"/>
  <text x="250" y="255" fill="#ffffff" font-family="monospace" font-size="11" text-anchor="middle">WET</text>
  <text x="340" y="255" fill="#ffffff" font-family="monospace" font-size="11" text-anchor="middle">DRY</text>
  <!-- Verified Badge -->
  <rect x="20" y="20" width="200" height="36" rx="6" fill="rgba(15,23,42,0.9)" stroke="#10b981" stroke-width="1.5"/>
  <text x="32" y="44" fill="#10b981" font-family="monospace" font-size="13" font-weight="bold">✓ DECONTAMINATED</text>
  <text x="300" y="375" fill="#10b981" font-family="sans-serif" font-size="13" font-weight="bold" text-anchor="middle">Bleach Sanitized &amp; Smart Segregation Bins Placed</text>
</svg>""",

    "tree_fallen_1.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="100%" height="100%">
  <defs>
    <linearGradient id="stormBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
  </defs>
  <rect width="600" height="400" fill="url(#stormBg)"/>
  <!-- Road tarmac -->
  <line x1="0" y1="290" x2="600" y2="290" stroke="#334155" stroke-width="2"/>
  <!-- Heavy trunk fallen across -->
  <path d="M 80 320 Q 250 240 480 270 L 490 300 Q 250 270 90 350 Z" fill="#78350f" stroke="#451a03" stroke-width="2"/>
  <!-- Foliage canopy -->
  <ellipse cx="440" cy="240" rx="90" ry="60" fill="#166534" opacity="0.85"/>
  <ellipse cx="380" cy="220" rx="70" ry="50" fill="#15803d" opacity="0.85"/>
  <!-- Warning badge -->
  <rect x="20" y="20" width="190" height="34" rx="6" fill="rgba(15,23,42,0.85)" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="32" y="42" fill="#f59e0b" font-family="monospace" font-size="13" font-weight="bold">▲ TRAFFIC BLOCKAGE</text>
  <text x="300" y="375" fill="#f59e0b" font-family="sans-serif" font-size="13" text-anchor="middle">Uprooted Tree Across Right-of-Way — Malleshwaram 8th Cross</text>
</svg>"""
}

for filename, content in svgs.items():
    filepath = os.path.join(SAMPLES_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip())

print(f"Generated {len(svgs)} sample SVG visual assets in {SAMPLES_DIR}")
