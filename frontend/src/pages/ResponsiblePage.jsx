import React, { useEffect, useState } from "react";
import { getResponsibles } from "../api.js";
import "./ResponsiblePage.css";

const FILE_EXTENSIONS = [".xlsx", ".xls"];

function fileName(file) {
  if (!file) return "";
  return file.file?.name || file.name || "";
}

function ResponsiblePage({ file, onBack, onGenerate }) {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState("");
  const [selectedResponsible, setSelectedResponsible] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");

    getResponsibles(file?.uploadId)
      .then((data) => {
        if (!active) return;
        const groupList = data.groups || [];
        setGroups(groupList);
        if (groupList.length > 0) {
          setSelectedGroup(groupList[0].group);
        }
      })
      .catch((err) => {
        if (!active) return;
        setError(err.message || "No se pudieron cargar los responsables.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [file?.uploadId]);

  const handleGroupChange = (group) => {
    setSelectedGroup(group);
    setSelectedResponsible("");
    setNotice("");
  };

  const currentGroup = groups.find((g) => g.group === selectedGroup);
  const responsibleOptions = currentGroup?.responsibles || [];

  return (
    <main className="upload-page responsible-page">
      <div className="upload-page__glow upload-page__glow--top" aria-hidden="true" />
      <div className="upload-page__glow upload-page__glow--bottom" aria-hidden="true" />

      <section className="responsible-content" aria-labelledby="responsible-title">
        <button className="responsible-back" type="button" onClick={onBack}>
          <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="m12.5 4.5-5.5 5.5 5.5 5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Volver
        </button>

        <div className="responsible-brand-mark" aria-hidden="true">
          <svg viewBox="0 0 40 40" fill="none">
            <path d="M11 12.5h18M11 20h12M11 27.5h8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
            <path d="m25 24 3.5 3.5L35 20" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>

        <p className="upload-eyebrow">PASO 2 DE 3</p>
        <h1 className="project-title" id="responsible-title">Bot-ComProject</h1>
        <p className="responsible-intro">Elige el grupo y el responsable para continuar.</p>

        <div className="responsible-file" title={fileName(file)}>
          <span className="responsible-file__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M7 3.75h7l4 4v12.5H7a2 2 0 0 1-2-2V5.75a2 2 0 0 1 2-2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
              <path d="M14 3.75v4.5h4.5M8.5 13h7M8.5 16.5h7" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
          </span>
          <span className="responsible-file__name">{fileName(file)}</span>
          <span className="responsible-file__status">{loading ? "Cargando…" : "Listo"}</span>
        </div>

        {error && (
          <p className="responsible-error" role="alert">
            {error}
          </p>
        )}

        <div className="responsible-card">
          <div className="responsible-section">
            <div className="responsible-section__heading">
              <span className="responsible-step">01</span>
              <div>
                <h2>Grupo de atención</h2>
                <p>Selecciona el grupo que atenderá los casos.</p>
              </div>
            </div>
            {loading ? (
              <p className="responsible-loading">Cargando grupos…</p>
            ) : (
              <div className="group-options" role="group" aria-label="Grupo de atención">
                {groups.map((group) => (
                  <button
                    className={`group-option${selectedGroup === group.group ? " group-option--selected" : ""}`}
                    type="button"
                    key={group.group}
                    aria-pressed={selectedGroup === group.group}
                    onClick={() => handleGroupChange(group.group)}
                  >
                    <span className="group-option__radio" aria-hidden="true">
                      {selectedGroup === group.group && <span />}
                    </span>
                    {group.group}
                    <span className="group-option__count">{group.total_cases} casos</span>
                  </button>
                ))}
                {groups.length === 0 && !loading && (
                  <p className="responsible-empty">No se encontraron grupos para este archivo.</p>
                )}
              </div>
            )}
          </div>

          <div className="responsible-divider" />

          <div className="responsible-section">
            <div className="responsible-section__heading">
              <span className="responsible-step">02</span>
              <div>
                <h2>Responsable</h2>
                <p>¿Quién estará a cargo de estos casos?</p>
              </div>
            </div>
            {loading ? (
              <p className="responsible-loading">Cargando responsables…</p>
            ) : (
              <div className="person-options" role="group" aria-label="Responsable">
                {responsibleOptions.map((person, index) => (
                  <button
                    className={`person-option${selectedResponsible === person.name ? " person-option--selected" : ""}`}
                    type="button"
                    key={person.name}
                    aria-pressed={selectedResponsible === person.name}
                    onClick={() => {
                      setSelectedResponsible(person.name);
                      setNotice("");
                    }}
                  >
                    <span className="person-avatar" aria-hidden="true">{person.name.split(" ").slice(0, 2).map((part) => part[0]).join("")}</span>
                    <span className="person-option__name">{person.name}</span>
                    <span className="person-option__cases">{person.total_cases} casos</span>
                    <span className="person-option__radio" aria-hidden="true">
                      {selectedResponsible === person.name && <span />}
                    </span>
                    <span className="sr-only">Opción {index + 1}</span>
                  </button>
                ))}
                {responsibleOptions.length === 0 && !loading && (
                  <p className="responsible-empty">Este grupo no tiene responsables asignados.</p>
                )}
              </div>
            )}
          </div>

          <button
            className="generate-button"
            type="button"
            disabled={!selectedResponsible || loading}
            onClick={() => onGenerate?.({
              file,
              group: selectedGroup,
              responsible: selectedResponsible,
            })}
          >
            Generar reporte
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M4 10h11m-4.5-4.5L15 10l-4.5 4.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <p className="generate-notice" role="status">{notice || " "}</p>
        </div>
        <p className="sample-data-note">Grupos y responsables obtenidos del maestro de casos cargado.</p>
      </section>
    </main>
  );
}

export default ResponsiblePage;