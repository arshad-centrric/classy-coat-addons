import frappe
from frappe import _

from classy_coat_addons.overrides.sales_invoice.payment_stage import get_payment_stages


def execute(filters=None):
	data = get_data(frappe._dict(filters or {}))
	return get_columns(), data, None, None, get_report_summary(data)


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 115},
		{
			"label": _("Ref. No."),
			"fieldname": "invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 185,
		},
		{
			"label": _("Party's Name"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 240,
		},
		{
			"label": _("Pending Amount"),
			"fieldname": "outstanding_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 145,
		},
		# Shows the project name; the JS formatter turns it into a link using the `project` id.
		# The Data columns set `align` because the datatable right-aligns a column whose first row is blank.
		{
			"label": _("Project"),
			"fieldname": "project_name",
			"fieldtype": "Data",
			"width": 260,
			"align": "left",
		},
		{
			"label": _("Project Manager"),
			"fieldname": "project_manager",
			"fieldtype": "Data",
			"width": 115,
			"align": "left",
		},
		{
			"label": _("Payment Stage"),
			"fieldname": "payment_stage",
			"fieldtype": "Data",
			"width": 165,
			"align": "left",
		},
		{"label": _("LPO No"), "fieldname": "lpo_no", "fieldtype": "Data", "width": 165, "align": "left"},
		{"label": _("Due on"), "fieldname": "due_date", "fieldtype": "Date", "width": 115},
		{
			"label": _("Overdue by days"),
			"fieldname": "overdue_days",
			"fieldtype": "Int",
			"width": 57,  # 1.5 cm
		},
	]


def get_data(filters):
	# Left joins: an invoice without a project (or a project without a supervisor) must still show up.
	# Down payment invoices are created without the LPO, so lpo_no falls back to the Sales Order's.
	data = frappe.db.sql(
		f"""
		SELECT
			si.posting_date,
			si.name AS invoice,
			si.customer,
			si.outstanding_amount,
			si.party_account_currency AS currency,
			si.project,
			project.project_name,
			COALESCE(NULLIF(user.full_name, ''), project.cen_project_supervisor) AS project_manager,
			COALESCE(
				NULLIF(si.cen_lpo_number, ''),
				(
					SELECT so.cen_lpo_number
					FROM `tabSales Invoice Item` item
					JOIN `tabSales Order` so ON so.name = item.sales_order
					WHERE item.parent = si.name AND so.cen_lpo_number != ''
					ORDER BY item.idx
					LIMIT 1
				)
			) AS lpo_no,
			si.due_date,
			DATEDIFF(CURDATE(), si.due_date) AS overdue_days
		FROM `tabSales Invoice` si
		LEFT JOIN `tabProject` project ON project.name = si.project
		LEFT JOIN `tabUser` user ON user.name = project.cen_project_supervisor
		WHERE si.docstatus = 1 AND si.outstanding_amount > 0 {get_conditions(filters)}
		ORDER BY si.due_date ASC, si.name ASC
		""",
		filters,
		as_dict=True,
	)

	stages = get_payment_stages([row.invoice for row in data])
	for row in data:
		row.payment_stage = stages.get(row.invoice, "")

	return data


def get_conditions(filters):
	# Only fixed fieldnames are interpolated; the values always go through query parameters.
	return "".join(
		f" AND si.{fieldname} = %({fieldname})s"
		for fieldname in ("company", "customer", "project")
		if filters.get(fieldname)
	)


def get_report_summary(data):
	if not data:
		return []

	return [
		{
			"label": _("Outstanding Amount"),
			"value": sum(row.outstanding_amount for row in data),
			"datatype": "Currency",
			"currency": data[0].currency,
			"indicator": "Red",
		}
	]
