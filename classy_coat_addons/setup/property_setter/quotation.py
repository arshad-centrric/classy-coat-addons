def get_quotation_property_setters():
	return [
		{
			# cen_contracting anchors Project Type (and Choose Project, which is itself anchored to
			# Project Type) under Customer Name in the left column, which gets crowded. Classy Coat
			# wants both moved into the right column, under Attention To. A Property Setter keeps this
			# a client-specific layout tweak instead of editing cen_contracting's own field definition.
			"doctype": "Quotation",
			"fieldname": "cen_project_type",
			"property": "insert_after",
			"value": "cc_attention_to",
		},
	]
