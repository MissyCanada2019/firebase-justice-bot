
'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FolderOpen, UploadCloud, FileText, Trash2, Download, Package, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Progress } from '@/components/ui/progress';
import { useAuth } from '@/hooks/use-auth';
import { storage } from '@/lib/firebase';
import { ref, uploadBytesResumable, getDownloadURL } from 'firebase/storage';

interface EvidenceFile {
  file: File;
  id: string;
  progress: number;
  url?: string;
}

export default function EvidenceLockerPage() {
  const [files, setFiles] = useState<EvidenceFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();
  const { user } = useAuth();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: `${file.name}-${file.lastModified}`,
      progress: 0,
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpeg', '.jpg', '.png'],
      'text/plain': ['.txt'],
    },
  });

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };
  
  const handleUpload = async () => {
    if (!user) {
      toast({ title: "You must be logged in to upload files.", variant: "destructive" });
      return;
    }

    if (files.some(f => f.progress > 0 && f.progress < 100)) {
      toast({ title: "Upload already in progress.", variant: "destructive" });
      return;
    }

    setIsUploading(true);

    const uploadPromises = files.map(fileWrapper => {
      const storageRef = ref(storage, `evidence/${user.uid}/${fileWrapper.file.name}`);
      const uploadTask = uploadBytesResumable(storageRef, fileWrapper.file);

      return new Promise<void>((resolve, reject) => {
        uploadTask.on('state_changed',
          (snapshot) => {
            const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
            setFiles(prev => prev.map(f => f.id === fileWrapper.id ? { ...f, progress } : f));
          },
          (error) => {
            console.error("Upload failed:", error);
            toast({ title: `Upload failed for ${fileWrapper.file.name}`, variant: "destructive" });
            reject(error);
          },
          async () => {
            const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
            setFiles(prev => prev.map(f => f.id === fileWrapper.id ? { ...f, url: downloadURL, progress: 100 } : f));
            resolve();
          }
        );
      });
    });

    try {
      await Promise.all(uploadPromises);
      toast({
        title: "Upload Complete",
        description: `${files.length} file(s) have been successfully processed and saved to your case.`
      });
    } catch (error) {
      console.error("An error occurred during upload:", error);
    } finally {
      setIsUploading(false);
    }
  }
  
  const isUploaded = files.length > 0 && files.every(f => f.progress === 100);

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <FolderOpen className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold tracking-tight font-headline">Evidence Locker</h1>
          <p className="text-muted-foreground">Upload, manage, and bundle your case evidence securely.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload Evidence</CardTitle>
          <CardDescription>Drag and drop files here, or click to select. Supported formats: PDF, JPG, PNG, TXT.</CardDescription>
        </CardHeader>
        <CardContent>
          <div {...getRootProps()} className={`flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer ${isDragActive ? 'border-primary bg-primary/10' : 'bg-card hover:bg-muted'}`}>
            <input {...getInputProps()} />
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <UploadCloud className="w-10 h-10 mb-3 text-muted-foreground" />
              <p className="mb-2 text-sm text-muted-foreground">
                <span className="font-semibold">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-muted-foreground">PDF, PNG, JPG, TXT</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>File Queue</CardTitle>
            <CardDescription>Review your selected files before uploading.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {files.map(fileWrapper => (
              <div key={fileWrapper.id} className="flex items-center gap-4 p-2 border rounded-lg">
                <FileText className="h-6 w-6 text-muted-foreground" />
                <div className="flex-grow">
                  <p className="font-medium">{fileWrapper.file.name}</p>
                  <p className="text-sm text-muted-foreground">{(fileWrapper.file.size / 1024).toFixed(2)} KB</p>
                   {isUploading || fileWrapper.progress > 0 && (
                       <Progress value={fileWrapper.progress} className="w-full mt-1" />
                    )}
                </div>
                <Button variant="ghost" size="icon" onClick={() => removeFile(fileWrapper.id)} disabled={isUploading}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </CardContent>
          <CardFooter className="flex-wrap gap-4">
            <Button onClick={handleUpload} disabled={isUploading || isUploaded}>
              {isUploading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin"/> Uploading...</> : isUploaded ? 'Uploaded' : 'Upload and Save Files'}
            </Button>
            <Button variant="outline" disabled={!isUploaded}>
                <Package className="mr-2 h-4 w-4" />
                Download as Court-Ready Bundle
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}
