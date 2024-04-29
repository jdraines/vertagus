SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

pytest -vvv --cov-config=$SCRIPT_DIR/.coveragerc --cov=vertagus --cov-report=term-missing
