# PhaseSpacePlot

![screenshot](screenshot.png)

## How to setup

```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip3 install Equation dearpygui numpy scipy clipboard
```

Your IDE may freak out because Equation is an old unmaintained lib. 
If you dont have Numpy installed in the virtual env, it should be ok.
In the case of errors with Equation library, go to the `.venv/lib/Equation/equation_base.py` and change `np.Inf` to `np.inf` and `np.NaN` to `np.nan` in the code.
