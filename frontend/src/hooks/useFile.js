import { useState } from 'react';
import { uploadFile } from '../services/uploadService';

export const useFile = () => {
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState('');
    const [fileData, setFileData] = useState(null);

    const upload = async (file, username) => {

        setUploading(true);
        setStatus('Uploading...');
        setFileData(null);

        uploadFile(file, username)
            .then(response => {
                setFileData(response.data);
                setStatus('Upload successful!');
            })
            .catch(err => {
                setStatus(err.response?.data?.detail)
            })
            .finally(() => {
                setUploading(false);
            },
            );

    };

    return { uploading, status, fileData, upload };
};
