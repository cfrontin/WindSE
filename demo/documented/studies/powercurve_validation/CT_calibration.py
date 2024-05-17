import yaml

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn

################################################################################
# this is a brief script for calibration of CT.
#
# data comes from a run at 7.0 m/s (region II) with all calibration factors set
# to zero. a convergence study is run with single_turbine.yaml, and the results
# are stored and saved in CTcalibration_data.csv.
#
# we target matching the reference CT at 7.0 m/s with the asymptotic simulation.
# we assume geometric convergence of thrust w.r.t. dx. this allows the hand-fit
# of the convergence data for an estimate of the asymptotic thrust, shown below.
#
################################################################################

# simulation properties
rho_fluid = 1.225  # kg/m^3
diameter_rotor = 130.0  # m
area_rotor = np.pi/4*diameter_rotor**2  # m^2
V_inf = 7.0  # m/s
Tf_fluid = 0.5*rho_fluid*area_rotor*V_inf**2/1e3
volume_domain = (780.0 - -390.0)*(390.0 - -390.0)*(520.0 - 0.04)

# load, amend calibration simulation data
fn_data = "CTcalibration_data.csv"
df_data = pd.read_csv(fn_data)
df_data["dx_elem"] = volume_domain/df_data.Nelem

# fit loge convergence with linear model
mb = np.polyfit(
  np.log10(df_data.dx_elem.to_numpy()[:-1]),
  np.log10(np.abs(rho_fluid*df_data.Tf.to_numpy()[:-1] - rho_fluid*df_data.Tf.to_numpy()[-1])),
  deg=1,
)
# i.e.:
#   log10(|J-Jinf|) = m*log(dx) + b
#   |J-Jinf| = dx**m * 10**b
#   Jinf = J -/+ dx**m * 10**b

# estimates of the true thrust based on each sample
Tf_inf_est = rho_fluid*df_data.Tf + df_data.dx_elem**mb[0] * 10**mb[1]
# Tf_inf_est = rho_fluid*df_data.Tf - df_data.dx_elem**mb[0] * 10**mb[1]

# plot the convergence behavior for validation
fig, axes = plt.subplots(2, sharex=True)

# power vs. discretization length
axes[0].semilogx(
  df_data.dx_elem.to_numpy(),
  rho_fluid*df_data.Tf.to_numpy(),
)
axes[0].semilogx(
  df_data.dx_elem.to_numpy(),
  Tf_inf_est.to_numpy(),
  "--", label="corrected value",
)
axes[0].semilogx(
  df_data.dx_elem.to_numpy(),
  Tf_inf_est.to_numpy()[-1]*np.ones_like(df_data.dx_elem.to_numpy()),
  "--", label="estimated asymptote",
)
axes[0].set_xlabel("discretization length, $\\Delta x$ (m)")
axes[0].set_ylabel("thrust force, $T$ (kN)")
axes[0].legend()

# apparent error vs. discretization length
axes[1].loglog(
  df_data.dx_elem.to_numpy()[:-1],
  np.abs(rho_fluid*df_data.Tf.to_numpy()[:-1] - rho_fluid*df_data.Tf.to_numpy()[-1]),
)
axes[1].loglog(
  df_data.dx_elem.to_numpy()[:-1],
  10**(mb[0]*np.log10(df_data.dx_elem.to_numpy()[:-1]) + mb[1]),
  "--", label="line of best fit",
)
axes[1].set_xlabel("discretization length, $\\Delta x$ (m)")
axes[1].set_ylabel("apparent thrust error, $e_T$ (kN)")
axes[1].legend()

# get the reference power curve we want to match
with open("writeup/FLORIS_IEA-3p4-130-RWT.yaml", "r") as f_yaml:
  data_refPC = yaml.safe_load(f_yaml)
V_refPC = data_refPC["power_thrust_table"]["wind_speed"]
CT_refPC = data_refPC["power_thrust_table"]["thrust_coefficient"]

# print out the CT values we see
print(f"estimated asymptotic CT: {Tf_inf_est.to_numpy()[-1]/Tf_fluid}")
print(f"reference powercurve CT: {np.interp(V_inf, V_refPC, CT_refPC)}")
print(f"correction: {np.interp(V_inf, V_refPC, CT_refPC)/(Tf_inf_est.to_numpy()[-1]/Tf_fluid)}")

# show and exit
plt.show()

###
