def loops():
    total = 0
    for i in range(200):
        i2 = i * i
        for j in range(50):
            total = total + i2 + j
    return total


print(loops())
