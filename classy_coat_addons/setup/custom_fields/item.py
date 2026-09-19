def get_item_fields():
    return {
        "Item": [
            {
                "fieldname": "cc_rack_info_section",
                "label": "Rack Info",
                "fieldtype": "Section Break",
                "insert_after": "inventory_settings_section"
            },
            {
                "fieldname": "cc_rack_locations",
                "label": "Rack Locations",
                "fieldtype": "Table",
                "options": "Item Rack Detail",
                "insert_after": "cc_rack_info_section"
            }
        ]
    }
