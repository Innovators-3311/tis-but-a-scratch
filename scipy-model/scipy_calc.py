from logging import warning
from math import pi

import numpy as np
from bokeh.io import output_file, show
from bokeh.layouts import column, row
from bokeh.models import Range1d
from bokeh.models.axes import LinearAxis
from bokeh.plotting import figure
from scipy.integrate import odeint, solve_ivp

m = 0.25                # Mass of the arm (kg)
I = m * (6.5e-5)    # kg * sqrt(m^4) -> kg m^2
g = 9.8                 # Gravitational Constant m/s^2
theta0 = 0              # Initial angle
r = 0.15                 # Distance from the axis to the center of mass (Estimate: 20 cm)
friction = 1e-3

def tau_gravity(**kw):
  """Torque due to gravity

  This function computes the torque due to gravity for given mass and radius.
  """
  return - r * m * np.cos(kw['theta'] * pi/180.0)

def tau_friction(**kw):
  """Friction is a constant force that points in the direction opposite motion.
  """
  # This can't be nonlinear.
  return - friction * np.tanh(kw['omega'])
  # return - friction * np.sign(kw['omega'])

# This function defines the derivative and acceleration given position and derivative
def armfunc(y, t):
  theta, omega = y
  kw = {"theta": theta, "omega": omega}
  # Sum all the taus we compute.  
  sigmatau = sum([x(**kw) for x in (tau_gravity, tau_friction)])
  # if F = ma , then a = F / m (or \alpha = \tau / I)
  dydt = [omega, sigmatau / I ] 
  return dydt 
# This function defines the derivative and acceleration given position and derivative
def armfunc(t, y):
  theta, omega = y
  kw = {"theta": theta, "omega": omega}
  # Sum all the taus we compute.  
  sigmatau = sum([x(**kw) for x in (tau_gravity, tau_friction)])
  # if F = ma , then a = F / m (or \alpha = \tau / I)
  dydt = [omega, sigmatau / I ] 
  return dydt 


# Initial conditions: Angle is 0 and its derivative is 0;
y0 = [30, 400]
tmax=5
t = np.linspace(0, tmax, 200)
res = solve_ivp(armfunc, [0, tmax], y0, 
                method='LSODA', 
                t_eval=t,
                first_step=0.1, min_step=1e-6, atol=0.1)
y = res["y"].T
t = res["t"]

fig = figure(height=200)
fig.line(t, y[:, 0], legend_label="Angle")
fig.line(t, y[:, 1], color='black', legend_label="Angle Rate")
fig.yaxis.axis_label = 'Arm angle (degrees)'
fig.xaxis.axis_label = 'Time (seconds)'
show(fig)

if not res['success']:
  warning(f"{res['message']}")
