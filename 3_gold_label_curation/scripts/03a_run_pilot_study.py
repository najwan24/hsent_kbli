#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 3A: Run Pilot Study (Refactored)
This script runs the pilot study using consolidated modules from src/.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.cli.arguments import create_pilot_study_parser
from src.api.gemini_client import GeminiClient
from src.pipeline.pilot_runner import PilotRunner
from src.utils.common import load_env_file


def main():
    """Main function - now just a thin CLI wrapper."""
    # Load environment variables
    load_env_file()
    
    # Parse command line arguments
    parser = create_pilot_study_parser()
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_models:
        GeminiClient.list_available_models()
        return
    
    try:
        # Create pilot runner and execute
        runner = PilotRunner()
        
        stats = runner.run_pilot_study(
            model_name=args.model,
            dataset_filename=args.dataset,
            n_runs=args.runs,
            temperature=args.temperature,
            output_dir=args.output_dir
        )
        
        print(f"\n📊 Execution completed successfully!")
        print(f"Statistics: {stats}")
        
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Process interrupted by user")
        print(f"🔄 To resume, run this script again - it will continue from where it left off")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print(f"🔄 To resume, run this script again after fixing the error")
        sys.exit(1)


if __name__ == "__main__":
    main()
