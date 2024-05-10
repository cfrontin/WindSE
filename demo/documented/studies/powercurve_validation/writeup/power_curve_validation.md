
# WindSE Power Curve Validation

`WindSE` has the ability to feather thrust and power coefficients in order to emulate a controlled turbine through multiple regions of the power curve.
In this study, we will validate the power curve behavior in isolation and with multiple inline turbines.
We consider the discretization dependence of the `WindSE` results, and the comparison of `WindSE` power estimates compared to other tools.

## Single turbine: discretization dependence

In this section we compare the `WindSE` results to the canonical IEA 3.4MW 130m turbine's power curve that is an input to `FLORIS`.

![Power curve convergence plot](single_turb_Pconv.png)

FLORIS includes cut-in behavior that is not modeled in region I or region I.5.
Comparison with the standard IEA-3.4MW-130m power curve used for FLORIS demonstrates similar power behavior in region II, with an apparent overprediction of $C_P$.
The FLORIS curve does not have thrust-peak shaving, while the `WindSE` power curve does, so there is a power mismatch in region II.5.
In region III, there appears to be a slight overprediction of power.

![$C_P$ curve convergence plot](single_turb_CPconv.png)

Plotting the power coefficient indicates that $C_P$ is in fact initially overpredicted in region II, and moreover $C_P$ is not quite constant in region II.
As noted previously, region II.5 is not modeled in the FLORIS power curve, but long run behavior of $C_P$ appears to be accurate, in region III.

## Multi-turbine: discretization dependence

TO DO!

## Single turbine: multi-tool comparison

TO DO!

## Multi-turbine: multi-tool comparison

TO DO!

<!-- -->
