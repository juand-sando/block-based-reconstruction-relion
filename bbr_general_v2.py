import sys
import pandas as pd
import numpy as np
import starfile
from scipy.spatial.transform import Rotation
from pathlib import Path
import copy

# Function to calculate rotation matrix
def zyz_euler_rotation_matrix(rot, tilt, psi):
    rotation_direct = Rotation.from_euler('ZYZ', [rot, tilt, psi], degrees=True)
    rotation_matrix = rotation_direct.inv()
    return rotation_matrix

# Read star file
def read_star_file(filename):
    return starfile.read(filename)

# Write star file
def write_star_file(df, output):
    starfile.write(df, output)

# Invert handedness
def invert_hand(df):
    df_invert_hand = copy.deepcopy(df)
    df_invert_hand['rlnAngleRot'] = [-x for x in df_invert_hand['rlnAngleRot']]
    df_invert_hand['rlnAngleTilt'] = [180 - x for x in df_invert_hand['rlnAngleTilt']]
    return df_invert_hand

# Function to filter particles outside the micrograph
def filter_particles_outside_micrograph(particles_df, micrograph_size):
    mask = (particles_df['rlnCoordinateX'] < micrograph_size) & \
           (particles_df['rlnCoordinateX'] > 0) & \
           (particles_df['rlnCoordinateY'] < micrograph_size) & \
           (particles_df['rlnCoordinateY'] > 0)
    filtered_particles_df = particles_df[mask]
    deleted_count = len(particles_df) - len(filtered_particles_df)
    return filtered_particles_df, deleted_count

# Perform calculations
def perform_calculations(particles_df, optics_df, delta_vector):
    # Create a dictionary to store pixel sizes for each optics group
    pixel_sizes = {}

    # Iterate over optics_df to retrieve pixel sizes for each optics group
    for index, row in optics_df.iterrows():
        optics_group = row['rlnOpticsGroup']
        ori_pix = row['rlnImagePixelSize']
        microg_pix = row['rlnMicrographOriginalPixelSize']
        pixel_sizes[optics_group] = {'ori_pix': ori_pix, 'microg_pix': microg_pix}

    # Iterate over particles_df to modify coordinates based on optics group
    for index, row in particles_df.iterrows():
        optics_group = row['rlnOpticsGroup']
        ori_pix = pixel_sizes[optics_group]['ori_pix']
        microg_pix = pixel_sizes[optics_group]['microg_pix']

        rot_angle = row['rlnAngleRot']
        tilt_angle = row['rlnAngleTilt']
        psi_angle = row['rlnAnglePsi']

        rotation_matrix = zyz_euler_rotation_matrix(rot_angle, tilt_angle, psi_angle)
        rot_vector = rotation_matrix.apply(delta_vector)

        new_vector = rot_vector * (ori_pix / microg_pix)
        new_x = row['rlnCoordinateX'] + float(new_vector[0])
        new_y = row['rlnCoordinateY'] + float(new_vector[1])
        new_defocusU = row['rlnDefocusU'] + float(new_vector[2] * microg_pix)
        new_defocusV = row['rlnDefocusV'] + float(new_vector[2] * microg_pix)

        particles_df.at[index, 'rlnCoordinateX'] = new_x
        particles_df.at[index, 'rlnCoordinateY'] = new_y
        particles_df.at[index, 'rlnDefocusU'] = new_defocusU
        particles_df.at[index, 'rlnDefocusV'] = new_defocusV

    return particles_df

# Function to print inputs to a log file
def print_log_file(filename, delta_vector, letter, hand_option, micrograph_size):
    log_filename = filename.parent / f"{filename.stem}_logfile.block{letter}.txt"
    with open(log_filename, 'w') as f:
        f.write("Input Log:\n")
        f.write(f"Star file: {filename}\n")
        f.write(f"Delta vector: {delta_vector}\n")
        f.write(f"Block name (LETTER): {letter}\n")
        f.write(f"Hand option: {hand_option}\n")
        f.write(f"Micrograph size: {micrograph_size}\n")
    print(f"Input log file saved as {log_filename}")


# Main function
def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <star file>")
        sys.exit(1)

    filename = Path(sys.argv[1])

    # Prompt the user to input delta vector
    while True:
        try:
            delta_x, delta_y, delta_z = map(int, input("Enter the delta vector (format: <X> <Y> <Z>), in particle pixel, separated by spaces: ").split())
            break
        except ValueError:
            print("Invalid input. Please enter integers.")

    # Prompt the user to input block name
    letter = input("Enter the block name (LETTER): ")

    delta_vector = np.array([delta_x, delta_y, delta_z])

    df = read_star_file(filename)

    particles_df = df['particles'].copy()
    optics_df = df['optics'].copy()

    output_suffix = f".block{letter}.bbr.star"

    while True:
        hand_option = input("Enter 1 to run with the current hand, 2 to invert hand, or 3 to run with both hands: ")
        if hand_option in ['1', '2', '3']:
            hand_option = int(hand_option)
            break
        else:
            print("Invalid input. Please enter 1, 2, or 3.")

    # Prompt the user to input micrograph size
    while True:
        try:
            micrograph_size = int(input("Enter the micrograph size: "))
            if micrograph_size <= 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a positive integer for micrograph size.")

    if hand_option == 2 or hand_option == 3:
        inverted_particles_df = invert_hand(particles_df)
        inverted_particles_df = perform_calculations(inverted_particles_df, optics_df, delta_vector)
        filtered_inverted_particles_df, deleted_count = filter_particles_outside_micrograph(inverted_particles_df, micrograph_size)
        print(f"For outputted data file {filename.with_suffix(output_suffix.replace('.star', '.hand2.star'))}, "
              f"{deleted_count} subparticles were deleted because they lie outside the micrograph.")
        df['particles'] = filtered_inverted_particles_df
        write_star_file(df, filename.with_suffix(output_suffix.replace(".star", ".hand2.star")))

    if hand_option == 1 or hand_option == 3:
        particles_df = perform_calculations(particles_df, optics_df, delta_vector)
        filtered_particles_df, deleted_count = filter_particles_outside_micrograph(particles_df, micrograph_size)
        print(f"For outputted data file {filename.with_suffix(output_suffix.replace('.star', '.hand1.star'))}, "
              f"{deleted_count} subparticles were deleted because they lie outside the micrograph.")
        df['particles'] = filtered_particles_df
        write_star_file(df, filename.with_suffix(output_suffix.replace(".star", ".hand1.star")))
    
    # Print inputs to a log file
    print_log_file(filename, delta_vector, letter, hand_option, micrograph_size)


if __name__ == "__main__":
    main()

