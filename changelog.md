# 1.4.7
* Added item level support for **Allflame Embers**. In other words, `ItemLevel` constraints in the block where a `.econ mbr` rule is declared are taken into consideration when selecting the `BaseType`s for the block. 

# 1.4.6
* Fixed a bug where the program would crash if a league name could not be resolved from GGGs list of leagues. This is often the case when asking for temp league economic values between leagues.
* Added `.econ` support for **Allflame Embers**. Note that even though Filled Coffins were added to poe.ninja, they cannot be discriminated filter-wise.

# 1.4.5
* Added the `:watch` command, which allows automatic execution of the `:generate` command when `.filter` files are changed. More information can be found on the [`:watch` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/:watch).

# 1.4.4
* `.econ` now always overrides the `BaseType` rules in the block, even if no applicable base types are found. This case always comments out the block regardless.
* Fixed a bug where the `pfg.exe` and `update.exe` executables would appear to exit successfully when an error occurred, as opposed to exiting with an appropriate error code.  

# 1.4.3
* Fixed a bug where the updater could not handle double quotes (`"`) in the release notes text.
* Fixed a bug where the cache couldn't have emojis written to it.

# 1.4.2
* Fixed a bug where getting text values from a line with `=` or empty operator yielded the opposite result of what was intended.
* Fixed a bug where not all lines with the same condition in a block were accounted for if any of them had no values.
* Fixed a bug where item classes could not be found for most `.econ` mnemonic `BaseType`s.
* Removed `.econ` "support" for beasts, as it never actually worked properly.

# 1.4.1
* Added **Omens** and **Tattoos** to `.econ`.
* Added a caching system to significantly improve performance for web requests.
* Added a `.game` handler, which allows pulling game data into the filter. More information can be found on the [`.game` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/.game).
* Added a `:clean` command which allows for manual deletion of the cache. More information can be found on the [`:clean` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/:clean).
* The `:help` command now displays a list of the terms that can be queried with it after displaying [the Usage article](https://github.com/ajoscram/PoE-Filter-Generator/wiki/Usage).
* The `:path` command now supports an argument called `remove`, which removes the directory where the PFG executable resides from the PATH environment variable.
* Fixed a bug where empty strings (`""`) could not count as admissible values in filter lines.
* Moved from using the PoE Wiki to [RePoE](https://lvlvllvlvllvlvl.github.io/RePoE) for the primary game data source.
* Moved to Python 3.12.

# 1.4.0
* Added commands, which are now the primary unit of execution for this tool instead of handlers. Command names start with a colon (`:`).
* Added the `:generate` command, which performs all filter generation. This command is also implied if it is not provided, so previous PFG invocations work the same way as they did. More information can be found on the [`:generate` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/:generate).
* Added the `:help` command, which provides information for a term found within the PFG wiki (commands, handlers, blocks, rules, etc). More information can be found on the [`:help` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/:help).
* Added the `:path` command, which adds the tool's current path to the user's Windows PATH environment variable. More information can be found on the [`:path` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/:path).
* Added the `:update` command, which updates the tool to the most recent version available. More information can be found on the [`:update` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/:update).
* Revamped the visuals of the tool with different colors to provide context to messages shown on the console.
* Implemented a system to show contextual usage hints for a user when an error happens.

# 1.3.0
* `.econ` now supports uniques. More information can now be found on the [`.econ` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/.econ).
* `.econ` now supports any combination of Ruthless, Standard and Hardcore league options. Keep in mind that less popular leagues might not have enough data. More information can now be found on the [`.econ` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/.econ).
* The `.combine` handler was renamed to `.choose`, because "combine" is too many letters and too confusing of a name. It was also changed to receive two integer values: one with the number of lines to combine and the size of each combination instead of setting an end tag.
* Implemented the `.if` handler, which allows omission of lines if a pattern is not found in the block declaring `.if` rules. More information can be found on the [`.if` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/.if).
* Implemented the `.alias` handler, which allows reuse of text via a name. More information can be found on the [`.alias` wiki page](https://github.com/ajoscram/PoE-Filter-Generator/wiki/.alias).

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