
PYUIC=pyuic5
PFLAGS=

all: ui/main_design.py ui/setcaption_design.py ui/vessel_design.py

ui/%_design.py: ui/%.ui
	$(PYUIC) $(PFLAGS) $< -o $@

clean:
	rm ui/*.py
