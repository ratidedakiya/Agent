import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  FileText, 
  Image, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Download,
  Eye,
  RotateCcw
} from 'lucide-react';

const HomeworkInterface = ({ session, onViewChange }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState('general');

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending'
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const processHomework = async () => {
    if (uploadedFiles.length === 0) return;

    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('homework_file', uploadedFiles[0].file);
      formData.append('session_id', session.session_id);
      formData.append('subject', selectedSubject);

      const response = await fetch('/api/homework/check', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process homework');
      }

      const result = await response.json();
      setResults(result);
      
      // Update file status
      setUploadedFiles(prev => prev.map(file => ({
        ...file,
        status: 'processed'
      })));
      
    } catch (error) {
      console.error('Error processing homework:', error);
      setUploadedFiles(prev => prev.map(file => ({
        ...file,
        status: 'error'
      })));
    } finally {
      setIsProcessing(false);
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const clearAll = () => {
    setUploadedFiles([]);
    setResults(null);
  };

  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) {
      return <Image className="h-8 w-8 text-blue-500" />;
    } else if (fileType === 'application/pdf') {
      return <FileText className="h-8 w-8 text-red-500" />;
    } else {
      return <FileText className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <div className="h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (results) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
            results.verdict === 'correct' ? 'bg-green-100' : 
            results.verdict === 'partial' ? 'bg-yellow-100' : 'bg-red-100'
          }`}>
            {results.verdict === 'correct' ? (
              <CheckCircle className="h-8 w-8 text-green-600" />
            ) : results.verdict === 'partial' ? (
              <AlertCircle className="h-8 w-8 text-yellow-600" />
            ) : (
              <XCircle className="h-8 w-8 text-red-600" />
            )}
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Homework Review Complete</h2>
          <p className="text-gray-600">Here's what I found</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          {/* Score and Verdict */}
          <div className="text-center mb-8">
            <div className="text-6xl font-bold text-blue-600 mb-2">
              {Math.round(results.score)}%
            </div>
            <div className={`text-xl font-semibold ${
              results.verdict === 'correct' ? 'text-green-600' : 
              results.verdict === 'partial' ? 'text-yellow-600' : 'text-red-600'
            }`}>
              {results.verdict === 'correct' ? 'Excellent Work!' : 
               results.verdict === 'partial' ? 'Good Effort!' : 'Needs Improvement'}
            </div>
            <p className="text-gray-600 mt-2">{results.short_reason}</p>
          </div>

          {/* Detailed Explanation */}
          {results.detailed_explanation && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Review</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">
                  {results.detailed_explanation}
                </p>
              </div>
            </div>
          )}

          {/* Suggestions */}
          {results.suggestions && results.suggestions.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Suggestions for Improvement</h3>
              <ul className="space-y-2">
                {results.suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                    <span className="text-gray-700">{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Confidence Level */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Review Confidence</h3>
            <div className="flex items-center space-x-3">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${results.confidence * 100}%` }}
                />
              </div>
              <span className="text-sm text-gray-600">
                {Math.round(results.confidence * 100)}% confident
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={clearAll}
              className="btn-primary"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Review Another
            </button>
            <button
              onClick={() => onViewChange('chat')}
              className="btn-secondary"
            >
              Ask Questions
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <Upload className="h-16 w-16 text-blue-500 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Homework Checker</h1>
        <p className="text-gray-600">Upload your homework for AI-powered review and feedback</p>
      </div>

      {/* Subject Selection */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Subject</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {['math', 'science', 'programming', 'general'].map((subject) => (
            <button
              key={subject}
              onClick={() => setSelectedSubject(subject)}
              className={`p-3 rounded-lg border-2 transition-colors duration-200 ${
                selectedSubject === subject
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
              }`}
            >
              {subject.charAt(0).toUpperCase() + subject.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* File Upload Area */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div
          {...getRootProps()}
          className={`file-upload-area ${
            isDragActive ? 'file-upload-area-dragover' : ''
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900 mb-2">
            {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
          </p>
          <p className="text-gray-600 mb-4">
            or click to select files
          </p>
          <p className="text-sm text-gray-500">
            Supports: Images (PNG, JPG, GIF), PDF, Text files
          </p>
          <p className="text-sm text-gray-500">
            Max size: 10MB per file
          </p>
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Uploaded Files</h3>
            <button
              onClick={clearAll}
              className="text-sm text-red-600 hover:text-red-700"
            >
              Clear All
            </button>
          </div>
          
          <div className="space-y-3">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="flex items-center space-x-4 p-3 border border-gray-200 rounded-lg">
                {getFileIcon(file.type)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(file.size)}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(file.status)}
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-gray-400 hover:text-red-600"
                  >
                    <XCircle className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex justify-center">
            <button
              onClick={processHomework}
              disabled={isProcessing || uploadedFiles.length === 0}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Check Homework
                </>
              )}
            </button>
          </div>
        </div>
      )}

      <div className="text-center">
        <button
          onClick={() => onViewChange('chat')}
          className="btn-secondary"
        >
          Back to Chat
        </button>
      </div>
    </div>
  );
};

export default HomeworkInterface;