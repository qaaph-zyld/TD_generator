"""
Version control integration system.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import git
import difflib
from pathlib import Path

@dataclass
class ChangeSet:
    file_path: str
    changes: List[Dict]
    metadata: Dict
    author: str
    timestamp: float

@dataclass
class VersionInfo:
    commit_hash: str
    branch: str
    tags: List[str]
    timestamp: float

class GitManager:
    """Manages Git repository integration."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
        self.logger = logging.getLogger(__name__)
    
    def get_current_version(self) -> VersionInfo:
        """Get current version information."""
        try:
            commit = self.repo.head.commit
            return VersionInfo(
                commit_hash=commit.hexsha,
                branch=self.repo.active_branch.name,
                tags=[tag.name for tag in self.repo.tags],
                timestamp=commit.committed_date
            )
        except Exception as e:
            self.logger.error(f"Failed to get version info: {str(e)}")
            raise
    
    def track_changes(self, file_path: str) -> List[ChangeSet]:
        """Track changes for a specific file."""
        try:
            changes = []
            file_path = Path(file_path)
            
            # Get file history
            for commit in self.repo.iter_commits(paths=str(file_path)):
                if len(commit.parents) > 0:
                    # Get diff between current and parent commit
                    diff = commit.diff(
                        commit.parents[0],
                        paths=str(file_path),
                        create_patch=True
                    )
                    
                    if diff:
                        changes.append(ChangeSet(
                            file_path=str(file_path),
                            changes=self._parse_diff(diff[0]),
                            metadata={
                                'commit': commit.hexsha,
                                'message': commit.message
                            },
                            author=commit.author.name,
                            timestamp=commit.committed_date
                        ))
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Failed to track changes: {str(e)}")
            raise
    
    def compare_versions(self,
                        file_path: str,
                        version1: str,
                        version2: str) -> Dict:
        """Compare file content between two versions."""
        try:
            # Get content from both versions
            content1 = self._get_file_content(file_path, version1)
            content2 = self._get_file_content(file_path, version2)
            
            # Generate diff
            diff = difflib.unified_diff(
                content1.splitlines(keepends=True),
                content2.splitlines(keepends=True),
                fromfile=f"{file_path}@{version1}",
                tofile=f"{file_path}@{version2}"
            )
            
            return {
                'diff': ''.join(diff),
                'changes': self._analyze_changes(content1, content2)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to compare versions: {str(e)}")
            raise
    
    def _get_file_content(self, file_path: str, version: str) -> str:
        """Get file content at specific version."""
        try:
            return self.repo.git.show(f"{version}:{file_path}")
        except Exception as e:
            self.logger.error(
                f"Failed to get content for {file_path}@{version}: {str(e)}"
            )
            raise
    
    def _parse_diff(self, diff) -> List[Dict]:
        """Parse git diff output."""
        changes = []
        
        # Parse the diff patch
        if diff.a_blob and diff.b_blob:
            diff_str = diff.diff.decode('utf-8')
            
            # Parse diff string into structured changes
            current_hunk = None
            for line in diff_str.split('\n'):
                if line.startswith('@@'):
                    if current_hunk:
                        changes.append(current_hunk)
                    current_hunk = {
                        'type': 'hunk',
                        'header': line,
                        'changes': []
                    }
                elif current_hunk:
                    if line.startswith('+'):
                        current_hunk['changes'].append({
                            'type': 'addition',
                            'content': line[1:]
                        })
                    elif line.startswith('-'):
                        current_hunk['changes'].append({
                            'type': 'deletion',
                            'content': line[1:]
                        })
            
            if current_hunk:
                changes.append(current_hunk)
        
        return changes
    
    def _analyze_changes(self, content1: str, content2: str) -> Dict:
        """Analyze changes between two content versions."""
        # Split content into lines
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, content1, content2).ratio()
        
        # Count changes
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        changes = {
            'additions': 0,
            'deletions': 0,
            'modifications': 0
        }
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'insert':
                changes['additions'] += j2 - j1
            elif tag == 'delete':
                changes['deletions'] += i2 - i1
            elif tag == 'replace':
                changes['modifications'] += max(i2 - i1, j2 - j1)
        
        return {
            'similarity': similarity,
            'changes': changes,
            'total_changes': sum(changes.values())
        }
