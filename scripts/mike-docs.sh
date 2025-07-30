#!/bin/bash
# Mike helper script for Vertagus documentation management

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR=$SCRIPT_DIR/..

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  init                Initialize Mike with the current version"
    echo "  deploy VERSION      Deploy documentation for a specific version"
    echo "  deploy-dev          Deploy development documentation"
    echo "  release VERSION     Deploy a release version and set as latest"
    echo "  list                List all deployed versions"
    echo "  delete VERSION      Delete a specific version"
    echo "  serve [VERSION]     Serve documentation locally (default: latest)"
    echo "  set-default VERSION Set the default version"
    echo ""
    echo "Examples:"
    echo "  $0 init"
    echo "  $0 deploy-dev"
    echo "  $0 release 1.0.0"
    echo "  $0 serve dev"
    echo "  $0 list"
}

get_current_version() {
    python -c "import tomli; print(tomli.load(open('$ROOT_DIR/pyproject.toml', 'rb'))['project']['version'])"
}

init_mike() {
    echo -e "${BLUE}Initializing Mike with current version...${NC}"
    current_version=$(get_current_version)
    echo -e "${YELLOW}Current version: $current_version${NC}"
    
    # Deploy current version as both the version and latest
    mike deploy --push --update-aliases "$current_version" latest
    mike set-default --push latest
    
    # Deploy dev version
    mike deploy --push dev
    
    echo -e "${GREEN}Mike initialized successfully!${NC}"
    echo -e "${YELLOW}Available versions:${NC}"
    mike list
}

deploy_version() {
    local version="$1"
    if [ -z "$version" ]; then
        echo -e "${RED}Error: Version required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Deploying documentation for version: $version${NC}"
    mike deploy --push "$version"
    echo -e "${GREEN}Deployed successfully!${NC}"
}

deploy_dev() {
    echo -e "${BLUE}Deploying development documentation...${NC}"
    # Check if we should push (for CI environments)
    if [[ "${CI:-}" == "true" ]]; then
        mike deploy --push dev
    else
        mike deploy dev
    fi
    echo -e "${GREEN}Development documentation deployed!${NC}"
}

release_version() {
    local version="$1"
    if [ -z "$version" ]; then
        echo -e "${RED}Error: Version required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Deploying release version: $version${NC}"
    # Check if we should push (for CI environments)
    if [[ "${CI:-}" == "true" ]]; then
        mike deploy --push --update-aliases "$version" latest
        mike set-default --push latest
    else
        mike deploy --update-aliases "$version" latest
        mike set-default latest
    fi
    echo -e "${GREEN}Release $version deployed and set as default!${NC}"
}

list_versions() {
    echo -e "${BLUE}Deployed documentation versions:${NC}"
    mike list
}

delete_version() {
    local version="$1"
    if [ -z "$version" ]; then
        echo -e "${RED}Error: Version required${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Are you sure you want to delete version '$version'? [y/N]${NC}"
    read -r confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        mike delete --push "$version"
        echo -e "${GREEN}Version $version deleted!${NC}"
    else
        echo -e "${YELLOW}Cancelled.${NC}"
    fi
}

serve_docs() {
    local version="${1:-latest}"
    echo -e "${BLUE}Serving documentation (version: $version)...${NC}"
    echo -e "${YELLOW}Open http://localhost:8000 in your browser${NC}"
    mike serve
}

set_default() {
    local version="$1"
    if [ -z "$version" ]; then
        echo -e "${RED}Error: Version required${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Setting default version to: $version${NC}"
    mike set-default --push "$version"
    echo -e "${GREEN}Default version set to $version!${NC}"
}

# Main command handling
case "${1:-}" in
    init)
        init_mike
        ;;
    deploy)
        deploy_version "$2"
        ;;
    deploy-dev)
        deploy_dev
        ;;
    release)
        release_version "$2"
        ;;
    list)
        list_versions
        ;;
    delete)
        delete_version "$2"
        ;;
    serve)
        serve_docs "$2"
        ;;
    set-default)
        set_default "$2"
        ;;
    help|--help|-h)
        print_usage
        ;;
    "")
        echo -e "${RED}Error: No command specified${NC}"
        print_usage
        exit 1
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        print_usage
        exit 1
        ;;
esac
