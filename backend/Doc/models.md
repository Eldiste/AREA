# Backend Models and Relationships

This document represents the models and their relationships in a simple, Markdown-compatible format.

---

## Models Overview

### Entities and Their Fields

| Entity        | Fields                                                                                   |
|---------------|------------------------------------------------------------------------------------------|
| **User**      | `id`, `username`, `email`, `created_at`, `updated_at`                                    |
| **Area**      | `id`, `user_id`, `action_id`, `reaction_id`, `created_at`, `updated_at`                  |
| **Action**    | `id`, `service_id`, `name`, `description`, `config`, `created_at`, `updated_at`          |
| **Reaction**  | `id`, `service_id`, `name`, `description`, `config`, `created_at`, `updated_at`          |
| **Trigger**   | `id`, `name`, `area_id`, `config`, `last_run`, `created_at`, `updated_at`                |
| **Service**   | `id`, `name`, `description`, `created_at`, `updated_at`                                  |
| **UserService** | `id`, `user_id`, `service_id`                                                         |

---

## Relationships

### **User**
- **Owns** → `Area` (One-to-Many)
- **Subscribes** → `Service` (via `UserService`, Many-to-Many)

### **Area**
- **Uses** → `Action` (One-to-One)
- **Uses** → `Reaction` (One-to-One)
- **Has** → `Trigger` (One-to-One)
- **Belongs to** → `User` (Many-to-One)

### **Action**
- **Belongs to** → `Service` (Many-to-One)
- **Used by** → `Area` (One-to-One)

### **Reaction**
- **Belongs to** → `Service` (Many-to-One)
- **Used by** → `Area` (One-to-One)

### **Trigger**
- **Linked to** → `Area` (One-to-One)

### **Service**
- **Contains** → `Action` (One-to-Many)
- **Contains** → `Reaction` (One-to-Many)
- **Linked to** → `User` (via `UserService`, Many-to-Many)

### **UserService**
- **Connects** → `User` and `Service` (Many-to-Many association)

---

## Summary
- **Primary Keys (PK):** Each entity has a unique `id` field as its primary key.
- **Foreign Keys (FK):** Relationships between entities are established using foreign keys (e.g., `user_id`, `service_id`).
- **One-to-One Relationships:** E.g., `Area` and `Trigger`.
- **One-to-Many Relationships:** E.g., `Service` to `Action` and `Reaction`.
- **Many-to-Many Relationships:** E.g., `User` and `Service` via `UserService`.
