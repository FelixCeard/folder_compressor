import glob
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm

import click

def compress_file(file: str, quality: int, path: Path, force: bool = False) -> None:
    source = path / file
    target = path / "compressed" / f"{Path(file).stem}.webp"

    # if the target file exists, skip it
    if target.exists() and not force:
        return

    subprocess.run(
        ["magick", str(source), "-quality", str(quality), str(target)],
        shell=False,
        check=True,
    )


@click.command()
@click.option('--path', default=None, help='Path to the folder to compress.')
@click.option('--extension', default="JPG", help='Extension of the files to compress.')
@click.option('--quality', default=75, help='Quality of the compressed files.')
@click.option('--max-workers', default=6, help='Maximum number of workers to use.')
@click.option('--force', is_flag=True, help='Force compression of existing files.')
def main(path: str = None, extension: str = "JPG", quality: int = 75, max_workers: int = 6, force: bool = False) -> None:
    if path is None:
        path = os.getcwd()
    path = Path(path)

    # find all files with extension
    files = glob.glob(f'*.{extension}', root_dir = path)
    print(f'Found {len(files)} files with extension {extension}')

    if len(files) == 0:
        return

    os.makedirs(path / "compressed", exist_ok=True)

    # compress the files using magick and in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(compress_file, file, quality, path, force) for file in files]
        for future in tqdm(as_completed(futures), total=len(futures), desc="Compressing files"):
            future.result()

if __name__ == "__main__":
    main()