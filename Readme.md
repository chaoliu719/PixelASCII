# 简介

这个工具可以将 ASCII 字符转换成像素数组。用户可以利用这些数组，在屏幕上用像素绘制出 ASCII 字符图像。

特性：用户可以指定这些图像的大小，比如说每个字符用 8x8 或 16x16 的小方块来表示。

原理：将每个 ASCII 字符渲染到一个预定义大小的位图上。这个位图是一个二维数组，其中每个元素代表一个像素。使用时，遍历数组，1 输出黑色像素，0 输出白色像素。


# 安装

需要预先安装 pillow 库

```
pip install pillow
```

# 功能及用法

一、寻找给定尺寸内，能容纳所有 ASCII 字符的最大字体号。

```
> python auto_gen.py
在 16x24 的尺寸内，所有 ASCII 字符的最大公共字号是: 21
ASCII 位图已保存到 ascii_bitmaps_with_border.txt 文件中。
示例句子的位图已保存到 sentence_bitmap.txt 文件中。
ASCII C 数组表示已保存到 ascii_c_arrays.txt 文件中。
紧凑版 ASCII C 数组表示已保存到 ascii_c_arrays_compact.txt 文件中。
视频字体数据头文件已保存到 video_font_data.h
```

二、预览每一个生成的像素位图。

![[preview of ASCII 'a']](pic/preview_a.png)

三、模拟句子按照像素位图打印在显示屏上的样子

![[preview of "Hello, world!"]](pic/preview_hello_world.png)

四、生成用于 C 语言的像素位图数组

![[pixil array]](pic/array.png)



五、生成用于 C 语言的像素位图数组（不可读版，用于缩小文件大小）

![[pixil array compact]](pic/array_compact.png)


# 使用示例

这里的 fbbase 就是线性的显示内存，lcd_total_column 是屏幕的总列数，也可以理解为每行的像素个数。

output_row 和 output_column 代表要输出到哪行哪列，c 是要输出的字符。

fg_color，bg_color 分别代表像素为 1 或 0 时输出什么颜色。

```
static inline void lcd_putchar(void *fbbase, int lcd_total_column, int output_column, int output_row, char c, int fg_color, int bg_color)
{
    int i, column, row;
    unsigned char bits;
    void *dst = fbbase + output_row * lcd_total_column + output_column;

    for (row = 0; row < VIDEO_FONT_SIZE_PER_ROW; row++) {
        for (column = 0; column < VIDEO_FONT_SIZE_PER_COLUMN; column++) {
            bits = video_fontdata[c * VIDEO_FONT_SIZE_PER_CHAR + row * VIDEO_FONT_SIZE_PER_COLUMN + column];
            for (i = 0; i < VIDEO_FONT_UNIT; i++) {
                *dst++ = (bits & 0x80) ? fg_color : bg_color;
                bits <<= 1;
            }
        }
        dst += lcd_total_column - VIDEO_FONT_WIDTH;
    }
}

```