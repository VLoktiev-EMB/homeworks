# Electrical calculation catalog

This catalog is the selection aid REPORT-04 asks for. It lists the calculation families an
embedded homework commonly needs, each with a stable id, so a report can name the family it
used and a reader can reproduce the result.

The catalog is a human tool, not a machine contract. The checker validates the calculation
table's eight columns and the non-empty `Input provenance`, `Result`, `Uncertainty`, and
`Assumption effect` cells; it never checks whether a row names one of the families below
(D-24). Choosing the relevant set is the author's judgment, recorded in the report.

## How to use this catalog

1. Read the design and list every quantity a reviewer would want to verify.
2. Match each quantity to the closest family below. A family that recurs across a design is a
   row in the calculation table; a family the design does not exercise is not a row.
3. Record the family id in the `Quantity` or `Formula` cell so the report states what was
   selected.
4. Copy the family's input provenance, uncertainty method, and assumption sensitivity into the
   matching columns, replacing the generic wording with the actual values and sources.

A calculation row that does not fit a family is still valid: state the formula, the units, the
provenance of every input, the uncertainty basis, and the assumption it depends on. The
families are a starting set, not a closed one.

## CALC-01 — Series resistor for an LED

**Formula.** `R = (V_s - V_f) / I`, then choose the nearest standard resistor value at or above
the result.

**Units.** Volts for the supply and forward voltage, amperes for the current, ohms for the
resistor.

**Input provenance.** `V_s` from the datasheet or a measurement of the rail; `V_f` from the LED
datasheet at the intended current; `I` a design choice bounded by the LED rating and the pin
limit. State which input is still pending a measurement.

**Uncertainty method.** A tolerance stack: sum the absolute contributions of the supply
tolerance, the forward-voltage spread, and the resistor tolerance, then divide by the current.
Report each contribution, or the single resulting bound when the parts are not independent.

**Assumption sensitivity.** Rounding up to a standard value lowers the current; a lower forward
voltage raises it, so state the forward-voltage assumption the result depends on.

## CALC-02 — LED operating current from supply, forward voltage, and resistance

**Formula.** `I = (V_s - V_f) / R`.

**Units.** Volts for the two voltages, ohms for the resistance, milliamperes for the current.

**Input provenance.** `V_s` and `V_f` from the datasheet or a measurement; `R` from the fitted
part and its tolerance. A calculation that depends on CALC-01 names the row it uses.

**Uncertainty method.** A tolerance stack over the two voltages and the resistor tolerance.
When a meter supplied a voltage, use its accuracy instead of the nominal tolerance.

**Assumption sensitivity.** A smaller forward voltage raises the current; a larger resistance
lowers it. State whether the result is a design target or a measured operating point.

## CALC-03 — Resistor power dissipation

**Formula.** `P = I^2 * R`.

**Units.** Amperes for the current, ohms for the resistance, milliwatts for the result.

**Input provenance.** `I` from the relevant CALC-02 row; `R` from the fitted part. Both are
calculated values until a measurement replaces them.

**Uncertainty method.** A tolerance stack dominated by the current, because the current is
squared; state the current uncertainty explicitly rather than adding a fixed margin.

**Assumption sensitivity.** A lower forward voltage raises both the current and the power, so
state the worst-case forward voltage and compare the result with the part rating.

## CALC-04 — Off-state reverse voltage across a dark LED

**Formula.** `V_r = V_s - V_f` when the opposite element is conducting and clamps the shared
node.

**Units.** Volts.

**Input provenance.** `V_s` from the datasheet or a measurement; `V_f` from the conducting
LED's datasheet; the reverse rating from the dark LED's datasheet.

**Uncertainty method.** A tolerance stack over the two voltages, or a datasheet bound when the
worst case is the rating rather than the nominal value.

**Assumption sensitivity.** The result holds only while the opposite LED conducts; a
high-impedance state floats the node, so state whether the calculation applies to that state.

## CALC-05 — Timing period from a base and rational holds

**Formula.** `T = base * sum(n_i / d_i)` over the holds in one frame, with `base` the tick
period.

**Units.** Milliseconds for the base and the period; the holds are dimensionless rationals.

**Input provenance.** The base and the holds from the firmware tables; the loop tick from the
implementation or a measurement. Name the source file or table.

**Uncertainty method.** The table-level period is exact as designed; the realized period adds
one loop tick of quantization, so state the tick and whether it was measured.

**Assumption sensitivity.** A loop period close to the shortest half-hold stretches the fastest
pattern, so state the assumption that bounds the loop period.

## CALC-06 — GPIO or pin current margin against an absolute maximum

**Formula.** `margin = I_max - I` and `utilization = I / I_max * 100`.

**Units.** Milliamperes for the currents and margin, percent for the utilization.

**Input provenance.** `I_max` from the datasheet absolute-maximum rating; `I` from the relevant
CALC-02 row. The maximum is a datasheet limit, never a measured value.

**Uncertainty method.** The current uncertainty from CALC-02 propagates to the margin; the
datasheet maximum is a bound, not a distribution, so report it as a limit.

**Assumption sensitivity.** A lower forward voltage raises the current and lowers the margin;
state the worst-case forward voltage and the resulting utilization.

## CALC-07 — Voltage divider for a sense input

**Formula.** `V_out = V_in * R2 / (R1 + R2)`, with `R1` from the source to the tap and `R2`
from the tap to ground.

**Units.** Volts for the input and output, ohms for the two resistors.

**Input provenance.** `V_in` from the datasheet or a measurement; `R1` and `R2` from the fitted
parts and their tolerances; the input threshold from the datasheet.

**Uncertainty method.** A tolerance stack over both resistors and the source voltage. When the
tap feeds an ADC, add the ADC reference and quantization contributions.

**Assumption sensitivity.** The divider loads the source and shifts the tap; state whether the
source impedance is small enough for the chosen resistors.

## CALC-08 — Pull-up or pull-down sizing from leakage and threshold

**Formula.** `R_max = (V_s - V_ih) / I_leak` for a pull-up, or `R_max = V_il / I_leak` for a
pull-down, where `V_ih` and `V_il` are the datasheet input thresholds.

**Units.** Volts for the thresholds and supply, amperes for the leakage, ohms for the resistor.

**Input provenance.** `V_ih` or `V_il` and `I_leak` from the datasheet; `V_s` from the
datasheet or a measurement. The chosen resistor is a design choice below the bound.

**Uncertainty method.** A datasheet bound: the leakage and threshold are limits, so the result
is a worst-case maximum rather than a nominal value. Add the resistor tolerance when the chosen
value is close to the bound.

**Assumption sensitivity.** Leakage rises with temperature and with the number of shared
inputs; state the temperature or fan-out assumption the bound relies on.

## Selecting the relevant set

Pick every family the design actually exercises. The 1.3 police-flasher, for example, selects
CALC-01 through CALC-06: a series resistor, its current, its power, the off-state reverse
voltage, the pattern period, and the pin margin. A design with a sense input adds CALC-07; a
design with a button or a shared bus adds CALC-08.

Record the rest as not applicable in the report's calculation table rather than omitting the
table. The table always exists; an unselected family is a design statement, not a gap.
