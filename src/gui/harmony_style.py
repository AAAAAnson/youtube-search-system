"""
鸿蒙 UI 风格规范
HarmonyOS Design Style Guide
参考：https://pixso.cn/community/file/36K86pnjsLzOIwR1N195AQ
"""

# ============ 配色体系 ============

class HarmonyColors:
    """鸿蒙配色规范"""

    # 主色调（品牌色）
    PRIMARY = "#007DFF"  # 鸿蒙蓝
    PRIMARY_HOVER = "#0061D5"  # 悬停态
    PRIMARY_PRESSED = "#0051B8"  # 按下态
    PRIMARY_LIGHT = "#E6F2FF"  # 浅色背景

    # 成功色
    SUCCESS = "#00C853"  # 鸿蒙绿
    SUCCESS_HOVER = "#00A344"
    SUCCESS_LIGHT = "#E8F5E9"

    # 警告色
    WARNING = "#FF9500"  # 鸿蒙橙
    WARNING_HOVER = "#E68600"
    WARNING_LIGHT = "#FFF3E0"

    # 错误色
    ERROR = "#FA2A2D"  # 鸿蒙红
    ERROR_HOVER = "#D81B1F"
    ERROR_LIGHT = "#FFEBEE"

    # 中性色（文字颜色）
    TEXT_PRIMARY = "#1A1A1A"  # 主要文字
    TEXT_SECONDARY = "#666666"  # 次要文字
    TEXT_TERTIARY = "#999999"  # 辅助文字
    TEXT_DISABLED = "#CCCCCC"  # 禁用文字

    # 背景色
    BG_PRIMARY = "#FFFFFF"  # 主背景（卡片）
    BG_SECONDARY = "#FAFBFC"  # 次背景（页面）
    BG_TERTIARY = "#F1F3F5"  # 三级背景
    BG_HOVER = "#F5F5F5"  # 悬停背景

    # 边框色
    BORDER_LIGHT = "#E5E5E5"  # 浅边框
    BORDER_DEFAULT = "#D9D9D9"  # 默认边框
    BORDER_DARK = "#BFBFBF"  # 深边框

    # 分割线
    DIVIDER = "#EEEEEE"

    # 阴影色
    SHADOW = "rgba(0, 0, 0, 0.08)"
    SHADOW_HOVER = "rgba(0, 0, 0, 0.12)"


# ============ 圆角规范 ============

class HarmonyRadius:
    """鸿蒙圆角规范"""
    SMALL = 6  # 小圆角：复选框、标签
    MEDIUM = 12  # 中圆角：按钮、输入框
    LARGE = 16  # 大圆角：卡片
    XLARGE = 20  # 超大圆角：主容器


# ============ 间距规范 ============

class HarmonySpacing:
    """鸿蒙间距规范（基于 4px 网格）"""
    XS = 4    # 超小间距
    SM = 8    # 小间距
    MD = 16   # 中间距
    LG = 24   # 大间距
    XL = 32   # 超大间距
    XXL = 48  # 超超大间距


# ============ 字体规范 ============

class HarmonyFonts:
    """鸿蒙字体规范"""

    # 字体族
    FAMILY = "HarmonyOS Sans SC"  # 优先使用鸿蒙字体
    FAMILY_FALLBACK = "Microsoft YaHei UI"  # 降级方案

    # 字号
    SIZE_DISPLAY = 24  # 展示型标题
    SIZE_H1 = 18  # 一级标题
    SIZE_H2 = 16  # 二级标题
    SIZE_H3 = 14  # 三级标题
    SIZE_BODY = 14  # 正文
    SIZE_CAPTION = 12  # 辅助文字
    SIZE_SMALL = 10  # 小号文字

    # 字重
    WEIGHT_REGULAR = "normal"
    WEIGHT_MEDIUM = "bold"
    WEIGHT_BOLD = "bold"


# ============ 组件尺寸规范 ============

class HarmonySizes:
    """鸿蒙组件尺寸规范"""

    # 按钮高度
    BUTTON_SMALL = 28
    BUTTON_MEDIUM = 36
    BUTTON_LARGE = 44

    # 输入框高度
    INPUT_HEIGHT = 40

    # 图标尺寸
    ICON_SMALL = 16
    ICON_MEDIUM = 20
    ICON_LARGE = 24


# ============ 动画时长 ============

class HarmonyAnimation:
    """鸿蒙动画时长规范（毫秒）"""
    FAST = 100
    NORMAL = 200
    SLOW = 300


# ============ 预设样式 ============

class HarmonyPresets:
    """鸿蒙预设样式组合"""

    @staticmethod
    def card_shadow():
        """卡片阴影"""
        return "0px 2px 8px rgba(0, 0, 0, 0.08)"

    @staticmethod
    def card_hover_shadow():
        """卡片悬停阴影"""
        return "0px 4px 16px rgba(0, 0, 0, 0.12)"

    @staticmethod
    def primary_button():
        """主按钮样式"""
        return {
            "fg_color": HarmonyColors.PRIMARY,
            "hover_color": HarmonyColors.PRIMARY_HOVER,
            "corner_radius": HarmonyRadius.MEDIUM,
            "border_width": 0,
            "text_color": "#FFFFFF",
        }

    @staticmethod
    def secondary_button():
        """次按钮样式"""
        return {
            "fg_color": "transparent",
            "hover_color": HarmonyColors.BG_HOVER,
            "corner_radius": HarmonyRadius.MEDIUM,
            "border_width": 1,
            "border_color": HarmonyColors.BORDER_DEFAULT,
            "text_color": HarmonyColors.TEXT_PRIMARY,
        }

    @staticmethod
    def success_button():
        """成功按钮样式"""
        return {
            "fg_color": HarmonyColors.SUCCESS,
            "hover_color": HarmonyColors.SUCCESS_HOVER,
            "corner_radius": HarmonyRadius.MEDIUM,
            "border_width": 0,
            "text_color": "#FFFFFF",
        }

    @staticmethod
    def input_field():
        """输入框样式"""
        return {
            "corner_radius": HarmonyRadius.MEDIUM,
            "border_width": 1,
            "border_color": HarmonyColors.BORDER_LIGHT,
            "fg_color": HarmonyColors.BG_PRIMARY,
        }

    @staticmethod
    def card_frame():
        """卡片框架样式"""
        return {
            "corner_radius": HarmonyRadius.LARGE,
            "fg_color": HarmonyColors.BG_PRIMARY,
            "border_width": 0,
        }
