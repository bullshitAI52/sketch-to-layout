"""
==============================================
  香蕉模型 草图 → 布局图   API 配置文件
==============================================
请在下方填写你的 API Key，支持多种服务商。
"""

# ── 选择使用的 API 服务商 ──────────────────────────────────────────────
# 可选值: "replicate" | "stability" | "openai"
PROVIDER = "replicate"

# ── Replicate (推荐, 支持 ControlNet + Stable Diffusion) ──────────────
# 获取 Key: https://replicate.com/account/api-tokens
REPLICATE_API_TOKEN = "r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ControlNet 模型 (默认用 canny 边缘检测, 适合草图)
REPLICATE_MODEL = "jagilley/controlnet-canny:aff48af9c68d162388d230a2ab003f68d2638d88ceded942fd87cae9b9765c42"

# ── Stability AI ──────────────────────────────────────────────────────
# 获取 Key: https://platform.stability.ai/account/keys
STABILITY_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
STABILITY_ENGINE  = "stable-diffusion-xl-1024-v1-0"

# ── OpenAI (DALL-E 3) ─────────────────────────────────────────────────
# 获取 Key: https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# ── 通用生成参数 ───────────────────────────────────────────────────────
DEFAULT_STEPS   = 30
DEFAULT_CFG     = 7.5
IMAGE_SIZE      = 1024   # 输出图像边长 (像素)

# ── Flask 服务设置 ────────────────────────────────────────────────────
FLASK_HOST      = "127.0.0.1"
FLASK_PORT      = 5050
FLASK_DEBUG     = False
UPLOAD_FOLDER   = "uploads"
OUTPUT_FOLDER   = "outputs"
MAX_CONTENT_MB  = 20
