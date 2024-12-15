// Utility Functions
function showMessage(message, type = 'success') {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message-box ${type === 'success' ? 'success' : 'error'}`;
    messageDiv.style.backgroundColor = type === 'success' ? '#2ecc71' : '#e74c3c';
    messageDiv.style.color = 'white';

    // Auto-clear message after 5 seconds
    setTimeout(() => {
        messageDiv.textContent = '';
        messageDiv.className = 'message-box';
    }, 5000);
}

/// File Upload Handler
document.getElementById('file-input').addEventListener('change', function() {
    const fileNamesList = document.getElementById('file-names');
    const files = this.files;

    fileNamesList.innerHTML = '';

    if (files.length > 0) {
        const fileNames = Array.from(files).map(file => `<li>${file.name}</li>`).join('');
        fileNamesList.innerHTML = `<ul>${fileNames}</ul>`;
    }
});

document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData();
    const files = document.getElementById('file-input').files;

    if (files.length === 0) {
        showMessage('Please select files to upload', 'error');
        return;
    }

    let uploadedCount = 0;

    for (let i = 0; i < files.length; i++) {
        const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
        if (!validTypes.includes(files[i].type)) {
            showMessage('Invalid file type. Please upload PDF, JPG, or PNG', 'error');
            return;
        }
        formData.append('files', files[i]);
    }

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showMessage(data.error, 'error');
            } else {
                uploadedCount = files.length;
                showMessage(`${uploadedCount} file(s) uploaded successfully!`);
                document.getElementById('file-input').value = '';
                document.getElementById('file-names').innerHTML = '';
                loadRecords(); 
            }
        })
        .catch(error => showMessage('Error uploading files', 'error'));
});

// Record Search Handler
document.getElementById('search-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('search-name').value.trim();
    const email = document.getElementById('search-email').value.trim();

    if (!name && !email) {
        showMessage('Please enter a name or email to search', 'error');
        return;
    }

    const query = new URLSearchParams({ name, email }).toString();

    fetch(`/search?${query}`)
        .then(response => response.json())
        .then(data => {
            const recordsDiv = document.getElementById('records');
            recordsDiv.innerHTML = '';

            if (data.records && data.records.length > 0) {
                data.records.forEach(record => {
                    const recordDiv = document.createElement('div');
                    recordDiv.className = 'record';
                    recordDiv.innerHTML = `
                        <h3>${record.Name || 'Unnamed Record'}</h3>
                        <p><strong>Email:</strong> ${record['Email ID'] || 'N/A'}</p>
                        <button onclick="viewDetails('${record._id}')" class="btn-primary">View Details</button>
                    `;
                    recordsDiv.appendChild(recordDiv);
                });
            } else {
                recordsDiv.innerHTML = '<p>No records found.</p>';
            }
        })
        .catch(error => showMessage('Error searching records', 'error'));
});

// Load Records Function
function loadRecords() {
    fetch('/records')
        .then(response => response.json())
        .then(data => {
            const recordsDiv = document.getElementById('records');
            recordsDiv.innerHTML = '';

            if (data.records && data.records.length > 0) {
                data.records.forEach(record => {
                    const recordDiv = document.createElement('div');
                    recordDiv.className = 'record';
                    recordDiv.innerHTML = `
                        <h3>${record.Name || 'Unnamed Record'}</h3>
                        <p><strong>Email:</strong> ${record['Email ID'] || 'N/A'}</p>
                        <button onclick="viewDetails('${record._id}')" class="btn-primary">View Details</button>
                    `;
                    recordsDiv.appendChild(recordDiv);
                });
            } else {
                recordsDiv.innerHTML = '<p>No records found.</p>';
            }
        })
        .catch(error => showMessage('Error loading records', 'error'));
}

// View Record Details
function viewDetails(recordId) {
    fetch(`/records/${recordId}`)
        .then(response => response.json())
        .then(data => {
            if (data) {
                const detailsDiv = document.getElementById('details');
                detailsDiv.innerHTML = `
                    <table>
                        <tr><th>Name</th><td>${data.Name || 'N/A'}</td></tr>
                        <tr><th>Email</th><td>${data['Email ID'] || 'N/A'}</td></tr>
                        <tr><th>Mobile</th><td>${data['Mobile'] || 'N/A'}</td></tr>
                        <tr><th>Date of Birth</th><td>${data['Date of Birth'] || 'N/A'}</td></tr>
                        <tr><th>Age</th><td>${data['Age'] || 'N/A'}</td></tr>
                        <tr><th>Gender</th><td>${data['Gender'] || 'N/A'}</td></tr>
                        <tr>
                            <th>Emergency Contact</th>
                            <td>
                                ${data['Emergency Contact'] 
                                    ? `${data['Emergency Contact']['Name'] || ''}, 
                                       ${data['Emergency Contact']['Number'] || ''}`
                                    : 'N/A'}
                            </td>
                            </tr>
                        <tr>
                            <th>Permanent Address</th>
                            <td>
                                ${data['Permanent Address'] 
                                    ? `${data['Permanent Address']['Street Address'] || ''}, 
                                       ${data['Permanent Address']['City'] || ''}, 
                                       ${data['Permanent Address']['State'] || ''} 
                                       ${data['Permanent Address']['Zip Code'] || ''}`
                                    : 'N/A'}
                            </td>
                            </tr>
                            <tr>
                            <th>Current Address</th>
                            <td>
                                ${data['Current Address'] 
                                    ? `${data['Current Address']['Street Address'] || ''}, 
                                       ${data['Current Address']['City'] || ''}, 
                                       ${data['Current Address']['State'] || ''} 
                                       ${data['Current Address']['Zip Code'] || ''}`
                                    : 'N/A'}
                            </td>
                        </tr>
                    </table>
                `;
                document.getElementById('record-details').style.display = 'block';
            }
        })
        .catch(error => showMessage('Error fetching record details', 'error'));
}

// Close Record Details
function closeDetails() {
    document.getElementById('record-details').style.display = 'none';
}

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
    loadRecords();
});