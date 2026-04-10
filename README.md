# BBR RELION Script

This repository contains a single script:

- `bbr_general_v2.py`

It applies a BBR delta vector to particles in a RELION STAR file, can optionally invert handedness, removes particles shifted outside the micrograph, and writes new STAR outputs.

## Requirements

Install Python 3 and these packages:

```bash
pip install numpy pandas scipy starfile
```

## Run

```bash
python3 bbr_general_v2.py path/to/particles.star
```

The script will prompt for:

- delta vector `X Y Z`
- block name
- hand option
- micrograph size

## Output

Depending on the hand option, the script writes one or both of:

- `particles.block<LETTER>.bbr.hand1.star`
- `particles.block<LETTER>.bbr.hand2.star`

It also writes:

- `particles_logfile.block<LETTER>.txt`

## Suggested GitHub Layout

Keep the repository minimal:

- `bbr_general_v2.py`
- `README.md`

That is enough if the goal is for users to download the script and run it on their own data.
