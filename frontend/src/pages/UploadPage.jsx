import React, { useRef, useState } from "react";
import { uploadExcel } from "../api.js";
import "./UploadPage.css";

const ACCEPTED_EXTENSIONS = [".xlsx", ".xls"];

function isExcelFile(file) {
  const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
  return ACCEPTED_EXTENSIONS.includes(extension);
}

function UploadPage({ onFileSelected }) {
  const inputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const chooseFile = async (file) => {
    if (!file) return;

    if (!isExcelFile(file)) {
      setSelectedFile(null);
      setError("Selecciona un archivo de Excel con formato .xlsx o .xls.");
      if (inputRef.current) inputRef.current.value = "";
      return;
    }

    setSelectedFile(file);
    setError("");
    setUploading(true);

    try {
      const result = await uploadExcel(file);
      onFileSelected?.({
        file,
        uploadId: result.upload_id,
        processingId: result.processing_id,
        totalCases: result.total_cases ?? null,
      });
    } catch (err) {
      setUploading(false);
      setError(err.message || "No se pudo cargar el archivo. Verifica que el backend esté activo.");
      setSelectedFile(null);
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    chooseFile(event.dataTransfer.files?.[0]);
  };

  return (
    <main className="upload-page">
      <div className="upload-page__glow upload-page__glow--top" aria-hidden="true" />
      <div className="upload-page__glow upload-page__glow--bottom" aria-hidden="true" />

      <section className="upload-content" aria-labelledby="project-title">
        <div className="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 40 40" fill="none">
            <path d="M11 12.5h18M11 20h12M11 27.5h8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
            <path d="m25 24 3.5 3.5L35 20" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>

        <p className="upload-eyebrow">GESTIÓN DE PROYECTOS</p>
        <h1 className="project-title" id="project-title">Bot-ComProject</h1>
        <p className="upload-intro">
          Comienza cargando el archivo de casos para preparar tu reporte.
        </p>

        <div
          className={`upload-card${isDragging ? " upload-card--dragging" : ""}${selectedFile ? " upload-card--selected" : ""}`}
          onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
          onDragOver={(event) => event.preventDefault()}
          onDragLeave={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget)) setIsDragging(false);
          }}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            className="upload-input"
            id="excel-file"
            type="file"
            accept=".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"
            onChange={(event) => chooseFile(event.target.files?.[0])}
            aria-describedby="upload-hint upload-error"
            disabled={uploading}
          />

          <label className="upload-card__label" htmlFor="excel-file">
            <span className="upload-icon" aria-hidden="true">
              {uploading ? (
                <svg viewBox="0 0 32 32" fill="none" className="upload-icon__spinner">
                  <circle cx="16" cy="16" r="10" stroke="currentColor" strokeWidth="2.4" strokeOpacity="0.35" />
                  <path d="M26 16a10 10 0 0 0-10-10" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
                </svg>
              ) : selectedFile ? (
                <svg viewBox="0 0 32 32" fill="none">
                  <path d="m8 16.5 5.2 5.2L24.5 10" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              ) : (
                <svg viewBox="0 0 32 32" fill="none">
                  <path d="M16 21V7m0 0-5 5m5-5 5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M8 20v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                </svg>
              )}
            </span>

            <span className="upload-card__title">
              {uploading ? "Cargando archivo…" : selectedFile ? "Archivo listo para cargar" : "Selecciona tu archivo Excel"}
            </span>
            <span className="upload-card__description">
              {uploading ? "Subiendo y procesando el maestro de casos" : selectedFile ? selectedFile.name : "Arrástralo aquí o búscalo en tu equipo"}
            </span>
            <span className="upload-button">
              {uploading ? "Subiendo…" : selectedFile ? "Cambiar archivo" : "Elegir archivo"}
            </span>
          </label>

          <p className="upload-hint" id="upload-hint">Formatos compatibles: <strong>.xlsx</strong> y <strong>.xls</strong></p>
        </div>

        <p className={`upload-error${error ? " upload-error--visible" : ""}`} id="upload-error" role="alert">
          {error || " "}
        </p>
        <p className="upload-footer">Tu archivo se utilizará para generar información del proyecto.</p>
      </section>
    </main>
  );
}

export default UploadPage;