function setDeleteAction(actionUrl) {
    const form = document.getElementById('confirmDeleteForm');
    if (form) {
        form.action = actionUrl;
    }
}
