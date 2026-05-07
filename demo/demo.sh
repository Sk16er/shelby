#!/bin/bash
# demo.sh - A scripted walkthrough for Shelby CLI
# Best recorded with: asciinema rec demo.cast -c "./demo.sh"

set -e

# Colors for the script messages
CYAN='\033[0;36m'
NC='\033[0m' # No Color

function type_msg {
    echo -e "${CYAN}$1${NC}"
    sleep 2
}

clear

type_msg "# Welcome to Shelby - Your AI Terminal Assistant"
type_msg "# Let's start by asking for a common task..."

echo "$ shelby 'find all python files larger than 1MB'"
shelby --dry-run "find all python files larger than 1MB"
sleep 3

type_msg "# Shelby handles complex operations with safety in mind."
type_msg "# Notice the CAUTION tier for system-modifying commands."

echo "$ shelby 'install requests and numpy'"
# Mocking a bit since we don't want to actually install in a demo if not needed
# But shelby --dry-run will show the behavior
shelby --dry-run "install requests and numpy"
sleep 3

type_msg "# It also explains what each flag does."

echo "$ shelby explain 'tar -xzvf archive.tar.gz'"
shelby explain "tar -xzvf archive.tar.gz"
sleep 5

type_msg "# And if a command fails, Shelby can fix it."

echo "$ rm non_existent_file"
rm non_existent_file || true
echo "$ shelby fix"
# We can't easily script the interactive part of fix here perfectly without expect,
# but we show the intent.
sleep 2

type_msg "# Shelby keeps history and allows semantic search."

echo "$ shelby history 'python files'"
shelby history "python files"
sleep 4

type_msg "# That's Shelby. Safety, Transparency, and Power."
type_msg "# Happy hacking!"
sleep 2
