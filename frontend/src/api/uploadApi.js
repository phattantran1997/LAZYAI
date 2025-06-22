import apiClient from "./api-client";

// -------------------------- Upload file request ------------------------------------->

export function uploadFileRequest(file, username) {
    const formData = new FormData();
    formData.append('file_uploaded_in', file);

    return apiClient.post(`/files/upload?username=${username}`, formData, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
    });
}
