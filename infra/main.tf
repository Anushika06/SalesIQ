terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run Service for FastAPI Backend
resource "google_cloud_run_v2_service" "api" {
  name     = "salesiq-api"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/salesiq-api:latest"
      resources {
        limits = {
          memory = "512Mi"
        }
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    service_account = google_service_account.api_sa.email
  }
}

# Service Account with least privilege
resource "google_service_account" "api_sa" {
  account_id   = "salesiq-api-sa"
  display_name = "SalesIQ API Service Account"
}

# IAM bindings for the SA
resource "google_project_iam_member" "datastore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "dlp_user" {
  project = var.project_id
  role    = "roles/dlp.user"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "tasks_enqueuer" {
  project = var.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

# Firestore Database in Native Mode
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = "nam5" # Multi-region US
  type        = "FIRESTORE_NATIVE"
}

# Cloud Tasks Queue
resource "google_cloud_tasks_queue" "followup_queue" {
  name     = "followup-queue"
  location = var.region

  rate_limits {
    max_dispatches_per_second = 10
    max_concurrent_dispatches = 5
  }

  retry_config {
    max_attempts = 3
  }
}

# BigQuery Dataset and Table
resource "google_bigquery_dataset" "salesiq" {
  dataset_id = "salesiq"
  location   = "US"
}

resource "google_bigquery_table" "ab_tests" {
  dataset_id = google_bigquery_dataset.salesiq.dataset_id
  table_id   = "ab_tests"

  schema = <<EOF
[
  {"name": "variant_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "lead_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "angle", "type": "STRING", "mode": "REQUIRED"},
  {"name": "predicted_open_rate", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "predicted_reply_rate", "type": "FLOAT", "mode": "REQUIRED"},
  {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"}
]
EOF
}

# Secrets in Secret Manager
resource "google_secret_manager_secret" "vertex_project" {
  secret_id = "VERTEX_AI_PROJECT"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "vertex_location" {
  secret_id = "VERTEX_AI_LOCATION"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gemini_model" {
  secret_id = "GEMINI_MODEL_NAME"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "firestore_db" {
  secret_id = "FIRESTORE_DB"
  replication {
    auto {}
  }
}

# Eventarc Trigger for Google Calendar
# Note: Google Calendar Eventarc triggers require specific configuration and enablement
resource "google_eventarc_trigger" "calendar_trigger" {
  name     = "calendar-event-trigger"
  location = var.region
  
  matching_criteria {
    attribute = "type"
    value     = "google.workspace.calendar.event.v1.created" # Conceptual type, actual depends on Workspace Events setup
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.api.name
      region  = var.region
      path    = "/api/v1/callprep/generate"
    }
  }

  service_account = google_service_account.api_sa.email
}
