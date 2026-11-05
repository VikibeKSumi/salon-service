terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "~> 6.0" }
  }
}

variable "project_id" {}
variable "region" { default = "asia-south1" }
variable "app" { default = "salon" }

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------- enable ----------
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "cloudbuild.googleapis.com",
    "clouddeploy.googleapis.com",
    "logging.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

# ---------- create ----------
resource "google_artifact_registry_repository" "repo" {
  repository_id = var.app
  format        = "DOCKER"
  location      = var.region
  depends_on    = [google_project_service.apis]
}

resource "google_storage_bucket" "release" {
  name                        = "${var.project_id}-release-bucket"
  location                    = var.region
  uniform_bucket_level_access = true
  depends_on                  = [google_project_service.apis]
}

resource "google_secret_manager_secret" "env" {
  secret_id = "${var.app}-secrets"
  replication {
    user_managed {
      replicas { location = var.region }
    }
  }
  depends_on = [google_project_service.apis]
}

resource "google_service_account" "sa" {
  for_each     = toset(["ci", "build", "deploy", "staging", "prod"])
  account_id   = "${var.app}-${each.key}"
  display_name = "${var.app} ${each.key}"
  depends_on   = [google_project_service.apis]
}

# ---------- bind: project-level ----------
locals {
  project_roles = {
    "ci-logs"       = { sa = "ci", role = "roles/logging.logWriter" }
    "build-logs"    = { sa = "build", role = "roles/logging.logWriter" }
    "build-release" = { sa = "build", role = "roles/clouddeploy.releaser" }
    "deploy-logs"   = { sa = "deploy", role = "roles/logging.logWriter" }
    "deploy-jobs"   = { sa = "deploy", role = "roles/clouddeploy.jobRunner" }
    "deploy-run"    = { sa = "deploy", role = "roles/run.admin" }
  }
}

resource "google_project_iam_member" "project" {
  for_each = local.project_roles
  project  = var.project_id
  role     = each.value.role
  member   = "serviceAccount:${google_service_account.sa[each.value.sa].email}"
}

# ---------- bind: repo ----------
resource "google_artifact_registry_repository_iam_member" "repo" {
  for_each = {
    build  = "roles/artifactregistry.writer"
    deploy = "roles/artifactregistry.reader"
  }
  repository = google_artifact_registry_repository.repo.name
  location   = var.region
  role       = each.value
  member     = "serviceAccount:${google_service_account.sa[each.key].email}"
}

# ---------- bind: bucket ----------
resource "google_storage_bucket_iam_member" "bucket" {
  for_each = toset(["roles/storage.objectAdmin", "roles/storage.legacyBucketReader"])
  bucket   = google_storage_bucket.release.name
  role     = each.key
  member   = "serviceAccount:${google_service_account.sa["build"].email}"
}

# ---------- bind: secret ----------
resource "google_secret_manager_secret_iam_member" "secret" {
  for_each  = toset(["staging", "prod"])
  secret_id = google_secret_manager_secret.env.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.sa[each.key].email}"
}

# ---------- bind: impersonation ----------
resource "google_service_account_iam_member" "build_acts_as_deploy" {
  service_account_id = google_service_account.sa["deploy"].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.sa["build"].email}"
}

resource "google_service_account_iam_member" "deploy_acts_as_runtime" {
  for_each           = toset(["staging", "prod"])
  service_account_id = google_service_account.sa[each.key].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.sa["deploy"].email}"
}

# ---------- delivery pipeline ----------
resource "google_clouddeploy_target" "staging" {
  name     = "staging"
  location = var.region
  run { location = "projects/${var.project_id}/locations/${var.region}" }
  execution_configs {
    usages          = ["RENDER", "DEPLOY"]
    service_account = google_service_account.sa["deploy"].email
  }
  depends_on = [google_project_service.apis]
}

resource "google_clouddeploy_target" "production" {
  name             = "production"
  location         = var.region
  require_approval = true
  run { location = "projects/${var.project_id}/locations/${var.region}" }
  execution_configs {
    usages          = ["RENDER", "DEPLOY"]
    service_account = google_service_account.sa["deploy"].email
  }
  depends_on = [google_project_service.apis]
}

resource "google_clouddeploy_delivery_pipeline" "pipeline" {
  name     = "${var.app}-pipeline"
  location = var.region
  serial_pipeline {
    stages {
      target_id = google_clouddeploy_target.staging.name
      profiles  = ["staging"]
    }
    stages {
      target_id = google_clouddeploy_target.production.name
      profiles  = ["production"]
    }
  }
}

output "repo_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${var.app}"
}
