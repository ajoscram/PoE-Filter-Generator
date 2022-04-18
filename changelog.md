# To do
* Investigate why standard hardcore is not supported on poe.ninja

# 1.1
* `.econ` now supports invitations, vials and delirium orbs
* `.econ` now comments out blocks if no `BaseType`s are found for the rule parameters
* Added the new `.import` handler, which allows importing of entire filters, blocks, or lines within blocks
* Replaced `.chaos` with `.tag`, a much more generic version of the same idea
* Added `Filter` and `Line` as new abstractions to provide more flexibility and code reuse to handlers.
* Renamed sections to blocks as that's the GGG standard name
* Refactored and cleaned up the code significantly, so that future work is simpler
* Used single underscore for private instead of double underscore

# 1.0
* Included the requests library
* Added the Section class
* Added the Rule class
* Added the Generator class
* Added the generate.py script, used to run the program. Calls should look like:
```        
python generator.py "input_and_output.filter" .strict 3
python generator.py "input.filter" "output.filter" .chaos
```
* Added a strictness handler (strictness.py)
* Added a chaos recipe handler (chaos.py)
* Added an economy handler (econ.py)
* Documented every module
* Atomized write operations on the same filter file.
* Added help on generate.py