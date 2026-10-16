def get_sales_invoice_fields():
	return {
		"Sales Invoice": [
			{
				"fieldname": "cc_attention_to",
				"label": "Attention To",
				"fieldtype": "Data",
				# Same fieldname as Quotation/Sales Order's cc_attention_to, so it carries across
				# "Make Sales Order" and "Make Sales Invoice" automatically (see sales_order.py).
				"insert_after": "cen_payment_terms",
			},
		]
	}
