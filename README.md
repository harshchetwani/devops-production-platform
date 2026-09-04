# Production-Grade DevOps Platform

A production-style DevOps platform built around a containerized Order Management API, demonstrating modern DevOps, Kubernetes, CI/CD, security, observability, autoscaling, self-healing, database reliability, and failure-testing practices.

## Project Overview

This project demonstrates the complete application lifecycle:

Code → Test → Build → Scan → Publish → Deploy → Monitor → Alert → Recover

The implementation runs locally using Kubernetes with Minikube, while the automated CD pipeline validates deployments using Kind.

## High-Level Architecture

Developer
↓
GitHub Repository
↓
GitHub Actions
↓
Tests → Docker Build → Trivy Scan → GHCR
↓
Helm Deployment
↓
Kubernetes Cluster
├── Order API
├── PostgreSQL
├── Prometheus
├── Grafana
├── Loki
└── Alertmanager
↓
Monitoring + Logging + Alerts + Self-Healing

## End-to-End DevOps Workflow

Developer pushes code to GitHub.

GitHub Actions starts the CI pipeline.

The pipeline performs:

Python dependency installation
Database initialization
Automated tests
Docker image build
Trivy vulnerability scan
Helm lint
Helm template validation

If CI succeeds, the Docker image is published to GitHub Container Registry.

The successful commit SHA is then used by the CD workflow.

CD creates a Kubernetes Kind cluster and deploys the application using Helm.

The deployment is verified through:

Kubernetes rollout status
Pod status
Service status
PostgreSQL status
Application health endpoint

The overall workflow is:

Git Push → CI → Test → Build → Scan → Publish → CD → Helm → Kubernetes → Health Check

## Continuous Integration

The CI pipeline validates application code before deployment.

The pipeline includes:

Test

The application is tested against PostgreSQL 16.

The database schema is initialized before running the test suite.

The test suite currently passes with:

7 tests passed

Docker Build

A Docker image is built using the application Dockerfile.

Security Scan

Trivy scans the container image for CRITICAL and HIGH vulnerabilities.

The configured CI policy ignores vulnerabilities for which no fixed version is available.

Helm Validation

The Helm chart is validated using:

Helm lint
Helm template

Image Publishing

Successful pushes to main publish the application image to GitHub Container Registry.

## Continuous Deployment

The CD pipeline runs automatically after a successful CI workflow on the main branch.

The deployment flow is:

GitHub Actions
↓
Checkout exact successful CI commit
↓
Create Kind Kubernetes cluster
↓
Validate Helm chart
↓
Generate database credentials
↓
Deploy PostgreSQL
↓
Initialize database
↓
Create least-privilege application user
↓
Create application Secret
↓
Deploy Order API
↓
Wait for rollout
↓
Run health verification

The deployment uses the exact successful Git commit SHA as the container image tag.

This prevents the deployment pipeline from accidentally deploying a different source revision.

## Application Architecture

The application is an Order Management API built using:

Python
FastAPI
SQLAlchemy
PostgreSQL
Uvicorn
Prometheus instrumentation

The API provides order management functionality and exposes health endpoints for Kubernetes.

## Application Health Model

The application exposes:

GET /health

Used for liveness.

A successful response indicates that the application process is healthy.

GET /ready

Used for readiness.

This endpoint determines whether the application is ready to receive traffic.

Kubernetes uses these endpoints for automatic health management.

## Docker Containerization

The application uses a lightweight Python 3.12 slim base image.

The container is hardened by:

Running as a non-root user
Disabling privilege escalation
Removing unnecessary package cache
Using a minimal base image
Setting Python to unbuffered mode
Defining a container health check
Using a dedicated application user
Keeping the application directory owned by the application user

The container runs Uvicorn as the main application process.

## Kubernetes Architecture

The application runs inside Kubernetes using separate workloads for:

Order API
PostgreSQL
PostgreSQL Exporter
Monitoring components
Logging components
Alerting components

The Order API is exposed internally through a Kubernetes Service.

Ingress provides external access to the application.

## Kubernetes Deployment

The Order API deployment uses:

2 minimum replicas
Rolling updates
Readiness probes
Liveness probes
CPU and memory requests
CPU and memory limits
Security context
Seccomp RuntimeDefault
Disabled service-account token mounting
Pod anti-affinity
Graceful termination

The rolling update strategy uses:

maxSurge: 1

maxUnavailable: 0

This allows new pods to become available before existing pods are removed.

## Helm

The Kubernetes resources are packaged using Helm.

Helm manages:

Deployment
Service
ConfigMap
PostgreSQL
PersistentVolumeClaim
HPA
NetworkPolicy
ServiceMonitor
PrometheusRule

The chart can be validated using Helm lint and rendered using Helm template.

## Ingress

NGINX Ingress is used to expose the Order API.

The local hostname is:

order-api.local

The traffic flow is:

Browser
↓
NGINX Ingress
↓
Order API Service
↓
Order API Pods
↓
PostgreSQL

The current local environment uses HTTP.

Production deployments should use HTTPS/TLS with managed certificates.

PostgreSQL

PostgreSQL 16 is used as the application's relational database.

The database contains the order data and supports persistent storage through a Kubernetes PersistentVolumeClaim.

PostgreSQL runs as a separate Kubernetes workload.

## Database Architecture

The database uses two different PostgreSQL roles.

order_user

Bootstrap/database administration account used during database initialization.

order_app

Runtime application account.

The Order API uses order_app rather than the bootstrap account.

This separates database initialization privileges from application runtime privileges.

## Database Least Privilege

The application database user is configured without:

Superuser privileges
Database creation privileges
Role creation privileges
Replication privileges
RLS bypass privileges

The application account receives only the permissions required by the application.

The permission boundary was tested by confirming that the application user cannot create databases.

## PostgreSQL Persistence

PostgreSQL uses a Kubernetes PersistentVolumeClaim.

The current local configuration provides:

Storage: 1Gi

Access mode: ReadWriteOnce

The persistence configuration was tested by:

Creating database data
Restarting/recreating the PostgreSQL pod
Verifying that the data remained available
## Database Backup and Restore

PostgreSQL backup and restore procedures were tested locally.

The workflow is:

PostgreSQL
↓
Logical backup
↓
Backup file
↓
Restore into PostgreSQL
↓
Verify schema/data

This demonstrates a basic database recovery workflow.

Production environments should additionally use scheduled backups, off-cluster storage, retention policies, encryption, and restore testing.

## Kubernetes Security

The Order API pod uses Kubernetes security hardening.

The configuration includes:

runAsNonRoot
runAsUser 1000
runAsGroup 1000
allowPrivilegeEscalation false
Drop ALL Linux capabilities
seccomp RuntimeDefault
automountServiceAccountToken false

This reduces the privileges available to the application container.

## Container Security

The container image is scanned using Trivy.

The current scan policy checks:

CRITICAL + HIGH vulnerabilities

and ignores vulnerabilities that currently have no fixed version.

The latest tested dependency image passed the configured security policy with:

0 CRITICAL vulnerabilities

0 HIGH vulnerabilities

No Python package vulnerabilities were reported under the configured policy.

## NetworkPolicies

NetworkPolicies are defined for the application and PostgreSQL.

The Order API is permitted to communicate with PostgreSQL on port 5432.

The application also requires DNS access.

PostgreSQL only accepts traffic from:

Order API pods
PostgreSQL Exporter

The policies are part of the Helm deployment.

The current Minikube networking configuration does not enforce NetworkPolicies because the local cluster is not using a NetworkPolicy-capable CNI.

Therefore, the policies are configured and ready for an appropriate production Kubernetes environment, but their enforcement was not claimed as successful in the default Minikube environment.

## Resource Management

The Order API defines:

CPU request: 100m

Memory request: 128Mi

CPU limit: 500m

Memory limit: 512Mi

PostgreSQL defines:

CPU request: 100m

Memory request: 128Mi

CPU limit: 500m

Memory limit: 512Mi

These settings provide predictable resource scheduling and prevent unlimited resource consumption.

## Horizontal Pod Autoscaling

The Order API uses Kubernetes Horizontal Pod Autoscaling.

Configuration:

Minimum replicas: 2

Maximum replicas: 5

CPU target: 70%

HPA behavior was tested under CPU load.

The application successfully scaled from:

2 pods → 5 pods

when CPU utilization increased.

After the load stopped, the workload returned toward the configured minimum replica count.

## Self-Healing

Kubernetes automatically recreates failed application pods.

The self-healing behavior was tested by deleting application pods.

The expected workflow is:

Pod fails
↓
Kubernetes detects missing replica
↓
ReplicaSet creates replacement pod
↓
New pod starts
↓
Readiness probe succeeds
↓
Traffic resumes

The Order API successfully recovered from individual pod failures.

## Multiple Pod Failure

Multiple Order API pods were intentionally deleted during testing.

Kubernetes recreated the required replicas.

The application returned to the expected healthy state.

This validated Kubernetes replica management and application recovery behavior.

## PostgreSQL Failure Recovery

The PostgreSQL pod was intentionally deleted.

Kubernetes recreated the PostgreSQL pod using the deployment configuration.

Persistent database storage remained available.

The application recovered after PostgreSQL became available again.

## Rolling Updates

The Order API uses Kubernetes rolling updates.

The update strategy ensures that unavailable replicas are minimized during deployment.

The rollout process was tested successfully.

The application remained available while the deployment was updated.

## Availability During Rolling Updates

Application requests were continuously sent while a rolling update was running.

Successful HTTP responses continued during the deployment.

This demonstrated that multiple replicas and the rolling update strategy can maintain application availability during normal updates.

## Graceful Shutdown

The Order API uses a termination grace period of:

30 seconds

When Kubernetes terminates a pod:

Traffic is removed from the terminating pod
↓
Application receives termination signal
↓
Uvicorn performs graceful shutdown
↓
Application exits cleanly

The application process was verified to run as the container's main process.

## Pod Anti-Affinity

Pod anti-affinity is configured for the Order API.

The scheduler prefers placing replicas on different Kubernetes nodes when possible.

This reduces the risk of losing all replicas because of a single node failure.

The configuration uses:

kubernetes.io/hostname

as the topology key.

The anti-affinity configuration was successfully rendered and applied through Helm.

## PodDisruptionBudget

A PodDisruptionBudget is configured for the Order API.

The purpose is to protect application availability during voluntary Kubernetes disruptions.

It provides an additional availability control alongside:

Multiple replicas
Rolling updates
Pod anti-affinity
Health probes
HPA
## Observability Architecture

The observability stack consists of:

Metrics

Prometheus

Visualization

Grafana

Logging

Loki and Alloy

Alerting

Alertmanager

The overall observability flow is:

Order API
↓
Metrics → Prometheus → Grafana

Application Logs
↓
Alloy
↓
Loki
↓
Grafana

Prometheus Alerts
↓
Alertmanager
↓
Alert Receiver

Prometheus

Prometheus collects application and infrastructure metrics.

The Order API exposes Prometheus metrics through application instrumentation.

Metrics include HTTP request information and application performance data.

Prometheus is also used for alert evaluation.

## PostgreSQL Monitoring

PostgreSQL Exporter exposes PostgreSQL metrics to Prometheus.

The exporter runs as a separate Kubernetes deployment.

Prometheus successfully reported:

pg_up = 1

This confirmed that PostgreSQL monitoring was working.

Database connection activity was also visible through PostgreSQL metrics.

## Grafana

Grafana is used for visualization.

Dashboards were created to observe:

Order API health
HTTP traffic
Request behavior
CPU usage
Memory usage
Kubernetes workloads
PostgreSQL metrics
Application logs

Grafana is connected to both Prometheus and Loki.

## Centralized Logging

The logging stack uses:

Alloy → Loki → Grafana

Application logs are collected centrally rather than relying only on kubectl logs.

This allows operators to search and analyze application logs through Grafana.

## Alertmanager

Alertmanager handles alerts generated by Prometheus.

The project includes alert routing for application error-rate conditions.

The alerting flow is:

Prometheus
↓
Alert Rule
↓
Alert Fires
↓
Alertmanager
↓
Webhook Receiver

When the condition clears:

Prometheus
↓
Alert Resolves
↓
Alertmanager
↓
Webhook Receiver

## Alert Testing

The OrderApiHighErrorRate alert was intentionally triggered during testing.

The test confirmed:

Prometheus detected the condition
The alert transitioned to firing
Alertmanager received the alert
The configured receiver was selected
The webhook returned HTTP 200
The alert later transitioned to resolved
Alertmanager delivered the resolved event

This validates the complete alerting path rather than only validating configuration files.

## CI/CD Security

GitHub Actions permissions are restricted.

CI uses:

contents: read

and package publishing permissions where required.

CD uses:

contents: read

and package read permissions.

The workflows do not request unnecessary cloud identity permissions.

Deployment uses the exact successful CI commit SHA.

## Immutable Image Deployment

The CD pipeline deploys the image using the Git commit SHA.

For example:

Repository commit
↓
CI builds image using commit SHA
↓
Image pushed to GHCR
↓
CD checks out same SHA
↓
CD deploys same SHA image

This prevents accidental deployment of a different image version.

## Trivy Vulnerability Scanning

Trivy is integrated into CI.

The Docker image is scanned before publication.

The security policy checks CRITICAL and HIGH vulnerabilities.

The scan is configured to fail the build when applicable vulnerabilities are detected.

The currently tested dependency image passed the configured CI security policy.

## Dependency Pinning

Python dependencies are pinned to tested versions.

The current requirements include pinned versions for:

FastAPI
Uvicorn
SQLAlchemy
psycopg2-binary
Pydantic
Pytest
HTTPX
prometheus-fastapi-instrumentator

Dependency pinning improves reproducibility and reduces unexpected dependency changes between builds.

The pinned dependency set was tested using:

pip freeze
pip check
pytest
Trivy
## Automated Testing

The automated test suite currently reports:

7 passed

The tests validate application behavior against PostgreSQL.

Testing is performed automatically during CI.

A deployment cannot proceed through the automated workflow unless CI succeeds.

## Failure Testing Matrix

The following failure scenarios were tested:

Order API single pod failure

Pod deleted → Kubernetes recreated pod → Application recovered.

Multiple Order API pod failure

Multiple pods deleted → Kubernetes recreated replicas → Application returned to healthy state.

PostgreSQL pod failure

PostgreSQL pod deleted → Kubernetes recreated PostgreSQL → Database became available again.

Rolling update

New version deployed → Old pods gradually replaced → Rollout completed successfully.

Availability during rolling update

Continuous requests → Deployment rollout → Requests continued successfully.

Alert firing

Error condition generated → Prometheus alert fired → Alertmanager notified webhook.

Alert recovery

Error condition cleared → Alert resolved → Resolved event delivered.

Database persistence

Database data created → PostgreSQL restarted → Data remained available.

## Security Architecture

The security model includes several layers:

Developer security
↓
GitHub Actions permissions
↓
Dependency pinning
↓
Container image scanning
↓
Non-root container
↓
Kubernetes security context
↓
NetworkPolicies
↓
Least-privilege database user
↓
Secret-based configuration

No single security control is treated as sufficient by itself.

## Secrets Management

Secrets are not committed to Git.

Kubernetes Secrets are used for database credentials.

The CD workflow generates temporary database credentials during deployment.

The bootstrap database credential and application database credential are separate.

The application uses the least-privilege database account at runtime.

Actual secret values are never stored in the repository documentation.

## Repository Structure

The project is organized around the major DevOps components.

application/

Contains the Python Order Management API.

helm/

Contains the Kubernetes Helm chart.

.github/workflows/

Contains CI/CD workflows.

terraform/

Contains infrastructure-related material retained from the earlier project structure, but the current implementation does not depend on AWS infrastructure.

docker-compose.yml

Provides a local container-based development option where applicable.

README.md

Contains project architecture, workflows, operational information, and validation results.

## Local Development Environment

The project was developed and tested using:

macOS
Docker Desktop
Minikube
kubectl
Helm
Git
GitHub
GitHub Actions
GitHub Container Registry

The primary local Kubernetes environment is Minikube.

The automated CD workflow uses Kind inside GitHub Actions for deployment validation.

## Local Deployment Architecture

Local development architecture:

Developer Machine
↓
Docker Desktop
↓
Minikube
↓
NGINX Ingress
↓
Order API
↓
PostgreSQL

Monitoring architecture:

Order API
↓
Prometheus
↓
Grafana

Logging architecture:

Order API
↓
Alloy
↓
Loki
↓
Grafana

Alerting architecture:

Prometheus
↓
Alertmanager
↓
Webhook Receiver

## Operational Workflow

A typical operator workflow is:

Check cluster
→ Check nodes
→ Check pods
→ Check deployments
→ Check services
→ Check ingress
→ Check application health
→ Check logs
→ Check metrics
→ Check alerts

For an application problem:

Check application health
→ Check pod status
→ Check pod events
→ Check application logs
→ Check PostgreSQL
→ Check Prometheus
→ Check Grafana
→ Check Alertmanager
→ Recover or rollback

## Application Health Verification

The application should be considered healthy when:

Pods are Running
Readiness probes succeed
Liveness probes succeed
/health returns healthy
/ready indicates readiness
PostgreSQL is available
Prometheus reports application metrics
No unexpected application errors are present
## Production-Style Reliability Model

The reliability design combines:

Multiple replicas

Protects against individual pod failure.

HPA

Adjusts capacity according to workload.

Readiness probes

Prevents traffic from reaching unready pods.

Liveness probes

Allows Kubernetes to restart unhealthy containers.

Rolling updates

Reduces deployment downtime.

Pod anti-affinity

Reduces replica concentration.

PodDisruptionBudget

Protects availability during voluntary disruptions.

Persistent storage

Protects database data from pod recreation.

Monitoring and alerting

Provides operational visibility.

## Production-Style Observability Model

The platform follows three major observability pillars:

Metrics

Prometheus collects quantitative system and application measurements.

Logs

Loki stores centrally collected application logs.

Alerts

Alertmanager routes actionable conditions.

Grafana provides a unified visualization layer.

## Production-Style Security Model

The security model follows defense in depth.

Application layer:

Dependency pinning
Automated tests
Secure container image

Container layer:

Non-root user
Dropped capabilities
No privilege escalation
Seccomp

Kubernetes layer:

NetworkPolicies
Resource limits
Restricted service-account token mounting

Database layer:

Separate runtime user
Least privilege
Persistent storage

CI/CD layer:

Restricted GitHub permissions
Image scanning
Immutable SHA deployment
## Complete Application Lifecycle

The complete platform lifecycle is:

Developer writes code
↓
Code pushed to GitHub
↓
GitHub Actions starts CI
↓
Dependencies installed
↓
Database initialized
↓
Tests executed
↓
Docker image built
↓
Trivy security scan
↓
Helm validation
↓
Image published to GHCR
↓
CD workflow starts
↓
Exact successful commit checked out
↓
Kind cluster created
↓
PostgreSQL deployed
↓
Database initialized
↓
Least-privilege user created
↓
Application Secret created
↓
Order API deployed
↓
Kubernetes rollout verified
↓
Health endpoint verified
↓
Prometheus collects metrics
↓
Grafana visualizes metrics
↓
Alloy collects logs
↓
Loki stores logs
↓
Prometheus evaluates alerts
↓
Alertmanager routes alerts
↓
Kubernetes provides self-healing
↓
Operators investigate and recover failures

## Project Validation

The project has been validated across multiple dimensions.

Application

Order API successfully deployed and tested.

Database

PostgreSQL persistence and recovery tested.

CI

Automated test, build, security scan, and Helm validation succeeded.

CD

Automated deployment workflow succeeded.

Security

Container, Kubernetes, database, secrets, permissions, and workflow security were reviewed.

Autoscaling

HPA scaling from 2 to 5 replicas was successfully tested.

Self-Healing

Single and multiple pod failures were successfully recovered.

Rolling Updates

Application remained available during tested rolling deployments.

Observability

Prometheus, Grafana, PostgreSQL Exporter, Loki, and Alloy were validated.

Alerting

Prometheus → Alertmanager → Webhook firing and resolution were successfully tested.

Backup

PostgreSQL backup and restore workflow was successfully tested.

## Security Checklist

✓ Secrets excluded from Git

✓ No production passwords committed

✓ No private keys committed

✓ Non-root application container

✓ Privilege escalation disabled

✓ Linux capabilities dropped

✓ Seccomp RuntimeDefault enabled

✓ Service-account token mounting disabled for Order API

✓ Least-privilege runtime database account

✓ Trivy scanning enabled

✓ Python dependencies pinned

✓ GitHub Actions permissions restricted

✓ SHA-based image deployment

✓ NetworkPolicies defined

✓ Kubernetes services use internal ClusterIP networking

## Reliability Checklist

✓ Multiple API replicas

✓ HPA enabled

✓ Readiness probes

✓ Liveness probes

✓ Resource requests

✓ Resource limits

✓ Rolling update strategy

✓ Graceful shutdown

✓ Pod anti-affinity

✓ PodDisruptionBudget

✓ Kubernetes self-healing

✓ PostgreSQL persistent storage

✓ PostgreSQL recovery tested

✓ Application failure tested

✓ Rolling update tested

✓ Availability during deployment tested

## Observability Checklist

✓ Prometheus

✓ Grafana

✓ Alertmanager

✓ PostgreSQL Exporter

✓ Loki

✓ Alloy

✓ Application metrics

✓ PostgreSQL metrics

✓ Centralized logs

✓ Alert firing test

✓ Alert resolution test

## Current Project Status

The current project demonstrates a complete production-style DevOps workflow running without an AWS dependency.

The platform includes:

Application

Order Management API

Database

PostgreSQL 16

Containerization

Docker

Orchestration

Kubernetes

Packaging

Helm

Ingress

NGINX Ingress

CI/CD

GitHub Actions

Registry

GitHub Container Registry

Security

Trivy + Kubernetes security hardening + least privilege

Monitoring

Prometheus + Grafana

Logging

Loki + Alloy

Alerting

Alertmanager

Scaling

Horizontal Pod Autoscaler

Reliability

Self-healing + rolling updates + anti-affinity + PDB

Database Reliability

Persistent storage + backup/restore testing

## Future Improvements

Possible future enhancements include:

Production Kubernetes cluster
Managed PostgreSQL
External secret management
TLS certificates
NetworkPolicy-capable production CNI
GitOps with Argo CD
Distributed tracing
OpenTelemetry
Advanced Grafana dashboards
Scheduled database backups
Off-cluster backup storage
Disaster recovery automation
Image signing
SBOM generation
Admission policies
Automated performance testing

These are future improvements and are not required for the current local implementation.

## Key DevOps Concepts Demonstrated

This project demonstrates practical knowledge of:

Linux containers
Docker
Kubernetes
Helm
Kubernetes networking
Ingress
ConfigMaps
Secrets
Persistent Volumes
Persistent Volume Claims
NetworkPolicies
Resource requests and limits
HPA
Self-healing
Rolling updates
Graceful shutdown
Pod anti-affinity
PodDisruptionBudget
PostgreSQL
Database permissions
Database persistence
Database backup and restore
Prometheus
Grafana
Loki
Alloy
Alertmanager
GitHub Actions
GitHub Container Registry
Trivy
Dependency management
CI/CD security
Failure testing
Operational troubleshooting

## Final Architecture Summary

The final platform can be summarized as:

Developer
↓
GitHub
↓
GitHub Actions
↓
Test
↓
Docker Build
↓
Trivy Scan
↓
GHCR
↓
Automated CD
↓
Helm
↓
Kubernetes
├── Order API
├── PostgreSQL
├── NGINX Ingress
├── Prometheus
├── Grafana
├── Loki
├── Alloy
└── Alertmanager

The platform demonstrates the complete DevOps lifecycle from source code to deployment, monitoring, alerting, failure recovery, and operational validation.

## Author

Harsh Chetwani

DevOps / Cloud / Kubernetes / CI/CD Portfolio Project

## License

This project is intended for educational, portfolio, and demonstration purposes.
