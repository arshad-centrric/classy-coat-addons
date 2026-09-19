# classy_coat_addons Developer Guide

## Architecture Overview
This app holds customizations specific to **Classy Coat Technical Services Co. LLC** on top of the generic `cen_contracting` app. It follows the same **DocType-centric directory structure** as `cen_contracting`, so logic stays isolated and easy to find across both apps.

* **`classy_coat_addons/classy_coat_addons/doctype/`**: New **standard** DocTypes owned by this app (e.g. `Warehouse Rack`, `Item Rack Detail`). Created as real DocType records (`custom = 0`) so they export to disk as JSON + controller files, not as Custom DocTypes living only in the database.
* **`classy_coat_addons/setup/`**: Python-based, programmatic schema changes to **existing** (standard or foreign-app) DocTypes — Custom Fields and Property Setters. Nothing here is a Frappe export fixture.
* **`classy_coat_addons/overrides/`**: All backend business logic — `validate`/`on_submit`/etc. hooks, doctype class overrides.
  * **Structure:** `overrides/[doctype_name]/[feature_name].py`
  * **Example:** `overrides/item/rack_validation.py`
* **`classy_coat_addons/public/js/`**: Client-side UI scripts, named after their DocType.

## Strict Development Rules

1. **NO EXPORTED FIXTURES FOR CUSTOM FIELDS OR PROPERTY SETTERS:**
   Do not use standard Frappe export fixtures. All new custom fields must be defined programmatically as a dictionary inside `classy_coat_addons/setup/custom_fields/<doctype>.py`, following the pattern in `item.py`. All property setter changes (making a standard field hidden, read-only, mandatory, changing its options, etc.) go in `classy_coat_addons/setup/property_setter/<doctype>.py`, using `make_property_setter`. Both are wired into `after_migrate` in `hooks.py` so they apply automatically on `bench migrate`.

2. **PREFIX CONVENTION:**
   Every custom field created for this app must strictly use the `cc_` prefix (e.g., `cc_rack_locations`), short for Classy Coat.

3. **CLIENT SCRIPTS:**
   Do not write JavaScript inside the standard ERPNext "Client Script" DocType GUI. All UI overrides must be written in `public/js/` and mapped in `hooks.py` using the `doctype_js` dictionary.

4. **ADDING NEW BUSINESS LOGIC:**
   Any future Python code that isn't schema setup (custom fields/property setters) — document hooks (`validate`, `on_submit`, `before_insert`, ...), doctype class overrides, standalone helper/domain logic — goes under `overrides/[doctype_name]/[feature_name].py`. Do not create a separate `domain/`, `custom_logic/`, or similar folder; `overrides/` is the single home for all backend logic in this app, same as in `cen_contracting`. Map any document hooks in `hooks.py`'s `doc_events` pointing at these functions.

5. **NEW STANDARD DOCTYPES:**
   When a feature needs its own DocType (not a field bolted onto an existing one), create it as a standard DocType (`custom = 0`) so it lives in `classy_coat_addons/classy_coat_addons/doctype/` and exports to disk — never as a Custom DocType kept only in the database.
