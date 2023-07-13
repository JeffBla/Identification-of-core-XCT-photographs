import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

x = np.linspace(0, 1, 100)
y = np.linspace(0, 1, 100)

Y, X = np.meshgrid(x, y)
Z = 1 - X - Y

Hu = 2232.875 * X - 1000 * Y

fig = px.scatter_3d(
    x=X.flatten(),
    y=Y.flatten(),
    z=Z.flatten(),
    color=Hu.flatten(),
    color_continuous_scale=['gold', 'mediumturquoise', 'magenta'],
    width=950,
    height=950)

import datapane as dp

dp.save_report(dp.Plot(fig), path="checkborad3d.html")
