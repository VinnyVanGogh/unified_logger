import click
import toml
from pathlib import Path
from typing import Optional, Dict, Tuple
import re

class VersionManager:
    def __init__(self, start_dir: Path = None):
        self.start_dir = start_dir or Path.cwd()
        self._pyproject_path = None
        self._config = None
        
    def find_pyproject(self) -> Optional[Path]:
        """Recursively find pyproject.toml."""
        current = self.start_dir
        while current != current.parent:
            pyproject = current / "pyproject.toml"
            if pyproject.exists():
                self._pyproject_path = pyproject
                return pyproject
            current = current.parent
        return None

    @property
    def config(self) -> Dict:
        if self._config is None and self.find_pyproject():
            self._config = toml.load(self._pyproject_path)
        return self._config

    def get_current_version(self) -> str:
        return self.config.get("tool", {}).get("poetry", {}).get("version", "0.1.0")

    def parse_version(self, version: str) -> Tuple[list, str, int]:
        match = re.match(r"(\d+\.\d+\.\d+)(([abc]|rc)(\d+))?", version)
        if not match:
            raise ValueError(f"Invalid version: {version}")
        
        base = match.group(1)
        pre_type = match.group(3) or ""
        pre_num = int(match.group(4)) if match.group(4) else 0
        
        return ([int(x) for x in base.split(".")], pre_type, pre_num)

    def get_next_version(self, current: str) -> str:
        """Calculate next version based on semantic versioning rules."""
        base_nums, pre_type, pre_num = self.parse_version(current)
        
        # Version progression logic
        if not pre_type:  # Regular version
            base_nums[-1] += 1
            return f"{'.'.join(map(str, base_nums))}a1"
            
        # Pre-release progression
        stages = ["a", "b", "rc", ""]
        current_stage_idx = stages.index(pre_type)
        
        if current_stage_idx == len(stages) - 1:
            # At final stage, increment version
            base_nums[-1] += 1
            return f"{'.'.join(map(str, base_nums))}a1"
            
        next_stage = stages[current_stage_idx + 1]
        base_ver = ".".join(map(str, base_nums))
        
        # Either move to next stage or increment current stage number
        if pre_num >= 3 and next_stage:  # Max 3 versions per stage
            return f"{base_ver}{next_stage}1"
        return f"{base_ver}{pre_type}{pre_num + 1}"

    def update_version(self, new_version: str) -> bool:
        if not self._pyproject_path:
            return False
            
        self.config["tool"]["poetry"]["version"] = new_version
        with open(self._pyproject_path, "w") as f:
            toml.dump(self.config, f)
        return True

@click.group()
def cli():
    """Version management for Python projects."""
    pass

@cli.command()
def check():
    """Check current and next version."""
    manager = VersionManager()
    if not manager.find_pyproject():
        click.echo("No pyproject.toml found")
        return
    
    current = manager.get_current_version()
    next_ver = manager.get_next_version(current)
    click.echo(f"Current: {current} → Next: {next_ver}")

@cli.command()
@click.option('--dry-run', is_flag=True, help="Preview changes without applying")
def next(dry_run):
    """Increment to next version."""
    manager = VersionManager()
    if not manager.find_pyproject():
        click.echo("No pyproject.toml found")
        return
    
    current = manager.get_current_version()
    next_ver = manager.get_next_version(current)
    
    if dry_run:
        click.echo(f"Would update: {current} → {next_ver}")
        return
        
    if manager.update_version(next_ver):
        click.echo(f"Updated: {current} → {next_ver}")
    else:
        click.echo("Update failed")

if __name__ == "__main__":
    cli()