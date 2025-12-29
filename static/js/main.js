document.addEventListener('DOMContentLoaded', () => {
    const hero = document.querySelector('.hero');
    const heroClose = document.getElementById('hero-close');

    if (hero) {
        const heroDismissed = document.cookie.split('; ').find(row => row.startsWith('hero_dismissed='));
        if (heroDismissed) {
            hero.remove();
        }

        if (heroClose) {
            heroClose.addEventListener('click', () => {
                document.cookie = `hero_dismissed=true; path=/; max-age=${60 * 60 * 24 * 30}`;
                hero.remove();
            });
        }
    }

    const copyButtons = document.querySelectorAll('.copy-link');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const url = btn.dataset.url;
            try {
                await navigator.clipboard.writeText(url);
                btn.innerHTML = '<i class="bi bi-check2"></i> Copied';
                setTimeout(() => {
                    btn.innerHTML = '<i class="bi bi-clipboard"></i> Copy link';
                }, 1200);
            } catch (e) {
                btn.innerHTML = '<i class="bi bi-x"></i> Failed';
            }
        });
    });

    const copyGroups = document.querySelectorAll('.copy-input');
    copyGroups.forEach(group => {
        const copyButton = group.querySelector('.copy-btn');
        const inputField = group.querySelector('input');

        if (copyButton && inputField) {
            copyButton.addEventListener('click', () => {
                inputField.select();
                navigator.clipboard.writeText(inputField.value);
            });
        }
    });

    const sortableTables = document.querySelectorAll('table.sortable');
    sortableTables.forEach(table => {
        const headers = table.tHead ? Array.from(table.tHead.querySelectorAll('th')) : [];
        const tbody = table.tBodies[0];
        if (!headers.length || !tbody) {
            return;
        }

        const collator = new Intl.Collator(undefined, { numeric: true, sensitivity: 'base' });

        const getCellValue = (row, index) => {
            const cell = row.cells[index];
            if (!cell) {
                return '';
            }
            return cell.dataset.sortValue != null ? cell.dataset.sortValue : cell.textContent.trim();
        };

        const sortBy = (th, ascending) => {
            headers.forEach(header => {
                if (header !== th) {
                    header.dataset.sortDir = '';
                    header.classList.remove('sorted-asc', 'sorted-desc');
                }
            });

            const index = headers.indexOf(th);
            const rows = Array.from(tbody.rows);

            rows.sort((a, b) => {
                const aVal = getCellValue(a, index);
                const bVal = getCellValue(b, index);
                return collator.compare(aVal, bVal) * (ascending ? 1 : -1);
            });

            rows.forEach(row => {
                tbody.appendChild(row);
            });

            th.dataset.sortDir = ascending ? 'asc' : 'desc';
            th.classList.remove('sorted-asc', 'sorted-desc', 'sorted', 'descending', 'ascending');
            th.classList.add(ascending ? 'sorted-asc' : 'sorted-desc');
        };

        headers.forEach(th => {
            th.addEventListener('click', () => {
                const ascending = th.dataset.sortDir !== 'asc';
                sortBy(th, ascending);
            });
        });

        const initialHeader = headers.find(h => h.classList.contains('sorted'));
        if (initialHeader) {
            const ascending = !initialHeader.classList.contains('descending');
            sortBy(initialHeader, ascending);
        }
    });

    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        const toggleBtn = () => {
            if (window.scrollY > 260) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        };
        window.addEventListener('scroll', toggleBtn);
        backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
        toggleBtn();
    }

    if (window.bootstrap) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    document.querySelectorAll('.unified-menu .dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            const menu = item.closest('[data-target]');
            const target = menu ? menu.dataset.target : null;
            if (!target) return;
            const value = item.dataset.value || '';
            const hiddenInput = document.getElementById(target);
            const group = item.closest('.btn-group');
            const label = group ? group.querySelector('.dropdown-label') : null;
            if (hiddenInput) hiddenInput.value = value;
            if (label) label.textContent = value || (target === 'language' ? 'Any language' : 'Any software');
        });
    });

    const viewerFrame = document.getElementById('viewer-frame');
    const viewerItems = document.querySelectorAll('.viewer-item');
    const openNew = document.getElementById('open-new');
    if (viewerItems.length) {
        viewerItems.forEach(btn => {
            btn.addEventListener('click', () => {
                const url = btn.dataset.url;
                viewerItems.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                if (viewerFrame) viewerFrame.src = url;
                if (openNew) openNew.href = url;
            });
        });
    }
});

function setStatus(id) {
    const select = document.getElementById("status-select-" + id);
    const varstatus = select.value;

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
        .catch(() => {});
}
