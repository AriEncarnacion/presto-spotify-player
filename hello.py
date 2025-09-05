from presto import Presto

presto = Presto()

display = presto.display

COLOR = display.create_pen(48, 241, 209)

display.set_pen(COLOR)
display.text("Hello I am Presto", 0, 0)
presto.update()