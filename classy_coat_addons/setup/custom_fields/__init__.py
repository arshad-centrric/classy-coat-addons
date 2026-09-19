from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as make_custom_fields

from .item import get_item_fields

def create_custom_fields():
    custom_fields = {}

    custom_fields.update(get_item_fields())

    make_custom_fields(custom_fields)
