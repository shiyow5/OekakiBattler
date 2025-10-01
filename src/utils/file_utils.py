"""
File utility functions
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
import hashlib
import json

def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if necessary"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def get_file_hash(file_path: str) -> Optional[str]:
    """Get MD5 hash of file for duplicate detection"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def copy_file_with_unique_name(source: str, destination_dir: str, base_name: str) -> Optional[str]:
    """Copy file with unique name if destination exists"""
    try:
        dest_dir = Path(destination_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        source_path = Path(source)
        extension = source_path.suffix
        
        # Generate unique filename
        counter = 0
        while True:
            if counter == 0:
                filename = f"{base_name}{extension}"
            else:
                filename = f"{base_name}_{counter}{extension}"
            
            dest_path = dest_dir / filename
            if not dest_path.exists():
                shutil.copy2(source, dest_path)
                return str(dest_path)
            counter += 1
            
            # Prevent infinite loop
            if counter > 1000:
                return None
                
    except Exception:
        return None

def get_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """Get all files in directory with specified extensions"""
    try:
        files = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return files
            
        for ext in extensions:
            pattern = f"*{ext.lower()}"
            files.extend([str(p) for p in dir_path.glob(pattern)])
            pattern = f"*{ext.upper()}"
            files.extend([str(p) for p in dir_path.glob(pattern)])
        
        return sorted(list(set(files)))  # Remove duplicates and sort
    except Exception:
        return []

def save_json(data: dict, file_path: str) -> bool:
    """Save dictionary as JSON file"""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def load_json(file_path: str) -> Optional[dict]:
    """Load JSON file as dictionary"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def clean_filename(filename: str) -> str:
    """Clean filename by removing/replacing invalid characters"""
    # Replace invalid characters with underscore
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove multiple consecutive underscores
    while '__' in filename:
        filename = filename.replace('__', '_')
    
    # Remove leading/trailing underscores and dots
    filename = filename.strip('_.')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed'
    
    return filename

def get_available_filename(directory: str, desired_name: str, extension: str = '') -> str:
    """Get available filename by adding counter if needed"""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    
    counter = 0
    while True:
        if counter == 0:
            filename = f"{desired_name}{extension}"
        else:
            filename = f"{desired_name}_{counter}{extension}"
        
        file_path = dir_path / filename
        if not file_path.exists():
            return str(file_path)
        
        counter += 1
        # Prevent infinite loop
        if counter > 1000:
            return str(dir_path / f"{desired_name}_{hash(desired_name) % 1000}{extension}")

def backup_file(file_path: str, backup_dir: str = None) -> Optional[str]:
    """Create backup of file"""
    try:
        source = Path(file_path)
        if not source.exists():
            return None
        
        if backup_dir is None:
            backup_dir = source.parent / "backups"
        else:
            backup_dir = Path(backup_dir)
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source.stem}_{timestamp}{source.suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(source, backup_path)
        return str(backup_path)
        
    except Exception:
        return None