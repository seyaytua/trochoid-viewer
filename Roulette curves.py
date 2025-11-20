import sys
import io
import base64
import platform
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QComboBox, QSlider, 
                               QPushButton, QGroupBox, QTextEdit, QCheckBox, QTabWidget, QScrollArea)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtSvgWidgets import QSvgWidget
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# OSに応じたフォント名を設定
if platform.system() == 'Darwin':  # macOS
    FONT_NAME = 'Hiragino Sans'
elif platform.system() == 'Windows':
    FONT_NAME = 'Meiryo'
else:
    FONT_NAME = 'sans-serif'

# matplotlib設定
plt.rcParams['font.family'] = FONT_NAME
plt.rcParams['mathtext.fontset'] = 'cm'

# ---------------------------------------------------------
# 数式画像を生成するヘルパー関数
# ---------------------------------------------------------
def latex_to_html(latex_str, fontsize=12):
    try:
        fig = Figure(figsize=(0.1, 0.1), dpi=120)
        canvas = FigureCanvasAgg(fig)
        text = fig.text(0, 0, f"${latex_str}$", fontsize=fontsize, va='bottom', ha='left')
        buf = io.BytesIO()
        canvas.draw()
        bbox = text.get_window_extent()
        width = bbox.width / 120 + 0.1
        height = bbox.height / 120 + 0.1
        fig.set_size_inches(width, height)
        text.set_position((0.05, 0.05))
        fig.savefig(buf, format='png', transparent=True, bbox_inches='tight', pad_inches=0.05)
        plt.close(fig)
        data = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f'<img src="data:image/png;base64,{data}" style="vertical-align: middle;">'
    except:
        return f"<code>{latex_str}</code>"

# ---------------------------------------------------------
# 曲線の定義データ（数式と説明を含む）
# ---------------------------------------------------------
CURVE_DEFINITIONS = {
    "cycloid": {
        "name": "サイクロイド (Cycloid)",
        "formulas": [
            "x = r(t - sin t)",
            "y = r(1 - cos t)"
        ],
        "description": "直線上を転がる円の円周上の点が描く軌跡。最速降下線（ブラキストクロン）として有名。",
        "k_meaning": "K: 使用しません",
        "d_meaning": "d: 使用しません（円周上の点 d=r）",
        "properties": [
            "• 最速降下線（ブラキストクロン）",
            "• 等時曲線（タウトクロン）",
            "• 曲線の長さ: L = 8r",
            "• 囲まれる面積: S = 3πr²"
        ]
    },
    "trochoid": {
        "name": "トロコイド (Trochoid)",
        "formulas": [
            "x = rt - d·sin t",
            "y = r - d·cos t"
        ],
        "description": "直線上を転がる円の円周外/内の点が描く軌跡。",
        "k_meaning": "K: 使用しません",
        "d_meaning": "d: 円の中心から追跡点までの距離（d>r でループ、d<r で滑らか）",
        "properties": [
            "• d > r: ループを持つ（長トロコイド）",
            "• d < r: 滑らかな波形（短トロコイド）",
            "• d = r: サイクロイドと一致",
            "• 機械工学で重要"
        ]
    },
    "cardioid": {
        "name": "カージオイド (Cardioid)",
        "formulas": [
            "x = 2r·cos t - r·cos 2t",
            "y = 2r·sin t - r·sin 2t"
        ],
        "description": "固定円の外側を同じ半径の円が転がるときの軌跡。心臓形。",
        "k_meaning": "K: 固定（k=1、エピサイクロイドの特殊例）",
        "d_meaning": "d: 固定（円周上の点）",
        "properties": [
            "• エピサイクロイドで k=1 の場合",
            "• 極座標: ρ = 2r(1 + cos θ)",
            "• 曲線の長さ: L = 16r",
            "• マイクの指向性パターン"
        ]
    },
    "nephroid": {
        "name": "ネフロイド (Nephroid)",
        "formulas": [
            "x = 3a·cos t - a·cos 3t",
            "y = 3a·sin t - a·sin 3t"
        ],
        "description": "固定円の外側を半分の半径の円が転がるときの軌跡。腎臓形。",
        "k_meaning": "K: 固定（k=2、エピサイクロイドの特殊例）",
        "d_meaning": "d: 固定（円周上の点）",
        "properties": [
            "• エピサイクロイドで k=2 の場合",
            "• 2つの尖点を持つ",
            "• 曲線の長さ: L = 24a",
            "• コーヒーカップの光輪"
        ]
    },
    "astroid": {
        "name": "アステロイド (Astroid)",
        "formulas": [
            "x = a·cos³ t",
            "y = a·sin³ t"
        ],
        "description": "固定円の内側を1/4の半径の円が転がるときの軌跡。星形。",
        "k_meaning": "K: 固定（k=4、ハイポサイクロイドの特殊例）",
        "d_meaning": "d: 固定（円周上の点）",
        "properties": [
            "• ハイポサイクロイドで k=4 の場合",
            "• x^(2/3) + y^(2/3) = a^(2/3)",
            "• 曲線の長さ: L = 6a",
            "• 4つの尖点を持つ"
        ]
    },
    "epicycloid": {
        "name": "エピサイクロイド (Epicycloid)",
        "formulas": [
            "x = (R+r)·cos t - r·cos((R+r)/r·t)",
            "y = (R+r)·sin t - r·sin((R+r)/r·t)"
        ],
        "description": "固定円の外側を円が転がるときの円周上の点が描く軌跡。",
        "k_meaning": "K: 尖点の数（転がる円の半径 = R/k）",
        "d_meaning": "d: 固定（円周上の点）",
        "properties": [
            "• k個の尖点を持つ",
            "• k=1: カージオイド",
            "• k=2: ネフロイド",
            "• 歯車設計に応用"
        ]
    },
    "epitrochoid": {
        "name": "エピトロコイド (Epitrochoid)",
        "formulas": [
            "x = (R+r)·cos t - d·cos((R+r)/r·t)",
            "y = (R+r)·sin t - d·sin((R+r)/r·t)"
        ],
        "description": "固定円の外側を転がる円の円周外/内の点が描く軌跡。",
        "k_meaning": "K: 基本パターンの繰り返し数（転がる円の半径 = R/k）",
        "d_meaning": "d: 円の中心から追跡点までの距離（可変）",
        "properties": [
            "• エピサイクロイドの一般化",
            "• d ≠ r で複雑な花びら模様",
            "• 装飾デザインに使用",
            "• k と d で無限のパターン"
        ]
    },
    "hypocycloid": {
        "name": "ハイポサイクロイド (Hypocycloid)",
        "formulas": [
            "x = (R-r)·cos t + r·cos((R-r)/r·t)",
            "y = (R-r)·sin t - r·sin((R-r)/r·t)"
        ],
        "description": "固定円の内側を円が転がるときの円周上の点が描く軌跡。",
        "k_meaning": "K: 尖点の数（転がる円の半径 = R/k）",
        "d_meaning": "d: 固定（円周上の点）",
        "properties": [
            "• k個の尖点を持つ",
            "• k=3: デルトイド",
            "• k=4: アステロイド",
            "• 星形・多角形を生成"
        ]
    },
    "hypotrochoid": {
        "name": "ハイポトロコイド (Hypotrochoid)",
        "formulas": [
            "x = (R-r)·cos t + d·cos((R-r)/r·t)",
            "y = (R-r)·sin t - d·sin((R-r)/r·t)"
        ],
        "description": "固定円の内側を転がる円の円周外/内の点が描く軌跡。スピログラフ！",
        "k_meaning": "K: 基本パターンの繰り返し数（転がる円の半径 = R/k）",
        "d_meaning": "d: 円の中心から追跡点までの距離（可変、スピログラフの核心）",
        "properties": [
            "• ハイポサイクロイドの一般化",
            "• スピログラフ玩具の原理",
            "• 美しい幾何学模様",
            "• d ≠ r で複雑なパターン"
        ]
    },
    "lissajous": {
        "name": "リサージュ曲線 (Lissajous)",
        "formulas": [
            "x = r·sin(at + δ)",
            "y = r·sin(bt)"
        ],
        "description": "2つの単振動の合成。オシロスコープで観測可能。",
        "k_meaning": "K: x方向の振動数 a（周波数比）",
        "d_meaning": "d: 位相差 δ（0〜2π）",
        "properties": [
            "• 振動の可視化",
            "• a/b が有理数で閉曲線",
            "• オシロスコープで観測",
            "• 音響学・電気工学で重要"
        ]
    },
    "rose": {
        "name": "正葉曲線 (Rose Curve)",
        "formulas": [
            "ρ = r·cos(kθ)",
            "x = ρ·cos θ",
            "y = ρ·sin θ"
        ],
        "description": "バラの花びらのような曲線。極座標で美しい対称性。",
        "k_meaning": "K: 花びらの数（奇数なら k 枚、偶数なら 2k 枚）",
        "d_meaning": "d: 使用しません",
        "properties": [
            "• k が奇数: k 枚の花びら",
            "• k が偶数: 2k 枚の花びら",
            "• 極座標で美しい対称性",
            "• 装飾デザインに応用"
        ]
    }
}

# ---------------------------------------------------------
# SVG分類図データ（元のまま）
# ---------------------------------------------------------
CLASSIFICATION_SVG = """
<svg width="1600" height="900" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title { font-family: 'Meiryo', 'Hiragino Sans', sans-serif; font-size: 24px; font-weight: bold; fill: #2c3e50; }
      .header { font-family: 'Meiryo', 'Hiragino Sans', sans-serif; font-size: 16px; font-weight: bold; fill: #34495e; }
      .subheader { font-family: 'Meiryo', 'Hiragino Sans', sans-serif; font-size: 14px; font-weight: bold; fill: #555; }
      .note { font-family: 'Meiryo', 'Hiragino Sans', sans-serif; font-size: 12px; fill: #7f8c8d; }
      .cell { fill: #ecf0f1; stroke: #95a5a6; stroke-width: 2; }
      .highlight { fill: #e8f6f3; stroke: #16a085; stroke-width: 2; }
      .header-cell { fill: #d5dbdb; stroke: #7f8c8d; stroke-width: 2; }
    </style>
  </defs>
  
  <text x="800" y="35" text-anchor="middle" class="title">トロコイド系曲線の分類体系（表形式）</text>
  <text x="800" y="60" text-anchor="middle" class="note">Trochoid Family Curves Classification Table</text>
  
  <rect x="50" y="100" width="200" height="60" class="header-cell"/>
  <text x="150" y="135" text-anchor="middle" class="header">転がる場所</text>
  
  <rect x="250" y="100" width="675" height="60" class="header-cell"/>
  <text x="587.5" y="135" text-anchor="middle" class="header">直線上を転がる</text>
  
  <rect x="925" y="100" width="625" height="60" class="header-cell"/>
  <text x="1237.5" y="135" text-anchor="middle" class="header">円の上を転がる</text>
  
  <rect x="50" y="160" width="200" height="60" class="header-cell"/>
  <text x="150" y="195" text-anchor="middle" class="header">追跡点の位置</text>
  
  <rect x="250" y="160" width="337.5" height="60" class="header-cell"/>
  <text x="418.75" y="195" text-anchor="middle" class="subheader">円周上 (d = r)</text>
  
  <rect x="587.5" y="160" width="337.5" height="60" class="header-cell"/>
  <text x="756.25" y="195" text-anchor="middle" class="subheader">円周外/内 (d ≠ r)</text>
  
  <rect x="925" y="160" width="312.5" height="60" class="header-cell"/>
  <text x="1081.25" y="185" text-anchor="middle" class="subheader">外側を転がる</text>
  
  <rect x="1237.5" y="160" width="312.5" height="60" class="header-cell"/>
  <text x="1393.75" y="185" text-anchor="middle" class="subheader">内側を転がる</text>
  
  <rect x="50" y="220" width="200" height="80" class="header-cell"/>
  <text x="150" y="265" text-anchor="middle" class="header">曲線名</text>
  
  <rect x="250" y="220" width="337.5" height="80" class="highlight"/>
  <text x="418.75" y="255" text-anchor="middle" class="subheader">サイクロイド</text>
  <text x="418.75" y="275" text-anchor="middle" class="note">Cycloid</text>
  
  <rect x="587.5" y="220" width="337.5" height="80" class="highlight"/>
  <text x="756.25" y="255" text-anchor="middle" class="subheader">トロコイド</text>
  <text x="756.25" y="275" text-anchor="middle" class="note">Trochoid</text>
  
  <rect x="925" y="220" width="312.5" height="80" class="highlight"/>
  <text x="1081.25" y="255" text-anchor="middle" class="subheader">エピサイクロイド</text>
  
  <rect x="1237.5" y="220" width="312.5" height="80" class="highlight"/>
  <text x="1393.75" y="255" text-anchor="middle" class="subheader">ハイポサイクロイド</text>
  
  <rect x="50" y="300" width="200" height="120" class="header-cell"/>
  <text x="150" y="365" text-anchor="middle" class="header">主な特徴</text>
  
  <rect x="250" y="300" width="337.5" height="120" class="cell"/>
  <text x="418.75" y="340" text-anchor="middle" class="note">・最速降下線</text>
  <text x="418.75" y="360" text-anchor="middle" class="note">・等時曲線</text>
  <text x="418.75" y="380" text-anchor="middle" class="note">・物理学で重要</text>
  
  <rect x="587.5" y="300" width="337.5" height="120" class="cell"/>
  <text x="756.25" y="345" text-anchor="middle" class="note">・波打つ形状</text>
  <text x="756.25" y="365" text-anchor="middle" class="note">・d &gt; r でループ</text>
  <text x="756.25" y="385" text-anchor="middle" class="note">・機械工学で重要</text>
  
  <rect x="925" y="300" width="312.5" height="120" class="cell"/>
  <text x="1081.25" y="340" text-anchor="middle" class="note">・花びら模様</text>
  <text x="1081.25" y="360" text-anchor="middle" class="note">・k個の尖点</text>
  <text x="1081.25" y="380" text-anchor="middle" class="note">・歯車設計</text>
  
  <rect x="1237.5" y="300" width="312.5" height="120" class="cell"/>
  <text x="1393.75" y="340" text-anchor="middle" class="note">・星形・多角形</text>
  <text x="1393.75" y="360" text-anchor="middle" class="note">・k個の尖点</text>
  <text x="1393.75" y="380" text-anchor="middle" class="note">・スピログラフ</text>
  
  <rect x="50" y="420" width="200" height="80" class="header-cell"/>
  <text x="150" y="465" text-anchor="middle" class="header">一般化</text>
  
  <rect x="250" y="420" width="337.5" height="80" class="cell"/>
  <text x="418.75" y="455" text-anchor="middle" class="note">→ トロコイド</text>
  
  <rect x="587.5" y="420" width="337.5" height="80" class="cell"/>
  <text x="756.25" y="465" text-anchor="middle" class="note">サイクロイドの</text>
  <text x="756.25" y="485" text-anchor="middle" class="note">一般化形</text>
  
  <rect x="925" y="420" width="312.5" height="80" class="highlight"/>
  <text x="1081.25" y="455" text-anchor="middle" class="subheader">エピトロコイド</text>
  
  <rect x="1237.5" y="420" width="312.5" height="80" class="highlight"/>
  <text x="1393.75" y="455" text-anchor="middle" class="subheader">ハイポトロコイド</text>
  
  <rect x="50" y="500" width="200" height="100" class="header-cell"/>
  <text x="150" y="555" text-anchor="middle" class="header">応用例</text>
  
  <rect x="250" y="500" width="337.5" height="100" class="cell"/>
  <text x="418.75" y="540" text-anchor="middle" class="note">物理学・力学</text>
  <text x="418.75" y="560" text-anchor="middle" class="note">最適化問題</text>
  
  <rect x="587.5" y="500" width="337.5" height="100" class="cell"/>
  <text x="756.25" y="540" text-anchor="middle" class="note">機械設計</text>
  <text x="756.25" y="560" text-anchor="middle" class="note">波形解析</text>
  
  <rect x="925" y="500" width="312.5" height="100" class="cell"/>
  <text x="1081.25" y="540" text-anchor="middle" class="note">歯車設計</text>
  <text x="1081.25" y="560" text-anchor="middle" class="note">装飾デザイン</text>
  
  <rect x="1237.5" y="500" width="312.5" height="100" class="cell"/>
  <text x="1393.75" y="540" text-anchor="middle" class="note">スピログラフ玩具</text>
  <text x="1393.75" y="560" text-anchor="middle" class="note">芸術・デザイン</text>
  
  <rect x="50" y="620" width="1500" height="240" fill="#f9f9f9" stroke="#bdc3c7" stroke-width="1" rx="5"/>
  <text x="800" y="650" text-anchor="middle" class="header" font-size="18">パラメータの意味</text>
  
  <text x="80" y="685" class="note" font-size="13"><tspan font-weight="bold">K（係数）の意味：</tspan></text>
  <text x="100" y="710" class="note" font-size="12">• エピ/ハイポサイクロイド系：尖点の数（転がる円の半径 = 固定円の半径 / k）</text>
  <text x="100" y="730" class="note" font-size="12">• リサージュ曲線：x方向の振動数（周波数比）</text>
  <text x="100" y="750" class="note" font-size="12">• 正葉曲線：花びらの基本数（奇数なら k 枚、偶数なら 2k 枚の花びら）</text>
  
  <text x="80" y="785" class="note" font-size="13"><tspan font-weight="bold">d（距離）の意味：</tspan></text>
  <text x="100" y="810" class="note" font-size="12">• トロコイド系：円の中心から追跡点までの距離（d = r で円周上、d ≠ r で円周外/内）</text>
  <text x="100" y="830" class="note" font-size="12">• リサージュ曲線：位相差 δ（0〜2π）</text>
  <text x="100" y="850" class="note" font-size="12">• その他：使用しない、または固定値</text>
</svg>
"""

# ---------------------------------------------------------
# 数学ロジッククラス（元のまま）
# ---------------------------------------------------------
class CurveMath:
    @staticmethod
    def get_point(curve_type, t, r, k, d):
        x, y = 0, 0
        
        if curve_type == "cycloid":
            x = r * (t - np.sin(t))
            y = r * (1 - np.cos(t))
        elif curve_type == "trochoid":
            x = r * t - d * np.sin(t)
            y = r - d * np.cos(t)
        elif curve_type == "cardioid":
            x = 2*r * np.cos(t) - r * np.cos(2*t)
            y = 2*r * np.sin(t) - r * np.sin(2*t)
        elif curve_type == "nephroid":
            R = r
            b = r / 2.0
            x = (R + b) * np.cos(t) - b * np.cos((R + b) / b * t)
            y = (R + b) * np.sin(t) - b * np.sin((R + b) / b * t)
        elif curve_type == "astroid":
            x = r * (np.cos(t) ** 3)
            y = r * (np.sin(t) ** 3)
        elif curve_type == "epicycloid":
            R = r
            r_small = r / k if k != 0 else 1
            x = (R + r_small) * np.cos(t) - r_small * np.cos((R + r_small) / r_small * t)
            y = (R + r_small) * np.sin(t) - r_small * np.sin((R + r_small) / r_small * t)
        elif curve_type == "epitrochoid":
            R = r
            r_small = r / k if k != 0 else 1
            x = (R + r_small) * np.cos(t) - d * np.cos((R + r_small) / r_small * t)
            y = (R + r_small) * np.sin(t) - d * np.sin((R + r_small) / r_small * t)
        elif curve_type == "hypocycloid":
            R = r
            r_small = r / k if k != 0 else 1
            x = (R - r_small) * np.cos(t) + r_small * np.cos((R - r_small) / r_small * t)
            y = (R - r_small) * np.sin(t) - r_small * np.sin((R - r_small) / r_small * t)
        elif curve_type == "hypotrochoid":
            R = r
            r_small = r / k if k != 0 else 1
            x = (R - r_small) * np.cos(t) + d * np.cos((R - r_small) / r_small * t)
            y = (R - r_small) * np.sin(t) - d * np.sin((R - r_small) / r_small * t)
        elif curve_type == "lissajous":
            freq_a = k
            freq_b = 3 
            delta = d 
            x = r * np.sin(freq_a * t + delta)
            y = r * np.sin(freq_b * t)
        elif curve_type == "rose":
            rad = r * np.cos(k * t)
            x = rad * np.cos(t)
            y = rad * np.sin(t)
            
        return x, y

    @staticmethod
    def get_auxiliary_data(curve_type, t, r, k, d):
        theta = np.linspace(0, 2*np.pi, 100)
        
        if curve_type in ["cycloid", "trochoid"]:
            fixed_x = np.linspace(-r, r * 4 * np.pi + r, 100)
            fixed_y = np.zeros_like(fixed_x)
            cx, cy = r * t, r
            roll_x = cx + r * np.cos(theta)
            roll_y = cy + r * np.sin(theta)
            return (fixed_x, fixed_y), (roll_x, roll_y), (cx, cy)
        elif curve_type in ["epicycloid", "cardioid", "nephroid", "epitrochoid"]:
            R = r
            if curve_type == "cardioid":
                r_small = r
            elif curve_type == "nephroid":
                r_small = r / 2.0
            else:
                r_small = r / k
            fixed_x = R * np.cos(theta)
            fixed_y = R * np.sin(theta)
            dist = R + r_small
            cx = dist * np.cos(t)
            cy = dist * np.sin(t)
            roll_x = cx + r_small * np.cos(theta)
            roll_y = cy + r_small * np.sin(theta)
            return (fixed_x, fixed_y), (roll_x, roll_y), (cx, cy)
        elif curve_type in ["hypocycloid", "astroid", "hypotrochoid"]:
            R = r
            if curve_type == "astroid":
                r_small = r / 4.0
            else:
                r_small = r / k
            fixed_x = R * np.cos(theta)
            fixed_y = R * np.sin(theta)
            dist = R - r_small
            cx = dist * np.cos(t)
            cy = dist * np.sin(t)
            roll_x = cx + r_small * np.cos(theta)
            roll_y = cy + r_small * np.sin(theta)
            return (fixed_x, fixed_y), (roll_x, roll_y), (cx, cy)
        return None, None, None

    @staticmethod
    def get_max_t(curve_type, k):
        if curve_type in ["cycloid", "trochoid"]: 
            return 4 * np.pi 
        elif curve_type in ["epicycloid", "epitrochoid", "hypocycloid", "hypotrochoid"]:
            return 2 * np.pi * k
        elif curve_type == "rose": 
            return 2 * np.pi if k % 2 != 0 else 2 * np.pi 
        return 2 * np.pi

    @staticmethod
    def calculate_stats(curve_type, r, k, d, max_t):
        steps = 1000
        t_vals = np.linspace(0, max_t, steps)
        xs = []
        ys = []
        for t in t_vals:
            x, y = CurveMath.get_point(curve_type, t, r, k, d)
            xs.append(x)
            ys.append(y)
        xs = np.array(xs)
        ys = np.array(ys)
        dx = np.diff(xs)
        dy = np.diff(ys)
        length = np.sum(np.sqrt(dx**2 + dy**2))
        area = 0.5 * np.abs(np.sum(xs[:-1] * ys[1:] - xs[1:] * ys[:-1]))
        return length, area

# ---------------------------------------------------------
# 練習問題データ（元のまま）
# ---------------------------------------------------------
print("数式画像を生成中...お待ちください...")

EXERCISE_DATA = {
    0: {
        "title": "【第1問】サイクロイドの長さ（基本）",
        "question": """
            <p>次の媒介変数表示された曲線の長さ {} を求めよ。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
        """.format(
            latex_to_html("L"),
            latex_to_html(r"x = r(t - \sin t)"),
            latex_to_html(r"y = r(1 - \cos t)"),
            latex_to_html(r"(0 \leqq t \leqq 2\pi, \ r > 0)")
        ),
        "answer": """
            <p><b>【解答】</b></p>
            <p>まず微分を計算します。</p>
            <div align='center'>
            {}
            </div>
            <p>ルートの中身を計算して整理します。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
            <p>半角の公式 {} を利用します。</p>
            <div align='center'>
            {}
            </div>
            <p>よって、積分を実行します（{} で {}）。</p>
            <div align='center'>
            {}<br>{}<br>{}<br>{}
            </div>
            <p><b>答：{}</b></p>
        """.format(
            latex_to_html(r"\frac{dx}{dt} = r(1 - \cos t), \quad \frac{dy}{dt} = r \sin t"),
            latex_to_html(r"\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2 = r^2(1 - \cos t)^2 + r^2 \sin^2 t"),
            latex_to_html(r"= r^2(1 - 2\cos t + \cos^2 t + \sin^2 t)"),
            latex_to_html(r"= 2r^2(1 - \cos t)"),
            latex_to_html(r"1 - \cos t = 2\sin^2 \frac{t}{2}"),
            latex_to_html(r"= 4r^2 \sin^2 \frac{t}{2}"),
            latex_to_html(r"0 \leqq t \leqq 2\pi"),
            latex_to_html(r"\sin \frac{t}{2} \geqq 0"),
            latex_to_html(r"L = \int_{0}^{2\pi} 2r \sin \frac{t}{2} dt"),
            latex_to_html(r"= 2r \left[ -2\cos \frac{t}{2} \right]_{0}^{2\pi}"),
            latex_to_html(r"= -4r (\cos \pi - \cos 0)"),
            latex_to_html(r"= -4r (-1 - 1)"),
            latex_to_html(r"L = 8r")
        )
    },
    1: {
        "title": "【第2問】アステロイドの長さ（標準）",
        "question": """
            <p>次の媒介変数表示された曲線の長さ {} を求めよ。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
        """.format(
            latex_to_html("L"),
            latex_to_html(r"x = a \cos^3 t"),
            latex_to_html(r"y = a \sin^3 t"),
            latex_to_html(r"(0 \leqq t \leqq 2\pi, \ a > 0)")
        ),
        "answer": """
            <p><b>【解答】</b></p>
            <p>微分を計算します。</p>
            <div align='center'>
            {}<br>{}
            </div>
            <p>ルートの中身を計算します。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
            <p>対称性を利用し、第一象限 {} を4倍します。</p>
            <div align='center'>
            {}<br>{}<br>{}<br>{}
            </div>
            <p><b>答：{}</b></p>
        """.format(
            latex_to_html(r"\frac{dx}{dt} = -3a \cos^2 t \sin t"),
            latex_to_html(r"\frac{dy}{dt} = 3a \sin^2 t \cos t"),
            latex_to_html(r"\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2 = 9a^2 \cos^4 t \sin^2 t + 9a^2 \sin^4 t \cos^2 t"),
            latex_to_html(r"= 9a^2 \sin^2 t \cos^2 t"),
            latex_to_html(r"= \frac{9}{4}a^2 \sin^2 2t"),
            latex_to_html(r"(0 \leqq t \leqq \frac{\pi}{2})"),
            latex_to_html(r"L = 4 \int_{0}^{\frac{\pi}{2}} \frac{3}{2}a \sin 2t dt"),
            latex_to_html(r"= 6a \int_{0}^{\frac{\pi}{2}} \sin 2t dt"),
            latex_to_html(r"= 6a \left[ -\frac{1}{2} \cos 2t \right]_{0}^{\frac{\pi}{2}}"),
            latex_to_html(r"= -3a(\cos \pi - \cos 0)"),
            latex_to_html(r"L = 6a")
        )
    },
    2: {
        "title": "【第3問】カージオイドの長さ（応用）",
        "question": """
            <p>次の媒介変数表示された曲線の長さ {} を求めよ。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
        """.format(
            latex_to_html("L"),
            latex_to_html(r"x = 2r \cos t - r \cos 2t"),
            latex_to_html(r"y = 2r \sin t - r \sin 2t"),
            latex_to_html(r"(0 \leqq t \leqq 2\pi, \ r > 0)")
        ),
        "answer": """
            <p><b>【解答】</b></p>
            <p>微分を計算します。</p>
            <div align='center'>
            {}<br>{}
            </div>
            <p>ルートの中身を計算します（加法定理 {} を使用）。</p>
            <div align='center'>
            {}<br>{}<br>{}<br>{}
            </div>
            <p>半角の公式 {} を利用します。</p>
            <div align='center'>
            {}
            </div>
            <p>積分を実行します。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
            <p><b>答：{}</b></p>
        """.format(
            latex_to_html(r"\frac{dx}{dt} = -2r \sin t + 2r \sin 2t"),
            latex_to_html(r"\frac{dy}{dt} = 2r \cos t - 2r \cos 2t"),
            latex_to_html(r"\cos(A-B)"),
            latex_to_html(r"\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2"),
            latex_to_html(r"= 4r^2(\sin^2 t - 2\sin t \sin 2t + \sin^2 2t)"),
            latex_to_html(r"+ 4r^2(\cos^2 t - 2\cos t \cos 2t + \cos^2 2t)"),
            latex_to_html(r"= 8r^2(1 - \cos t)"),
            latex_to_html(r"1 - \cos t = 2\sin^2 \frac{t}{2}"),
            latex_to_html(r"= 16r^2 \sin^2 \frac{t}{2}"),
            latex_to_html(r"L = \int_{0}^{2\pi} 4r \sin \frac{t}{2} dt"),
            latex_to_html(r"= 4r \left[ -2\cos \frac{t}{2} \right]_{0}^{2\pi}"),
            latex_to_html(r"= -8r(-1-1)"),
            latex_to_html(r"L = 16r")
        )
    },
    3: {
        "title": "【第4問】ネフロイドの長さ（発展）",
        "question": """
            <p>次の媒介変数表示された曲線の長さ {} を求めよ。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
        """.format(
            latex_to_html("L"),
            latex_to_html(r"x = 3a \cos t - a \cos 3t"),
            latex_to_html(r"y = 3a \sin t - a \sin 3t"),
            latex_to_html(r"(0 \leqq t \leqq 2\pi, \ a > 0)")
        ),
        "answer": """
            <p><b>【解答】</b></p>
            <p>微分を計算します。</p>
            <div align='center'>
            {}<br>{}
            </div>
            <p>ルートの中身を整理します（加法定理を使用）。</p>
            <div align='center'>
            {}<br>{}<br>{}
            </div>
            <p>半角の公式 {} を利用します。</p>
            <div align='center'>
            {}
            </div>
            <p>絶対値に注意して積分します（{} を2倍）。</p>
            <div align='center'>
            {}<br>{}<br>{}<br>{}
            </div>
            <p><b>答：{}</b></p>
        """.format(
            latex_to_html(r"\frac{dx}{dt} = -3a \sin t + 3a \sin 3t"),
            latex_to_html(r"\frac{dy}{dt} = 3a \cos t - 3a \cos 3t"),
            latex_to_html(r"\left(\frac{dx}{dt}\right)^2 + \left(\frac{dy}{dt}\right)^2"),
            latex_to_html(r"= 9a^2(2 - 2(\cos 3t \cos t + \sin 3t \sin t))"),
            latex_to_html(r"= 18a^2(1 - \cos 2t)"),
            latex_to_html(r"1 - \cos 2t = 2\sin^2 t"),
            latex_to_html(r"= 36a^2 \sin^2 t"),
            latex_to_html(r"0 \leqq t \leqq \pi"),
            latex_to_html(r"L = 2 \int_{0}^{\pi} 6a \sin t dt"),
            latex_to_html(r"= 12a \left[ -\cos t \right]_{0}^{\pi}"),
            latex_to_html(r"= -12a(-1-1)"),
            latex_to_html(r"= 24a"),
            latex_to_html(r"L = 24a")
        )
    },
    4: {
        "title": "【第5問】トロコイドの性質（理論）",
        "question": """
            <p>半径 {} の円が直線上を転がるとき、円の中心から距離 {} の点が描く曲線（トロコイド）について考える。</p>
            <p>(1) {} のとき、曲線はどのような特徴を持つか説明せよ。</p>
            <p>(2) {} のとき、曲線はどのような特徴を持つか説明せよ。</p>
        """.format(
            latex_to_html("r"),
            latex_to_html("d"),
            latex_to_html("d = r"),
            latex_to_html("d > r")
        ),
        "answer": """
            <p><b>【解答】</b></p>
            <p><b>(1) {} の場合：</b></p>
            <p>これは通常のサイクロイドになります。曲線は尖点（カスプ）を持ち、最速降下線の性質を持ちます。</p>
            <p><b>(2) {} の場合：</b></p>
            <p>曲線は波打つ形状になり、ループを持ちます。追跡点が円周より外側にあるため、円が転がるときに一時的に後退する動きが生じ、これがループを形成します。</p>
            <p>一般に、トロコイドの媒介変数表示は：</p>
            <div align='center'>
            {}<br>{}
            </div>
            <p>で与えられます。{} のとき、曲線は {} 軸と交差します。</p>
        """.format(
            latex_to_html("d = r"),
            latex_to_html("d > r"),
            latex_to_html(r"x = rt - d\sin t"),
            latex_to_html(r"y = r - d\cos t"),
            latex_to_html("d > r"),
            latex_to_html("x")
        )
    },
    5: {
        "title": "【第6問】ハイポサイクロイドの特殊例（挑戦）",
        "question": """
            <p>半径 {} の固定円の内側を、半径 {} の円が転がるとき、転がる円周上の点が描く曲線について：</p>
            <p>(1) {} のとき、曲線の名称と特徴を述べよ。</p>
            <p>(2) {} のとき、曲線の名称を述べよ。</p>
            <p>(3) 一般に {} のとき、曲線は何個の尖点を持つか答えよ。</p>
        """.format(
            latex_to_html("R"),
            latex_to_html("r"),
            latex_to_html("R = 4r"),
            latex_to_html("R = 3r"),
            latex_to_html("R = kr")
        ),
        "answer": """
            <p><b>【解答】</b></p>
            <p><b>(1) {} の場合：</b></p>
            <p>これはアステロイド（星形）と呼ばれる曲線です。4つの尖点を持ち、方程式は：</p>
            <div align='center'>
            {}<br>{}
            </div>
            <p>または {} で表されます。</p>
            <p><b>(2) {} の場合：</b></p>
            <p>これはデルトイド（三角形風）と呼ばれる曲線です。3つの尖点を持ちます。</p>
            <p><b>(3) 一般の場合：</b></p>
            <p>ハイポサイクロイドは {} 個の尖点を持ちます。これは転がる円が固定円の内側を {} 周して元の位置に戻るためです。</p>
        """.format(
            latex_to_html("R = 4r"),
            latex_to_html(r"x = a\cos^3 t"),
            latex_to_html(r"y = a\sin^3 t"),
            latex_to_html(r"x^{2/3} + y^{2/3} = a^{2/3}"),
            latex_to_html("R = 3r"),
            latex_to_html("k"),
            latex_to_html("k")
        )
    }
}

# ---------------------------------------------------------
# UI メインウィンドウ
# ---------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("トロコイド系曲線ビューアー / Trochoid Family Curves Viewer")
        self.resize(1400, 950)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.tab_viewer = QWidget()
        self.init_viewer_ui()
        self.tabs.addTab(self.tab_viewer, "曲線ビューアー")
        
        self.tab_tree = QWidget()
        self.init_tree_ui()
        self.tabs.addTab(self.tab_tree, "分類図")
        
        self.tab_exercise = QWidget()
        self.init_exercise_ui()
        self.tabs.addTab(self.tab_exercise, "練習問題 (数学Ⅲ)")
        
        self.timer = QTimer()
        self.timer.setInterval(20) 
        self.timer.timeout.connect(self.update_animation)
        
        self.update_description()
        self.reset()

    def init_tree_ui(self):
        layout = QVBoxLayout(self.tab_tree)
        
        title = QLabel("トロコイド系曲線の分類体系")
        title.setFont(QFont(FONT_NAME, 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        svg_widget = QSvgWidget()
        svg_widget.load(CLASSIFICATION_SVG.encode())
        svg_widget.setMinimumSize(1600, 900)
        
        scroll.setWidget(svg_widget)
        layout.addWidget(scroll)

    def init_viewer_ui(self):
        self.curve_type = "cycloid"
        self.radius = 50
        self.k_val = 3.0
        self.d_val = 50.0
        self.speed = 5
        self.t_current = 0.0
        self.is_playing = False
        self.show_aux = True 
        
        layout = QHBoxLayout(self.tab_viewer)
        
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setFixedWidth(480)
        
        title_label = QLabel("曲線設定")
        title_label.setFont(QFont(FONT_NAME, 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(title_label)
        
        grp_select = QGroupBox("曲線の種類")
        l_select = QVBoxLayout()
        self.combo_curve = QComboBox()
        self.combo_curve.addItems([
            "サイクロイド", "トロコイド",
            "カージオイド", "ネフロイド", 
            "アステロイド", 
            "エピサイクロイド", "エピトロコイド",
            "ハイポサイクロイド", "ハイポトロコイド",
            "リサージュ曲線", "正葉曲線"
        ])
        self.combo_curve.currentIndexChanged.connect(self.on_curve_change)
        l_select.addWidget(self.combo_curve)
        grp_select.setLayout(l_select)
        control_layout.addWidget(grp_select)
        
        # 数式表示エリア（新規追加）
        grp_formula = QGroupBox("媒介変数方程式")
        l_formula = QVBoxLayout()
        self.text_formula = QTextEdit()
        self.text_formula.setReadOnly(True)
        self.text_formula.setMaximumHeight(100)
        self.text_formula.setStyleSheet(
            "background-color: #f0f8ff; "
            "border: 2px solid #4682b4; "
            "padding: 8px; "
            "font-family: 'Courier New', monospace; "
            "font-size: 11pt;"
        )
        l_formula.addWidget(self.text_formula)
        grp_formula.setLayout(l_formula)
        control_layout.addWidget(grp_formula)
        
        grp_params = QGroupBox("パラメータ設定")
        l_params = QVBoxLayout()
        
        self.lbl_radius = QLabel(f"半径 R: {self.radius}")
        self.slider_radius = QSlider(Qt.Horizontal)
        self.slider_radius.setRange(10, 100)
        self.slider_radius.setValue(self.radius)
        self.slider_radius.valueChanged.connect(self.on_radius_change)
        l_params.addWidget(self.lbl_radius)
        l_params.addWidget(self.slider_radius)
        
        self.lbl_k = QLabel(f"係数 K: {self.k_val}")
        self.slider_k = QSlider(Qt.Horizontal)
        self.slider_k.setRange(1, 10)
        self.slider_k.setValue(int(self.k_val))
        self.slider_k.valueChanged.connect(self.on_k_change)
        l_params.addWidget(self.lbl_k)
        l_params.addWidget(self.slider_k)
        
        # K の意味表示（新規追加）
        self.lbl_k_meaning = QLabel("💡 K: 使用しません")
        self.lbl_k_meaning.setStyleSheet(
            "color: #666; "
            "font-size: 10pt; "
            "padding: 5px; "
            "background-color: #fff3cd; "
            "border-radius: 3px;"
        )
        self.lbl_k_meaning.setWordWrap(True)
        l_params.addWidget(self.lbl_k_meaning)
        
        self.lbl_d = QLabel(f"追跡点の距離 d: {self.d_val}")
        self.slider_d = QSlider(Qt.Horizontal)
        self.slider_d.setRange(10, 150)
        self.slider_d.setValue(int(self.d_val))
        self.slider_d.valueChanged.connect(self.on_d_change)
        l_params.addWidget(self.lbl_d)
        l_params.addWidget(self.slider_d)
        
        # d の意味表示（新規追加）
        self.lbl_d_meaning = QLabel("💡 d: 使用しません")
        self.lbl_d_meaning.setStyleSheet(
            "color: #666; "
            "font-size: 10pt; "
            "padding: 5px; "
            "background-color: #d1ecf1; "
            "border-radius: 3px;"
        )
        self.lbl_d_meaning.setWordWrap(True)
        l_params.addWidget(self.lbl_d_meaning)

        self.lbl_speed = QLabel(f"描画速度: {self.speed}")
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(1, 20)
        self.slider_speed.setValue(self.speed)
        self.slider_speed.valueChanged.connect(self.on_speed_change)
        l_params.addWidget(self.lbl_speed)
        l_params.addWidget(self.slider_speed)
        
        grp_params.setLayout(l_params)
        control_layout.addWidget(grp_params)
        
        grp_view = QGroupBox("表示オプション")
        l_view = QVBoxLayout()
        self.chk_aux = QCheckBox("補助円を表示する")
        self.chk_aux.setChecked(True)
        self.chk_aux.toggled.connect(self.on_aux_toggle)
        l_view.addWidget(self.chk_aux)
        grp_view.setLayout(l_view)
        control_layout.addWidget(grp_view)
        
        l_btns = QHBoxLayout()
        self.btn_play = QPushButton("▶ 再生")
        self.btn_play.setFixedHeight(40)
        self.btn_play.clicked.connect(self.toggle_play)
        self.btn_reset = QPushButton("リセット")
        self.btn_reset.setFixedHeight(40)
        self.btn_reset.clicked.connect(self.reset)
        l_btns.addWidget(self.btn_play)
        l_btns.addWidget(self.btn_reset)
        control_layout.addLayout(l_btns)
        
        grp_stats = QGroupBox("統計情報")
        l_stats = QVBoxLayout()
        self.lbl_length = QLabel("曲線の長さ: 0.00")
        self.lbl_area = QLabel("囲まれる面積: 0.00")
        self.lbl_t = QLabel("パラメータ t: 0.00")
        l_stats.addWidget(self.lbl_t)
        l_stats.addWidget(self.lbl_length)
        l_stats.addWidget(self.lbl_area)
        grp_stats.setLayout(l_stats)
        control_layout.addWidget(grp_stats)
        
        # 説明エリア（スクロール対応）
        scroll_desc = QScrollArea()
        scroll_desc.setWidgetResizable(True)
        self.text_desc = QTextEdit()
        self.text_desc.setReadOnly(True)
        self.text_desc.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc; padding: 8px;")
        scroll_desc.setWidget(self.text_desc)
        control_layout.addWidget(scroll_desc)
        
        layout.addWidget(control_panel)
        
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle=':', alpha=0.6)
        
        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='軌跡')
        self.point, = self.ax.plot([], [], 'ro', zorder=5, markersize=6, label='現在の点')
        self.aux_fixed, = self.ax.plot([], [], 'k--', linewidth=1, alpha=0.5, label='固定円/線') 
        self.aux_rolling, = self.ax.plot([], [], 'g--', linewidth=1, alpha=0.7, label='転がる円') 
        self.aux_arm, = self.ax.plot([], [], 'g-', linewidth=1, alpha=0.7) 
        self.ax.legend(loc='upper right', fontsize='small')
        layout.addWidget(self.canvas, stretch=1)

    def init_exercise_ui(self):
        layout = QVBoxLayout(self.tab_exercise)
        
        top_bar = QHBoxLayout()
        lbl_sel = QLabel("問題を選択:")
        self.combo_ex = QComboBox()
        self.combo_ex.addItems([
            "第1問: サイクロイドの長さ（基本）",
            "第2問: アステロイドの長さ（標準）",
            "第3問: カージオイドの長さ（応用）",
            "第4問: ネフロイドの長さ（発展）",
            "第5問: トロコイドの性質（理論）",
            "第6問: ハイポサイクロイドの特殊例（挑戦）"
        ])
        self.combo_ex.currentIndexChanged.connect(self.load_exercise)
        top_bar.addWidget(lbl_sel)
        top_bar.addWidget(self.combo_ex)
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        self.ex_title = QLabel("タイトル")
        self.ex_title.setFont(QFont(FONT_NAME, 14, QFont.Bold))
        layout.addWidget(self.ex_title)
        
        scroll_q = QScrollArea()
        scroll_q.setWidgetResizable(True)
        self.ex_question = QTextEdit()
        self.ex_question.setReadOnly(True)
        self.ex_question.setStyleSheet("background-color: #eef; font-size: 14px; padding: 10px;")
        scroll_q.setWidget(self.ex_question)
        scroll_q.setMaximumHeight(250)
        layout.addWidget(scroll_q)
        
        self.btn_show_ans = QPushButton("解答・解説を表示")
        self.btn_show_ans.setCheckable(True)
        self.btn_show_ans.clicked.connect(self.toggle_answer)
        layout.addWidget(self.btn_show_ans)
        
        scroll_a = QScrollArea()
        scroll_a.setWidgetResizable(True)
        self.ex_answer = QTextEdit()
        self.ex_answer.setReadOnly(True)
        self.ex_answer.setStyleSheet("background-color: #fff; font-size: 14px; padding: 10px;")
        scroll_a.setWidget(self.ex_answer)
        self.ex_answer.setVisible(False)
        layout.addWidget(scroll_a)
        
        self.load_exercise(0)

    def load_exercise(self, index):
        data = EXERCISE_DATA[index]
        self.ex_title.setText(data["title"])
        self.ex_question.setHtml(data["question"])
        self.ex_answer.setHtml(data["answer"])
        self.btn_show_ans.setChecked(False)
        self.btn_show_ans.setText("解答・解説を表示")
        self.ex_answer.setVisible(False)

    def toggle_answer(self):
        if self.btn_show_ans.isChecked():
            self.ex_answer.setVisible(True)
            self.btn_show_ans.setText("解答・解説を隠す")
        else:
            self.ex_answer.setVisible(False)
            self.btn_show_ans.setText("解答・解説を表示")

    def on_curve_change(self, index):
        keys = ["cycloid", "trochoid", "cardioid", "nephroid", "astroid", 
                "epicycloid", "epitrochoid", "hypocycloid", "hypotrochoid",
                "lissajous", "rose"]
        self.curve_type = keys[index]
        self.update_description()
        self.update_parameter_meanings()
        self.reset()
        
    def on_radius_change(self, value):
        self.radius = value
        self.lbl_radius.setText(f"半径 R: {self.radius}")
        if not self.is_playing: self.draw_static()

    def on_k_change(self, value):
        self.k_val = float(value)
        self.lbl_k.setText(f"係数 K: {self.k_val}")
        if not self.is_playing: self.draw_static()
        
    def on_d_change(self, value):
        self.d_val = float(value)
        self.lbl_d.setText(f"追跡点の距離 d: {self.d_val}")
        if not self.is_playing: self.draw_static()
            
    def on_speed_change(self, value):
        self.speed = value
        self.lbl_speed.setText(f"描画速度: {self.speed}")
        
    def on_aux_toggle(self, checked):
        self.show_aux = checked
        if not self.is_playing: self.draw_static()

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.btn_play.setText("⏸ 一時停止")
            self.timer.start()
        else:
            self.btn_play.setText("▶ 再生")
            self.timer.stop()
            
    def reset(self):
        self.is_playing = False
        self.timer.stop()
        self.btn_play.setText("▶ 再生")
        self.t_current = 0.0
        self.draw_static()
        
    def update_animation(self):
        max_t = CurveMath.get_max_t(self.curve_type, self.k_val)
        dt = 0.01 * (self.speed / 5.0)
        self.t_current += dt
        if self.t_current > max_t:
            self.t_current = max_t
            self.toggle_play() 
        self.update_plot(self.t_current)
        
    def draw_static(self):
        self.update_plot(self.t_current)
        
    def update_plot(self, current_t):
        t_vals = np.linspace(0, current_t, int(current_t * 50) + 10)
        xs = []
        ys = []
        for t in t_vals:
            x, y = CurveMath.get_point(self.curve_type, t, self.radius, self.k_val, self.d_val)
            xs.append(x)
            ys.append(y)
        self.line.set_data(xs, ys)
        
        cx, cy = CurveMath.get_point(self.curve_type, current_t, self.radius, self.k_val, self.d_val)
        self.point.set_data([cx], [cy])
        
        if self.show_aux:
            fixed_data, roll_data, center_data = CurveMath.get_auxiliary_data(
                self.curve_type, current_t, self.radius, self.k_val, self.d_val
            )
            if fixed_data is not None:
                self.aux_fixed.set_data(fixed_data[0], fixed_data[1])
                self.aux_rolling.set_data(roll_data[0], roll_data[1])
                self.aux_arm.set_data([center_data[0], cx], [center_data[1], cy])
                self.aux_fixed.set_visible(True)
                self.aux_rolling.set_visible(True)
                self.aux_arm.set_visible(True)
            else:
                self.aux_fixed.set_visible(False)
                self.aux_rolling.set_visible(False)
                self.aux_arm.set_visible(False)
        else:
            self.aux_fixed.set_visible(False)
            self.aux_rolling.set_visible(False)
            self.aux_arm.set_visible(False)
        
        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.margins(0.1)
        self.canvas.draw_idle()
        
        max_t_for_calc = CurveMath.get_max_t(self.curve_type, self.k_val)
        length, area = CurveMath.calculate_stats(self.curve_type, self.radius, self.k_val, self.d_val, max_t_for_calc)
        deg_current = np.degrees(current_t)
        
        self.lbl_length.setText(f"曲線の長さ: {length:.2f}")
        self.lbl_area.setText(f"囲まれる面積: {area:.2f}")
        self.lbl_t.setText(f"パラメータ t: {current_t:.2f} ({deg_current:.1f}°) / {max_t_for_calc:.2f}")

    def update_parameter_meanings(self):
        """K と d パラメータの意味を更新"""
        curve_def = CURVE_DEFINITIONS.get(self.curve_type, {})
        k_meaning = curve_def.get("k_meaning", "K: 使用しません")
        d_meaning = curve_def.get("d_meaning", "d: 使用しません")
        
        self.lbl_k_meaning.setText(f"💡 {k_meaning}")
        self.lbl_d_meaning.setText(f"💡 {d_meaning}")

    def update_description(self):
        """曲線の説明と数式を更新"""
        curve_def = CURVE_DEFINITIONS.get(self.curve_type, {})
        
        # 数式表示
        formulas = curve_def.get("formulas", [])
        formula_html = "<br>".join([f"<b style='font-size: 12pt;'>{f}</b>" for f in formulas])
        self.text_formula.setHtml(f"<div style='text-align: center; padding: 5px;'>{formula_html}</div>")
        
        # 説明文
        name = curve_def.get("name", "")
        desc = curve_def.get("description", "")
        props = curve_def.get("properties", [])
        
        html = f"""
        <h2 style='color: #2c3e50;'>{name}</h2>
        <p style='font-size: 11pt; line-height: 1.6;'>{desc}</p>
        <h3 style='color: #34495e;'>主な特性:</h3>
        <ul style='font-size: 10pt; line-height: 1.8;'>
        """
        for prop in props:
            html += f"<li>{prop}</li>"
        html += "</ul>"
        
        self.text_desc.setHtml(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())