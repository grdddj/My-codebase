from pathlib import Path

HERE = Path(__file__).resolve().parent

to_rename = HERE / "lichess" / "black_with_mate"

for index, file in enumerate(Path(to_rename).rglob("*.png"), start=1):
    new_name = f"{index:04}.png"
    file.rename(to_rename / new_name)
