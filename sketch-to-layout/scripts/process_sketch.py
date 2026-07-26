import os
import glob
from PIL import Image, ImageOps

# 引入 Google API 库 (如果使用官方的新 SDK: google-genai)
# 请先运行: pip install google-genai
# from google import genai
# from google.genai import types

# 定义默认的输入输出文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(BASE_DIR)
INPUT_DIR = os.path.join(BASE_DIR, 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
STYLES_DIR = os.path.join(SKILL_ROOT, 'styles')

def preprocess_image(input_path, output_path):
    """
    基础图像预处理：增强对比度，转为灰度图（有助于 AI 识别线条）。
    """
    try:
        img = Image.open(input_path)
        # 如果图片是RGBA，先转换为RGB，以免在转灰度或保存时出问题
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # 转灰度
        img = img.convert('L')
        # 自动调整对比度
        img = ImageOps.autocontrast(img)
        # 保存
        img.save(output_path)
        print(f"  -> Pre-processed image saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"  -> Error during pre-processing: {e}")
        return None

def get_style_prompt(style_name):
    """
    从 styles 文件夹中读取指定风格的 prompt，如果未找到则返回默认 prompt。
    """
    default_prompt = "Professional architectural floor plan, high-quality color rendering, detailed spatial layout, banana model style, clean lines."
    if not style_name:
        return default_prompt
        
    style_path = os.path.join(STYLES_DIR, f"{style_name}.txt")
    if os.path.exists(style_path):
        with open(style_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return default_prompt

def call_google_api(image_path, output_path, style_name=None):
    """
    调用 Google API 进行草图到布局图的转换。
    可以传入 style_name (如 'modern_minimalist') 来读取对应的 prompt。
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("  -> [警告] 未检测到 GOOGLE_API_KEY，跳过 API 调用。请在系统环境变量中设置。")
        return

    prompt = get_style_prompt(style_name)
    style_display = style_name if style_name else "default"
    print(f"  -> 正在请求 Google API 进行转换 (风格: {style_display})...")
    # ========================================================
    #  ⬇️ 这里填写你的 Google API 代码逻辑 ⬇️
    # ========================================================
    # 示例 (Gemini API 伪代码):
    # client = genai.Client(api_key=api_key)
    # img = Image.open(image_path)
    # 
    # response = client.models.generate_content(
    #     model='gemini-2.5-pro',
    #     contents=[prompt, img]
    # )
    # 
    # 或者如果你是用来生成图片的 (Imagen 3):
    # response = client.models.generate_images(...)
    # 
    # 然后将生成的图片保存到 output_path (这里可能需要自己处理怎么获取字节流保存)
    # with open(output_path, "wb") as f:
    #     f.write(response.generated_image)
    # ========================================================

def process_all_images(style_name=None):
    """
    一键执行：处理输入文件夹中的所有图片，存放至输出文件夹。
    可通过 style_name 参数指定渲染风格。
    """
    # 1. 确保输入、输出、风格文件夹存在
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(STYLES_DIR, exist_ok=True)

    # 2. 搜索输入文件夹中的图片
    extensions = ('*.png', '*.jpg', '*.jpeg', '*.bmp')
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob.glob(os.path.join(INPUT_DIR, ext)))
        image_paths.extend(glob.glob(os.path.join(INPUT_DIR, ext.upper())))

    # 去重防重复
    image_paths = list(set(image_paths))

    if not image_paths:
        print(f"The 'input' folder is empty: {INPUT_DIR}")
        print("Please place your sketch images here and run the script again.")
        return

    # 3. 循环处理
    print(f"Found {len(image_paths)} image(s). Start processing...")
    for idx, input_path in enumerate(image_paths, 1):
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        
        # 预处理后的中间文件
        preprocessed_filename = f"{name}_preprocessed{ext}"
        preprocessed_path = os.path.join(OUTPUT_DIR, preprocessed_filename)
        
        # 最终 API 返回生成的布局图文件
        style_suffix = f"_{style_name}" if style_name else ""
        final_output_filename = f"{name}{style_suffix}_layout.png" 
        final_output_path = os.path.join(OUTPUT_DIR, final_output_filename)
        
        print(f"[{idx}/{len(image_paths)}] Processing: {filename}")
        
        # 第一步：预处理
        processed_img_path = preprocess_image(input_path, preprocessed_path)
        
        # 第二步：调用 Google API 进行转换
        if processed_img_path:
            call_google_api(processed_img_path, final_output_path, style_name)
        
    print("\nAll done!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process sketch images and convert them to layouts.")
    parser.add_argument(
        "--style", 
        type=str, 
        default=None, 
        help="Specify the style name to use (e.g., modern_minimalist, luxury_office). It will read from styles/<style>.txt. If not specified, a default prompt will be used."
    )
    
    args = parser.parse_args()
    
    # 获取风格名字 (去掉可能输入的 .txt 后缀)
    style_name = args.style
    if style_name and style_name.endswith('.txt'):
        style_name = style_name[:-4]
        
    process_all_images(style_name)
