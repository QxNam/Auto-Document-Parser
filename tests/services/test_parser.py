import io
from adp.services.parse.parse import Parse
from argparse import ArgumentParser

def get_file_obj_from_path(path: str) -> io.BytesIO:
    with open(path, "rb") as f:
        buf = io.BytesIO(f.read())
    buf.seek(0)
    print(f"Loaded file from {path}, size: {buf.getbuffer().nbytes} bytes")
    return buf

def test_parse(args):
    parser = Parse()
    file_obj = get_file_obj_from_path(args.file_path)
    result = parser.parse(file_obj=file_obj, file_name=args.file_name)
    output_path = "output_result.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result) 
    print(f"--- saved to: {output_path} ---")
    print("Parsed Result:\n", result[:200])  # Print first 200 characters of the result

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--file-path", type=str, help="Path to the input file to parse")
    parser.add_argument("--file_name", type=str, help="Name of the input file to parse")
    args = parser.parse_args()
    test_parse( args)