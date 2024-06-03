import pprint
import yaml

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use(
    [
        "dark_background",
        # "https://raw.githubusercontent.com/cfrontin/tools_cvf/main/tools_cvf/stylesheet_cvf.mplstyle",
        # "https://raw.githubusercontent.com/cfrontin/tools_cvf/main/tools_cvf/stylesheet_nrel.mplstyle",
    ]
)

with open("FLORIS_IEA-3p4-130-RWT.yaml", "r") as f_floris:
  data_FLORIS = yaml.safe_load(f_floris)

do_single_turbine=True
do_multi_turbine=False

### SINGLE TURBINE CASE

if do_single_turbine:
  # extract three levels of discretization
  casename = "kestrel_nx19ny13nz06" # "nx19ny13nz06"
  df_curves_lo = pd.read_csv(f"../curves_{casename}.csv", names=["V","P","Tf"])
  df_curves_collection = [df_curves_lo]
  casename = "kestrel_nx27ny18nz09" # "nx27ny18nz09"
  df_curves_mid = pd.read_csv(f"../curves_{casename}.csv", names=["V","P","Tf"])
  df_curves_collection = [df_curves_lo, df_curves_mid]
  # casename = "kestrel_nx38ny25nz13" # "nx38ny25nz13"
  # df_curves_hi = pd.read_csv(f"../curves_{casename}.csv", names=["V","P","Tf"])
  # df_curves_collection = [df_curves_lo, df_curves_mid, df_curves_hi]
  label_collection = [
    "$N_x=19$, $N_y=13$, $N_z=6$",
    "$N_x=27$, $N_y=18$, $N_z=9$",
    "$N_x=38$, $N_y=25$, $N_z=13$",
  ]

  # get FLORIS reference data
  rho_fluid = 1.225
  D_rotor=130.0
  A_rotor = np.pi/4*D_rotor**2
  Ts_fluid = lambda V: 0.5*rho_fluid*A_rotor*V**2/1e3  # kN
  Ps_fluid = lambda V: 0.5*rho_fluid*A_rotor*V**3/1e6  # MW

  maxV = np.max([np.max(df.V) for df in df_curves_collection])
  V_floris = np.array(data_FLORIS["power_thrust_table"]["wind_speed"])[data_FLORIS["power_thrust_table"]["wind_speed"] <= maxV]
  P_floris = np.array(data_FLORIS["power_thrust_table"]["power"])[data_FLORIS["power_thrust_table"]["wind_speed"] <= maxV]
  Vrated_floris = 9.812675420388173
  Prated_floris = 3622.3451711828
  CPrated_floris = Prated_floris/1e3/Ps_fluid(Vrated_floris)
  CT_floris = np.array(data_FLORIS["power_thrust_table"]["thrust_coefficient"])[data_FLORIS["power_thrust_table"]["wind_speed"] <= maxV]

  ## power plot

  fig, ax = plt.subplots()

  for df_power, label_case in zip(df_curves_collection, label_collection):
    ax.plot(df_power.V, rho_fluid*df_power.P, label=label_case)
  # ax.plot(df_power_lo.V, rho_fluid*df_power_lo.P, label="$N_x=19$, $N_y=13$, $N_z=6$")
  # ax.plot(df_power_mid.V, rho_fluid*df_power_mid.P, label="$N_x=27$, $N_y=18$, $N_z=9$")
  # ax.plot(df_power_hi.V, rho_fluid*df_power_hi.P, label="$N_x=38$, $N_y=25$, $N_z=13$")
  ax.plot(
    V_floris,
    P_floris/1e3,
    "w--",
    label="IEA-3.4MW-130m reference",
  )
  ax.plot(Vrated_floris, Prated_floris/1e3, "wo")
  ax.plot(
    V_floris,
    np.minimum(
      Prated_floris/1e3*np.ones_like(V_floris),
      CPrated_floris*Ps_fluid(V_floris)),
    "w:",
    label="IEA-3.4MW-130m: $\\min(\\frac{1}{2} C_P A V^3, P_{\\mathrm{rated}}/\\rho)$"
  )
  ax.set_xlabel("hub-height farfield velocity, $V$ (m/s)")
  ax.set_ylabel("turbine power, $P(V)$ (MW)")
  ax.legend()
  fig.savefig("single_turb_Pconv.png", dpi=300, bbox_inches="tight")

  ## CP plot

  fig, ax = plt.subplots()

  for df_power, label_case in zip(df_curves_collection, label_collection):
    ax.plot(df_power.V, rho_fluid*df_power.P/Ps_fluid(df_power.V), label=label_case)
  # ax.plot(df_power_lo.V, rho_fluid*df_power_lo.P/Ps_fluid(df_power_lo.V), label="$N_x=19$, $N_y=13$, $N_z=6$")
  # ax.plot(df_power_mid.V, rho_fluid*df_power_mid.P/Ps_fluid(df_power_mid.V), label="$N_x=27$, $N_y=18$, $N_z=9$")
  # ax.plot(df_power_hi.V, rho_fluid*df_power_hi.P/Ps_fluid(df_power_hi.V), label="$N_x=38$, $N_y=25$, $N_z=13$")
  ax.plot(
    V_floris[1:],
    P_floris[1:]/1e3/Ps_fluid(V_floris[1:]),
    "w--",
    label="IEA-3.4MW-130m reference",
  )
  ax.plot(Vrated_floris, CPrated_floris, "wo")
  ax.plot(
    V_floris[1:],
    np.minimum(
      Prated_floris/1e3/Ps_fluid(V_floris[1:]),
      CPrated_floris),
    "w:",
    label="IEA-3.4MW-130m: $\\min(C_P, P_{\\mathrm{rated}}/P_{\\mathrm{fluid}})$"
  )
  ax.set_xlabel("hub-height farfield velocity, $V$ (m/s)")
  ax.set_ylabel("power_coefficient, $C_P(V)$ (-)")
  ax.legend()
  fig.savefig("single_turb_CPconv.png", dpi=300, bbox_inches="tight")

  fig, ax = plt.subplots()

  for df_power, label_case in zip(df_curves_collection, label_collection):
    ax.plot(
      df_power.V,
      (
        rho_fluid*df_power.P/Ps_fluid(df_power.V)
      )/np.interp(
        df_power.V,
        V_floris[1:],
        P_floris[1:]/1e3/Ps_fluid(V_floris[1:]),
      ),
      label=label_case,
    )

  ## thrust plot

  fig, ax = plt.subplots()

  for df_thrust, label_case in zip(df_curves_collection, label_collection):
    ax.plot(df_thrust.V, rho_fluid*df_thrust.Tf, label=label_case)
  # ax.plot(df_thrust_lo.V, rho_fluid*df_thrust_lo.Tf, label="$N_x=19$, $N_y=13$, $N_z=6$")
  # ax.plot(df_thrust_mid.V, rho_fluid*df_thrust_mid.Tf, label="$N_x=27$, $N_y=18$, $N_z=9$")
  # ax.plot(df_thrust_hi.V, rho_fluid*df_thrust_hi.Tf, label="$N_x=38$, $N_y=25$, $N_z=13$")
  ax.plot(
    V_floris,
    CT_floris*Ts_fluid(V_floris),
    "w--",
    label="IEA-3.4MW-130m reference",
  )
  ax.set_xlabel("hub-height farfield velocity, $V$ (m/s)")
  ax.set_ylabel("turbine thrust, $T(V)$ (kN)")
  ax.legend()
  fig.savefig("single_turb_Tconv.png", dpi=300, bbox_inches="tight")

  ## CT plot

  fig, ax = plt.subplots()

  for df_thrust, label_case in zip(df_curves_collection, label_collection):
    ax.plot(df_thrust.V, rho_fluid*df_thrust.Tf/Ts_fluid(df_thrust.V), label=label_case)
  # ax.plot(df_thrust_lo.V, rho_fluid*df_thrust_lo.Tf/Ts_fluid(df_thrust_lo.V), label="$N_x=19$, $N_y=13$, $N_z=6$")
  # ax.plot(df_thrust_mid.V, rho_fluid*df_thrust_mid.Tf/Ts_fluid(df_thrust_mid.V), label="$N_x=27$, $N_y=18$, $N_z=9$")
  # ax.plot(df_thrust_hi.V, rho_fluid*df_thrust_hi.Tf/Ts_fluid(df_thrust_hi.V), label="$N_x=38$, $N_y=25$, $N_z=13$")
  ax.plot(
    V_floris,
    CT_floris,
    "w--",
    label="IEA-3.4MW-130m reference",
  )
  ax.set_xlabel("hub-height farfield velocity, $V$ (m/s)")
  ax.set_ylabel("thrust coefficient, $C_T(V)$ (-)")
  ax.legend()
  fig.savefig("single_turb_CTconv.png", dpi=300, bbox_inches="tight")



### MULTI TURBINE CASE

if do_multi_turbine:
  # extract three levels of discretization
  # df_lo = pd.read_csv("../curves_nx19ny13nz06.csv", names=["V","P"])
  # # df_collection = [df_lo]
  df_curves_mid = pd.read_csv("../curves_multi.csv", names=["V","Ptot","P1","P2","P3"])
  df_curves_collection = [df_curves_mid]
  # df_hi = pd.read_csv("../curves_nx38ny25nz13.csv", names=["V","P"])
  # df_collection = [df_lo, df_mid, df_hi]

  # get FLORIS reference data
  maxV = np.max([np.max(df) for df in df_curves_collection])
  V_floris = np.array(data_FLORIS["power_thrust_table"]["wind_speed"])[data_FLORIS["power_thrust_table"]["wind_speed"] <= maxV]
  P_floris = np.array(data_FLORIS["power_thrust_table"]["power"])[data_FLORIS["power_thrust_table"]["wind_speed"] <= maxV]
  Vrated_floris = 9.812675420388173
  Prated_floris = 3622.3451711828
  CPrated_floris = Prated_floris*1e3/(0.5*data_FLORIS["power_thrust_table"]["ref_air_density"]*np.pi/4*data_FLORIS["rotor_diameter"]**2*Vrated_floris**3)

  rho_fluid = 1.225
  A_rotor = np.pi/4*130.0**2
  Ps_fluid = lambda V: 0.5*A_rotor*V**3/1e6

  ## power plot

  fig, ax = plt.subplots()

  # ax.plot(df_lo.V, df_lo.P, label="$N_x=19$, $N_y=13$, $N_z=6$")
  pt0 = ax.plot(df_curves_mid.V, df_curves_mid.Ptot/3, label="mid mesh, average")
  ax.plot(df_curves_mid.V, df_curves_mid.P1, "--", c= pt0[-1].get_color(), label="mid mesh, T1")
  ax.plot(df_curves_mid.V, df_curves_mid.P2, "--", c= pt0[-1].get_color(), label="mid mesh, T2")
  ax.plot(df_curves_mid.V, df_curves_mid.P3, "--", c= pt0[-1].get_color(), label="mid mesh, T3")
  # ax.plot(df_hi.V, df_hi.P, label="$N_x=38$, $N_y=25$, $N_z=13$")
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
  ax.set_ylabel("specific turbine power, $P(V)/\\rho$ ($10^6$ m$^5$/s$^3$)")
  ax.legend()
  fig.savefig("single_turb_Pconv.png", dpi=300, bbox_inches="tight")

  # ## CP plot
  #
  # fig, ax = plt.subplots()
  #
  # # # # ax.plot(df_lo.V, df_lo.P/Ps_fluid(df_lo.V), label="$N_x=19$, $N_y=13$, $N_z=6$")
  # ax.plot(df_mid.V, df_mid.P/Ps_fluid(df_mid.V), label="$N_x=27$, $N_y=18$, $N_z=9$")
  # # # # ax.plot(df_hi.V, df_hi.P/Ps_fluid(df_hi.V), label="$N_x=38$, $N_y=25$, $N_z=13$")
  # ax.plot(
  #   V_floris[1:],
  #   P_floris[1:]/data_FLORIS["power_thrust_table"]["ref_air_density"]/1e3/Ps_fluid(V_floris[1:]),
  #   "w--",
  #   label="IEA-3.4MW-130m reference",
  # )
  # ax.plot(Vrated_floris, CPrated_floris, "wo")
  # ax.plot(
  #   V_floris[1:],
  #   np.minimum(
  #     Prated_floris/1.225/1e3*np.ones_like(V_floris)[1:]/Ps_fluid(V_floris)[1:],
  #     CPrated_floris),
  #   "w:",
  #   label="IEA-3.4MW-130m: $\\min(C_P, P_{\\mathrm{rated}}/P_{\\mathrm{fluid}})$"
  # )
  # ax.set_xlabel("hub-height farfield velocity, $V$ (m/s)")
  # ax.set_ylabel("power_coefficient, $C_P(V)$ (-)")
  # ax.legend()
  # fig.savefig("single_turb_CPconv.png", dpi=300, bbox_inches="tight")

plt.show()
