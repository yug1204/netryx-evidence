# NETRYX EVIDENCE 🛡️🔍

> **Enterprise Cloud-Native Digital Forensics, Incident Response & Threat Graph Investigation Platform**

[![Deploy Frontend to GitHub Pages](https://github.com/yug1204/netryx-evidence/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/yug1204/netryx-evidence/actions/workflows/deploy-pages.yml)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue?style=flat&logo=github)](https://yug1204.github.io/netryx-evidence/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react)](https://react.dev)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph%20DB-008CC1?style=flat&logo=neo4j)](https://neo4j.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://www.docker.com)

---

## 🌐 Live Access

- **Public Interactive App:** [https://yug1204.github.io/netryx-evidence/](https://yug1204.github.io/netryx-evidence/)
- **Repository:** [https://github.com/yug1204/netryx-evidence](https://github.com/yug1204/netryx-evidence)

---

## 🚀 One-Command Cloud VPS Deployment

Deploy the entire 8-container microservices platform to any Ubuntu/Debian Cloud VPS (AWS EC2, DigitalOcean, Hetzner, Linode) in 60 seconds:

```bash
curl -sSL https://raw.githubusercontent.com/yug1204/netryx-evidence/master/deploy.sh | sudo bash
```

The script automatically:
1. Installs Docker Engine and Docker Compose
2. Clones the repository to `/opt/netryx-evidence`
3. Generates cryptographically secure production keys for PostgreSQL, Neo4j, MinIO, and JWT
4. Builds and boots all 8 microservices via Docker Compose
5. Configures Nginx reverse proxy with routing and security headers
6. Verifies container health and prints your live server access points

---

## 🏗️ Architecture & Component Stack

```mermaid
graph TD
    Client[Browser / Threat Analyst] -->|HTTPS :443 / HTTP :80| Nginx[Nginx Reverse Proxy & Static Host]
    Nginx -->|Frontend SPA Routes| ReactApp[React 19 + Cytoscape + Lucide]
    Nginx -->|/api/*| FastAPI[FastAPI Core Engine :8000]

    subgraph Storage & Knowledge Layer
        FastAPI -->|Relational Data & Vectors| PG[(PostgreSQL 16 + pgvector)]
        FastAPI -->|Knowledge Graph / Attack Paths| Neo4j[(Neo4j 5.20 Graph Database)]
        FastAPI -->|Object Storage / Raw Disk & PCAP| MinIO[(MinIO S3 Evidence Store)]
        FastAPI -->|Task Broker & Token Cache| Redis[(Redis 7.2)]
    end

    subgraph Distributed Processing Engine
        Redis -->|Queue Tasks| Celery[Celery Async Analysis Workers]
        Celery -->|Extract Hashes / Yara / IOCs| PG
        Celery -->|Inject IOC & Entity Relationships| Neo4j
        Celery -->|Stream Raw Artifacts| MinIO
    end
```

---

## 🔑 Core Features

1. **Enterprise Case Management & Forensic Vault:**
   - Multi-tenant case tracking with full evidentiary chain of custody (NIST SP 800-86 compliant).
   - Immutable SHA-256 and MD5 cryptographic integrity verification on upload.
   - S3-compatible chunked upload handling disk images (E01/RAW), PCAPs, memory dumps, and logs.

2. **Interactive Graph Visualizer (Cytoscape.js):**
   - Real-time cyber threat graph mapping Threat Actors, Malware Families, C2 Infrastructure, Infected Hosts, and Lateral Movement.
   - Blast-radius discovery and Dijkstra shortest attack path routing.

3. **Autonomous Celery Worker Pipeline:**
   - Asynchronous parsing of PCAPs, PE/ELF binaries, Sysmon EVTX, and memory dumps.
   - YARA rule matching, high-entropy packed section detection, and IoC extraction.
   - Threat scoring algorithm (0-100) factoring CVSS, reputation feeds, and graph centrality.

4. **AI-Powered Forensic Assistant:**
   - Autonomous query engine for investigating IoCs, generating timeline summaries, and drafting incident triage reports.
   - Multi-turn investigation dialog with simulated evidence correlation.

5. **Production Dockerized Infrastructure:**
   - Multi-stage Docker builds for minimal attack surface.
   - Healthcheck orchestration across PostgreSQL, Neo4j, Redis, MinIO, and Celery.
   - Nginx reverse proxy with gzip compression and strict security headers.

---

## 💻 Local Development Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose (optional for containerized mode)

### 1. Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Access the dev server at `http://localhost:5173`.

### 2. Run Backend with Docker
```bash
cp .env.example .env
docker compose up --build
```
Access:
- Frontend: `http://localhost`
- API Docs: `http://localhost:8000/api/docs`
- Neo4j Browser: `http://localhost:7474`
- MinIO Console: `http://localhost:9001`

---

## 🛡️ License

MIT License. Designed and engineered for high-consequence incident response teams and cyber forensic investigations.
