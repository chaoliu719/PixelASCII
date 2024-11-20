from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def can_fit_all_ascii(size, width, height, font_path):
    font = ImageFont.truetype(font_path, size)
    img = Image.new('L', (width, height), color=255)
    draw = ImageDraw.Draw(img)

    for i in range(256):
        char = chr(i)
        try:
            text_bbox = draw.textbbox((0, 0), char, font=font)
            if text_bbox[2] > width or text_bbox[3] > height:
                return False
        except:
            return False
    return True

def find_max_font_size_for_all_ascii(width, height, font_path):
    low, high = 1, max(width, height) * 2
    best_size = 1

    while low <= high:
        mid = (low + high) // 2
        if can_fit_all_ascii(mid, width, height, font_path):
            best_size = mid
            low = mid + 1
        else:
            high = mid - 1

    return best_size

def render_char_to_bitmap(char, font, width, height):
    img = Image.new('1', (width, height), color=1)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), char, font=font, fill=0)
    return list(img.getdata())

def bitmap_to_ascii_with_border(bitmap, width, height):
    top_border = '   ' + ''.join(f'{i:2d} ' for i in range(width))
    result = [top_border, '  ┌' + '─' * (width * 3) + '┐']

    for y in range(height):
        row = f'{y:2d}│'
        for x in range(width):
            pixel = bitmap[y * width + x]
            row += '██ ' if pixel == 0 else '   '
        row += '│'
        result.append(row)

    result.append('  └' + '─' * (width * 3) + '┘')

    return '\n'.join(result)

def generate_all_ascii_bitmaps(font_path, font_size, width, height):
    font = ImageFont.truetype(font_path, font_size)
    result = []

    for i in range(256):
        char = chr(i)
        try:
            bitmap = render_char_to_bitmap(char, font, width, height)
            ascii_representation = bitmap_to_ascii_with_border(bitmap, width, height)
            result.append(f"ASCII {i} ({repr(char)[1:-1]}):\n{ascii_representation}\n")
        except:
            result.append(f"ASCII {i} (不可渲染)\n")

    return '\n'.join(result)

def render_sentence(sentence, font_path, font_size, char_width, char_height):
    font = ImageFont.truetype(font_path, font_size)
    result = []
    for char in sentence:
        try:
            bitmap = render_char_to_bitmap(char, font, char_width, char_height)
            char_result = []
            for i in range(0, len(bitmap), char_width):
                row = ''.join('██' if pixel == 0 else '  ' for pixel in bitmap[i:i+char_width])
                char_result.append(row)
            result.append(char_result)
        except:
            result.append(['  ' * char_width] * char_height)

    # 将所有字符的位图并排输出
    return '\n'.join(' '.join(row) for row in zip(*result))

def bitmap_to_c_array(bitmap, width, height, char, char_code):
    bytes_per_row = (width + 7) // 8  # 计算每行需要多少个字节
    result = [f"/* {char_code} 0x{char_code:02X} {repr(char)[1:-1]} */"]

    for y in range(height):
        row_bytes = []
        binary_string = ""

        for x in range(0, width, 8):
            byte = 0
            for bit in range(min(8, width - x)):
                if bitmap[y * width + x + bit] == 0:
                    byte |= (1 << (7 - bit))
                binary_string += '1' if bitmap[y * width + x + bit] == 0 else '0'
            row_bytes.append(f"0x{byte:02X}")

        # 格式化输出
        row_string = ", ".join(row_bytes)
        result.append(f"{row_string}, /* Binary digit: {binary_string} */")

    return '\n'.join(result)

def generate_all_ascii_c_arrays(font_path, font_size, width, height):
    font = ImageFont.truetype(font_path, font_size)
    result = []

    for i in range(256):
        char = chr(i)
        try:
            bitmap = render_char_to_bitmap(char, font, width, height)
            c_array = bitmap_to_c_array(bitmap, width, height, char, i)
            result.append(c_array)
        except:
            result.append(f"/* {i} 0x{i:02X} (不可渲染) */")

    return '\n\n'.join(result)

def bitmap_to_c_array_compact(bitmap, width, height, char, char_code):
    bytes_per_row = (width + 7) // 8
    result = []
    line = ""
    byte_count = 0

    for y in range(height):
        for x in range(0, width, 8):
            byte = 0
            for bit in range(min(8, width - x)):
                if bitmap[y * width + x + bit] == 0:
                    byte |= (1 << (7 - bit))

            new_item = f"0x{byte:02X},"
            if len(line) + len(new_item) > 160:
                result.append(line.rstrip())
                line = new_item
            else:
                line += new_item

            byte_count += 1

    if line:
        result.append(line)
    return '\n'.join(result)

def generate_all_ascii_c_arrays_compact(font_path, font_size, width, height):
    font = ImageFont.truetype(font_path, font_size)
    result = []

    for i in range(256):
        char = chr(i)
        try:
            bitmap = render_char_to_bitmap(char, font, width, height)
            c_array = bitmap_to_c_array_compact(bitmap, width, height, char, i)
            result.append(c_array)
        except:
            result.append(f"/* {i:3d} 0x{i:02X} (不可渲染) */")

    return '\n'.join(result)

def generate_header_file(ascii_arrays, width, height, email, company):
    current_year = datetime.now().strftime("%Y")
    current_date = datetime.now().strftime("%Y-%m-%d")
    header = """/*
 *  <video_font_data.h> - <video font data>
 *
 *  Copyright (C) {year} {company}.
 *  History:
 *      <{date}> <{email}>
 *
 *      The above copyright notice shall be
 *      included in all copies or substantial portions of the Software.
 *
 *      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *      EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 *      MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 *      IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 *      CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 *      TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 *      SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#ifndef _VIDEO_FONT_DATA_
#define _VIDEO_FONT_DATA_

#define VIDEO_FONT_CHARS            256
#define VIDEO_FONT_WIDTH            {width}
#define VIDEO_FONT_HEIGHT           {height}
#define VIDEO_FONT_UNIT             (sizeof(char) * 8)
#define VIDEO_FONT_SIZE_PER_COLUMN  (VIDEO_FONT_WIDTH / VIDEO_FONT_UNIT)
#define VIDEO_FONT_SIZE_PER_ROW     VIDEO_FONT_HEIGHT
#define VIDEO_FONT_SIZE_PER_CHAR    (VIDEO_FONT_SIZE_PER_ROW * VIDEO_FONT_SIZE_PER_COLUMN)
#define VIDEO_FONT_SIZE             (VIDEO_FONT_CHARS * VIDEO_FONT_SIZE_PER_CHAR)

static unsigned char video_fontdata[VIDEO_FONT_SIZE] = {{
{data}
}};

#endif
"""
    return header.format(year=current_year, date=current_date, email=email, company=company,
                         width=width, height=height, data=ascii_arrays)


# 0. 使用示例
width, height = 16, 24  # 位图大小
font_path = r".\MonaspaceNeon-Regular.otf"  # 替换为你的字体路径

max_font_size = find_max_font_size_for_all_ascii(width, height, font_path)
print(f"在 {width}x{height} 的尺寸内，所有 ASCII 字符的最大公共字号是: {max_font_size}")

# 1. ASCII 位图保存到文件
ascii_bitmaps = generate_all_ascii_bitmaps(font_path, max_font_size, width, height)

with open("ascii_bitmaps_with_border.txt", "w", encoding="utf-8") as f:
    f.write(f"位图大小: {width}x{height}, 最大字号: {max_font_size}\n\n")
    f.write(ascii_bitmaps)

print("ASCII 位图已保存到 ascii_bitmaps_with_border.txt 文件中。")

# 2. 渲染示例句子
example_sentence = "Hello, World!"
sentence_bitmap = render_sentence(example_sentence, font_path, max_font_size, width, height)

# 将示例句子的渲染结果也保存到文件
with open("sentence_bitmap.txt", "w", encoding="utf-8") as f:
    f.write(f"示例句子 '{example_sentence}' 的渲染结果：\n\n")
    f.write(sentence_bitmap)

print("示例句子的位图已保存到 sentence_bitmap.txt 文件中。")

# 3. 生成所有 ASCII 字符的 C 数组表示
ascii_c_arrays = generate_all_ascii_c_arrays(font_path, max_font_size, width, height)

# 将结果保存到文件
with open("ascii_c_arrays.txt", "w", encoding="utf-8") as f:
    f.write(f"// 位图大小: {width}x{height}, 字号: {max_font_size}\n\n")
    f.write(ascii_c_arrays)

print("ASCII C 数组表示已保存到 ascii_c_arrays.txt 文件中。")

# 4. 生成紧凑版所有 ASCII 字符的 C 数组表示
ascii_c_arrays = generate_all_ascii_c_arrays_compact(font_path, max_font_size, width, height)

# 将结果保存到文件
with open("ascii_c_arrays_compact.txt", "w", encoding="utf-8") as f:
    f.write(f"// w{width}h{height}\n")
    f.write(ascii_c_arrays)

print("紧凑版 ASCII C 数组表示已保存到 ascii_c_arrays_compact.txt 文件中。")

# 5. 增加头文件

# 使用示例
ascii_c_arrays_compact = generate_all_ascii_c_arrays_compact(font_path, max_font_size, width, height)
email = "sample@sample.com"  # 替换为你的邮箱地址
company = "Sample LLC"  # 替换为你的公司名称

# 生成头文件
header_content = generate_header_file(ascii_c_arrays_compact, width, height, email, company)

# 将结果保存到文件
with open("video_font_data.h", "w", encoding="utf-8") as f:
    f.write(header_content)

print("视频字体数据头文件已保存到 video_font_data.h")