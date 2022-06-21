import time
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111)

i = 0
x, y = [], []

while True:
	x.append(i)
	y.append(np.random.randint(1, 100))

	ax.plot(x, y, color='b')

	fig.canvas.draw()

	ax.set_xlim(left=max(0, i - 50), right=i + 50)
	fig.show()
	plt.pause(0.05)
	i += 1