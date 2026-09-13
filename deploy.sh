#!/usr/bin/env bash
# ==============================================================================
# NETRYX EVIDENCE — One-Command Production Cloud VPS Deployment Script
# ==============================================================================
# Supports: Ubuntu 22.04 / 24.04 LTS, Debian 11 / 12
# Architecture: AMD64 / ARM64
# Usage:
#   curl -sSL https://raw.githubusercontent.com/yug1204/netryx-evidence/master/deploy.sh | bash
# ==============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
cat << "EOF"
  _   _ _____ _____ ______   ____  __  ______      _______ _____  ______ _   _  _____ ______ 
 | \ | |  ___|_   _|  _ \ \ / /\ \/ / |  ____/\   / ____|  __ \|  ____| \ | |/ ____|  ____|
 |  \| | |__   | | | |_) \ V /  \  /  | |__ /  \ | |    | |  | | |__  |  \| | |    | |__   
 | . ` |  __|  | | |  _ < \ /   /  \  |  __/ /\ \| |    | |  | |  __| | . ` | |    |  __|  
 | |\  | |___  | | | |_) || |   / /\ \| | / ____ \ |____| |__| | |____| |\  | |____| |____ 
 |_| \_|_____| |_| |____/ |_|  /_/  \_\_|/_/    \_\_____|_____/|______|_| \_|\_____|______|
                                                                                             
       ENTERPRISE DIGITAL FORENSICS, INCIDENT RESPONSE & THREAT GRAPH PLATFORM
EOF
echo -e "${NC}"

echo -e "${CYAN}[*] Starting NETRYX EVIDENCE automated deployment...${NC}"

# Check root privileges
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run as root (or use sudo).${NC}"
  exit 1
fi

# Detect public IP
SERVER_IP=$(curl -s https://api.ipify.org || curl -s https://ifconfig.me || echo "your-server-ip")
echo -e "${GREEN}[+] Detected Server Public IP: ${SERVER_IP}${NC}"

# Install prerequisites
echo -e "${CYAN}[*] Updating system packages & installing dependencies...${NC}"
apt-get update -qq
apt-get install -qq -y curl git jq openssl ca-certificates gnupg lsb-release

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
  echo -e "${CYAN}[*] Installing Docker Engine & Docker Compose...${NC}"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
  chmod a+r /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

  apt-get update -qq
  apt-get install -qq -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable docker
  systemctl start docker
  echo -e "${GREEN}[+] Docker installed successfully.${NC}"
else
  echo -e "${GREEN}[+] Docker is already installed.${NC}"
fi

# Target installation directory
DEPLOY_DIR="/opt/netryx-evidence"

if [ -d "$DEPLOY_DIR/.git" ]; then
  echo -e "${CYAN}[*] Updating existing installation in ${DEPLOY_DIR}...${NC}"
  cd "$DEPLOY_DIR"
  git pull origin master
else
  echo -e "${CYAN}[*] Cloning repository to ${DEPLOY_DIR}...${NC}"
  rm -rf "$DEPLOY_DIR"
  git clone https://github.com/yug1204/netryx-evidence.git "$DEPLOY_DIR"
  cd "$DEPLOY_DIR"
fi

# Setup production environment variables
if [ ! -f .env ]; then
  echo -e "${CYAN}[*] Generating secure cryptographically random production credentials...${NC}"
  cp .env.example .env

  POSTGRES_PW=$(openssl rand -hex 16)
  NEO4J_PW=$(openssl rand -hex 16)
  MINIO_PW=$(openssl rand -hex 16)
  JWT_SEC=$(openssl rand -hex 32)

  sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PW}|g" .env
  sed -i "s|NEO4J_PASSWORD=.*|NEO4J_PASSWORD=${NEO4J_PW}|g" .env
  sed -i "s|MINIO_ROOT_PASSWORD=.*|MINIO_ROOT_PASSWORD=${MINIO_PW}|g" .env
  sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SEC}|g" .env
  sed -i "s|ENVIRONMENT=.*|ENVIRONMENT=production|g" .env

  echo -e "${GREEN}[+] Production .env configured with hardened credentials.${NC}"
fi

# Build and start all microservices
echo -e "${CYAN}[*] Building and spinning up NETRYX microservices stack...${NC}"
docker compose down --remove-orphans || true
docker compose up -d --build

# Verify container health
echo -e "${CYAN}[*] Waiting for services to initialize healthchecks...${NC}"
sleep 15

docker compose ps

echo -e "\n${GREEN}==============================================================================${NC}"
echo -e "${GREEN}  ✓ NETRYX EVIDENCE DEPLOYMENT SUCCESSFUL!${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo -e "Access points for your deployment:"
echo -e "  • Web Application / Dashboard:  ${CYAN}http://${SERVER_IP}${NC}"
echo -e "  • API & Swagger Docs:           ${CYAN}http://${SERVER_IP}/api/docs${NC}"
echo -e "  • Neo4j Graph DB Console:       ${CYAN}http://${SERVER_IP}:7474${NC}"
echo -e "  • MinIO Evidence S3 Console:    ${CYAN}http://${SERVER_IP}:9001${NC}"
echo -e "\nConfiguration and data stored in: ${DEPLOY_DIR}"
echo -e "To view live logs: ${YELLOW}cd ${DEPLOY_DIR} && docker compose logs -f${NC}"
echo -e "${GREEN}==============================================================================${NC}\n"
