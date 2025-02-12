import json

skeletons = [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], [7, 9],
                         [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]


color_pallete = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1,1,1,1,1]

color_list = [
    ((255, 0, 0), "Red"),
    ((0, 255, 0), "Green"),
    ((0, 0, 255), "Blue"),
    ((0, 255, 255), "Yellow"),
]

with open("config2.json", "r") as file:
    file = json.load(file)
    point_configuration = file['point_config']
    angle_cluster = file['angle_clusters']
    angle_ranges = file['angle_ranges']