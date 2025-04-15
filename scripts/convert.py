import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.convert_utils import flatten_annotation_json
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert exported JSON to readable format")
    parser.add_argument("--input_json_path", type=str, required=True, help="Path to the exported JSON file")
    parser.add_argument("--output_dir_path", type=str, required=True, help="Path to save the output Directory")
    args = parser.parse_args()

    input_json_path = args.input_json_path
    output_dir_path = args.output_dir_path
    
    # Create the directory if it does not exist
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)
    
    # Get the file name from input path
    file_name = os.path.basename(input_json_path).split(".")[0]
    
    output_csv_path = os.path.join(output_dir_path, "formatted_{}.csv ".format(file_name))
    output_json_path = os.path.join(output_dir_path, "formatted_{}.json".format(file_name))

    # Convert the JSON file
    df = flatten_annotation_json(input_json_path, output_csv_path, output_json_path)