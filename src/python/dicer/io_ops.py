from pathlib import Path
import yaml

def read_yaml(file: Path|str) -> dict:
    with open(file, 'r') as f:
        return yaml.load(f, Loader=yaml.Loader)

def write_yaml(data: dict|list,
               file: Path|str,
               force: bool = False
               ):
    if Path(file).exists() and not force:
        raise FileExistsError()
    with open(file, 'w') as f:
        yaml.dump(data, f)
    return

def load_txt(file: str|Path) -> str:
    with open(file, 'r') as f:
        cont = f.read()
    return cont
