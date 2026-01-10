#!/bin/bash
# Re-enable GitHub Actions workflows for next season
# This uncomments the schedule triggers in all workflow files

echo "=========================================="
echo "RE-ENABLING GITHUB ACTIONS WORKFLOWS"
echo "=========================================="
echo ""

WORKFLOWS_DIR=".github/workflows"

# Re-enable Friday scraper
echo "Step 1: Re-enabling Friday scraper..."
sed -i.bak 's/^  # schedule:/  schedule:/g; s/^  #   # Runs every Friday/    # Runs every Friday/g; s/^  #   - cron:/    - cron:/g' "$WORKFLOWS_DIR/friday_scraper.yml"
sed -i.bak '/SCHEDULE DISABLED/,/workflow_dispatch:/s/^  # schedule:/  schedule:/' "$WORKFLOWS_DIR/friday_scraper.yml"
sed -i.bak '/SCHEDULE DISABLED/d' "$WORKFLOWS_DIR/friday_scraper.yml"
rm -f "$WORKFLOWS_DIR/friday_scraper.yml.bak"
echo "  ✅ Friday scraper re-enabled"

# Re-enable Monday scraper
echo "Step 2: Re-enabling Monday scraper..."
sed -i.bak '/SCHEDULE DISABLED/,/workflow_dispatch:/s/^  # schedule:/  schedule:/' "$WORKFLOWS_DIR/monday_scraper.yml"
sed -i.bak 's/^  #   - cron:/    - cron:/g' "$WORKFLOWS_DIR/monday_scraper.yml"
sed -i.bak '/SCHEDULE DISABLED/d' "$WORKFLOWS_DIR/monday_scraper.yml"
rm -f "$WORKFLOWS_DIR/monday_scraper.yml.bak"
echo "  ✅ Monday scraper re-enabled"

# Re-enable Tuesday scraper
echo "Step 3: Re-enabling Tuesday scraper..."
sed -i.bak '/SCHEDULE DISABLED/,/workflow_dispatch:/s/^  # schedule:/  schedule:/' "$WORKFLOWS_DIR/tuesday_scraper.yml"
sed -i.bak 's/^  #   - cron:/    - cron:/g' "$WORKFLOWS_DIR/tuesday_scraper.yml"
sed -i.bak '/SCHEDULE DISABLED/d' "$WORKFLOWS_DIR/tuesday_scraper.yml"
rm -f "$WORKFLOWS_DIR/tuesday_scraper.yml.bak"
echo "  ✅ Tuesday scraper re-enabled"

echo ""
echo "=========================================="
echo "RE-ENABLE COMPLETE!"
echo "=========================================="
echo ""
echo "⚠️  Note: Manual uncommenting may be easier. The workflow files have:"
echo "   - Schedule sections commented out"
echo "   - Manual trigger (workflow_dispatch) still enabled"
echo ""
echo "To manually re-enable:"
echo "  1. Edit each workflow file in .github/workflows/"
echo "  2. Uncomment the schedule: section"
echo "  3. Commit and push changes"
echo ""

