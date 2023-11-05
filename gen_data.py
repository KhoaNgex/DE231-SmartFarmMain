import pandas as pd
import random

# Khởi tạo danh sách trống cho mỗi trường
data = {
    'temp': [],
    'humidity': [],
    'soil': [],
    'light': [],
    'label': []
}

# Tạo dữ liệu theo quy luật phức tạp
for _ in range(1000000):
    temperature = random.uniform(-50, 100)
    humidity = random.uniform(0, 100)
    soil = random.uniform(0, 100)
    light = random.uniform(0, 10000)

    if (temperature > 30 and humidity < 40) or \
    (soil > 50 and humidity < 50 and light > 1000) or \
    (temperature > 25 and soil > 60):
        label = 1  # Bơm nước
    else:
        label = 0  # Không bơm nước

    data['temp'].append(temperature)
    data['humidity'].append(humidity)
    data['soil'].append(soil)
    data['light'].append(light)
    data['label'].append(label)

# Tạo DataFrame từ dữ liệu
df = pd.DataFrame(data)

# Lưu DataFrame thành một tệp CSV
df.to_csv('du_lieu.csv', index=False)
