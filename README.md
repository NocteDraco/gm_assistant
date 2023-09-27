# General instructions

Command to generate in-directory outputs
```bash
python make_llm_text.py test_rules.txt 2 --party_size 5
```




## Output files

If the `output` parameter is set to `example.txt` then the user should have the following output files:

- `example.txt`
- `example.stats.csv`
- `example.rules.txt`
- `example.fam.txt`

In their output directory.

.txt files:

These are all creature descriptions meeting the filters set by the user.

.stats.csv files:

These are creature stats with no description.

.rules.txt files:

These are encounter rules adjusted for party size.

.fam.txt files:

These are creature family descriptions for all families meeting the filters set by the user.

## Example commands

```bash
python make_llm_text.py D:\02-gm_assistant_output\test_prompt.txt 3 --party_size 5 --max_creatures 25
```