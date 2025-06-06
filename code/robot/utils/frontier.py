def is_frontier_cell(map, x, y):
    if map[x][y].visitada != True:  # 0 = libre
        return False
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if map[x+dx][y+dy] == False:  # -1 = desconocido
                return True
    return False

def detect_frontiers(map,limite):
    frontiers = []
    for x in range(1, len(map)-1):
        for y in range(1, len(map[0])-1):
            celda = map[x][y]
            if celda and celda.visitada:
                if is_frontier_cell(map, x, y):
                    if x<=limite and y<=limite:
                        frontiers.append((x, y))
    return frontiers

def get_closest_frontier(frontiers, robot_position):
    if not frontiers:
        return None
    closest = min(frontiers, key=lambda f: (f[0] - robot_position[0])**2 + (f[1] - robot_position[1])**2)
    return closest