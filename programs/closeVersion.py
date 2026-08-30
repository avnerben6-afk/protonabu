""" Module: Protonabu Project Development
    - Product: Protonabu Utility Programs Package
    - Author: Avner Ben
        - Created: 5-Jun-2026
        - Revised: 9-Jun-2026
    - Producer: Antigravity (Gemini 3.1 Pro)
        - Produced: 5-Jun-2026
    - Generator: Protonabu 0.9.5
        - Generated: 5-Jun-2026
    - Generator: Antigravity (Gemini 3.5 Flash)
        - Improved: 6-Jun-2026
        - Improved: 11-Jun-2026
            - Strip double quotes from git status filepaths to handle paths with spaces/parentheses
"""

from typing import Any
import os
import re
from pathlib import Path
import subprocess
import semver
import argparse

class GitVersionControl:
    """ Git Version Control
        - Purpose: Wrapper for git operations to support dry-run and encapsulation 
    """
    def __init__(self, isDryRun: bool=False):
        """ to INITIALIZE Git Version Control
            - Input [OPT "False"]: is Dry Run
        """
        self.isDryRun = isDryRun

    def status(self) -> str:
        """ to retrieve git status
            - Output: console output
        """
        # to invoke Git for status
        result = subprocess.run(
            ['git', 'status', '--porcelain'], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout

    def add(self, files: list[str]):
        """ to add files to git staging
            - Input: files
        """
        # [Esc]: no files
        if not files: return
        # [Esc]: dry run
        if self.isDryRun:
            # [Msg]: to print dry run add message
            print(f"[DRY RUN] git add {' '.join(files)}")
            return
        # to invoke Git for add
        subprocess.run(['git', 'add'] + files, check=True)

    def commit(self, message: str):
        """ to commit staged changes
            - Input: message
        """
        # [Esc]: dry run
        if self.isDryRun:
            # [Msg]: to print dry run commit message
            print(f"[DRY RUN] git commit -m '{message}'")
            return
        # to invoke Git for commit
        subprocess.run(['git', 'commit', '-m', message], check=True)

    def tag(self, version: str):
        """ to tag git commit
            - Input: Version
        """
        # [Esc]: dry run
        if self.isDryRun:
            # [Msg]: to print dry run version message
            print(f"[DRY RUN] git tag v{version}")
            return
        # to invoke Git for tag
        subprocess.run(['git', 'tag', f"v{version}"], check=True)

def parseGit(gitStatusPorcelainOutput: str) -> list[tuple[str, str]]:
    """ to parse git status output
        - Input: Git Status Porcelain Output
        - Output: Parsed Git Status
    """
    parsed = []
    # [Scan]: to parse git status file and status
    for line in gitStatusPorcelainOutput.splitlines():
        # [Esc Once]: line shorter than 4
        if len(line) < 4: continue
        status = line[:2]
        filepath = line[3:]
        if filepath.startswith('"') and filepath.endswith('"'):
            filepath = filepath[1:-1]
        parsed.append((status, filepath))
    # [Esc "Exhausted"]: No files
    return parsed

def pruneStagingList(rawstaginglist: list[tuple[str, str]]) -> list[str]:
    """ to prune staging-list
        - Input: raw staging list
            - Contains: status
            - Contains: filepath
        - Output: Staging List
    """
    staginglist = [] 
    # [Scan]: to prune staging-list
    for status, filepath in rawstaginglist:
        # [Opt "renamed"]: to extract filename
        if ' -> ' in filepath:
            filepath = filepath.split(' -> ')[1]
        # [Esc Once]: pycache
        if '__pycache__' in filepath: continue
        staginglist.append(filepath)
    # [Esc "Exhausted"]: None staged
    return staginglist

def removeTemp(tempFile: str, rawstaginglist: list[tuple[str, str]]):
    """ to remove temporary file
        - Input: Temporary File
        - Input: Raw Staging List
        - Contains: status
        - Contains: filepath
    """
    # [Scan]: to remove temporary file from raw staging list
    for i, (status, path) in enumerate(rawstaginglist):
        # [Esc Done]: found
        if path == tempFile:
            rawstaginglist.pop(i)
            break
    # [Guard]: to remove temporary file from disk
    try:
        os.remove(tempFile)
        # to print removed file
        print(f"Removed temporary file: {tempFile}")
    # [Esc]: to print removal failure warning
    except Exception as e:
        print(f"Could not remove {tempFile}: {e}")

def approveTemps(tempFiles: list[str]) -> tuple[list[str], list[str]]:
    """ to display temporary-file-list for approval
        - Input: temp Files
            - Contains: temporary file
        - Output: Selected Temporary File List
            - Contains: selected temporary file name
            - Contains: rejected temporary file name
    """
    # [Esc]: no temporary files
    if not tempFiles: return [], []
    # to print untacked-files informative message
    print("\nFound the following untracked files (potential temporary files):")
    # [Scan]: to display temporary-file-list for approval
    for i, f in enumerate(tempFiles):
        # to print temporary file name
        print(f"  {i+1}. {f}")
    # to get temporary file selection from console
    ans = input("\nEnter the numbers of the files to KEEP (comma-separated), 'all' to keep all, or 'none' to delete all: ").strip().lower()
    # [Esc Done]: all selected
    if ans == 'all': return tempFiles, []
    # [Esc Done]: none selected
    if ans == 'none' or not ans: return [], tempFiles
    keep_indices = []
    # [Scan; Opt]: to pick temp files to keep by index
    for x in ans.split(','):
        if (x := x.strip()).isdigit():
            keep_indices.append(int(x) - 1)
    selected, notSelected = [], []
    # [Scan]: to filter temporary files
    for i, f in enumerate(tempFiles):
        # [Alt "Keep"]: to append temorary file to keep-list by index
        if i in keep_indices:
            selected.append(f)
        # [Alt "Delete"]: to append temorary file to delete-list by index
        else:
            notSelected.append(f)
    return selected, notSelected

def removeTempFiles(rawstaginglist: list[tuple[str, str]]):
    """ to remove temporary files
        - Input: Raw Staging List
            - Contains: status
            - Contains: filepath
    """
    tempFiles = []
    # [Scan]: to pick temporary file to remove
    for status, filepath in rawstaginglist:
        if status == '??':
            tempFiles.append(filepath)
    # [Esc Done]: no temporary files to remove
    if not tempFiles: return
    # [Msg]: to display temporary-file-list for approval
    selected, deleteFiles = approveTemps(tempFiles)
    # [Msg; Scan]: to remove temporary file
    for temporaryFile in deleteFiles:
        removeTemp(temporaryFile, rawstaginglist)

def collectFiles(git: GitVersionControl) -> list[tuple[str, str]]:
    """ to collect files added changed renamed moved or removed since last commit
        - Output: Raw Staging List
            - Contains: status
            - Contains: filepath
        - Input: git
    """
    # [Msg]: to retrieve git status
    gitStatusPorcelainOutput = git.status()
    # [Msg]: to parse git status output
    parsedGitStatus = parseGit(gitStatusPorcelainOutput)
    # to detect moved and renamed files
    rawstaginglist = parsedGitStatus ## todo...
    return rawstaginglist

def stage(git: GitVersionControl):
    """ to stage files for archiving
        - Input: git
    """
    # [Msg]: to collect files added changed renamed moved or removed since last commit
    rawstaginglist = collectFiles(git)
    # [Msg]: to remove temporary files
    removeTempFiles(rawstaginglist)
    # [Msg]: to stage all tracked changes (modifications & deletions)
    if not git.isDryRun:
        subprocess.run(['git', 'add', '-u'], check=True)
    else:
        print("[DRY RUN] git add -u")
    # [Msg]: to stage any new/untracked files that we want to keep
    untracked_to_keep = []
    for status, filepath in rawstaginglist:
        if status == '??':
            if os.path.exists(filepath):
                untracked_to_keep.append(filepath)
    if untracked_to_keep:
        git.add(untracked_to_keep)

def updateVersion(version: semver.Version, isDryRun: bool):
    """ to update the current Protonabu version Number
        - Input: Version
        - Input: is dry run
    """
    def replaceValue(filepath: str, key: str, value: str):
        """ to replace value in file
            - Input: filepath
            - Input: key
            - Input: value
        """
        with open(filepath, 'r') as f:
            content = f.read()
        # [Alt "python"]: to replace value after key in python file
        if filepath.endswith('.py'):
            content = re.sub(rf'{key}\s*=\s*[\'"].*?[\'"]', f"{key} = '{value}'", content)
        # [Alt "toml"]: to replace value after key in toml file
        elif filepath.endswith('.toml'):
            content = re.sub(rf'{key}\s*=\s*[\'"].*?[\'"]', f'{key} = "{value}"', content)
        with open(filepath, 'w') as f:
            f.write(content)
    # [Scan]: to update the current Protonabu version Number
    for filepath, key in [
        ("src/protonabu/__init__.py", "__version__"),
        ("pyproject.toml", "version")
    ]:
        # [Alt "dry run"]: to log dry run
        if isDryRun:
            # to print dry run update message
            print(f"[DRY RUN] Would update {key} to {str(version)} in {filepath}")
        # [Alt]: to replace value in file
        else:
            replaceValue(filepath, key, str(version))

def getFormalVersion(filename: str, key: str) -> semver.Version:
    """ to parse version in file
        - Input: filename
        - Input: key
    """
    sVersion = ''
    with open(filename, 'r') as f:
        # [Opt; Msg]: to match key value string
        match = re.search(rf'{key}\s*=\s*[\'"](.*?)[\'"]', f.read()) #, re.DOTALL)
        # [Esc Error]: version not found in file
        if not match:
            raise ValueError(f"Could not find {key} in content")
        sVersion = match.group(1)
    # to parse version
    return semver.Version.parse(sVersion)

def bumpVersion(versionPart: str, isDryRun: bool) -> semver.Version:
    """ to bump the current Protonabu version number
        - Input: version Part
        - Input: dry_run
    """
    # [Msg]: to parse version in file
    versionNumber: semver.Version = getFormalVersion(
        'src/protonabu/__init__.py', 
        '__version__'
    )
    # [Opt]: to [Crit]: "Version part"
    match versionPart:
        # [Alt "Patch"]: to bump patch version number
        case "Patch":
            # [Plfm]: to bump patch version
            versionNumber = versionNumber.bump_patch()
        # [Alt "Minor"]: to bump minor version number
        case "Minor":
            # [Plfm]: to bump minor version
            versionNumber = versionNumber.bump_minor()
        # [Alt "Major"]: to bump major version number
        case "Major":
            # [Plfm]: to bump major version
            versionNumber = versionNumber.bump_major()
    # [Msg]: to update the current Protonabu version Number
    updateVersion(versionNumber, isDryRun)
    return versionNumber

def main():
    """ to close Protonabu version
    """
    def parseCmdLineArguments() -> tuple[str, str, bool]:
        """ to parse command line arguments
            - Output: Command Line Arguments
                - Contains: Version part
                - Contains: Commit message
                - Contains: Dry run flag
        """
        parser = argparse.ArgumentParser(description="Close Protonabu version")
        parser.add_argument(
            "version_part", 
            choices=["Major", "Minor", "Patch"], 
            help="Version part to bump"
        )
        parser.add_argument(
            "-m", 
            "--message", 
            default="", 
            help="Commit message"
        )
        parser.add_argument(
            "--dry-run", 
            action="store_true", 
            help="Perform a trial run with no changes made"
        )
        args = parser.parse_args()
        return args.version_part, args.message, args.dry_run

    # to switch to project root directory
    os.chdir(
        Path(__file__).resolve().parent.parent
    )    
    # [Msg]: to parse command line arguments
    versionPart, commitMessage, isDryRun = parseCmdLineArguments()
    # [Msg]: to INITIALIZE Git Version Control
    git = GitVersionControl(isDryRun=isDryRun)
    # [Msg]: to do bump the current Protonabu version number
    newProtonabuVersionNumber: semver.Version = bumpVersion(versionPart, isDryRun)
    # [Msg]: to stage files for archiving
    stage(git)
    # [Msg]: to commit staged changes
    git.commit(
        commitMessage if commitMessage 
        else f"Bumped version to {str(newProtonabuVersionNumber)}"
    )
    # [Msg]: to tag git commit
    git.tag(str(newProtonabuVersionNumber))

if __name__ == "__main__":
    # [Msg]: to close Protonabu version
    main()
