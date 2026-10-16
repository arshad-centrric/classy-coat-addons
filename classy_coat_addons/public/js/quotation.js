// Fetches the selected Customer's Tax ID into Customer Tax ID (cc_customer_tax_id) so it's visible on
// the quotation without opening the Customer record. party_name is a Dynamic Link (Customer/Lead/
// Prospect per quotation_to), so this can't be a declarative fetch_from.
frappe.ui.form.on("Quotation", {
	quotation_to(frm) {
		frm.trigger("party_name");
	},
	party_name(frm) {
		if (frm.doc.quotation_to !== "Customer" || !frm.doc.party_name) {
			frm.set_value("cc_customer_tax_id", "");
			return;
		}

		frappe.db.get_value("Customer", frm.doc.party_name, "tax_id").then(({ message }) => {
			frm.set_value("cc_customer_tax_id", (message && message.tax_id) || "");
		});
	},
});
