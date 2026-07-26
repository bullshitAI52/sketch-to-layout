"""
香蕉模型  草图 → 布局图  ——  Flask 主后端
"""
import os, uuid, base64, io, json, traceback
from pathlib import Path

from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image, ImageFilter, ImageEnhance

import config

# ── 初始化 ───────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_MB * 1024 * 1024

UPLOAD_DIR = Path(config.UPLOAD_FOLDER)
OUTPUT_DIR = Path(config.OUTPUT_FOLDER)
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

STYLE_MAP = {
    "modern":    "modern minimalist interior design floor plan, clean lines, white tones",
    "luxury":    "luxury residential apartment floor plan, rich warm tones, elegant furnishing",
    "office":    "commercial office space floor plan, open layout, professional business style",
    "garden":    "landscape garden design top view, green tones, plants and pathways",
    "industrial":"industrial loft style floor plan, exposed brick, raw concrete tones",
}

# ── 工具函数 ─────────────────────────────────────────────────────────
def preprocess(img: Image.Image) -> Image.Image:
    """ 草图预处理：转灰度 → 锐化 → 增强对比度，便于 AI 识别 """
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2.0)
    return img.convert("RGB")

def img_to_b64(img: Image.Image, fmt="PNG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode()

def b64_to_img(b64: str) -> Image.Image:
    data = base64.b64decode(b64)
    return Image.open(io.BytesIO(data))

# ── API 调用层 ───────────────────────────────────────────────────────
def call_replicate(processed_img: Image.Image, prompt: str) -> Image.Image:
    import replicate
    os.environ["REPLICATE_API_TOKEN"] = config.REPLICATE_API_TOKEN
    img_b64 = img_to_b64(processed_img)
    output = replicate.run(
        config.REPLICATE_MODEL,
        input={
            "image": f"data:image/png;base64,{img_b64}",
            "prompt": prompt,
            "num_samples": 1,
            "num_inference_steps": config.DEFAULT_STEPS,
            "guidance_scale": config.DEFAULT_CFG,
            "image_resolution": str(config.IMAGE_SIZE),
        },
    )
    # Replicate 返回 URL 列表
    import requests
    resp = requests.get(list(output)[0], timeout=60)
    return Image.open(io.BytesIO(resp.content))

def call_stability(processed_img: Image.Image, prompt: str) -> Image.Image:
    import requests, base64
    buf = io.BytesIO()
    processed_img.resize((config.IMAGE_SIZE, config.IMAGE_SIZE)).save(buf, format="PNG")
    resp = requests.post(
        f"https://api.stability.ai/v1/generation/{config.STABILITY_ENGINE}/image-to-image",
        headers={"Authorization": f"Bearer {config.STABILITY_API_KEY}", "Accept": "application/json"},
        files={"init_image": buf.getvalue()},
        data={
            "text_prompts[0][text]": prompt,
            "text_prompts[0][weight]": 1,
            "cfg_scale": config.DEFAULT_CFG,
            "steps": config.DEFAULT_STEPS,
            "image_strength": 0.35,
        },
        timeout=120,
    )
    resp.raise_for_status()
    b64 = resp.json()["artifacts"][0]["base64"]
    return b64_to_img(b64)

def call_openai(processed_img: Image.Image, prompt: str) -> Image.Image:
    from openai import OpenAI
    import requests as req
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    buf = io.BytesIO()
    processed_img.resize((1024, 1024)).save(buf, format="PNG")
    buf.seek(0)
    resp = client.images.edit(
        model="dall-e-2",
        image=buf,
        prompt=prompt[:1000],
        n=1,
        size="1024x1024",
    )
    url = resp.data[0].url
    r = req.get(url, timeout=60)
    return Image.open(io.BytesIO(r.content))

PROVIDERS = {
    "replicate": call_replicate,
    "stability": call_stability,
    "openai":    call_openai,
}

# ── 路由 ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/outputs/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        # 1. 接收文件
        if "sketch" not in request.files:
            return jsonify({"error": "未上传草图文件"}), 400
        file = request.files["sketch"]
        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_EXT:
            return jsonify({"error": f"不支持的文件格式: {suffix}"}), 400

        style   = request.form.get("style", "modern")
        extra   = request.form.get("extra_prompt", "").strip()
        provider_override = request.form.get("provider", "").strip()

        # 2. 读取 & 预处理
        raw_img = Image.open(file.stream).convert("RGB")
        processed = preprocess(raw_img)

        # 3. 构建 Prompt
        style_desc = STYLE_MAP.get(style, STYLE_MAP["modern"])
        prompt = (
            f"Professional architectural floor plan layout drawing, top-down view, "
            f"{style_desc}, high-quality color rendering, detailed spatial layout, "
            f"clean precise lines, accurate proportions. "
            f"{extra}"
        )

        # 4. 调用 API
        provider_name = provider_override or config.PROVIDER
        if provider_name not in PROVIDERS:
            return jsonify({"error": f"未知服务商: {provider_name}"}), 400

        result_img = PROVIDERS[provider_name](processed, prompt)

        # 5. 保存输出
        out_name = f"{uuid.uuid4().hex}.png"
        result_img.save(OUTPUT_DIR / out_name)

        return jsonify({
            "success": True,
            "output_url": f"/outputs/{out_name}",
            "prompt_used": prompt,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    """运行时读取/更新 API 配置 (保存到 config.py)"""
    if request.method == "GET":
        return jsonify({
            "provider":  config.PROVIDER,
            "has_replicate": config.REPLICATE_API_TOKEN != "r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "has_stability": config.STABILITY_API_KEY  != "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "has_openai":    config.OPENAI_API_KEY     != "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        })
    data = request.get_json(force=True)
    lines = Path("config.py").read_text(encoding="utf-8").splitlines()
    replacements = {
        "PROVIDER":              f'PROVIDER = "{data.get("provider", config.PROVIDER)}"',
        "REPLICATE_API_TOKEN":   f'REPLICATE_API_TOKEN = "{data.get("replicate_key", config.REPLICATE_API_TOKEN)}"',
        "STABILITY_API_KEY":     f'STABILITY_API_KEY = "{data.get("stability_key", config.STABILITY_API_KEY)}"',
        "OPENAI_API_KEY":        f'OPENAI_API_KEY = "{data.get("openai_key", config.OPENAI_API_KEY)}"',
    }
    new_lines = []
    for line in lines:
        replaced = False
        for key, new_val in replacements.items():
            if line.startswith(key + " ="):
                new_lines.append(new_val)
                replaced = True
                break
        if not replaced:
            new_lines.append(line)
    Path("config.py").write_text("\n".join(new_lines), encoding="utf-8")
    # 重新加载 config 模块
    import importlib
    importlib.reload(config)
    return jsonify({"success": True})

if __name__ == "__main__":
    print(f"\n🍌  香蕉模型 草图 → 布局图  已启动")
    print(f"🌐  访问: http://{config.FLASK_HOST}:{config.FLASK_PORT}\n")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
