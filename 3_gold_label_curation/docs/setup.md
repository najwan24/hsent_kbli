# Installation and Environment Setup

## Prerequisites

- Python 3.8 or higher
- Git (for version control)
- A Google Cloud account with Gemini API access

## Installation Steps

### 1. Install Dependencies

Navigate to the project directory and install the required packages:

```bash
cd 3_gold_label_curation
pip install -r requirements.txt
```

### 2. API Configuration

#### Get Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create or select a project
3. Generate a new API key

#### Environment Setup
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your API key:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```

#### Load Environment Variables

**For PowerShell (Windows):**
```powershell
Get-Content .env | ForEach-Object { 
    $key, $value = $_ -split '=', 2
    [Environment]::SetEnvironmentVariable($key, $value, "Process")
}
```

**Alternative direct method:**
```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

**For Bash (Linux/Mac):**
```bash
export $(cat .env | xargs)
```

### 3. Verify Installation

Test your setup by running the validation script:
```bash
python src/setup_and_validate.py
```

## Rate Limits and Quotas

Understanding API rate limits is crucial for successful execution:

| Model | RPM Limit (Free Tier) | Min Delay Required |
|-------|----------------------|-------------------|
| gemini-1.5-flash-latest | 15 RPM | 4+ seconds |
| gemini-1.5-pro-latest | 2 RPM | 30+ seconds |
| gemini-2.5-flash-lite | 15 RPM | 4+ seconds |

## Troubleshooting Setup Issues

### Common Issues

1. **API Key Issues**
   - Ensure your API key is valid and has proper permissions
   - Check that the key isn't expired or rate-limited

2. **Dependencies**
   - If installation fails, try upgrading pip: `pip install --upgrade pip`
   - For version conflicts, consider using a virtual environment

3. **Environment Variables**
   - Verify environment variables are loaded: `echo $env:GEMINI_API_KEY` (PowerShell)
   - Restart your terminal session if variables aren't recognized

### Virtual Environment (Recommended)

For better dependency management:

```bash
# Create virtual environment
python -m venv acses_env

# Activate (Windows PowerShell)
.\acses_env\Scripts\Activate.ps1

# Activate (Linux/Mac)
source acses_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```
