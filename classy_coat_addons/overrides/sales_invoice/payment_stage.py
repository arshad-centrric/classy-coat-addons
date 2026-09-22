from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import flt

# Item created by cen_downpayment_invoice: positive lines are down payments,
# the negative line is the deduction added to the final invoice.
DOWN_PAYMENT_ITEM = "DOWN-PAY"


def get_payment_stages(invoices):
	"""Return {invoice: stage} for the given Sales Invoices.

	cen_downpayment_invoice stores neither a stage nor a percentage, so both are derived from the
	DOWN-PAY lines: a down payment invoice is (line amount / Sales Order total) percent, and an invoice
	carrying a negative DOWN-PAY line is the final invoice that settles them. Invoices without a
	DOWN-PAY line have no stage and are left out.
	"""
	if not invoices:
		return {}

	lines = frappe.db.sql(
		"""
		SELECT item.parent AS invoice, item.amount, so.grand_total AS order_total
		FROM `tabSales Invoice Item` item
		LEFT JOIN `tabSales Order` so ON so.name = item.sales_order
		WHERE item.parent IN %(invoices)s AND item.item_code = %(item_code)s
		""",
		{"invoices": tuple(invoices), "item_code": DOWN_PAYMENT_ITEM},
		as_dict=True,
	)

	down_payment_percent = defaultdict(float)
	final_invoices = set()
	for line in lines:
		if line.amount < 0:
			final_invoices.add(line.invoice)
		elif line.order_total:
			down_payment_percent[line.invoice] += line.amount / line.order_total * 100

	stages = {}
	for invoice in invoices:
		if invoice in final_invoices:
			stages[invoice] = _("Final Invoice")
		elif invoice in down_payment_percent:
			stages[invoice] = _("{0}% Down Payment").format(f"{flt(down_payment_percent[invoice], 2):g}")

	return stages
