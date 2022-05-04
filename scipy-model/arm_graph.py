from bokeh.models import Range1d
from bokeh.models.axes import LinearAxis
from bokeh.layouts import row, column

from arm_model import Arm
from bokeh.io import output_notebook, show
from bokeh.plotting import figure


def time_vs_y(ylabel, get_y):

    def fun(arm: Arm, fig=None, height=400, width=600, color='black'):
        if fig is None:
            fig = figure(height=height, width=width)
        t = arm.times
        y = get_y(arm)
        fig.line(t, y, color=color)
        fig.xaxis.axis_label = 'time (seconds)'
        fig.yaxis.axis_label = ylabel
        return fig
    return fun


time_vs_angle = time_vs_y('θ (degrees)',
                          lambda arm: [
                              x[0] for x in arm.states])
time_vs_power = time_vs_y('Power',
                          lambda arm: arm.powers
                          )

time_vs_internal_angle = time_vs_y('internal θ (degrees)',
                                   lambda arm: [x[2] for x in arm.states])

time_vs_angle_rate = time_vs_y('dθ/dt (degrees/sec)',
                               lambda arm: [x[1] for x in arm.states])
