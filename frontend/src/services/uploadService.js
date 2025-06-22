import { uploadFileRequest } from "../api/uploadApi";

// -------------------------- Upload file service ------------------------------------->

export function uploadFile(file, username) {
    return uploadFileRequest(file, username);
}