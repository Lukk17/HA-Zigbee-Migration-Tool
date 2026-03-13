document.addEventListener('DOMContentLoaded', () => {
    const migrationForm = document.getElementById('migrationForm');
    if (migrationForm) {
        migrationForm.addEventListener('submit', handleMigrationSubmit);
    }
});

async function handleMigrationSubmit(event) {
    event.preventDefault();

    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('status');
    const direction = document.getElementById('direction').value;
    const selectedIeees = getSelectedIeees();

    if (selectedIeees.length === 0) {
        alert('Select at least one device');
        return;
    }

    setLoadingState(submitBtn, statusDiv);

    try {
        const response = await executeMigration(selectedIeees, direction);
        const result = await response.json();
        updateStatus(statusDiv, result);
    } catch (error) {
        showError(statusDiv, error.message);
    } finally {
        submitBtn.disabled = false;
    }
}

function getSelectedIeees() {
    return Array.from(document.querySelectorAll('input[name="ieee"]:checked'))
        .map(cb => cb.value);
}

function setLoadingState(btn, status) {
    btn.disabled = true;
    status.className = 'status status-info';
    status.innerHTML = 'Migrating...';
}

async function executeMigration(ieees, direction) {
    return await fetch('migrate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ieees, direction})
    });
}

function updateStatus(statusDiv, result) {
    if (result.status === 'success') {
        const count = result.results.length;
        statusDiv.className = 'status status-success';
        statusDiv.innerHTML = `Migration successful! ${count} devices processed.`;
    } else {
        statusDiv.className = 'status status-error';
        statusDiv.innerHTML = `Migration failed: ${result.detail}`;
    }
}

function showError(statusDiv, message) {
    statusDiv.className = 'status status-error';
    statusDiv.innerHTML = `Error: ${message}`;
}
