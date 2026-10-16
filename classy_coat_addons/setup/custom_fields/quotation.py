def get_quotation_fields():
	return {
		"Quotation": [
			{
				"fieldname": "cc_attention_to",
				"label": "Attention To",
				"fieldtype": "Data",
				# cen_payment_terms ("Payment Term") sits in the Details tab, right column, after Valid Till.
				"insert_after": "cen_payment_terms",
			},
			{
				"fieldname": "cc_hide_item_code",
				"label": "Hide Item Code",
				"fieldtype": "Check",
				"default": "1",
				# Checked by default so existing behaviour (no Item Code column on the print format)
				# doesn't change for anyone; uncheck it on a quotation to print that column.
				"insert_after": "group_same_items",
			},
			{
				"fieldname": "cc_customer_tax_id",
				"label": "Customer Tax ID",
				"fieldtype": "Data",
				"read_only": 1,
				# Fetched by public/js/quotation.js whenever Customer is (re)selected; not fetch_from
				# because party_name is a Dynamic Link and the party type isn't always Customer.
				"insert_after": "cen_customer_category",
			},
		]
	}
