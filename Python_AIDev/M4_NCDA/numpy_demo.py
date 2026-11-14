import numpy as np

#***********************************
# Numpy List vs Array
#***********************************

# prices = [100, 200, 300]  # 18
# updated_prices = []
# for price in prices:
#     updated_prices.append(price * 1.18)
# print(updated_prices)

# prices = np.array([100, 200, 300])
# updated_prices = prices * 1.18
# print(updated_prices)

#***********************************
# 1D Array
#***********************************

arr = np.array([1, 2, 3, 4, 5])
print(arr)
print(type(arr))
print(arr.shape)
print(arr.ndim)

#***********************************
# 2D Array
#***********************************

arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
print(arr_2d)
print(type(arr_2d))
print(arr_2d.shape)
print(arr_2d.ndim)

#***********************************
# 3D Array
#***********************************

arr_3d = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
print(arr_3d)
print(type(arr_3d))
print(arr_3d.shape)
print(arr_3d.ndim)