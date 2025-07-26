#!/usr/bin/env python3
"""
Migration script to move from old structure to new organized structure
This script helps transition the existing files to the new organized structure.
"""
import shutil
from pathlib import Path

def migrate_structure():
    """Migrate existing files to new structure"""
    print("🔄 ACSES Project Structure Migration")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    src_old = project_root / "src"
    scripts_new = project_root / "scripts"
    
    # Create backup of current src folder
    backup_dir = project_root / "src_backup"
    if src_old.exists() and not backup_dir.exists():
        print(f"📦 Creating backup: {backup_dir}")
        shutil.copytree(src_old, backup_dir)
    
    # Files that should become scripts (executable entry points)
    script_files = [
        "00_prepare_codebook.py",
        "02a_add_unique_ids.py", 
        "03a_run_pilot_study.py",
        "03b_run_multi_model_pilot.py",
        "analyze_results.py",
        "setup_and_validate.py",
        "test_rate_limiting.py"
    ]
    
    # Files that should become library modules (keep in src)
    utility_files = [
        "analyze_gemini_2_5.py",  # -> src/analysis/
        "convert_to_jsonl.py",    # -> src/utils/
    ]
    
    # Convenience scripts that can be removed (functionality moved to main scripts)
    deprecated_files = [
        "add_ids.py"  # Functionality moved to add_unique_ids.py
    ]
    
    print("\n📋 Migration Plan:")
    print(f"Scripts folder: {scripts_new}")
    print(f"Script files to move: {len(script_files)}")
    print(f"Utility files to reorganize: {len(utility_files)}")
    print(f"Deprecated files: {len(deprecated_files)}")
    
    # Show what would be migrated
    print("\n📝 Files to migrate to scripts/:")
    for file in script_files:
        old_path = src_old / file
        if old_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} (not found)")
    
    # Confirm before proceeding
    response = input("\n🔄 Proceed with migration? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration cancelled")
        return
    
    # Proceed with migration
    print("\n🚀 Starting migration...")
    
    # Move script files
    moved_count = 0
    for file in script_files:
        old_path = src_old / file
        new_path = scripts_new / file.replace("00_", "").replace("02a_", "").replace("03a_", "run_pilot_study.py").replace("03b_", "run_multi_model_pilot.py")
        
        if old_path.exists():
            try:
                shutil.move(str(old_path), str(new_path))
                print(f"  ✓ Moved {file} → scripts/{new_path.name}")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ Failed to move {file}: {e}")
    
    print(f"\n✅ Migration completed!")
    print(f"📊 Moved {moved_count} files to scripts/")
    print(f"📦 Backup created at: {backup_dir}")
    
    print("\n📋 Next Steps:")
    print("1. Review the migrated scripts in scripts/ folder")
    print("2. Update import statements in the scripts")
    print("3. Test the new structure")
    print("4. Remove src_backup/ when satisfied")

if __name__ == "__main__":
    migrate_structure()
