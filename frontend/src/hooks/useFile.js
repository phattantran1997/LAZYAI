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
                const code = err?.response?.status;
                if (code === 400)
                    setStatus('Error: File name has existed. Please rename your file and try again.');
                else
                    setStatus(`Error: ${err?.message || 'Upload failed'}`);
            })
            .finally(() => {
                setUploading(false);
            },
            );

    };

    return { uploading, status, fileData, upload };
};
