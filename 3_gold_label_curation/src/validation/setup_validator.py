"""
Validation module for ACSES pilot study setup and environment.
Provides comprehensive validation of environment, files, and dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd


class SetupValidator:
    """Validates setup and environment for ACSES pilot study."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the validator.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        
    def check_python_version(self, min_version: Tuple[int, int] = (3, 8)) -> Dict[str, Any]:
        """
        Check if Python version meets requirements.
        
        Args:
            min_version: Minimum required Python version tuple
            
        Returns:
            Dictionary with check results
        """
        current_version = sys.version_info[:2]
        is_valid = current_version >= min_version
        
        return {
            "check": "Python Version",
            "valid": is_valid,
            "current": f"{current_version[0]}.{current_version[1]}.{sys.version_info.micro}",
            "required": f"{min_version[0]}.{min_version[1]}+",
            "message": "✅ Python version OK" if is_valid else f"❌ Python {min_version[0]}.{min_version[1]}+ required"
        }
    
    def check_required_files(self) -> List[Dict[str, Any]]:
        """
        Check if all required files exist.
        
        Returns:
            List of file check results
        """
        required_files = [
            ("data/input/kbli_codebook.csv", "KBLI codebook"),
            ("data/input/kbli_codebook_hierarchical.csv", "Hierarchical codebook"),
            ("data/input/mini_test.csv", "Test dataset"),
            ("prompts/master_prompt.txt", "Master prompt template"),
        ]
        
        results = []
        
        for rel_path, description in required_files:
            file_path = self.project_root / rel_path
            exists = file_path.exists()
            
            results.append({
                "check": "Required File",
                "file": rel_path,
                "description": description,
                "valid": exists,
                "path": str(file_path),
                "message": f"✅ {description}: Found" if exists else f"❌ {description}: Missing - {rel_path}"
            })
        
        return results
    
    def check_dependencies(self) -> List[Dict[str, Any]]:
        """
        Check if required Python packages are installed.
        
        Returns:
            List of dependency check results
        """
        required_packages = [
            ("pandas", "Data manipulation"),
            ("google-generativeai", "Gemini API client"),
            ("python-dotenv", "Environment variables (optional)"),
        ]
        
        results = []
        
        for package, description in required_packages:
            try:
                __import__(package.replace('-', '_'))
                is_installed = True
                message = f"✅ {description}: Installed"
            except ImportError:
                is_installed = False
                message = f"❌ {description}: Missing - pip install {package}"
            
            results.append({
                "check": "Python Package",
                "package": package,
                "description": description,
                "valid": is_installed,
                "message": message
            })
        
        return results
    
    def check_environment_variables(self) -> List[Dict[str, Any]]:
        """
        Check if required environment variables are set.
        
        Returns:
            List of environment variable check results
        """
        env_vars = [
            ("GEMINI_API_KEY", "Gemini API key for LLM calls", True),  # Required
        ]
        
        results = []
        
        for var_name, description, is_required in env_vars:
            value = os.getenv(var_name)
            is_set = value is not None and value.strip() != ""
            
            if is_required:
                message = f"✅ {description}: Set" if is_set else f"❌ {description}: Missing"
            else:
                message = f"✅ {description}: Set" if is_set else f"ℹ️  {description}: Optional (not set)"
            
            results.append({
                "check": "Environment Variable",
                "variable": var_name,
                "description": description,
                "required": is_required,
                "valid": is_set or not is_required,
                "message": message
            })
        
        return results
    
    def check_data_integrity(self) -> List[Dict[str, Any]]:
        """
        Check integrity of data files.
        
        Returns:
            List of data integrity check results
        """
        results = []
        
        # Check KBLI codebook
        codebook_path = self.data_dir / "input" / "kbli_codebook.csv"
        if codebook_path.exists():
            try:
                df = pd.read_csv(codebook_path, dtype={'kode': str})
                required_columns = ['kode', 'judul', 'deskripsi', 'digit']
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    results.append({
                        "check": "Data Integrity",
                        "file": "kbli_codebook.csv",
                        "valid": False,
                        "message": f"❌ Missing columns: {missing_columns}"
                    })
                else:
                    results.append({
                        "check": "Data Integrity",
                        "file": "kbli_codebook.csv",
                        "valid": True,
                        "rows": len(df),
                        "message": f"✅ KBLI codebook: {len(df)} entries loaded successfully"
                    })
                    
            except Exception as e:
                results.append({
                    "check": "Data Integrity",
                    "file": "kbli_codebook.csv",
                    "valid": False,
                    "message": f"❌ Error reading codebook: {e}"
                })
        
        # Check test dataset
        test_path = self.data_dir / "input" / "mini_test.csv"
        if test_path.exists():
            try:
                df = pd.read_csv(test_path, dtype={'kbli_code': str})
                required_columns = ['kbli_code', 'job_description']
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    results.append({
                        "check": "Data Integrity",
                        "file": "mini_test.csv",
                        "valid": False,
                        "message": f"❌ Missing columns: {missing_columns}"
                    })
                else:
                    results.append({
                        "check": "Data Integrity",
                        "file": "mini_test.csv",
                        "valid": True,
                        "rows": len(df),
                        "message": f"✅ Test dataset: {len(df)} samples loaded successfully"
                    })
                    
            except Exception as e:
                results.append({
                    "check": "Data Integrity",
                    "file": "mini_test.csv",
                    "valid": False,
                    "message": f"❌ Error reading test dataset: {e}"
                })
        
        return results
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """
        Run all validation checks and return comprehensive results.
        
        Returns:
            Dictionary containing all validation results
        """
        print("🔍 RUNNING COMPREHENSIVE VALIDATION")
        print("=" * 50)
        
        # Collect all checks
        checks = []
        
        # Python version
        python_check = self.check_python_version()
        checks.append(python_check)
        print(python_check["message"])
        
        # Required files
        print("\n📁 CHECKING REQUIRED FILES")
        file_checks = self.check_required_files()
        checks.extend(file_checks)
        for check in file_checks:
            print(check["message"])
        
        # Dependencies
        print("\n📦 CHECKING DEPENDENCIES")
        dep_checks = self.check_dependencies()
        checks.extend(dep_checks)
        for check in dep_checks:
            print(check["message"])
        
        # Environment variables
        print("\n🔐 CHECKING ENVIRONMENT VARIABLES")
        env_checks = self.check_environment_variables()
        checks.extend(env_checks)
        for check in env_checks:
            print(check["message"])
        
        # Data integrity
        print("\n🔍 CHECKING DATA INTEGRITY")
        data_checks = self.check_data_integrity()
        checks.extend(data_checks)
        for check in data_checks:
            print(check["message"])
        
        # Summary
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks if check["valid"])
        failed_checks = total_checks - passed_checks
        
        all_passed = failed_checks == 0
        
        print(f"\n📊 VALIDATION SUMMARY")
        print("=" * 30)
        print(f"✅ Passed: {passed_checks}/{total_checks}")
        print(f"❌ Failed: {failed_checks}/{total_checks}")
        
        if all_passed:
            print("\n🎉 ALL CHECKS PASSED! You're ready to run the pilot study.")
        else:
            print(f"\n⚠️  {failed_checks} checks failed. Please fix the issues above before proceeding.")
        
        return {
            "overall_status": "PASSED" if all_passed else "FAILED",
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "all_checks": checks
        }
    
    def run_quick_test(self) -> bool:
        """
        Run a quick API connectivity test.
        
        Returns:
            True if test passes, False otherwise
        """
        print("\n🧪 RUNNING QUICK API TEST")
        print("-" * 30)
        
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("❌ GEMINI_API_KEY not found. Cannot test API connectivity.")
                return False
            
            genai.configure(api_key=api_key)
            
            # Simple test
            model = genai.GenerativeModel("models/gemini-2.5-flash-lite")
            response = model.generate_content("Say 'API test successful'")
            
            if response.text and "successful" in response.text.lower():
                print("✅ API connectivity test PASSED")
                return True
            else:
                print("⚠️  API responded but test phrase not found")
                return False
                
        except Exception as e:
            print(f"❌ API connectivity test FAILED: {e}")
            return False


def check_environment() -> bool:
    """
    Convenience function for backwards compatibility.
    Runs comprehensive validation.
    
    Returns:
        True if all checks pass, False otherwise
    """
    validator = SetupValidator()
    results = validator.run_comprehensive_validation()
    return results["overall_status"] == "PASSED"


def main():
    """Main function for running as a script."""
    validator = SetupValidator()
    
    # Run comprehensive validation
    results = validator.run_comprehensive_validation()
    
    # Run API test if basic validation passes
    if results["overall_status"] == "PASSED":
        api_test_passed = validator.run_quick_test()
        if not api_test_passed:
            print("\n⚠️  API test failed, but environment setup is correct.")
            print("   This might be due to network issues or API key problems.")
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
