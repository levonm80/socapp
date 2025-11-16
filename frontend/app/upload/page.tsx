'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { logsApi, LogFile } from '@/lib/api/logs';

export default function UploadPage() {
  const router = useRouter();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [logFile, setLogFile] = useState<LogFile | null>(null);
  const [preview, setPreview] = useState<string[]>([]);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setUploadedFile(file);
    setUploadError(null);
    setIsUploading(true);
    setUploadProgress(0);
    setLogFile(null);
    setPreview([]);

    try {
      const response = await logsApi.uploadLog(file, (progress) => {
        setUploadProgress(progress);
      });

      // Upload complete, fetch file details
      const fileDetails = await logsApi.getLogFile(response.log_file_id);
      setLogFile(fileDetails);
      
      // Fetch preview
      setIsLoadingPreview(true);
      try {
        const previewData = await logsApi.getLogFilePreview(response.log_file_id, 10);
        setPreview(previewData.preview);
      } catch (previewError) {
        console.error('Failed to load preview:', previewError);
        // Preview is optional, don't fail the whole upload
      } finally {
        setIsLoadingPreview(false);
      }

      setUploadProgress(100);
    } catch (error: any) {
      console.error('Upload error:', error);
      setUploadError(error.response?.data?.error || error.message || 'Failed to upload file');
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcess = () => {
    if (logFile) {
      router.push(`/dashboard?log_file_id=${logFile.id}`);
    } else {
      router.push('/dashboard');
    }
  };

  const handleReset = () => {
    setUploadedFile(null);
    setUploadProgress(0);
    setUploadError(null);
    setLogFile(null);
    setPreview([]);
    setIsUploading(false);
  };

  return (
    <div className="relative flex h-auto min-h-screen w-full flex-col dark overflow-x-hidden bg-background-light dark:bg-background-dark">
      <div className="layout-container flex h-full grow flex-col">
        {/* Header */}
        <header className="sticky top-0 z-50 flex items-center justify-between whitespace-nowrap border-b border-solid border-border-dark px-6 sm:px-10 py-3 bg-background-dark/80 backdrop-blur-sm">
          <div className="flex items-center gap-4 text-white">
            <div className="size-6 text-primary">
              <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                <g clipPath="url(#clip0_6_330)">
                  <path
                    clipRule="evenodd"
                    d="M24 0.757355L47.2426 24L24 47.2426L0.757355 24L24 0.757355ZM21 35.7574V12.2426L9.24264 24L21 35.7574Z"
                    fill="currentColor"
                    fillRule="evenodd"
                  ></path>
                </g>
                <defs>
                  <clipPath id="clip0_6_330">
                    <rect fill="white" height="48" width="48"></rect>
                  </clipPath>
                </defs>
              </svg>
            </div>
            <h2 className="text-white text-xl font-bold leading-tight tracking-[-0.015em]">Security Analytics</h2>
          </div>
          <div className="flex flex-1 justify-end gap-4 md:gap-8">
            <div className="hidden md:flex items-center gap-8">
              <Link href="/dashboard" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                Dashboard
              </Link>
              <Link href="/upload" className="text-white text-sm font-medium leading-normal px-3 py-2 rounded-lg bg-primary/20">
                Upload
              </Link>
              <Link href="/logs" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                Logs
              </Link>
              <Link href="/ai-copilot" className="text-gray-300 hover:text-white text-sm font-medium leading-normal">
                AI Assistant
              </Link>
            </div>
            <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border-2 border-border-dark bg-primary/20"></div>
          </div>
        </header>

        <main className="px-4 sm:px-6 lg:px-10 py-8">
          <div className="px-4 md:px-10 lg:px-20 xl:px-40 flex flex-1 justify-center py-5">
            <div className="layout-content-container flex flex-col w-full max-w-[960px] flex-1 gap-8">
              {/* PageHeading */}
              <div className="flex flex-wrap justify-between gap-3">
                <div className="flex min-w-72 flex-col gap-3">
                  <p className="text-text-primary-dark text-4xl font-black leading-tight tracking-[-0.033em]">
                    Upload and Process Logs
                  </p>
                  <p className="text-text-secondary-dark text-base font-normal leading-normal">
                    Upload, review, and process your Zscaler Web Proxy Logs
                  </p>
                </div>
              </div>

              {/* EmptyState - Drag and Drop Uploader */}
              <div className="flex flex-col p-4 bg-component-dark rounded-xl border border-border-dark">
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  accept=".csv,.txt,.log,.zip"
                  onChange={handleFileInput}
                />
                <div
                  className={`flex flex-col items-center gap-6 rounded-lg border-2 border-dashed px-6 py-14 transition-colors cursor-pointer ${
                    dragActive ? 'border-primary bg-primary/5' : 'border-[#324d67]'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => {
                    document.getElementById('file-upload')?.click();
                  }}
                >
                  <span className="material-symbols-outlined text-5xl text-text-secondary-dark">upload_file</span>
                  <div className="flex max-w-[480px] flex-col items-center gap-2">
                    <p className="text-text-primary-dark text-lg font-bold leading-tight tracking-[-0.015em] max-w-[480px] text-center">
                      Drag & drop your log file here, or click to browse
                    </p>
                    <p className="text-text-secondary-dark text-sm font-normal leading-normal max-w-[480px] text-center">
                      Supports .csv, .txt, .log, .zip files up to 2GB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      document.getElementById('file-upload')?.click();
                    }}
                    className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#233648] text-text-primary-dark text-sm font-bold leading-normal tracking-[0.015em] hover:bg-border-dark"
                  >
                    <span className="truncate">Select File</span>
                  </button>
                </div>
              </div>

              {/* Upload Error */}
              {uploadError && (
                <div className="flex flex-col gap-3 p-4 bg-danger/10 rounded-xl border border-danger">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-danger">error</span>
                    <p className="text-danger text-base font-medium">Upload Failed</p>
                  </div>
                  <p className="text-text-secondary-dark text-sm">{uploadError}</p>
                  <button
                    onClick={handleReset}
                    className="self-start flex items-center justify-center px-4 py-2 rounded-lg bg-component-dark text-text-primary-dark text-sm font-medium hover:bg-[#233648]"
                  >
                    Try Again
                  </button>
                </div>
              )}

              {/* Upload Progress Section */}
              {uploadedFile && (
                <div className="flex flex-col gap-6 p-4 bg-component-dark rounded-xl border border-border-dark">
                  {/* List Item with Progress Bar */}
                  <div className="flex items-center gap-4 min-h-[72px] justify-between">
                    <div className="flex items-center gap-4">
                      <div className="text-text-primary-dark flex items-center justify-center rounded-lg bg-[#233648] shrink-0 size-12">
                        <span className="material-symbols-outlined text-3xl">drive_zip</span>
                      </div>
                      <div className="flex flex-col justify-center">
                        <p className="text-text-primary-dark text-base font-medium leading-normal line-clamp-1">
                          {uploadedFile.name}
                        </p>
                        <p className="text-text-secondary-dark text-sm font-normal leading-normal line-clamp-2">
                          {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <div className="shrink-0 flex items-center gap-3">
                      {uploadProgress === 100 && !isUploading ? (
                        <p className="text-sm font-medium leading-normal text-success">Complete</p>
                      ) : isUploading ? (
                        <p className="text-sm font-medium leading-normal text-text-secondary-dark">Uploading...</p>
                      ) : (
                        <p className="text-sm font-medium leading-normal text-text-secondary-dark">Processing...</p>
                      )}
                      {!isUploading && (
                        <button
                          onClick={handleReset}
                          className="flex items-center justify-center h-8 w-8 rounded-lg hover:bg-[#233648]"
                        >
                          <span className="material-symbols-outlined text-text-secondary-dark text-xl">close</span>
                        </button>
                      )}
                    </div>
                  </div>
                  {/* ProgressBar */}
                  {isUploading && uploadProgress < 100 && (
                    <div className="flex flex-col gap-3">
                      <div className="flex gap-6 justify-between">
                        <p className="text-text-primary-dark text-base font-medium leading-normal">Uploading...</p>
                        <p className="text-text-primary-dark text-sm font-normal leading-normal">{uploadProgress}%</p>
                      </div>
                      <div className="w-full rounded bg-[#324d67] h-2">
                        <div
                          className="h-2 rounded bg-success transition-all duration-300"
                          style={{ width: `${uploadProgress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                  {uploadProgress === 100 && !isUploading && logFile && (
                    <div className="flex flex-col gap-3">
                      <p className="text-text-secondary-dark text-sm font-normal leading-normal">
                        Upload complete. {logFile.status === 'processing' ? 'Processing log entries...' : 'Ready to process.'}
                      </p>
                      {logFile.status === 'completed' && (
                        <p className="text-success text-sm font-medium">
                          Processed {logFile.total_entries?.toLocaleString() || 0} log entries
                        </p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Metadata and Preview Section */}
              {uploadedFile && uploadProgress === 100 && !isUploading && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Metadata Display */}
                  <div className="flex flex-col gap-4 p-6 bg-component-dark rounded-xl border border-border-dark">
                    <h3 className="text-text-primary-dark text-lg font-bold">File Metadata</h3>
                    <div className="flex flex-col gap-4">
                      <div className="flex justify-between items-center">
                        <span className="text-text-secondary-dark text-sm">Log Type</span>
                        <span className="text-text-primary-dark text-sm font-medium bg-[#233648] px-2 py-1 rounded">
                          Zscaler Web Proxy
                        </span>
                      </div>
                      {logFile?.date_range_start && logFile?.date_range_end && (
                        <div className="flex justify-between items-center">
                          <span className="text-text-secondary-dark text-sm">Date Range</span>
                          <span className="text-text-primary-dark text-sm font-medium">
                            {new Date(logFile.date_range_start).toLocaleDateString()} to {new Date(logFile.date_range_end).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                      <div className="flex justify-between items-center">
                        <span className="text-text-secondary-dark text-sm">Status</span>
                        <span className={`text-sm font-medium px-2 py-1 rounded ${
                          logFile?.status === 'completed' ? 'bg-success/20 text-success' :
                          logFile?.status === 'processing' ? 'bg-warning/20 text-warning' :
                          logFile?.status === 'failed' ? 'bg-danger/20 text-danger' :
                          'bg-[#233648] text-text-primary-dark'
                        }`}>
                          {logFile?.status?.toUpperCase() || 'UNKNOWN'}
                        </span>
                      </div>
                      {logFile?.total_entries !== undefined && (
                        <div className="flex justify-between items-center">
                          <span className="text-text-secondary-dark text-sm">Total Records</span>
                          <span className="text-text-primary-dark text-sm font-medium">
                            {logFile.total_entries.toLocaleString()}
                          </span>
                        </div>
                      )}
                      {logFile?.uploaded_at && (
                        <div className="flex justify-between items-center">
                          <span className="text-text-secondary-dark text-sm">Uploaded At</span>
                          <span className="text-text-primary-dark text-sm font-medium">
                            {new Date(logFile.uploaded_at).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  {/* Log Preview */}
                  <div className="flex flex-col gap-4 p-6 bg-component-dark rounded-xl border border-border-dark">
                    <h3 className="text-text-primary-dark text-lg font-bold">Log File Preview (First 10 lines)</h3>
                    <div className="bg-background-dark p-4 rounded-lg overflow-x-auto h-36">
                      {isLoadingPreview ? (
                        <div className="flex items-center justify-center h-full text-text-secondary-dark">
                          Loading preview...
                        </div>
                      ) : preview.length > 0 ? (
                        <pre className="text-xs text-text-secondary-dark whitespace-pre">
                          <code>
                            {preview.join('\n')}
                          </code>
                        </pre>
                      ) : (
                        <div className="flex items-center justify-center h-full text-text-secondary-dark">
                          Preview not available
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              {uploadedFile && uploadProgress === 100 && !isUploading && (
                <div className="flex justify-end gap-4 p-4">
                  <button
                    onClick={handleReset}
                    className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-6 bg-component-dark text-text-primary-dark text-base font-bold leading-normal tracking-[0.015em] border border-border-dark hover:bg-[#233648]"
                  >
                    <span className="truncate">Upload a Different File</span>
                  </button>
                  <button
                    onClick={handleProcess}
                    disabled={logFile?.status === 'processing'}
                    className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-6 bg-primary text-white text-base font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="truncate">
                      {logFile?.status === 'processing' ? 'Processing...' : 'View Dashboard'}
                    </span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

