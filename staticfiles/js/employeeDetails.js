function fetchEmployeeDetails(employeeName) {
    fetch(`/get-employee-details/${encodeURIComponent(employeeName)}/`)
        .then(response => response.json())
        .then(data => {
            if (data && data.employees && data.employees.length > 0) {
                const employee = data.employees[0]; // Assuming single selection
                displayEmployeeDetails(employee);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('Failed to retrieve employee details.');
        });
}

function displayEmployeeDetails(employee) {
    const employeeInfoSection = document.getElementById('employee-info-section');

    // Clear existing employee info textboxes if any
    employeeInfoSection.innerHTML = '';

    // Create textboxes for department, team_or_division, and division
    createTextbox('Department', employee.department);
    createTextbox('Team/Division', employee.team_or_division);
    createTextbox('Division', employee.division);
}

function createTextbox(labelText, value) {
    const employeeInfoSection = document.getElementById('employee-info-section');

    // Create label
    const label = document.createElement('label');
    label.textContent = labelText;
    label.style.marginLeft = '10px'; // Optional: add some margin

    // Create textbox
    const textbox = document.createElement('input');
    textbox.type = 'text';
    textbox.value = value || ''; // Use value if available
    textbox.style.marginLeft = '5px'; // Space between label and textbox

    // Append label and textbox to the section
    employeeInfoSection.appendChild(label);
    employeeInfoSection.appendChild(textbox);
}

function clearEmployeeInfoSection() {
    const employeeInfoSection = document.getElementById('employee-info-section');
    employeeInfoSection.innerHTML = ''; // Clear any existing content
}
