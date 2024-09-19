import math
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def load_and_process_data(file_path, fill_missing=False, fill_method='interpolate'):
    """
    Loads and processes the race car data file.
    
    Returns a reshaped DataFrame with time as index and each channel as a separate column.
    """
    # Read the file into a DataFrame
    df = pd.read_csv(file_path, sep='\t')
    
    # Pivot the table to have channels as columns, and time as index
    df_pivot = df.pivot(index='time', columns='channel', values='value')

    # Fill missing values if specified
    if fill_missing:
        if fill_method == 'interpolate':
            df_pivot.interpolate(method='linear', inplace=True)
        elif fill_method == 'ffill':
            df_pivot.ffill(inplace=True)
        elif fill_method == 'bfill':
            df_pivot.bfill(inplace=True)
    
    # Rename columns to 'Channel_1', 'Channel_2', etc.
    df_pivot.columns = [f'Channel_{int(col)}' for col in df_pivot.columns]
    
    # Compute Channel_7 = Channel_5 - Channel_4
    df_pivot['Channel_7'] = df_pivot['Channel_5'] - df_pivot['Channel_4']
    
    return df_pivot


def find_first_conditions(df):
    """
    Finds the first time where the specified conditions are met:
    1. Channel 2 < -0.5
    2. Channel 7 < 0
    3. Both conditions at the same time.
    
    Returns the times for each condition.
    """
    condition_1 = df['Channel_2'] < -0.5
    condition_2 = df['Channel_7'] < 0
    both_conditions = condition_1 & condition_2
    
    # Get the first time each condition is satisfied
    first_condition_1 = df[condition_1].index.min()
    first_condition_2 = df[condition_2].index.min()
    first_both_conditions = df[both_conditions].index.min()
    
    return first_condition_1, first_condition_2, first_both_conditions


def plot_conditions(df, title):
    """
    Plots the data for Channel 2 and Channel 7, highlighting where conditions are met.
    Condition 1: Channel 2 < -0.5
    Condition 2: Channel 7 < 0
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(16, 8))

    # Remove x-y pairs with missing values for each channel
    df_2 = df.dropna(subset=['Channel_2'])['Channel_2']
    df_7 = df.dropna(subset=['Channel_7'])['Channel_7']
    
    # Plot Channel 2 and Channel 7
    ax.plot(df_2.index, df_2, label='Channel_2', color='blue', alpha=0.7, marker='o')
    ax.plot(df_7.index, df_7, label='Channel_7', color='red', alpha=0.7, marker='o')
    
    # Highlight areas where the conditions are met
    condition_1 = df_2 < -0.5
    condition_2 = df_7 < 0
    
    # Fill between the conditions
    if fill_missing:
        ax.fill_between(df_2.index, df_2, -0.5, where=condition_1, color='blue', alpha=0.3, label='Channel_2 < -0.5', interpolate=True)
        ax.fill_between(df_7.index, df_7, 0, where=condition_2, color='red', alpha=0.3, label='Channel_7 < 0', interpolate=True)

    # Plot the threshold values
    ax.axhline(-0.5, color='blue', linestyle='--', alpha=0.5, label='Channel_2 Threshold')
    ax.axhline(0, color='red', linestyle='--', alpha=0.5, label='Channel_7 Threshold')

    # Plot the first time when both conditions are met
    _, _, first_conditions = find_first_conditions(df)
    ax.axvline(first_conditions, color='green', linestyle='--', alpha=0.5, label='First Both Conditions Met')
    if not math.isnan(first_conditions):
        ax.text(first_conditions, 0, str(first_conditions), color='green')

    # Labeling the plot
    if fill_missing:
        ax.set_title(f'Conditions Visualization - {title} - Fill Missing: {fill_method}')
    else:
        ax.set_title(f'Conditions Visualization - {title} - Fill Missing: {fill_missing}')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Channel Value')
    ax.legend()

    # Save the plot
    if fill_missing:
        plt.savefig(f'plots/{title.lower()}_{fill_method}.png', bbox_inches='tight')
    else:
        plt.savefig(f'plots/{title.lower()}_no_fill.png', bbox_inches='tight')


"""
Usage:

python main.py -i <input_file_path> -f -m <fill_method>

where:
    -i is the input data file path (required).
    -f is an optional flag to fill missing values (interpolate by default).
    -m is an optional argument to specify the fill method (interpolate, ffill, bfill).
"""
if __name__ == "__main__":
    # Define default file path and fill missing methods
    file_path = ''
    fill_missing = False
    fill_method = 'interpolate'

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='Input file path')
    parser.add_argument('-f', '--fill', action='store_true', help='Fill missing values')
    parser.add_argument('-m', '--method', type=str, help='Fill missing method (interpolate, ffill, bfill)')
    args = parser.parse_args()

    # Update file path and fill missing values if specified
    if args.input:
        file_path = args.input
    if args.fill:
        fill_missing = True
    if args.method:
        if args.method not in ['interpolate', 'ffill', 'bfill']:
            raise ValueError('Invalid fill method. Please choose from interpolate, ffill, bfill.')
        fill_method = args.method

    # Load and process data
    practice_df = load_and_process_data(file_path, fill_missing, fill_method)

    # Show the first few rows of the processed data for inspection
    print("Processed Data (First Few Rows):\n")
    print(practice_df.head(), '\n')

    # Find the first conditions for the data
    first_conditions_practice = find_first_conditions(practice_df)
    print("First Time Channel_2 < -0.5 is Met:", first_conditions_practice[0])
    print("First Time Channel_7 < 0 is Met:", first_conditions_practice[1])
    print("First Time Both Conditions are Met:", first_conditions_practice[2])

    # Plot the conditions for the data
    plot_conditions(practice_df, file_path)