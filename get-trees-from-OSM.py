import osmnx as ox

# Параметры запроса
tags = {'natural': 'tree'}  # Фильтр для деревьев
location = "Moscow, Russia"  # Локация

# Загрузка данных
trees = ox.features_from_place(location, tags)

# Вывод первых строк
print(trees.head())

# Сохранение в файл
trees.to_file("data_input/trees_moscow.geojson", driver="GeoJSON")


## ЛЕСА 
tags = {'natural': 'wood'}  # Фильтр для лесов
location = "Moscow, Russia"  # Локация

# Загрузка данных
woods = ox.features_from_place(location, tags)
woods.to_file("../data_input/woods_moscow.geojson", driver="GeoJSON")

# Школы 

tags = {'amenity': 'school'}  # Фильтр для школ
location = "Moscow, Russia"  # Локация

df = ox.features_from_place(location, tags)
df.to_file("../data_input/school_moscow.geojson", driver="GeoJSON")