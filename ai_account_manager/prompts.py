import os
import sys


def move_selection(index: int, direction: str, size: int) -> int:
    if size < 1:
        raise ValueError("selection needs at least one option")
    if direction == "up":
        return (index - 1) % size
    if direction == "down":
        return (index + 1) % size
    return index


def _numbered_prompt(prompt: str, options: list[str], input_stream, output_stream) -> str:
    output_stream.write(prompt + "\n")
    for number, option in enumerate(options, 1):
        output_stream.write(f"  {number}) {option}\n")
    output_stream.flush()
    answer = input_stream.readline().strip()
    try:
        return options[int(answer) - 1]
    except (ValueError, IndexError) as exc:
        raise ValueError("invalid menu selection") from exc


def select_option(prompt: str, options: list[str], input_stream=sys.stdin, output_stream=sys.stdout) -> str:
    if not options:
        raise ValueError("options cannot be empty")
    if not input_stream.isatty() or not output_stream.isatty():
        return _numbered_prompt(prompt, options, input_stream, output_stream)
    if os.name == "nt":
        import msvcrt

        def read_key():
            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                return {"H": "up", "P": "down"}.get(msvcrt.getwch(), "")
            return "enter" if key == "\r" else key
    else:
        import termios
        import tty

        def read_key():
            old_settings = termios.tcgetattr(input_stream.fileno())
            try:
                tty.setraw(input_stream.fileno())
                key = input_stream.read(1)
                if key == "\x1b" and input_stream.read(1) == "[":
                    return {"A": "up", "B": "down"}.get(input_stream.read(1), "")
                return "enter" if key in ("\r", "\n") else key
            finally:
                termios.tcsetattr(input_stream.fileno(), termios.TCSADRAIN, old_settings)

    index = 0
    output_stream.write(prompt + "\n")
    while True:
        output_stream.write("\033[2K\r  " + "  ".join(
            f"[{option}]" if position == index else option for position, option in enumerate(options)
        ))
        output_stream.flush()
        key = read_key()
        if key == "enter":
            output_stream.write("\n")
            return options[index]
        index = move_selection(index, key, len(options))
