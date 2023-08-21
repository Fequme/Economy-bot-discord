from easy_pil import Editor, Canvas, Font, load_image_async

canvas = Canvas ((2000, 1000))

font_50 = Font("assets/font.ttf", size=50)
font_60 = Font("assets/font.ttf", size=60)

font_bighaustitul_50 = Font("assets/font_bighaustitul.ttf", size=50)

profile = Editor("assets/profile/themes/theme_default.png") # путь к картине

editor = Editor(canvas)

editor.paste(profile.image, (0, 0))

# Валюта
editor.text((1068, 125), "10", color="white", font=font_bighaustitul_50, align="left")

# Голосовая активность
editor.text((1068, 267), "100000", color="white", font=font_bighaustitul_50, align="left")

# Количество сообщений
editor.text((1740, 125), "100000", color="white", font=font_bighaustitul_50, align="left")

# Место в топе по голосовой активности
editor.text((1740, 267), "100000", color="white", font=font_bighaustitul_50, align="left")\

name = "AAAAAAAAAA"
member_name = (name[:9] + '...') if len(name) > 10 else name

# Ник
editor.text((1461, 390), member_name, color="black", font=font_60, align="center")

# Ник партнёра
editor.text((1185, 822), "Ы", color="black", font=font_50, align="center")

editor.show()