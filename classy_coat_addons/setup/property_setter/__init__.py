from frappe.custom.doctype.property_setter.property_setter import make_property_setter

from .quotation import get_quotation_property_setters


def create_property_setters():
	property_setters = []
	property_setters.extend(get_quotation_property_setters())

	for ps in property_setters:
		make_property_setter(
			ps["doctype"],
			ps["fieldname"],
			ps["property"],
			ps["value"],
			ps.get("property_type", "Data"),
		)
