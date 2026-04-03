# Resource Providers Mock Data

---

## Top-Level Fields

Matches the generic Tapis response

| Field | Type | Description |
|---|---|---|
| `message` | string | Status message from the API. |
| `metadata.count` | number | Total number of resource providers returned. |
| `resourceProviders` | array | List of resource provider objects (see below). |
| `status` | string | API status (`"success"`, etc.). |
| `version` | string | Version of API. |

---

## Resource Provider Object

Each entry in `resourceProviders` represents a single HPC center or computing facility.

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for the resource provider (e.g., `"rp_tacc"`). |
| `name` | string | Display name of the institution or facility. |
| `institution` | string | The university or national lab that operates this RP. |
| `description` | string | Brief summary of the RP. |
| `status` | string | Availability of the RP (e.g., `"available"`, `"disabled"`). |
| `location` | string | Physical location of the facility (city, state, country). |
| `systems` | array | List of systems operated by this RP (see below). |
| `configFields` | array | Dynamic form fields required to configure a job submission for this RP (see below). |

---

## System Object (`systems[]`)

Each entry in `systems` represents a specific supercomputer or cluster operated by the RP.

| Field | Type | Description |
|---|---|---|
| `id` | string | Identifier for the system (e.g., `"frontera"`, `"stampede3"`). |
| `name` | string | Display name. |
| `status` | string | Availability status of the system (e.g., `"available"`, `"disabled"`). |
| `description` | string | Brief description of the system. |

---

## Config Field Object (`configFields[]`)

Each entry in `configFields` defines a form input that a user must fill out when connecting to or submitting work on the RP. These fields vary per provider.

| Field | Type | Description |
|---|---|---|
| `key` | string | The parameter name used when submitting the config (e.g., `"allocation_id"`, `"target_system"`). |
| `label` | string | Label shown in the UI form. |
| `type` | string | Input type. Since returned by an API, we used `dynamic_select` |
| `required` | boolean | Whether the field must be filled before submission. |
| `optionsEndpoint` | string | Endpoint for retrieving the options from the RP. |

---

## Resource Providers Included

| ID | Name | Systems |
|---|---|---|
| `rp_tacc` | Texas Advanced Computing Center (TACC) | Frontera, Stampede3, Lonestar6 |
| `rp_sdsc` | San Diego Supercomputer Center (SDSC) | Expanse, Voyager |
| `rp_jetstream2_006` | Jetstream2 | Jetstream2 Main |
| `rp_osc_010` | Ohio Supercomputer Center (OSC) | Owens, Pitzer |

