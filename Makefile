.PHONY: install icp qualify sequence export test

install:
	pip install -e .

# --- full workflow shortcuts ---
icp:
	origami icp https://www.scriptmasterlabs.com

campaigns:
	origami campaigns

qualify:
	origami qualify 1

sequence:
	origami sequence 1

export:
	origami export 1

# run all five steps end-to-end (after placing leads.csv)
run: icp campaigns qualify sequence export

test:
	python -m pytest tests/ -v
