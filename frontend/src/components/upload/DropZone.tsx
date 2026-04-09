"use client";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion } from "framer-motion";
import { Upload, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { uploadFile, getStatus } from "@/lib/api";

export function DropZone() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState<string>("");

  const onDrop = useCallback(async (files: File[]) => {
    const f = files[0];
    if (!f) return;
    if (!f.name.toLowerCase().endsWith(".txt")) {
      toast.error("Please upload a .txt WhatsApp export");
      return;
    }
    if (f.size > 50 * 1024 * 1024) {
      toast.error("Max file size is 50 MB");
      return;
    }
    setBusy(true);
    setStage("Uploading...");
    try {
      const { session_id } = await uploadFile(f);
      setStage("Parsing messages...");
      // Poll status
      for (let i = 0; i < 120; i++) {
        const s = await getStatus(session_id);
        if (s.status === "done") {
          setStage("Opening dashboard...");
          router.push(`/analyze/${session_id}`);
          return;
        }
        if (s.status === "error") {
          toast.error(s.error || "Analysis failed");
          setBusy(false);
          return;
        }
        await new Promise((r) => setTimeout(r, 1200));
      }
      toast.error("Analysis timed out");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Upload failed");
    } finally {
      setBusy(false);
    }
  }, [router]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/plain": [".txt"] },
    maxFiles: 1,
    disabled: busy,
  });

  return (
    <motion.div
      whileHover={{ scale: busy ? 1 : 1.01 }}
      {...getRootProps()}
      className={`glass ring-brand cursor-pointer p-10 md:p-14 text-center transition-all
        ${isDragActive ? "border-brand scale-[1.02]" : ""}
        ${busy ? "opacity-80 cursor-wait" : "hover:border-brand/50"}`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        {busy ? (
          <Loader2 className="w-10 h-10 text-brand animate-spin" />
        ) : (
          <Upload className="w-10 h-10 text-brand" />
        )}
        <div className="text-lg font-medium">
          {busy ? stage : isDragActive ? "Drop the file here" : "Drop your WhatsApp chat export"}
        </div>
        <div className="text-xs text-white/50">
          .txt only · max 50 MB · processed locally
        </div>
      </div>
    </motion.div>
  );
}
