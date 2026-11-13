"""A hands-on introduction to Python file handling.

Run this file to see each example. It creates its sample files in a temporary
folder, so the examples cannot overwrite your own documents.

Common modes:
    "r"  read an existing file
    "w"  write; create or erase the file first
    "a"  append; create the file if needed
    "x"  create a new file; fail if it already exists
    "+"  allow both reading and writing (for example, "r+")
    "b"  binary data (for example, "rb"); use bytes, not text
    "t"  text data; this is the default (for example, "rt")
"""

from pathlib import Path
from tempfile import TemporaryDirectory

def main() -> None:
    with TemporaryDirectory(prefix="python-file-handling-") as folder:
        demo_folder = Path(folder)
        text_path = demo_folder / "demo.txt"

        print(f"Sample files are in a temporary folder: {demo_folder}\n")

        # "w" creates a file or clears it before writing. write() does not
        # add a newline, so include \n where you want one.
        print('1. Writing with "w"')
        with text_path.open("w", encoding="utf-8") as file:
            file.write("First line\n")
            file.write("Second line\n")
        print("Created demo.txt with two lines.\n")

        # "r" reads an existing text file. read() returns the remaining text
        # as one string.
        print('2. Reading with "r" and read()')
        with text_path.open("r", encoding="utf-8") as file:
            print(file.read(), end="")
        print()

        # These are three ways to read lines. A line usually includes its
        # trailing newline, so rstrip() makes printed output tidier.
        print("3. Reading lines")
        with text_path.open("r", encoding="utf-8") as file:
            print("readline():", repr(file.readline()))

        with text_path.open("r", encoding="utf-8") as file:
            print("readlines():", file.readlines())

        print("Iterating (good for large files):")
        with text_path.open("r", encoding="utf-8") as file:
            for line in file:
                print("  ", line.rstrip())
        print()

        # "a" adds text at the end and creates the file if it is missing.
        print('4. Appending with "a"')
        with text_path.open("a", encoding="utf-8") as file:
            file.write("Appended line\n")
        with text_path.open("r", encoding="utf-8") as file:
            print(file.read(), end="")
        print()

        # writelines() writes each string as-is; it does not add newlines.
        print("5. Writing a list of lines with writelines()")
        lines_path = demo_folder / "lines.txt"
        lines = ["Red\n", "Green\n", "Blue\n"]
        with lines_path.open("w", encoding="utf-8") as file:
            file.writelines(lines)
        print(lines_path.read_text(encoding="utf-8"), end="")
        print()

        # "x" is useful when overwriting an existing file would be a mistake.
        print('6. Creating safely with "x"')
        exclusive_path = demo_folder / "new_file.txt"
        with exclusive_path.open("x", encoding="utf-8") as file:
            file.write("This file was newly created.\n")
        try:
            exclusive_path.open("x", encoding="utf-8")
        except FileExistsError:
            print("Opening it with x again raises FileExistsError, as expected.\n")

        # "+" combines reading and writing. seek() moves the file position.
        print('7. Updating with "r+" and moving with seek()')
        update_path = demo_folder / "update.txt"
        update_path.write_text("Alpha\nBeta\n", encoding="utf-8")
        with update_path.open("r+", encoding="utf-8") as file:
            print("tell() at start:", file.tell())
            file.write("Omega")  # Replaces characters; it does not insert text.
            file.seek(0)
            print("Updated contents:", repr(file.read()))
        print()

        # "w+" allows reading and writing, but erases old contents on open.
        print('8. Reading and writing with "w+"')
        write_read_path = demo_folder / "write_read.txt"
        with write_read_path.open("w+", encoding="utf-8") as file:
            file.write("Written using w+.\n")
            file.seek(0)  # Writing moved the position; rewind before reading.
            print(file.read(), end="")
        print()

        # In "a+" mode, reads are allowed, but writes always go to the end.
        print('9. Reading and appending with "a+"')
        with text_path.open("a+", encoding="utf-8") as file:
            file.seek(0)
            print("Before append:", repr(file.read()))
            file.write("Appended using a+.\n")
            file.seek(0)
            print("After append:", repr(file.read()))
        print()

        # Binary mode is for bytes, such as image or PDF data. Do not pass
        # encoding= in binary mode.
        print('10. Binary files with "wb" and "rb"')
        binary_path = demo_folder / "sample.bin"
        original_bytes = b"\x00\x01\x02Hello"
        with binary_path.open("wb") as file:
            file.write(original_bytes)
        with binary_path.open("rb") as file:
            print("Read bytes:", file.read())
        print()

        # Missing files in "r" mode raise FileNotFoundError.
        print("11. Handling a common file error")
        missing_path = demo_folder / "does_not_exist.txt"
        try:
            missing_path.open("r", encoding="utf-8")
        except FileNotFoundError:
            print("Reading a missing file raises FileNotFoundError.")

        print("\nAll examples finished. The temporary files will now be removed.")


if __name__ == "__main__":
    main()