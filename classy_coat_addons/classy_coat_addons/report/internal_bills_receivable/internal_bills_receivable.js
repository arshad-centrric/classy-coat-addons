frappe.query_reports["Internal Bills Receivable"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
	],

	// Share any spare page width between the long text columns so the table fills the page while short
	// columns (dates, amounts, days) stay compact. This runs after every render (first load and filter
	// refreshes) with the same calls the datatable makes when you drag a column border, so every column
	// stays draggable and the table scrolls sideways when you widen it past the page.
	after_datatable_render(datatable) {
		try {
			// Columns that take up the spare width, and their share of it (Project gets the most).
			const shares = { project_name: 3, customer: 2, invoice: 1, payment_stage: 1, lpo_no: 1 };

			const row = datatable.bodyScrollable.querySelector(".dt-row") || datatable.header.querySelector(".dt-row");
			const flexible = datatable.datamanager.getColumns().filter((column) => shares[column.id]);
			// Keep some room for cell borders and a possible vertical scrollbar.
			const spare = datatable.datatableWrapper.offsetWidth - row.offsetWidth - 40;

			if (spare <= 0 || !flexible.length) return;

			const total_share = flexible.reduce((sum, column) => sum + shares[column.id], 0);
			flexible.forEach((column) => {
				const extra = Math.floor((spare * shares[column.id]) / total_share);
				datatable.datamanager.updateColumn(column.colIndex, { width: column.width + extra });
				datatable.columnmanager.setColumnHeaderWidth(column.colIndex);
				datatable.columnmanager.setColumnWidth(column.colIndex);
			});
			datatable.style.setBodyStyle();
		} catch (error) {
			console.error("Internal Bills Receivable: could not fit the columns to the page", error);
		}
	},

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "project_name" && data?.project && data?.project_name) {
			value = frappe.utils.get_form_link(
				"Project",
				data.project,
				true,
				frappe.utils.escape_html(data.project_name)
			);
		}

		if (column.fieldname === "overdue_days" && data && data.overdue_days > 0) {
			value = `<span style="color: red; font-weight: bold">${value}</span>`;
		}

		return value;
	},
};
