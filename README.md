# Block-Based Reconstruction for RELION 3.1+

This repository contains a single script, `bbr_relion_3-1.py`, for preparing block-based subparticle coordinates in RELION after refinement with imposed symmetry followed by symmetry expansion.

This is a simple RELION implementation of the block-based reconstruction idea described in:

Zhu D, Wang X, Fang Q, Van Etten JL, Rossmann MG, Rao Z, Zhang X. "Pushing the resolution limit by correcting the Ewald sphere effect in single-particle Cryo-EM reconstructions." Nature Communications 9, 1552 (2018). https://www.nature.com/articles/s41467-018-04051-9

In this workflow, the script applies a user-defined delta vector to each symmetry-expanded particle, updates the particle coordinates, updates `rlnDefocusU` and `rlnDefocusV` for the shifted block position, removes particles that fall outside the micrograph boundaries, and writes new STAR outputs for downstream extraction.

## Intended Use

Use this script on a RELION particle STAR file:

- after refinement with imposed symmetry
- after symmetry expansion
- before particle extraction for focused subparticle refinement

After this program is run, use the output STAR file as the input for particle extraction, then continue with further focused subparticle refinement in RELION.

## Requirements

Install Python 3 and these packages:

```bash
pip install numpy pandas scipy starfile
```

## Run

```bash
python3 bbr_relion_3-1.py path/to/particles.star
```

The script will prompt for:

- delta vector `X Y Z` in particle pixels
- block name
- hand/correction option
- micrograph size

## What The Script Changes

For each particle, the script:

- rotates the input delta vector using the particle Euler angles
- shifts `rlnCoordinateX` and `rlnCoordinateY`
- updates `rlnDefocusU` and `rlnDefocusV` based on the rotated Z component, unless option 4 is selected
- filters out shifted particles that move outside the micrograph

The hand/correction options are:

- `1`: current hand with defocus correction
- `2`: inverted hand with defocus correction
- `3`: both hands with defocus correction
- `4`: current hand without defocus correction; coordinates are still shifted and particles outside the micrograph are still removed

## Output

Depending on the hand option, the script writes one or both of:

- `particles.block<LETTER>.bbr.hand1.star`
- `particles.block<LETTER>.bbr.hand2.star`
- `particles.block<LETTER>.bbr.hand1_no_defocus.star`

It also writes:

- `particles_logfile.block<LETTER>.txt`
