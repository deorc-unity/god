function deleteLink(linkId) {
    fetch('/delete-link', {
        method: 'POST',
        body: JSON.stringify({linkId: linkId})
    }).then((_res) => {
        window.location.href="/";
    });
}

function toggleFormMode(isAddMode) {
    document.getElementById('linkFormHeading').innerText = isAddMode ? 'New Link' : 'Update Link';
    document.getElementById('submitButton').innerText = isAddMode ? 'Add Link' : 'Update';
    document.getElementById('cancelButton').style.display = isAddMode ? 'none' : 'block';
}

function editLink(linkId, custom, android, apple, fallback) {
    document.getElementById('custom').value = custom;
    document.getElementById('android').value = android;
    document.getElementById('apple').value = apple;
    document.getElementById('fallback').value = fallback;

    toggleFormMode(false);

    document.getElementById('link').onsubmit = function(event) {
        event.preventDefault(); 

        var updatedData = {
            linkId: linkId,
            custom: document.getElementById('custom').value,
            android: document.getElementById('android').value,
            apple: document.getElementById('apple').value,
            fallback: document.getElementById('fallback').value
        };

        fetch('/update-link', {
            method: 'POST',
            body: JSON.stringify(updatedData)
        }).then(response => {
            if (response.ok) {
                document.getElementById('link').reset();
                toggleFormMode(true);
                window.location.href="/";
            } else {
                response.json().then(data => {
                    alert(data.message);
                });
            }
        }).catch(error => {
            console.error('Error:', error);
        });
    };

    document.getElementById('cancelButton').addEventListener('click', function() {
        document.getElementById('link').reset();
        toggleFormMode(true);
    });
}