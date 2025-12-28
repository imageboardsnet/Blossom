document.addEventListener('DOMContentLoaded', function () {

	const copyGroups = document.querySelectorAll('.copy-input');

	copyGroups.forEach(function (group) {
		const copyButton = group.querySelector('.copy-btn');
		const inputField = group.querySelector('input');

		if (copyButton && inputField) {
			copyButton.addEventListener('click', function () {
				inputField.select();
				navigator.clipboard.writeText(inputField.value);
			});
		}
	});

	const sortableTables = document.querySelectorAll('table.sortable');

	sortableTables.forEach(function (table) {
		const headers = table.tHead ? Array.from(table.tHead.querySelectorAll('th')) : [];
		const tbody = table.tBodies[0];
		if (!headers.length || !tbody) {
			return;
		}

		const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: 'base' });

		const getCellValue = function (row, index) {
			const cell = row.cells[index];
			if (!cell) {
				return '';
			}
			return cell.dataset.sortValue != null ? cell.dataset.sortValue : cell.textContent.trim();
		};

		const sortBy = function (th, ascending) {
			headers.forEach(function (header) {
				if (header !== th) {
					header.dataset.sortDir = '';
					header.classList.remove('sorted-asc', 'sorted-desc');
				}
			});

			const index = headers.indexOf(th);
			const rows = Array.from(tbody.rows);

			rows.sort(function (a, b) {
				const aVal = getCellValue(a, index);
				const bVal = getCellValue(b, index);
				return collator.compare(aVal, bVal) * (ascending ? 1 : -1);
			});

			rows.forEach(function (row) {
				tbody.appendChild(row);
			});

			th.dataset.sortDir = ascending ? 'asc' : 'desc';
			th.classList.remove('sorted-asc', 'sorted-desc', 'sorted', 'descending', 'ascending');
			th.classList.add(ascending ? 'sorted-asc' : 'sorted-desc');
		};

		headers.forEach(function (th) {
			th.addEventListener('click', function () {
				const ascending = th.dataset.sortDir !== 'asc';
				sortBy(th, ascending);
			});
		});

		const initialHeader = headers.find(function (h) { return h.classList.contains('sorted'); });
		if (initialHeader) {
			const ascending = !initialHeader.classList.contains('descending');
			sortBy(initialHeader, ascending);
		}
	});
});

function setStatus(id) {
	var select = document.getElementById("status-select-" + id);
	var varstatus = select.value;

	fetch('/imageboard/status/' + id, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ status: varstatus })
	})
		.then(response => response.json())
		.then(data => {
			if (data.status == "ok") {
				location.reload();
			}
		})
		.catch(error => {

		});
}
