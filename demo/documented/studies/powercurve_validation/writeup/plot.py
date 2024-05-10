import yaml

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use(
    [
        "dark_background",
        "https://raw.githubusercontent.com/cfrontin/tools_cvf/main/tools_cvf/stylesheet_cvf.mplstyle",
        "https://raw.githubusercontent.com/cfrontin/tools_cvf/main/tools_cvf/stylesheet_nrel.mplstyle",
    ]
)

with open("FLORIS_IEA-3p4-130-RWT.yaml", "r") as f_floris:
  data_FLORIS = yaml.safe_load(f_floris)

### SINGLE TURBINE CASE

# extract three levels of discretization
df_lo = pd.read_csv("../pc_nx19ny13nz06.csv", names=["V","P"])
df_mid = pd.read_csv("../pc_nx27ny18nz09.csv", names=["V","P"])
df_hi = pd.read_csv("../pc_nx38ny25nz13.csv", names=["V","P"])

# get FLORIS reference data
maxV = np.max([np.max(df_hi), np.max(df_mid), np.max(df_lo),])
V_floris = np.array(data_FLORIS["power_thrust_table"]["wind_speed"])[data_FLORIS["power_thrust_table"]["wind_speed"] <= maxV]
P_floris = np.array(data_FLORIS["power_thrust_table"]["power"])[data_FLORIS["power_thrust_table"]["wind_speed"] <= maxV]
Vrated_floris = 9.812675420388173
Prated_floris = 3622.3451711828
CPrated_floris = Prated_floris*1e3/(0.5*data_FLORIS["power_thrust_table"]["ref_air_density"]*np.pi/4*data_FLORIS["rotor_diameter"]**2*Vrated_floris**3)

rho_fluid = 1.225
A_rotor = np.pi/4*130.0**2
Ps_fluid = lambda V: 0.5*A_rotor*V**3/1e6

V_CP_calib = 7.0
V_Prated_calib = 17.0
CP_windse_calib = np.interp(V_CP_calib, df_hi.V, df_hi.P/rho_fluid/Ps_fluid(df_hi.V))
Prated_windse_calib = np.interp(V_Prated_calib, df_hi.V, df_hi.P*rho_fluid)
print(f"CPrated from FLORIS: {CPrated_floris}")
print(f"CP_calibration from data: {CP_windse_calib}")
print(f"CP calibration factor: {CPrated_floris/CP_windse_calib}")
print(f"Prated from FLORIS: {Prated_floris/1e3}")
print(f"Prated_calibration from data: {Prated_windse_calib}")
print(f"P calibration factor: {Prated_floris/1e3/Prated_windse_calib}")

## power plot

fig, ax = plt.subplots()

ax.plot(df_lo.V, df_lo.P, label="$N_x=38$, $N_y=25$, $N_z=13$")
ax.plot(df_mid.V, df_mid.P, label="$N_x=27$, $N_y=18$, $N_z=9$")
ax.plot(df_hi.V, df_hi.P, label="$N_x=19$, $N_y=13$, $N_z=6$")
ax.plot(
  V_floris,
  P_floris/data_FLORIS["power_thrust_table"]["ref_air_density"]/1e3,
  "w--",
  label="IEA-3.4MW-130m reference",
)
ax.plot(Vrated_floris, Prated_floris/1.225/1e3, "wo")
ax.plot(
  V_floris,
  np.minimum(
    Prated_floris/1.225/1e3*np.ones_like(V_floris),
    CPrated_floris*Ps_fluid(V_floris)),
  "w:",
  label="IEA-3.4MW-130m: $\\min(\\frac{1}{2} C_P A V^3, P_{\\mathrm{rated}}/\\rho)$"
)
ax.set_xlabel("hub-height farfield velocity, $V$ (m/s)")
ax.set_ylabel("specific turbine power, $P(V)$ ($10^6$ m$^5$/s$^3$)")
ax.legend()
fig.savefig("single_turb_Pconv.png", dpi=300, bbox_inches="tight")

## CP plot

fig, ax = plt.subplots()

ax.plot(df_lo.V, df_lo.P/Ps_fluid(df_lo.V), label="$N_x=38$, $N_y=25$, $N_z=13$")
ax.plot(df_mid.V, df_mid.P/Ps_fluid(df_mid.V), label="$N_x=27$, $N_y=18$, $N_z=9$")
ax.plot(df_hi.V, df_hi.P/Ps_fluid(df_hi.V), label="$N_x=19$, $N_y=13$, $N_z=6$")
ax.plot(
  V_floris,
  P_floris/data_FLORIS["power_thrust_table"]["ref_air_density"]/1e3/Ps_fluid(V_floris),
  "w--",
  label="IEA-3.4MW-130m reference",
)
ax.plot(Vrated_floris, CPrated_floris, "wo")
ax.set_xlabel("hub-height farfield velocity, $V$ (m/s)")
ax.set_ylabel("power_coefficient, $C_P(V)$ (-)")
ax.legend()
fig.savefig("single_turb_CPconv.png", dpi=300, bbox_inches="tight")

plt.show()
