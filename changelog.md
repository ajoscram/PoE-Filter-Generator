# To do
* Investigate why standard hardcore is not supported on poe.ninja
* Add a mechanism to emit warnings and return no block on econ if base_types is empty.
* Investigate what happens when two equivalent styles are added to the same block. This could be helpful in deciding how to hide and show blocks

# 1.2
* Added the new `.combine` handler, which allows the creation of multiple blocks from a single one by creating combinations of lines within it
* Added the new `.format` handler, which removes rules, empty lines and trailing whitespace from the filter
* Removed all formatting done on `.import`. `.format` can now be invoked after performing imports to clean up the filter output

# 1.1
* Renamed sections to blocks as that's the GGG standard name
* Refactored and cleaned up the code significantly, so that future work is simpler
* Added `Filter` and `Line` as new abstractions to provide more flexibility and code reuse to handlers
* Used single underscore for private instead of double underscore throughout the codebase
* `.econ` now supports invitations, vials and delirium orbs
* `.econ` now comments out blocks if no `BaseType`s are found for the rule parameters
* Added the new `.import` handler, which allows importing of entire filters, blocks, or lines within blocks
* Replaced `.chaos` with `.tag`, a much more generic version of the same idea
* Added wildcards to the `.tag` rule
* Added a way to comment out rules so the generator ignores them
* Updated the documentation on GitHub with the new stuff

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
* Atomized write operations on the same filter file
* Added help on generate.py