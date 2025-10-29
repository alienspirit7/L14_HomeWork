# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- google-generativeai (for Gemini translation)
- anthropic (for Claude translation)
- sentence-transformers (for embeddings)
- numpy, scikit-learn (for calculations)
- matplotlib (for visualization)
- tqdm (for progress bars)
- python-dotenv (for configuration)

## Step 2: Configure API Key

1. Copy the environment template:
```bash
cp .env.template .env
```

2. **Choose your API provider** and edit `.env`:

**Option A: Google Gemini (Recommended - Free Tier)**
```bash
API_PROVIDER=gemini
GOOGLE_API_KEY=your-actual-api-key-here
```
Get your API key: https://aistudio.google.com/app/apikey

**Option B: Anthropic Claude**
```bash
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-actual-api-key-here
```
Get your API key: https://console.anthropic.com/account/keys

## Step 3: Test the Setup (Optional but Recommended)

Run a quick test with just 2 sentences:

```bash
python test_pipeline.py
```

This will:
- Verify your API key works (Gemini or Anthropic)
- Test all components
- Run a mini pipeline with 2 sentences
- Takes about 30-60 seconds

## Step 4: Run the Full Pipeline

```bash
python main.py
```

This will:
- Generate 30 English sentences (configurable)
- Translate each through EN → RU → HE → EN
- Calculate semantic drift for each
- Generate statistics and visualization
- Save results to `./results/` directory

**Time**: ~15 minutes (with 30 second wait between sentences)
**Cost**:
- **Gemini**: FREE (free tier)
- **Anthropic**: ~$0.10-$0.30

## Step 5: View Results

After completion, check:

```bash
ls results/
```

You'll find:
- `translation_results.json` - Complete data
- `distance_plot.png` - Visualization
- `intermediate_results_*.json` - Checkpoints

### View the Graph

Open the plot:
```bash
# macOS
open results/distance_plot.png

# Linux
xdg-open results/distance_plot.png

# Windows
start results/distance_plot.png
```

### View Statistics

```bash
# Pretty print the JSON
python -m json.tool results/translation_results.json | less

# Or just view statistics
python -c "import json; data=json.load(open('results/translation_results.json')); print('Average distance:', data['statistics']['mean']); print('Variance:', data['statistics']['variance'])"
```

## Troubleshooting

### "Missing API key" Error
**For Gemini:**
```
API_PROVIDER=gemini
GOOGLE_API_KEY=your-api-key-here
```

**For Anthropic:**
```
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key-here
```

Make sure `.env` file exists and contains the correct keys.

### "Module not found"
Install dependencies:
```bash
pip install -r requirements.txt
```

### Pipeline is slow
This is normal! Each sentence requires 3 API calls plus wait time. For faster testing:
1. Edit `config.py`: Set `NUM_SENTENCES = 10` and `WAIT_TIME_BETWEEN_SENTENCES = 10`
2. Or use `test_pipeline.py` for quick tests

### Want to customize?

Edit `config.py`:
```python
NUM_SENTENCES = 10              # Fewer sentences = faster
WAIT_TIME_BETWEEN_SENTENCES = 10  # Reduce wait time for testing
AGENT_TIMEOUT = 90              # Increase if timeouts occur
API_PROVIDER = "gemini"         # Switch between "gemini" or "anthropic"
```

## What's Next?

1. **Analyze Results**: Open `results/translation_results.json` to explore the data
2. **Understand Metrics**: See README.md for interpretation guide
3. **Customize**: Edit `config.py` to adjust settings
4. **Experiment**: Try different language chains in `translation_agents.py`

## Full Documentation

For complete documentation, see:
- **README.md** - Comprehensive guide
- **PRD_Translation_Pipeline.md** - Product requirements and specifications

## Quick Reference

```bash
# Test setup (2 sentences)
python test_pipeline.py

# Run full pipeline (30 sentences, ~15 min)
python main.py

# View results
cat results/translation_results.json
open results/distance_plot.png
```

## API Provider Comparison

| Feature | Gemini (Default) | Anthropic |
|---------|-----------------|-----------|
| Cost | FREE (free tier) | ~$0.10-$0.30 |
| Speed | Fast | Fast |
| Rate Limit | 1,500 req/day | Varies by tier |
| Setup | `API_PROVIDER=gemini` | `API_PROVIDER=anthropic` |
| Best For | Development/Testing | Production |

## Support

If you encounter issues:
1. Run `python test_pipeline.py` to diagnose
2. Check the Troubleshooting section in README.md
3. Verify your API key has credits
4. Check your internet connection

---

Happy translating! 🌐
