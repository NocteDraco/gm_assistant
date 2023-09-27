# General instructions

Command to generate in-directory outputs
```bash
python make_llm_text.py test_rules 2 --party_size 5
```


## Output files

Output files are dated to the second with the following extensions.

- `.llm.crtdsc.txt`
- `.llm.crtstats.csv`
- `.llm.famdsc.txt`
- `.llm.llmprompt.txt`
- `.llm.rules.txt`

In their output directory.

.llm.crtdsc.txt files:

These are all creature descriptions meeting the filters set by the user.

.llm.crtstats.csv files:

These are creature stats with no description.

.llm.famdsc.txt files:

These are encounter rules adjusted for party size.

.llm.rules.txt files:

These are creature family descriptions for all families meeting the filters set by the user.

## Example commands

```bash
python make_llm_text.py D:\02-gm_assistant_output\ 3 --party_size 5 --max_creatures 25
```