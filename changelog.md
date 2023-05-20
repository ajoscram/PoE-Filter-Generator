# 1.2.2
* `.econ` now supports uniques. More information can now be found on the [`.econ` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/.econ).
* `.econ` now supports any combination of Ruthless, Standard and Hardcore league flags. Keep in mind that less popular leagues might not have enough data. More information can now be found on the [`.econ` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/.econ).
* The `combine` handler was renamed to `choose`, because "combine" is too many letters and too confusing of a name. It was also changed to receive two integer values: one with the number of lines to combine and the size of each combination instead of setting an end tag.

# 1.2.1
* Fixed a `.import` bug which prevented the loading of filter files when importing.

# 1.2.0
* Added handler chaining, which allows application of multiple handlers in a row without having to invoke PFG multiple times
* Added the new `.combine` handler, which allows the creation of multiple blocks from a single one by creating combinations of lines within it
* Added the new `.index` handler, which allows creation an index of sections and subsections to quickly move around the filter
* Added the new `.format` handler, which removes rules, trailing whitespace and extraneous empty lines from the filter
* Removed all formatting done on `.import`. `.format` can now be invoked after performing imports to clean up the filter output

# 1.1.0
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

# 1.0.0
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