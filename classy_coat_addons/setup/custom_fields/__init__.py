from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as make_custom_fields

from .employee import get_employee_fields
from .item import get_item_fields
from .quotation import get_quotation_fields
from .sales_invoice import get_sales_invoice_fields
from .sales_order import get_sales_order_fields

def create_custom_fields():
    custom_fields = {}

    custom_fields.update(get_item_fields())
    custom_fields.update(get_employee_fields())
    custom_fields.update(get_quotation_fields())
    custom_fields.update(get_sales_order_fields())
    custom_fields.update(get_sales_invoice_fields())

    make_custom_fields(custom_fields)
