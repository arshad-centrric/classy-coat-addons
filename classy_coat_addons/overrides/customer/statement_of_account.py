import frappe
from frappe import _
from frappe.utils import date_diff, flt, fmt_money, formatdate, nowdate

from classy_coat_addons.overrides.sales_invoice.payment_stage import get_payment_stages

DATE_FORMAT = "dd/mm/yyyy"


def get_contact(customer, primary_contact=None):
	"""The contact the statement is addressed to: the customer's primary contact if one is set,
	otherwise the linked contact flagged as primary, otherwise the first contact linked to the customer.
	"""
	fields = ["salutation", "first_name", "last_name", "mobile_no", "phone"]

	if primary_contact:
		contact = frappe.db.get_value("Contact", primary_contact, fields, as_dict=True)
		if contact:
			return contact

	contacts = frappe.db.sql(
		"""
		SELECT ct.salutation, ct.first_name, ct.last_name, ct.mobile_no, ct.phone
		FROM `tabContact` ct
		JOIN `tabDynamic Link` link ON link.parent = ct.name AND link.parenttype = 'Contact'
		WHERE link.link_doctype = 'Customer' AND link.link_name = %s
		ORDER BY ct.is_primary_contact DESC, ct.creation ASC
		LIMIT 1
		""",
		customer,
		as_dict=True,
	)
	return contacts[0] if contacts else frappe._dict()


def get_statement_of_account(customer, company=None):
	"""Return what the Statement of Account print shows for a customer (registered as a Jinja method).

	Lists the customer's submitted invoices that still have an amount outstanding, in the company's
	currency so the amounts can be added up. Received is what has been settled against an invoice
	(Amount - Balance), so it also covers credit notes and advances.
	"""
	if not frappe.has_permission("Sales Invoice", "read"):
		frappe.throw(_("You are not permitted to view Sales Invoices"), frappe.PermissionError)

	company = (
		company
		or frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
	)
	if not company:
		frappe.throw(_("Set a default Company to print the Statement of Account"))

	company_details = frappe.db.get_value(
		"Company", company, ["company_name", "tax_id", "email", "default_currency"], as_dict=True
	)
	customer_details = frappe.db.get_value(
		"Customer",
		customer,
		["customer_name", "tax_id", "mobile_no", "customer_primary_contact"],
		as_dict=True,
	)
	contact = get_contact(customer, customer_details.customer_primary_contact)

	currency = company_details.default_currency
	precision = frappe.get_precision("Sales Invoice", "outstanding_amount")
	today = nowdate()

	invoices = frappe.db.sql(
		"""
		SELECT
			si.name,
			si.posting_date,
			si.due_date,
			project.project_name,
			COALESCE(NULLIF(si.rounded_total, 0), si.grand_total) AS amount,
			si.outstanding_amount AS balance
		FROM `tabSales Invoice` si
		LEFT JOIN `tabProject` project ON project.name = si.project
		WHERE si.docstatus = 1 AND si.outstanding_amount > 0
			AND si.customer = %(customer)s AND si.company = %(company)s
			AND si.currency = %(currency)s AND si.party_account_currency = %(currency)s
		ORDER BY si.posting_date ASC, si.name ASC
		""",
		{"customer": customer, "company": company, "currency": currency},
		as_dict=True,
	)

	stages = get_payment_stages([invoice.name for invoice in invoices])
	rows = [
		frappe._dict(
			date=formatdate(invoice.posting_date, DATE_FORMAT),
			invoice=invoice.name,
			description=invoice.project_name or "",
			payment_stage=stages.get(invoice.name, ""),
			amount=fmt_money(invoice.amount, precision),
			received=fmt_money(flt(invoice.amount - invoice.balance, precision), precision),
			balance=fmt_money(invoice.balance, precision),
			# Not yet due counts as 0 rather than a negative number on a customer facing document.
			due_days=max(date_diff(today, invoice.due_date), 0),
		)
		for invoice in invoices
	]

	total_amount = sum(invoice.amount for invoice in invoices)
	outstanding = sum(invoice.balance for invoice in invoices)

	def money(value):
		return f"{currency} {fmt_money(flt(value, precision), precision)}"

	return frappe._dict(
		customer_name=customer_details.customer_name,
		customer_tax_id=customer_details.tax_id or "",
		attn=" ".join(filter(None, [contact.salutation, contact.first_name, contact.last_name])),
		phone=customer_details.mobile_no or contact.mobile_no or contact.phone or "",
		statement_date=formatdate(today, DATE_FORMAT),
		company_name=company_details.company_name,
		company_tax_id=company_details.tax_id or "",
		company_email=company_details.email or "",
		currency=currency,
		rows=rows,
		total_amount=money(total_amount),
		total_received=money(total_amount - outstanding),
		outstanding=money(outstanding),
	)
